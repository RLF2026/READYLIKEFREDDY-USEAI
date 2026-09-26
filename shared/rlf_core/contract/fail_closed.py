"""Principi fail-closed del sistema RLF.

Implementa §4.1 i §5.2.5 del document mestre canònic.

Les quatre regles:

1. Dada no demostrable -> no inventar.
2. Entitat no validable -> HOLD.
3. Contradicció -> REJECT.
4. Evidència suficient -> ACCEPT / ADVANCE.

L'ordre d'avaluació és part de la regla: una contradicció té prioritat sobre
una dada que falta, perquè una contradicció ja és informació (dues fonts es
neguen) mentre que una dada absent només és ignorància.
"""

from typing import Any, Optional

from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

DECISION_ACCEPT: str = "accept"
DECISION_HOLD: str = "hold"
DECISION_REJECT: str = "reject"

RULE_NO_INVENTION: int = 1
RULE_HOLD: int = 2
RULE_REJECT: int = 3
RULE_ADVANCE: int = 4

POLICY_NAME: str = "RLF_PLUS_LAUREL_LEDGER_FAIL_CLOSED"

logger = get_logger(__name__)


def apply_fail_closed(
    evidence: Optional[dict[str, Any]],
    contradictions: Optional[list[str]] = None,
    missing_fields: Optional[list[str]] = None,
    validation_passed: bool = False,
) -> dict[str, Any]:
    """Aplica el principi fail-closed a una decisió.

    Args:
        evidence: Diccionari amb l'evidència recollida. Buit o None es tracta
            com a absència d'evidència.
        contradictions: Contradiccions detectades entre fonts.
        missing_fields: Camps obligatoris que falten.
        validation_passed: True si totes les validacions han passat.

    Returns:
        Un resultat canònic. `data` conté la decisió, la regla aplicada i el
        detall. FAILURE si es produeix una excepció inesperada.
    """
    try:
        pending: list[str] = list(missing_fields or [])
        conflicts: list[str] = list(contradictions or [])

        if not isinstance(evidence, dict) or not evidence:
            pending.append("evidence")

        if conflicts:
            logger.warning("fail_closed_reject", contradictions=conflicts)
            return make_success(
                {
                    "decision": DECISION_REJECT,
                    "rule_applied": RULE_REJECT,
                    "policy": POLICY_NAME,
                    "details": {"contradictions": conflicts},
                }
            )

        if pending or not validation_passed:
            logger.info("fail_closed_hold", missing_fields=pending)
            return make_success(
                {
                    "decision": DECISION_HOLD,
                    "rule_applied": RULE_HOLD,
                    "policy": POLICY_NAME,
                    "details": {
                        "missing_fields": pending,
                        "validation_passed": validation_passed,
                    },
                }
            )

        logger.info("fail_closed_accept", evidence_count=len(evidence))
        return make_success(
            {
                "decision": DECISION_ACCEPT,
                "rule_applied": RULE_ADVANCE,
                "policy": POLICY_NAME,
                "details": {"evidence_count": len(evidence)},
            }
        )
    except Exception as exception:  # noqa: BLE001 - contracte FAILURE és explícit
        logger.critical("fail_closed_unexpected", error=str(exception))
        return make_failure(
            f"Excepció inesperada: {exception}",
            meta={"exception_type": type(exception).__name__},
        )


def decide(
    evidence: Optional[dict[str, Any]],
    contradictions: Optional[list[str]] = None,
    missing_fields: Optional[list[str]] = None,
    validation_passed: bool = False,
) -> str:
    """Retorna només la decisió, com a comoditat per a cridadors simples.

    Args:
        evidence: Evidència recollida.
        contradictions: Contradiccions detectades.
        missing_fields: Camps que falten.
        validation_passed: Si les validacions han passat.

    Returns:
        Un dels tres valors de decisió. Davant d'un FAILURE intern, retorna
        HOLD: davant la incertesa, tancar.
    """
    result = apply_fail_closed(evidence, contradictions, missing_fields, validation_passed)
    if result["status"] != "SUCCESS" or not isinstance(result["data"], dict):
        return DECISION_HOLD
    return result["data"]["decision"]


def assert_no_blanks(record: dict[str, Any], required_fields: list[str]) -> dict[str, Any]:
    """Comprova que un registre no té buits prohibits (R17).

    Args:
        record: Registre a comprovar.
        required_fields: Camps obligatoris per a aquell registre.

    Returns:
        Un resultat canònic SUCCESS amb la llista de buits trobats, o HOLD si
        n'hi ha. REJECT si el registre no és un diccionari.
    """
    if not isinstance(record, dict):
        return make_reject("El registre no és un diccionari")

    blanks: list[str] = []
    for field_name in required_fields:
        value = record.get(field_name)
        if value is None:
            blanks.append(field_name)
            continue
        if isinstance(value, str) and value.strip().upper() in {"", "UNKNOWN", "TBD"}:
            blanks.append(field_name)

    if blanks:
        return make_hold(
            "Camps obligatoris buits o no resolts (R17)", meta={"blanks": blanks}
        )

    return make_success({"blanks": []})
