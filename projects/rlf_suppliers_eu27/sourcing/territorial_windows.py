"""Finestres territorials del motor de sourcing.

Implementa §3.3.2 i §3.3.3 del document mestre canonic v2.6.0.

La unitat territorial es descriu com a pais, regio, ciutat, conjunt de cerques,
lane i resultat. La metodologia d'esgotament de §3.3.3 diu que una ciutat es
considera explorada quan ha completat el protocol de cerques, **amb
independencia dels resultats**: el que compta es haver-les fetes, no que donin
fruit.
"""

import hashlib
from typing import Any, Optional

from shared.rlf_core.contract.return_contract import (
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.lanes.lane_assigner import assign_lane
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

EXHAUSTION_PENDING: str = "pending"
EXHAUSTION_IN_PROGRESS: str = "in_progress"
EXHAUSTION_EXHAUSTED: str = "exhausted"

SEPARATOR: str = "::"

logger = get_logger(__name__)


class TerritorialWindow:
    """Una unitat territorial del motor de sourcing (§3.3.2 i §3.3.9)."""

    def __init__(
        self,
        country: str,
        locality: str,
        search_protocol: Optional[list[str]] = None,
    ) -> None:
        """Inicialitza una finestra territorial.

        Args:
            country: Codi de pais, dins la UE-27.
            locality: Nom de la ciutat o localitat.
            search_protocol: Conjunt de cerques del protocol. Si no es dona,
                el protocol queda buit i la unitat no es pot considerar
                explorada.
        """
        self.country = country
        self.locality = locality
        self.search_protocol: list[str] = list(search_protocol or [])
        self.completed_searches: list[str] = []
        self.cursor: Optional[str] = None
        self.exhaustion = EXHAUSTION_PENDING
        self.results: list[dict[str, Any]] = []
        self.errors: list[str] = []
        self.sources_consulted: list[str] = []
        self.checkpoint: Optional[str] = None
        self.last_update: Optional[str] = None
        self.unit_id = f"{country}{SEPARATOR}{locality}"
        self.lane = assign_lane(self.unit_id)

    def as_dict(self) -> dict[str, Any]:
        """Retorna la finestra com a diccionari.

        Returns:
            Un diccionari amb tots els camps de la unitat territorial.
        """
        return {
            "unit_id": self.unit_id,
            "country": self.country,
            "locality": self.locality,
            "lane": self.lane,
            "cursor": self.cursor,
            "exhaustion": self.exhaustion,
            "protocol_size": len(self.search_protocol),
            "completed_searches": len(self.completed_searches),
            "results": len(self.results),
            "errors": list(self.errors),
            "sources_consulted": list(self.sources_consulted),
            "checkpoint": self.checkpoint,
            "last_update": self.last_update,
            "exhausted": self.exhaustion == EXHAUSTION_EXHAUSTED,
        }

    def run_search(self, search: str, found: list[dict[str, Any]]) -> dict[str, Any]:
        """Executa una cerca del protocol i n'enregistra el resultat.

        La cerca compta com a feta encara que no trobi res, perque §3.3.3 fixa
        que l'esgotament depen del protocol completat i no dels resultats.

        Args:
            search: Cerca a executar.
            found: Resultats trobats, possiblement buits.

        Returns:
            Un resultat canonic SUCCESS amb l'estat de la unitat. REJECT si la
            cerca no pertany al protocol o si ja s'havia executat.
        """
        if search not in self.search_protocol:
            return make_reject(
                "La cerca no pertany al protocol d'aquesta unitat",
                meta={"unit_id": self.unit_id, "search": search},
            )
        if search in self.completed_searches:
            return make_reject(
                "La cerca ja s'havia executat",
                meta={"unit_id": self.unit_id, "search": search},
            )

        self.completed_searches.append(search)
        self.results.extend(found)
        self.exhaustion = EXHAUSTION_IN_PROGRESS
        self.cursor = search

        if len(self.completed_searches) >= len(self.search_protocol):
            self.exhaustion = EXHAUSTION_EXHAUSTED
            logger.info("territorial_unit_exhausted", unit_id=self.unit_id)

        return make_success(self.as_dict())

    def register_error(self, error: str) -> dict[str, Any]:
        """Enregistra un error d'execucio sense aturar la unitat.

        Args:
            error: Descripcio de l'error.

        Returns:
            Un resultat canonic SUCCESS amb la finestra actualitzada. REJECT si
            l'error es buit.
        """
        if not error:
            return make_reject("L'error no pot ser buit")
        self.errors.append(error)
        return make_success(self.as_dict())

    def set_checkpoint(self, checkpoint: str) -> dict[str, Any]:
        """Fixa el checkpoint de la unitat.

        Args:
            checkpoint: Identificador del checkpoint.

        Returns:
            Un resultat canonic SUCCESS amb la finestra actualitzada. REJECT si
            el checkpoint es buit.
        """
        if not checkpoint:
            return make_reject("El checkpoint no pot ser buit")
        self.checkpoint = checkpoint
        return make_success(self.as_dict())


class TerritorialWindows:
    """Conjunt de finestres territorials del motor principal i del Laurel Ledger."""

    def __init__(self, expected_protocol: Optional[list[str]] = None) -> None:
        """Inicialitza el conjunt de finestres.

        Args:
            expected_protocol: Protocol de cerques que s'aplicara a cada unitat
                que s'hi afegeixi sense protocol propi.
        """
        self.expected_protocol: list[str] = list(expected_protocol or [])
        self._windows: dict[str, TerritorialWindow] = {}

    def add(self, country: str, locality: str) -> dict[str, Any]:
        """Afegeix una unitat territorial.

        Args:
            country: Codi de pais.
            locality: Nom de la localitat.

        Returns:
            Un resultat canonic SUCCESS amb la unitat creada. REJECT si el pais
            o la localitat son buits o si la unitat ja existeix.
        """
        if not country or not locality:
            return make_reject("El pais i la localitat son obligatoris")

        unit_id = f"{country}{SEPARATOR}{locality}"
        if unit_id in self._windows:
            return make_reject("La unitat ja existeix", meta={"unit_id": unit_id})

        window = TerritorialWindow(country, locality, self.expected_protocol)
        self._windows[unit_id] = window
        return make_success(window.as_dict())

    def get(self, unit_id: str) -> dict[str, Any]:
        """Retorna una unitat territorial pel seu identificador.

        Args:
            unit_id: Identificador de la unitat.

        Returns:
            Un resultat canonic SUCCESS amb la unitat. HOLD si no existeix.
        """
        window = self._windows.get(unit_id)
        if window is None:
            return make_hold("Unitat no trobada", meta={"unit_id": unit_id})
        return make_success(window.as_dict())

    def by_lane(self, lane: int) -> dict[str, Any]:
        """Retorna les unitats assignades a una lane concreta.

        Args:
            lane: Numero de lane, de 1 a 100.

        Returns:
            Un resultat canonic SUCCESS amb les unitats de la lane.
        """
        units = [
            window.as_dict()
            for window in self._windows.values()
            if window.lane == lane
        ]
        return make_success({"units": units}, meta={"lane": lane, "count": len(units)})

    def exhausted(self) -> dict[str, Any]:
        """Retorna les unitats amb el protocol completat.

        Returns:
            Un resultat canonic SUCCESS amb les unitats esgotades i el recompte
            total.
        """
        done = [
            window.as_dict()
            for window in self._windows.values()
            if window.exhaustion == EXHAUSTION_EXHAUSTED
        ]
        return make_success(
            {"units": done},
            meta={"exhausted": len(done), "total": len(self._windows)},
        )

    def statistics(self) -> dict[str, Any]:
        """Resumeix l'estat del conjunt de finestres.

        Returns:
            Un resultat canonic SUCCESS amb els recomptes per estat d'esgotament
            i el nombre de lanes amb treball.
        """
        counts = {
            EXHAUSTION_PENDING: 0,
            EXHAUSTION_IN_PROGRESS: 0,
            EXHAUSTION_EXHAUSTED: 0,
        }
        lanes = set()
        for window in self._windows.values():
            counts[window.exhaustion] = counts.get(window.exhaustion, 0) + 1
            lanes.add(window.lane)

        return make_success(
            {
                "counts": counts,
                "total": len(self._windows),
                "lanes_in_use": len(lanes),
            },
            meta={"source": "S3.3.2, S3.3.3"},
        )

    def protocol_fingerprint(self) -> dict[str, Any]:
        """Calcula l'empremta del protocol de cerques.

        Returns:
            Un resultat canonic SUCCESS amb el SHA-256 del protocol, util per
            comprovar que totes les unitats segueixen el mateix patro.
        """
        payload = SEPARATOR.join(sorted(self.expected_protocol)).encode("utf-8")
        return make_success(
            {"fingerprint": hashlib.sha256(payload).hexdigest(), "size": len(self.expected_protocol)},
            meta={"source": "S3.3.3"},
        )
