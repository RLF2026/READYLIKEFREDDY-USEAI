"""Configuració del sistema RLF.

Implementa §5.2.8 (portability) del document mestre canònic.

Regla dura: **cap credencial viu al repositori**. `deployment/README.md` ho
declara i aquest mòdul ho fa executable. La configuració es llegeix de
variables d'entorn i de valors per defecte declarats aquí; cap clau, token ni
contrasenya s'escriu mai en un fitxer versionat.
"""

import os
from typing import Any, Mapping, Optional

from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_hold,
    make_success,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

LANE_COUNT: int = 100
LAUREL_LEDGER_LOCALITIES: int = 100
LAUREL_LEDGER_STATES: int = 27
LAUREL_LEDGER_UNITS: int = LAUREL_LEDGER_LOCALITIES * LAUREL_LEDGER_STATES

SUPPLIER_PRELAUNCH_GATE: int = 10000
KB_PRELAUNCH_GATE: int = 15000

DISCOUNT_MINIMUM_PERCENT: float = 70.0
NET_PROFIT_MINIMUM_EUR: float = 25.0
NET_PROFIT_TARGET_LOW_EUR: float = 40.0
NET_PROFIT_TARGET_HIGH_EUR: float = 90.0

ENTRY_TRANSIT_MAX_HOURS: int = 96
ENTRY_TRANSIT_IDEAL_HOURS: int = 72

FRESHNESS_REVALIDATION_DAYS: int = 30

SALE_SLOTS: int = 1000
BACKUP_SLOTS: int = 100
PRODUCT_POOL_TARGET: int = 4000

SALE_BACKUP_MONITOR_MINUTES: int = 5
POOL_MONITOR_CYCLES_PER_12H: int = 2

DEFAULT_WEIGHTS: dict[str, float] = {
    "discount": 0.30,
    "net_profit": 0.25,
    "competition": 0.15,
    "condition": 0.10,
    "demand": 0.10,
    "category": 0.05,
    "era": 0.03,
    "rarity": 0.02,
}

DEFAULT_HOST: str = "127.0.0.1"
DEFAULT_USER_AGENT: str = "RLFPrelovedBot/1.0 (+https://readylikefreddy.shop)"
DOMAIN_THROTTLE_SECONDS: int = 5

logger = get_logger(__name__)

_SECRET_KEY_PATTERN = (
    "KEY",
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "CREDENTIAL",
    "PRIVATE",
)


def default_config() -> dict[str, Any]:
    """Retorna la configuració canònica del sistema.

    Returns:
        Un diccionari amb tots els paràmetres declarats al document mestre.
        No conté cap credencial.
    """
    return {
        "lane_count": LANE_COUNT,
        "laurel_ledger_units": LAUREL_LEDGER_UNITS,
        "gates": {
            "supplier_prelaunch_validated": SUPPLIER_PRELAUNCH_GATE,
            "kb_prelaunch_full_certified": KB_PRELAUNCH_GATE,
        },
        "economics": {
            "discount_minimum_percent": DISCOUNT_MINIMUM_PERCENT,
            "net_profit_minimum_eur": NET_PROFIT_MINIMUM_EUR,
            "net_profit_target_low_eur": NET_PROFIT_TARGET_LOW_EUR,
            "net_profit_target_high_eur": NET_PROFIT_TARGET_HIGH_EUR,
        },
        "logistics": {
            "entry_transit_max_hours": ENTRY_TRANSIT_MAX_HOURS,
            "entry_transit_ideal_hours": ENTRY_TRANSIT_IDEAL_HOURS,
        },
        "freshness_revalidation_days": FRESHNESS_REVALIDATION_DAYS,
        "commercial": {
            "product_pool_target": PRODUCT_POOL_TARGET,
            "sale_slots": SALE_SLOTS,
            "backup_slots": BACKUP_SLOTS,
            "sale_backup_monitor_minutes": SALE_BACKUP_MONITOR_MINUTES,
            "pool_monitor_cycles_per_12h": POOL_MONITOR_CYCLES_PER_12H,
        },
        "default_weights": dict(DEFAULT_WEIGHTS),
        "monitoring": {
            "host": DEFAULT_HOST,
            "user_agent": DEFAULT_USER_AGENT,
            "domain_throttle_seconds": DOMAIN_THROTTLE_SECONDS,
        },
    }


def assert_weights_sum_to_one(weights: Optional[Mapping[str, float]] = None) -> dict[str, Any]:
    """Comprova que els pesos de scoring sumen 1,00 (§3.8.5).

    Args:
        weights: Pesos a comprovar. Per defecte, els canònics.

    Returns:
        Un resultat canònic SUCCESS amb la suma, REJECT si no suma 1,00.
    """
    chosen = dict(weights if weights is not None else DEFAULT_WEIGHTS)
    total = round(sum(chosen.values()), 4)
    if total != 1.0:
        return make_reject(
            f"Els pesos de scoring han de sumar 1,00; sumen {total}",
            meta={"total": total, "weights": chosen},
        )
    return make_success({"total": total, "factors": len(chosen)})


def load_config(environment: Optional[Mapping[str, str]] = None) -> dict[str, Any]:
    """Carrega la configuració aplicant sobreescriptures de l'entorn.

    Només s'accepten sobreescriptures **no sensibles**: qualsevol variable
    d'entorn el nom de la qual contingui KEY, TOKEN, SECRET, PASSWORD,
    CREDENTIAL o PRIVATE es descarta i es registra com a advertiment.

    Args:
        environment: Mapatge d'entorn. Per defecte, os.environ.

    Returns:
        Un resultat canònic SUCCESS amb la configuració efectiva. HOLD si la
        configuració resultant és incoherent. FAILURE davant d'una excepció.
    """
    try:
        source = environment if environment is not None else os.environ
        config = default_config()
        ignored: list[str] = []
        applied: list[str] = []

        for raw_key, value in source.items():
            if not raw_key.startswith("RLF_"):
                continue
            name = raw_key[len("RLF_") :].lower()
            if any(marker in raw_key.upper() for marker in _SECRET_KEY_PATTERN):
                ignored.append(raw_key)
                logger.warning("config_secret_ignored", variable=raw_key)
                continue
            if name in config:
                config[name] = value
                applied.append(name)

        weights_check = assert_weights_sum_to_one(config.get("default_weights"))
        if weights_check["status"] != "SUCCESS":
            return make_hold(
                "Configuració incoherent: pesos de scoring",
                meta={"detail": weights_check["reason"]},
            )

        return make_success(
            config,
            meta={
                "applied_overrides": sorted(applied),
                "ignored_secret_variables": sorted(ignored),
            },
        )
    except Exception as exception:  # noqa: BLE001 - contracte FAILURE és explícit
        logger.critical("config_unexpected", error=str(exception))
        return make_failure(
            f"Excepció inesperada: {exception}",
            meta={"exception_type": type(exception).__name__},
        )


def assert_no_secrets(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Comprova que un mapatge no conté cap clau semblant a un secret.

    Args:
        payload: Mapatge a comprovar.

    Returns:
        Un resultat canònic SUCCESS si és net, REJECT amb les claus trobades
        si en conté.
    """
    if not isinstance(payload, Mapping):
        return make_reject("El payload no és un mapatge")

    suspicious = [
        key
        for key in payload
        if any(marker in str(key).upper() for marker in _SECRET_KEY_PATTERN)
    ]
    if suspicious:
        return make_reject(
            "El payload conté claus semblants a credencials",
            meta={"suspicious_keys": sorted(map(str, suspicious))},
        )
    return make_success({"checked_keys": len(payload)})
