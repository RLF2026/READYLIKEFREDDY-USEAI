"""Orquestrador del motor de sourcing. Autoritat operativa del sistema.

Implementa §2.2.5, §3.3.6 i §3.3.7 del document mestre canonic v2.6.0.

L'orquestrador es l'autoritat operativa del motor: carrega l'estat, distribueix
la feina entre les lanes, recull els resultats, consolida i actualitza els
cursors. El flux canonic de §3.3.7 es inicialitzacio, assignacio, execucio,
recollida, consolidacio, actualitzacio i repeticio.

L'orquestrador no decideix sobre el contingut de les dades: nomes reparteix
treball, verifica idempotencia i manté l'estat. Cap decisio d'elegibilitat, de
scoring ni de seleccio es pren aqui.
"""

from typing import Any, Callable, Optional

from shared.rlf_core.contract.return_contract import (
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.hashing.idempotency import MemoryLedger, apply_idempotent
from shared.rlf_core.lanes.lane_assigner import LANE_COUNT, assign_lane
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

PHASE_INITIALISATION: str = "initialisation"
PHASE_ASSIGNMENT: str = "assignment"
PHASE_EXECUTION: str = "execution"
PHASE_COLLECTION: str = "collection"
PHASE_CONSOLIDATION: str = "consolidation"
PHASE_UPDATE: str = "update"

CANONICAL_PHASES: tuple[str, ...] = (
    PHASE_INITIALISATION,
    PHASE_ASSIGNMENT,
    PHASE_EXECUTION,
    PHASE_COLLECTION,
    PHASE_CONSOLIDATION,
    PHASE_UPDATE,
)

WORKER_IDLE: str = "idle"
WORKER_BUSY: str = "busy"
WORKER_ISOLATED: str = "isolated"

OUTCOME_APPLIED: str = "applied"

logger = get_logger(__name__)


class Worker:
    """Un worker del motor de sourcing.

    El worker executa unitats de treball d'una lane. No pren decisions de
    politica: nomes executa allo que l'orquestrador li assigna.
    """

    def __init__(self, worker_id: str, capacity: int = 1) -> None:
        """Inicialitza un worker.

        Args:
            worker_id: Identificador unic del worker.
            capacity: Nombre d'unitats que pot tenir en curs alhora.

        Raises:
            ValueError: Si l'identificador es buit o la capacitat no es positiva.
        """
        if not worker_id:
            raise ValueError("L'identificador del worker no pot ser buit")
        if capacity <= 0:
            raise ValueError("La capacitat ha de ser positiva")
        self.worker_id = worker_id
        self.capacity = capacity
        self.status = WORKER_IDLE
        self.assigned: list[int] = []
        self.completed = 0
        self.failures = 0

    def can_accept(self) -> bool:
        """Indica si el worker te capacitat per a mes feina.

        Returns:
            True si no esta aillat i el nombre d'unitats assignades es inferior
            a la seva capacitat.
        """
        return self.status != WORKER_ISOLATED and len(self.assigned) < self.capacity

    def as_dict(self) -> dict[str, Any]:
        """Retorna el worker com a diccionari.

        Returns:
            Un diccionari amb l'estat complet del worker.
        """
        return {
            "worker_id": self.worker_id,
            "capacity": self.capacity,
            "status": self.status,
            "assigned": list(self.assigned),
            "completed": self.completed,
            "failures": self.failures,
        }


class Orchestrator:
    """Orquestrador del motor de sourcing, segons §2.2.5."""

    def __init__(self, workers: Optional[list[Worker]] = None) -> None:
        """Inicialitza l'orquestrador.

        Args:
            workers: Workers disponibles. Si no es donen, no n'hi ha cap.
        """
        self.workers: dict[str, Worker] = {
            worker.worker_id: worker for worker in (workers or [])
        }
        self.ledger = MemoryLedger()
        self.phase = PHASE_INITIALISATION
        self._cursor: dict[int, Optional[str]] = {
            lane: None for lane in range(1, LANE_COUNT + 1)
        }
        self._assignments: dict[int, str] = {}

    def register_worker(self, worker: Worker) -> dict[str, Any]:
        """Registra un worker a l'orquestrador.

        Args:
            worker: Worker a registrar.

        Returns:
            Un resultat canonic SUCCESS amb el worker. REJECT si ja existia un
            worker amb aquell identificador.
        """
        if worker.worker_id in self.workers:
            return make_reject(
                "Ja existeix un worker amb aquest identificador",
                meta={"worker_id": worker.worker_id},
            )
        self.workers[worker.worker_id] = worker
        return make_success(worker.as_dict())

    def advance_phase(self, phase: str) -> dict[str, Any]:
        """Avança el cicle de l'orquestrador a una fase concreta.

        Les fases avancen en l'ordre canonic de §3.3.7 i no es pot retrocedir.

        Args:
            phase: Fase de desti.

        Returns:
            Un resultat canonic SUCCESS amb la fase nova. REJECT si la fase no
            es canonica o si trenca l'ordre del cicle.
        """
        if phase not in CANONICAL_PHASES:
            return make_reject(
                "Fase no canonica", meta={"phase": phase, "allowed": CANONICAL_PHASES}
            )

        current_index = CANONICAL_PHASES.index(self.phase)
        target_index = CANONICAL_PHASES.index(phase)
        if target_index < current_index:
            return make_reject(
                "No es pot retrocedir en el cicle de l'orquestrador",
                meta={"from": self.phase, "to": phase},
            )

        self.phase = phase
        logger.info("orchestrator_phase", phase=phase)
        return make_success({"phase": phase})

    def assign_work(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        """Distribueix unitats de treball entre les lanes i els workers.

        Cada unitat va a la lane que li pertoca per la seva clau canonica, i
        dins de la lane al primer worker amb capacitat. Si no hi ha cap worker
        amb capacitat, la unitat queda sense assignar i el resultat es HOLD.

        Args:
            items: Unitats de treball, cada una amb les claus sequence, action,
                country i cursor.

        Returns:
            Un resultat canonic SUCCESS amb les assignacions fetes. HOLD si
            alguna unitat queda sense assignar per manca de capacitat. REJECT
            si alguna unitat no porta sequencia o pais.
        """
        if not items:
            return make_reject("No hi ha unitats a distribuir")

        assigned: list[dict[str, Any]] = []
        unassigned: list[int] = []

        for item in items:
            sequence = item.get("sequence")
            country = item.get("country", "")
            cursor = item.get("cursor", "")
            action = item.get("action", "")

            if sequence is None or not country:
                return make_reject(
                    "Una unitat no te sequencia o pais", meta={"item": item}
                )

            lane = assign_lane(f"{country}::{cursor}::{action}")
            worker = self._first_available_worker()

            if worker is None:
                unassigned.append(sequence)
                continue

            worker.assigned.append(sequence)
            worker.status = WORKER_BUSY
            self._assignments[sequence] = worker.worker_id
            assigned.append(
                {"sequence": sequence, "lane": lane, "worker": worker.worker_id}
            )

        self.phase = PHASE_ASSIGNMENT
        payload = {"assigned": assigned, "unassigned": unassigned}

        if unassigned:
            logger.warning("orchestrator_capacity_shortfall", unassigned=len(unassigned))
            return make_hold(
                "Capacitat insuficient: algunes unitats queden sense assignar",
                meta=payload,
            )

        return make_success(payload, meta={"assigned": len(assigned)})

    def execute(self, sequence: int, operation: Callable[[], Any]) -> dict[str, Any]:
        """Executa una unitat de treball de manera idempotent.

        Reintentar la mateixa unitat no duplica efectes: la segona execucio es
        resol com a replayed-noop, segons §4.3.2.

        Args:
            sequence: Numero de sequencia de la unitat.
            operation: Funcio sense arguments que executa la unitat.

        Returns:
            Un resultat canonic SUCCESS amb el resultat i l'outcome. HOLD si la
            unitat no te cap worker assignat. FAILURE si l'operacio falla.
        """
        worker_id = self._assignments.get(sequence)
        if worker_id is None:
            return make_hold(
                "La unitat no te cap worker assignat", meta={"sequence": sequence}
            )

        outcome = apply_idempotent(self.ledger, f"orchestrator::{sequence}", operation)
        if outcome["status"] != "SUCCESS":
            return outcome

        worker = self.workers[worker_id]
        if outcome["data"]["outcome"] == OUTCOME_APPLIED:
            worker.completed += 1
        if sequence in worker.assigned:
            worker.assigned.remove(sequence)
        if not worker.assigned:
            worker.status = WORKER_IDLE

        self.phase = PHASE_EXECUTION
        return outcome

    def collect(self) -> dict[str, Any]:
        """Recull l'estat dels workers i consolida el resultat del cicle.

        Returns:
            Un resultat canonic SUCCESS amb l'estat de tots els workers i els
            recomptes de completades, fallades, ocupats i lliures.
        """
        self.phase = PHASE_COLLECTION
        total_completed = sum(worker.completed for worker in self.workers.values())
        total_failures = sum(worker.failures for worker in self.workers.values())
        busy = sum(
            1 for worker in self.workers.values() if worker.status == WORKER_BUSY
        )

        return make_success(
            {
                "workers": [worker.as_dict() for worker in self.workers.values()],
                "completed": total_completed,
                "failures": total_failures,
                "busy": busy,
                "idle": len(self.workers) - busy,
            },
            meta={"phase": self.phase},
        )

    def update_cursor(self, lane: int, position: str) -> dict[str, Any]:
        """Actualitza el cursor d'una lane.

        Cada lane te un cursor independent, de manera que dues lanes no
        consumeixen mai el mateix espai de treball, segons §3.3.6.

        Args:
            lane: Numero de lane, de 1 a 100.
            position: Posicio nova del cursor.

        Returns:
            Un resultat canonic SUCCESS amb el cursor anterior i el nou. REJECT
            si la lane es fora de rang o la posicio es buida.
        """
        if not 1 <= lane <= LANE_COUNT:
            return make_reject("Lane fora de rang", meta={"lane": lane})
        if not position:
            return make_reject("La posicio no pot ser buida")

        previous = self._cursor.get(lane)
        self._cursor[lane] = position
        self.phase = PHASE_UPDATE
        return make_success({"lane": lane, "previous": previous, "position": position})

    def cursors(self) -> dict[str, Any]:
        """Retorna l'estat de tots els cursors actius.

        Returns:
            Un resultat canonic SUCCESS amb el mapa de lanes a posicions i el
            recompte de cursors actius sobre el total de cent lanes.
        """
        active = {lane: pos for lane, pos in self._cursor.items() if pos is not None}
        return make_success(
            {"cursors": active},
            meta={"active": len(active), "total_lanes": LANE_COUNT},
        )

    def _first_available_worker(self) -> Optional[Worker]:
        """Retorna el primer worker amb capacitat disponible.

        Returns:
            El worker, o None si cap en te.
        """
        for worker in self.workers.values():
            if worker.can_accept():
                return worker
        return None

    def statistics(self) -> dict[str, Any]:
        """Resumeix l'estat de l'orquestrador.

        Returns:
            Un resultat canonic SUCCESS amb la fase actual, el nombre de
            workers, les unitats assignades i les operacions registrades.
        """
        return make_success(
            {
                "phase": self.phase,
                "workers": len(self.workers),
                "assigned_units": len(self._assignments),
                "operations_recorded": len(list(self.ledger.keys())),
            },
            meta={"source": "S2.2.5"},
        )
