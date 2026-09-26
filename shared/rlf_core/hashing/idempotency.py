"""Hashing i idempotència del sistema RLF.

Implementa §3.3.10, §4.3.2 i §4.4.2 del document mestre canònic.

La clau d'idempotència és:

    clau = SHA-256(país|lane|cursor|acció)

El separador `|` és obligatori: evita col·lisions per concatenació (lane 1 +
cursor "12" no pot coincidir amb lane 11 + cursor "2").
"""

import hashlib
from typing import Any, Iterable, Optional, Protocol

from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_reject,
    make_success,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

LANE_ASSIGNER_VERSION: str = "1.1"
LANE_ASSIGNER_SALT: str = "lane_assigner/1.1"
LANE_COUNT: int = 100

OUTCOME_APPLIED: str = "applied"
OUTCOME_REPLAYED_NOOP: str = "replayed-noop"

logger = get_logger(__name__)

_SEPARATOR = "|"


def sha256_hex(payload: bytes) -> str:
    """Calcula el SHA-256 d'un contingut en hexadecimal.

    Args:
        payload: Bytes d'entrada.

    Returns:
        El digest en hexadecimal, en minúscules, de 64 caràcters.
    """
    return hashlib.sha256(payload).hexdigest()


def sha256_file_hex(path: str) -> str:
    """Calcula el SHA-256 d'un fitxer llegint-lo per blocs.

    Args:
        path: Ruta del fitxer.

    Returns:
        El digest en hexadecimal, en minúscules.
    """
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_idempotency_key(country: str, lane: int, cursor: str, action: str) -> str:
    """Construeix la clau d'idempotència canònica.

    Args:
        country: Codi de país o clau territorial.
        lane: Número de lane.
        cursor: Cursor dins la lane.
        action: Acció que s'executa.

    Returns:
        El SHA-256 hexadecimal de la clau composta amb separador `|`.

    Raises:
        ValueError: Si algún component conté el separador reservat.
    """
    components = [country, str(lane), cursor, action]
    for component in components:
        if _SEPARATOR in component:
            raise ValueError("El separador '|' és reservat i no pot aparèixer als components")
    return sha256_hex(_SEPARATOR.join(components).encode("utf-8"))


def assign_lane(canonical_key: str) -> int:
    """Assigna una lane determinista a una clau canònica (§3.3.4).

    Fórmula canònica:

        lane = (SHA-256("lane_assigner/1.1" + "|" + clau_canònica) mod 100) + 1

    Args:
        canonical_key: Clau canònica de l'entitat.

    Returns:
        El número de lane, de 1 a 100, amb precisió aritmètica completa.

    Raises:
        ValueError: Si la clau canònica és buida o conté el separador.
    """
    if not canonical_key:
        raise ValueError("La clau canònica no pot ser buida")
    if _SEPARATOR in canonical_key:
        raise ValueError("El separador '|' és reservat a la clau canònica")

    payload = f"{LANE_ASSIGNER_SALT}{_SEPARATOR}{canonical_key}".encode("utf-8")
    big_integer = int.from_bytes(hashlib.sha256(payload).digest(), byteorder="big")
    return (big_integer % LANE_COUNT) + 1


class OperationLedger(Protocol):
    """Protocol del llibre d'operacions persistent."""

    def has(self, key: str) -> bool:
        """Indica si una clau ja existeix al llibre."""
        ...

    def record(self, key: str, result: Any) -> None:
        """Registra una clau amb el seu resultat."""
        ...

    def get(self, key: str) -> Optional[Any]:
        """Retorna el resultat emmagatzemat d'una clau."""
        ...


class MemoryLedger:
    """Llibre d'operacions en memòria, només per a proves."""

    def __init__(self) -> None:
        """Inicialitza un llibre buit."""
        self._entries: dict[str, Any] = {}

    def has(self, key: str) -> bool:
        """Indica si la clau és al llibre."""
        return key in self._entries

    def record(self, key: str, result: Any) -> None:
        """Emmagatzema una clau i el seu resultat."""
        self._entries[key] = result

    def get(self, key: str) -> Optional[Any]:
        """Retorna el resultat d'una clau, o None."""
        return self._entries.get(key)

    def keys(self) -> Iterable[str]:
        """Retorna les claus emmagatzemades."""
        return self._entries.keys()


def apply_idempotent(
    ledger: OperationLedger,
    key: str,
    action_callable: Any,
) -> dict[str, Any]:
    """Executa una acció de manera idempotent sobre un llibre.

    Primera aplicació -> applied. Reintent sobre la mateixa clau ->
    replayed-noop amb el resultat emmagatzemat. Zero duplicacions.

    Args:
        ledger: Magatzem que compleix OperationLedger.
        key: Clau d'idempotència.
        action_callable: Funció sense arguments que produeix el resultat.

    Returns:
        Un resultat canònic SUCCESS amb el resultat i l'outcome. REJECT si la
        clau és invàlida. FAILURE si l'acció llança una excepció inesperada.
    """
    if not key:
        return make_reject("La clau d'idempotència no pot ser buida")

    try:
        if ledger.has(key):
            logger.info("idempotent_replay", key=key, outcome=OUTCOME_REPLAYED_NOOP)
            return make_success(
                {"outcome": OUTCOME_REPLAYED_NOOP, "result": ledger.get(key)},
                meta={"key": key},
            )

        result = action_callable()
        ledger.record(key, result)
        logger.info("idempotent_apply", key=key, outcome=OUTCOME_APPLIED)
        return make_success(
            {"outcome": OUTCOME_APPLIED, "result": result}, meta={"key": key}
        )
    except Exception as exception:  # noqa: BLE001 - contracte FAILURE és explícit
        logger.critical("idempotent_unexpected", key=key, error=str(exception))
        return make_failure(
            f"Excepció inesperada: {exception}",
            meta={"exception_type": type(exception).__name__},
        )


def content_address(payload: bytes) -> str:
    """Adreça un contingut pel seu propi hash (§4.4.4).

    Args:
        payload: Bytes del contingut.

    Returns:
        El SHA-256 hexadecimal del contingut.
    """
    return sha256_hex(payload)
