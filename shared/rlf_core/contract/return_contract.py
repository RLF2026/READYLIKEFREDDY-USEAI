"""Contracte de retorn canònic del sistema RLF.

Implementa SPEC-CODE-001 §6.1.6 i §6.6 del document mestre canònic.

Tots els mòduls del sistema retornen un diccionari amb la mateixa forma:

    {
        "status": str,   # SUCCESS | SKIPPED | HOLD | REJECT | ERROR | FAILURE
        "reason": Optional[str],
        "data": Optional[object],
        "meta": Optional[dict],
    }

Cap mòdul queda exempt d'aquest contracte (R7, §0.2).
"""

from typing import Any, Optional

VERSION: str = "1.0"

STATUS_SUCCESS: str = "SUCCESS"
STATUS_SKIPPED: str = "SKIPPED"
STATUS_HOLD: str = "HOLD"
STATUS_REJECT: str = "REJECT"
STATUS_ERROR: str = "ERROR"
STATUS_FAILURE: str = "FAILURE"

CANONICAL_STATUSES: frozenset[str] = frozenset(
    {
        STATUS_SUCCESS,
        STATUS_SKIPPED,
        STATUS_HOLD,
        STATUS_REJECT,
        STATUS_ERROR,
        STATUS_FAILURE,
    }
)

STATUSES_WITH_DATA: frozenset[str] = frozenset({STATUS_SUCCESS})


def _make(
    status: str,
    reason: Optional[str],
    data: Optional[object] = None,
    meta: Optional[dict] = None,
) -> dict[str, Any]:
    """Construeix un resultat canònic amb validació d'estat i de forma.

    Args:
        status: Un dels sis estats canònics.
        reason: Motiu llegible. Obligatori per a tots els estats excepte SUCCESS.
        data: Resultat. Només pot ser no nul a SUCCESS.
        meta: Metadades lliures.

    Returns:
        Un dict amb status, reason, data i meta.

    Raises:
        ValueError: Si l'estat no és canònic, si falta el motiu o si la dada
            no és coherent amb l'estat.
    """
    if status not in CANONICAL_STATUSES:
        raise ValueError(f"Estat no canònic: {status!r}")

    if status == STATUS_SUCCESS and reason is not None:
        raise ValueError("Un resultat SUCCESS no porta motiu")

    if status != STATUS_SUCCESS and not reason:
        raise ValueError(f"Un resultat {status} requereix motiu")

    if status not in STATUSES_WITH_DATA and data is not None:
        raise ValueError(f"Un resultat {status} no pot portar data")

    return {"status": status, "reason": reason, "data": data, "meta": meta}


def make_success(data: Any, meta: Optional[dict] = None) -> dict[str, Any]:
    """Crea un resultat SUCCESS.

    Args:
        data: El resultat de l'operació.
        meta: Metadades opcionals.

    Returns:
        Un dict canònic amb status SUCCESS.
    """
    return _make(STATUS_SUCCESS, None, data, meta)


def make_skipped(reason: str, meta: Optional[dict] = None) -> dict[str, Any]:
    """Crea un resultat SKIPPED (no processat, sense error)."""
    return _make(STATUS_SKIPPED, reason, None, meta)


def make_hold(reason: str, meta: Optional[dict] = None) -> dict[str, Any]:
    """Crea un resultat HOLD (ajornat per incertesa, fail-closed)."""
    return _make(STATUS_HOLD, reason, None, meta)


def make_reject(reason: str, meta: Optional[dict] = None) -> dict[str, Any]:
    """Crea un resultat REJECT (contradicció o criteri incomplert)."""
    return _make(STATUS_REJECT, reason, None, meta)


def make_error(reason: str, meta: Optional[dict] = None) -> dict[str, Any]:
    """Crea un resultat ERROR (error d'entorn recuperable)."""
    return _make(STATUS_ERROR, reason, None, meta)


def make_failure(reason: str, meta: Optional[dict] = None) -> dict[str, Any]:
    """Crea un resultat FAILURE (excepció inesperada)."""
    return _make(STATUS_FAILURE, reason, None, meta)


def is_canonical(result: object) -> bool:
    """Comprova si un valor compleix el contracte de retorn.

    Args:
        result: Valor a comprovar.

    Returns:
        True si és un dict amb les quatre claus i un estat canònic.
    """
    if not isinstance(result, dict):
        return False
    if set(result.keys()) != {"status", "reason", "data", "meta"}:
        return False
    return result.get("status") in CANONICAL_STATUSES


def unwrap(result: dict[str, Any]) -> Any:
    """Extreu la dada d'un resultat SUCCESS o llança si no ho és.

    Args:
        result: Un resultat canònic.

    Returns:
        El contingut del camp data.

    Raises:
        ValueError: Si el resultat no és SUCCESS.
    """
    if result.get("status") != STATUS_SUCCESS:
        raise ValueError(
            f"unwrap() sobre un resultat {result.get('status')!r}: {result.get('reason')!r}"
        )
    return result.get("data")
