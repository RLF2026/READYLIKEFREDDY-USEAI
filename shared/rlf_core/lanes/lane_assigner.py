"""Assignador de lanes determinista del sistema RLF.

Implementa S3.3.4 i S3.3.13 del document mestre canonic.
"""

import hashlib
from typing import Any, Iterable

from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.1"

LANE_ASSIGNER_VERSION: str = "1.1"
LANE_ASSIGNER_SALT: str = "lane_assigner/1.1"
LANE_COUNT: int = 100

LAUREL_LEDGER_LOCALITIES: int = 100
LAUREL_LEDGER_STATES: int = 27
LAUREL_LEDGER_UNITS: int = LAUREL_LEDGER_LOCALITIES * LAUREL_LEDGER_STATES

_SEPARATOR = "|"

logger = get_logger(__name__)


def assign_lane(canonical_key: str) -> int:
    if not canonical_key:
        raise ValueError("La clau canonica no pot ser buida")
    if _SEPARATOR in canonical_key:
        raise ValueError("El separador es reservat a la clau canonica")

    payload = f"{LANE_ASSIGNER_SALT}{_SEPARATOR}{canonical_key}".encode("utf-8")
    big_integer = int.from_bytes(hashlib.sha256(payload).digest(), byteorder="big")
    return (big_integer % LANE_COUNT) + 1


def distribute(keys: Iterable[str]) -> dict[str, Any]:
    try:
        buckets: dict[str, list[str]] = {str(i): [] for i in range(1, LANE_COUNT + 1)}
        for key in keys:
            if not key:
                return make_reject("Una clau canonica es buida")
            buckets[str(assign_lane(key))].append(key)

        used = sum(1 for lane in buckets.values() if lane)
        return make_success(
            {"lanes": buckets},
            meta={"assigned": sum(len(v) for v in buckets.values()), "lanes_used": used},
        )
    except ValueError as exception:
        return make_reject(str(exception))
    except Exception as exception:
        logger.critical("distribute_unexpected", error=str(exception))
        return make_failure(
            f"Excepcio inesperada: {exception}",
            meta={"exception_type": type(exception).__name__},
        )


class PriorityQueue:
    def __init__(self) -> None:
        self._units: dict[str, dict[str, Any]] = {}

    def add(self, unit_id: str, cursor_exhausted: bool, wilson_lower: float) -> dict[str, Any]:
        if not unit_id:
            return make_reject("L'identificador d'unitat no pot ser buit")
        if not 0.0 <= wilson_lower <= 1.0:
            return make_reject(
                "La cota de Wilson ha de ser dins [0,1]", meta={"wilson_lower": wilson_lower}
            )

        self._units[unit_id] = {
            "unit_id": unit_id,
            "cursor_exhausted": bool(cursor_exhausted),
            "wilson_lower": float(wilson_lower),
        }
        return make_success(dict(self._units[unit_id]))

    def next_unit(self) -> dict[str, Any]:
        active = [u for u in self._units.values() if not u["cursor_exhausted"]]
        if not active:
            return make_hold(
                "Cap unitat amb cursor actiu: totes esgotades",
                meta={"registered_units": len(self._units)},
            )

        ordering = sorted(active, key=lambda u: u["wilson_lower"], reverse=True)
        return make_success(
            {"selected": ordering[0], "ranking": ordering},
            meta={"rule": "mai s'abandona una unitat amb cursor actiu"},
        )

    def mark_exhausted(self, unit_id: str) -> dict[str, Any]:
        if unit_id not in self._units:
            return make_hold("Unitat no registrada", meta={"unit_id": unit_id})
        self._units[unit_id]["cursor_exhausted"] = True
        return make_success(dict(self._units[unit_id]))

    def snapshot(self) -> dict[str, Any]:
        return make_success(
            {"units": list(self._units.values()), "total": len(self._units)},
            meta={"canonical_total_units": LAUREL_LEDGER_UNITS},
        )


def laurel_ledger_units() -> dict[str, Any]:
    return make_success(
        {
            "localities": LAUREL_LEDGER_LOCALITIES,
            "states": LAUREL_LEDGER_STATES,
            "total_units": LAUREL_LEDGER_UNITS,
            "all_countries_can_work_simultaneously": True,
        },
        meta={"provenance": "100 localitats x 27 estats UE"},
    )


def lane_structure(lane_id: int) -> dict[str, Any]:
    if not 1 <= lane_id <= LANE_COUNT:
        return make_reject(
            "L'identificador de lane ha d'estar entre 1 i 100", meta={"lane_id": lane_id}
        )

    return make_success(
        {
            "lane_id": lane_id,
            "territory": None,
            "rank": None,
            "state": None,
            "cursor": None,
            "results": [],
            "errors": [],
            "checkpoint": None,
            "last_update": None,
        },
        meta={"source": "S3.3.5"},
    )
