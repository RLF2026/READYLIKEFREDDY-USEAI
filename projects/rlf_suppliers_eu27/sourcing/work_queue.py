"""Work Queue del motor de sourcing — cua de treball oberta i append-only.

Implementa §3.3.4 del document mestre canonic v2.6.0.

La cua de treball es **oberta i append-only**: no te sostre fix, continua
consumint blocs fins que el gate global de §3.3.12 queda tancat. Les cent lanes
son una particio de concurrencia i persistencia, no una quota de cobertura.

La cua no descarta mai cap unitat territorial: l'exhaustivitat de §3.3.1 es
manté sempre, i el que canvia amb §3.3.13 es nomes l'**ordre** de consum.
"""

from typing import Any, Optional

from shared.rlf_core.contract.return_contract import (
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.hashing.idempotency import build_idempotency_key
from shared.rlf_core.lanes.lane_assigner import assign_lane
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

STATUS_PENDING: str = "pending"
STATUS_CLAIMED: str = "claimed"
STATUS_DONE: str = "done"
STATUS_FAILED: str = "failed"

_SEP = "#"

logger = get_logger(__name__)


class WorkItem:
    """Una unitat de treball de la cua."""

    def __init__(
        self,
        sequence: int,
        action: str,
        country: str,
        cursor: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> None:
        """Inicialitza una unitat de treball.

        Args:
            sequence: Numero de sequencia global, assignat per la cua.
            action: Accio a executar.
            country: Pais o clau territorial.
            cursor: Cursor dins la unitat territorial.
            payload: Dades addicionals del treball.
        """
        self.sequence = sequence
        self.action = action
        self.country = country
        self.cursor = cursor
        self.payload = dict(payload or {})
        self.lane = assign_lane(f"{country}{_SEP}{cursor}{_SEP}{action}")
        self.status = STATUS_PENDING
        self.idempotency_key = build_idempotency_key(country, self.lane, cursor, action)
        self.result: Optional[Any] = None
        self.error: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        """Retorna la unitat com a diccionari.

        Returns:
            Un diccionari amb tots els camps de la unitat de treball.
        """
        return {
            "sequence": self.sequence,
            "action": self.action,
            "country": self.country,
            "cursor": self.cursor,
            "lane": self.lane,
            "status": self.status,
            "idempotency_key": self.idempotency_key,
            "payload": self.payload,
            "result": self.result,
            "error": self.error,
        }


class WorkQueue:
    """Cua de treball append-only del motor de sourcing."""

    def __init__(self) -> None:
        """Inicialitza una cua buida."""
        self._items: list[WorkItem] = []
        self._next_sequence = 1

    def append(
        self,
        action: str,
        country: str,
        cursor: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Afegeix una unitat de treball al final de la cua.

        Args:
            action: Accio a executar.
            country: Pais o clau territorial.
            cursor: Cursor dins la unitat territorial.
            payload: Dades addicionals.

        Returns:
            Un resultat canonic SUCCESS amb la unitat creada. REJECT si falten
            l'accio o el pais.
        """
        if not action or not country:
            return make_reject("L'accio i el pais son obligatoris")

        item = WorkItem(self._next_sequence, action, country, cursor, payload)
        self._items.append(item)
        self._next_sequence += 1

        return make_success(item.as_dict(), meta={"queue_size": len(self._items)})

    def pending(self, lane: Optional[int] = None) -> dict[str, Any]:
        """Retorna les unitats pendents, opcionalment filtrades per lane.

        Args:
            lane: Numero de lane, o None per a totes.

        Returns:
            Un resultat canonic SUCCESS amb les unitats pendents.
        """
        items = [
            item for item in self._items
            if item.status == STATUS_PENDING and (lane is None or item.lane == lane)
        ]
        return make_success(
            {"items": [item.as_dict() for item in items]},
            meta={"pending": len(items), "lane": lane},
        )

    def claim(self, sequence: int) -> dict[str, Any]:
        """Marca una unitat com a reclamada per un worker.

        Args:
            sequence: Numero de sequencia de la unitat.

        Returns:
            Un resultat canonic SUCCESS amb la unitat reclamada. HOLD si no es
            pendent. REJECT si la sequencia no existeix.
        """
        item = self._find(sequence)
        if item is None:
            return make_reject("Unitat no trobada", meta={"sequence": sequence})
        if item.status != STATUS_PENDING:
            return make_hold(
                "La unitat ja no es pendent",
                meta={"sequence": sequence, "status": item.status},
            )

        item.status = STATUS_CLAIMED
        return make_success(item.as_dict())

    def complete(self, sequence: int, result: Any) -> dict[str, Any]:
        """Marca una unitat com a completada amb el seu resultat.

        Args:
            sequence: Numero de sequencia de la unitat.
            result: Resultat de l'execucio.

        Returns:
            Un resultat canonic SUCCESS amb la unitat tancada. REJECT si la
            sequencia no existeix.
        """
        item = self._find(sequence)
        if item is None:
            return make_reject("Unitat no trobada", meta={"sequence": sequence})

        item.status = STATUS_DONE
        item.result = result
        return make_success(item.as_dict())

    def fail(self, sequence: int, error: str) -> dict[str, Any]:
        """Marca una unitat com a fallida amb el motiu.

        Args:
            sequence: Numero de sequencia de la unitat.
            error: Motiu de la fallada.

        Returns:
            Un resultat canonic SUCCESS amb la unitat marcada. REJECT si la
            sequencia no existeix.
        """
        item = self._find(sequence)
        if item is None:
            return make_reject("Unitat no trobada", meta={"sequence": sequence})

        item.status = STATUS_FAILED
        item.error = error
        return make_success(item.as_dict())

    def _find(self, sequence: int) -> Optional[WorkItem]:
        """Cerca una unitat pel seu numero de sequencia.

        Args:
            sequence: Numero de sequencia.

        Returns:
            La unitat, o None si no existeix.
        """
        for item in self._items:
            if item.sequence == sequence:
                return item
        return None

    def statistics(self) -> dict[str, Any]:
        """Resumeix l'estat de la cua.

        Returns:
            Un resultat canonic SUCCESS amb els recomptes per estat, el total
            i el nombre de lanes amb treball.
        """
        counts = {
            STATUS_PENDING: 0, STATUS_CLAIMED: 0, STATUS_DONE: 0, STATUS_FAILED: 0,
        }
        lanes = set()
        for item in self._items:
            counts[item.status] = counts.get(item.status, 0) + 1
            lanes.add(item.lane)

        return make_success(
            {"counts": counts, "total": len(self._items), "lanes_with_work": len(lanes)},
            meta={"append_only": True, "has_fixed_ceiling": False},
        )

    def idempotency_keys(self) -> dict[str, Any]:
        """Retorna les claus d'idempotencia de totes les unitats.

        Returns:
            Un resultat canonic SUCCESS amb les claus i el recompte de
            duplicats, per comprovar la propietat d'idempotencia de §4.3.2.
        """
        keys = [item.idempotency_key for item in self._items]
        unique = set(keys)
        return make_success(
            {"keys": keys},
            meta={
                "total": len(keys),
                "unique": len(unique),
                "duplicates": len(keys) - len(unique),
            },
        )
