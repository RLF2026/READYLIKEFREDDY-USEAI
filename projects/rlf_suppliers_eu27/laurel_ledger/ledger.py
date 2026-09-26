"""Laurel Ledger: les dues mil set-centes unitats territorials del motor.

Implementa §3.3.9 i §3.3.13 del document mestre canonic v2.6.0.

El Laurel Ledger es una matriu de cent localitats per vint-i-set estats de la
UE, que dona dues mil set-centes unitats territorials. Les unitats son
independents i es poden posar en cua simultaniament: els vint-i-set paisos
poden tenir treball actiu al mateix temps, subjecte a la capacitat real de
workers i a les regles de cortesia per domini.

El registre canonic es global: una mateixa empresa no pot comptar dues vegades
perque aparegui en diverses ciutats, dominis o fonts.
"""

from typing import Any, Optional

from shared.rlf_core.contract.return_contract import (
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.lanes.lane_assigner import (
    LAUREL_LEDGER_LOCALITIES,
    LAUREL_LEDGER_UNITS,
    assign_lane,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

EU27_COUNTRIES: tuple[str, ...] = (
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
)

EXHAUSTION_PENDING: str = "pending"
EXHAUSTION_EXHAUSTED: str = "exhausted"

UNIT_SEPARATOR: str = "::"

logger = get_logger(__name__)


class LedgerUnit:
    """Una unitat territorial del Laurel Ledger."""

    def __init__(self, country: str, locality: str) -> None:
        """Inicialitza una unitat territorial.

        Args:
            country: Codi de pais, dins la UE-27.
            locality: Nom de la localitat.
        """
        self.country = country
        self.locality = locality
        self.unit_id = f"{country}{UNIT_SEPARATOR}{locality}"
        self.lane = assign_lane(self.unit_id)
        self.cursor: Optional[str] = None
        self.exhaustion = EXHAUSTION_PENDING
        self.results: list[dict[str, Any]] = []
        self.sources_consulted: list[str] = []
        self.errors: list[str] = []
        self.checkpoint: Optional[str] = None
        self.last_update: Optional[str] = None
        self.wilson_lower: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        """Retorna la unitat com a diccionari.

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
            "results": len(self.results),
            "sources_consulted": list(self.sources_consulted),
            "errors": list(self.errors),
            "checkpoint": self.checkpoint,
            "last_update": self.last_update,
            "wilson_lower": self.wilson_lower,
        }


class LaurelLedger:
    """La matriu de dues mil set-centes unitats territorials (§3.3.9)."""

    def __init__(self, localities: Optional[list[str]] = None) -> None:
        """Inicialitza el Laurel Ledger.

        Args:
            localities: Localitats base que es creuaran amb els vint-i-set
                estats. Si no es donen, la matriu queda buida.

        Raises:
            ValueError: Si es donen mes localitats de les cent canoniques.
        """
        if localities is not None and len(localities) > LAUREL_LEDGER_LOCALITIES:
            raise ValueError(
                f"El Laurel Ledger admet com a maxim {LAUREL_LEDGER_LOCALITIES} localitats"
            )
        self.localities: list[str] = list(localities or [])
        self._units: dict[str, LedgerUnit] = {}

    def build(self, localities: list[str]) -> dict[str, Any]:
        """Construeix la matriu creuant localitats amb els vint-i-set estats.

        Args:
            localities: Localitats base.

        Returns:
            Un resultat canonic SUCCESS amb el nombre d'unitats creades.
            REJECT si la llista es buida, supera les cent localitats o conte
            duplicats.
        """
        if not localities:
            return make_reject("Cal almenys una localitat per construir la matriu")
        if len(localities) > LAUREL_LEDGER_LOCALITIES:
            return make_reject(
                "Massa localitats per a la matriu canonica",
                meta={"given": len(localities), "maximum": LAUREL_LEDGER_LOCALITIES},
            )
        if len(set(localities)) != len(localities):
            return make_reject("Hi ha localitats duplicades a la llista")

        self.localities = list(localities)
        self._units.clear()

        for country in EU27_COUNTRIES:
            for locality in self.localities:
                unit = LedgerUnit(country, locality)
                self._units[unit.unit_id] = unit

        logger.info("laurel_ledger_built", units=len(self._units))
        return make_success(
            {
                "units": len(self._units),
                "localities": len(self.localities),
                "countries": len(EU27_COUNTRIES),
            },
            meta={"source": "S3.3.9"},
        )

    def get(self, unit_id: str) -> dict[str, Any]:
        """Retorna una unitat territorial pel seu identificador.

        Args:
            unit_id: Identificador de la unitat.

        Returns:
            Un resultat canonic SUCCESS amb la unitat. HOLD si no existeix.
        """
        unit = self._units.get(unit_id)
        if unit is None:
            return make_hold("Unitat no trobada", meta={"unit_id": unit_id})
        return make_success(unit.as_dict())

    def by_country(self, country: str) -> dict[str, Any]:
        """Retorna les unitats d'un pais.

        Args:
            country: Codi de pais.

        Returns:
            Un resultat canonic SUCCESS amb les unitats del pais. REJECT si el
            pais no pertany a la UE-27.
        """
        code = (country or "").strip().upper()
        if code not in EU27_COUNTRIES:
            return make_reject("El pais no pertany a la UE-27", meta={"country": code})

        units = [unit.as_dict() for unit in self._units.values() if unit.country == code]
        return make_success(
            {"units": units}, meta={"country": code, "count": len(units)}
        )

    def update_priority(self, unit_id: str, wilson_lower: float) -> dict[str, Any]:
        """Actualitza la cota inferior de Wilson d'una unitat (§3.3.13).

        Args:
            unit_id: Identificador de la unitat.
            wilson_lower: Cota inferior de confianca, de zero a u.

        Returns:
            Un resultat canonic SUCCESS amb la unitat actualitzada. HOLD si no
            existeix. REJECT si la cota es fora d'interval.
        """
        if not 0.0 <= wilson_lower <= 1.0:
            return make_reject(
                "La cota de Wilson ha de ser dins l'interval de zero a u",
                meta={"wilson_lower": wilson_lower},
            )

        unit = self._units.get(unit_id)
        if unit is None:
            return make_hold("Unitat no trobada", meta={"unit_id": unit_id})

        unit.wilson_lower = float(wilson_lower)
        return make_success(unit.as_dict())

    def mark_exhausted(self, unit_id: str) -> dict[str, Any]:
        """Marca una unitat com a esgotada.

        Args:
            unit_id: Identificador de la unitat.

        Returns:
            Un resultat canonic SUCCESS amb la unitat actualitzada. HOLD si no
            existeix.
        """
        unit = self._units.get(unit_id)
        if unit is None:
            return make_hold("Unitat no trobada", meta={"unit_id": unit_id})

        unit.exhaustion = EXHAUSTION_EXHAUSTED
        return make_success(unit.as_dict())

    def statistics(self) -> dict[str, Any]:
        """Resumeix l'estat de la matriu.

        Returns:
            Un resultat canonic SUCCESS amb els recomptes d'unitats, esgotades,
            paisos amb treball i lanes en us, mes el total canonic de dues mil
            set-centes unitats.
        """
        exhausted = sum(
            1 for unit in self._units.values() if unit.exhaustion == EXHAUSTION_EXHAUSTED
        )
        countries = {unit.country for unit in self._units.values()}
        lanes = {unit.lane for unit in self._units.values()}

        return make_success(
            {
                "units": len(self._units),
                "canonical_units": LAUREL_LEDGER_UNITS,
                "exhausted": exhausted,
                "countries_with_work": len(countries),
                "lanes_in_use": len(lanes),
            },
            meta={"all_countries_can_work_simultaneously": True, "source": "S3.3.9"},
        )
