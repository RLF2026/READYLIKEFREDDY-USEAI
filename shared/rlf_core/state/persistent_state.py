"""Primitives d'estat persistent, cursors i checkpoints del sistema RLF.

Implementa §3.4.2 (estat persistent), §4.3.1 (cursors) i §4.4.3 (recovery)
del document mestre canònic.

L'estat és append-only (§5.2.6): s'escriuen esdeveniments, no s'edita el passat.
L'estat vigent es reconstrueix llegint la seqüència.

Cursors canònics (§4.3.1):

    A1.1  Sourcing     Cursor del motor de sourcing (§3.3)
    S0.1  Selecció     Cursor del sistema comercial (§3.8)
    K0.1  Coneixement  Cursor del sistema de coneixement (§3.6)
"""

import json
from typing import Any, Iterable, Optional

from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.hashing.idempotency import sha256_hex
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

CURSOR_SOURCING: str = "A1.1"
CURSOR_SELECTION: str = "S0.1"
CURSOR_KNOWLEDGE: str = "K0.1"

CANONICAL_CURSORS: frozenset[str] = frozenset(
    {CURSOR_SOURCING, CURSOR_SELECTION, CURSOR_KNOWLEDGE}
)

STATE_UNINITIALISED: str = "uninitialised"
STATE_RUNNING: str = "running"
STATE_PAUSED: str = "paused"
STATE_CLOSED: str = "closed"

logger = get_logger(__name__)


class EventLog:
    """Registre append-only d'esdeveniments d'estat.

    Cada entrada porta un hash del contingut per poder verificar integritat
    (§4.4.2) i un hash de l'entrada anterior per encadenar-les.
    """

    GENESIS_HASH: str = "0" * 64

    def __init__(self) -> None:
        """Inicialitza un registre buit amb la marca de gènesi."""
        self._entries: list[dict[str, Any]] = []

    def append(self, event: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Afegeix un esdeveniment al registre.

        Args:
            event: Nom de l'esdeveniment.
            payload: Contingut de l'esdeveniment.

        Returns:
            L'entrada creada, amb seqüència, hash propi i hash anterior.

        Raises:
            ValueError: Si l'esdeveniment és buit.
        """
        if not event:
            raise ValueError("L'esdeveniment no pot ser buit")

        sequence = len(self._entries) + 1
        previous_hash = self._entries[-1]["hash"] if self._entries else self.GENESIS_HASH
        body = json.dumps(
            {"sequence": sequence, "event": event, "payload": payload},
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
        entry = {
            "sequence": sequence,
            "event": event,
            "payload": payload,
            "previous_hash": previous_hash,
            "hash": sha256_hex((previous_hash + body).encode("utf-8")),
        }
        self._entries.append(entry)
        return entry

    def entries(self) -> Iterable[dict[str, Any]]:
        """Retorna les entrades en ordre d'append."""
        return tuple(self._entries)

    def verify_chain(self) -> dict[str, Any]:
        """Verifica la integritat de tota la cadena (§4.4.2).

        Returns:
            Un resultat canònic SUCCESS amb el nombre d'entrades verificades.
            REJECT si la cadena està trencada.
        """
        previous_hash = self.GENESIS_HASH
        for entry in self._entries:
            if entry["previous_hash"] != previous_hash:
                return make_reject(
                    "Cadena d'estat trencada: hash anterior no coincideix",
                    meta={"sequence": entry["sequence"]},
                )
            body = json.dumps(
                {
                    "sequence": entry["sequence"],
                    "event": entry["event"],
                    "payload": entry["payload"],
                },
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            )
            expected = sha256_hex((previous_hash + body).encode("utf-8"))
            if entry["hash"] != expected:
                return make_reject(
                    "Cadena d'estat trencada: hash propi no coincideix",
                    meta={"sequence": entry["sequence"]},
                )
            previous_hash = entry["hash"]

        return make_success({"verified_entries": len(self._entries)})


class CursorStore:
    """Emmagatzema cursors per clau, sobre un EventLog."""

    def __init__(self, event_log: Optional[EventLog] = None) -> None:
        """Inicialitza el magatzem de cursors.

        Args:
            event_log: Registre on persistir els canvis. Se'n crea un si no es dona.
        """
        self.event_log = event_log if event_log is not None else EventLog()
        self._cursors: dict[str, str] = {}

    def set_cursor(self, cursor_id: str, position: str) -> dict[str, Any]:
        """Situa un cursor en una posició.

        Args:
            cursor_id: Identificador del cursor.
            position: Posició nova.

        Returns:
            Un resultat canònic SUCCESS amb la posició anterior i la nova.
            REJECT si l'identificador o la posició són buits.
        """
        if not cursor_id:
            return make_reject("L'identificador de cursor no pot ser buit")
        if not position:
            return make_reject("La posició no pot ser buida")

        previous = self._cursors.get(cursor_id)
        self._cursors[cursor_id] = position
        self.event_log.append(
            "cursor_set",
            {"cursor_id": cursor_id, "previous": previous, "position": position},
        )
        logger.info("cursor_set", cursor_id=cursor_id, position=position)
        return make_success(
            {"cursor_id": cursor_id, "previous": previous, "position": position}
        )

    def get_cursor(self, cursor_id: str) -> dict[str, Any]:
        """Llegeix la posició d'un cursor.

        Args:
            cursor_id: Identificador del cursor.

        Returns:
            Un resultat canònic SUCCESS amb la posició, HOLD si el cursor no
            existeix, REJECT si l'identificador és buit.
        """
        if not cursor_id:
            return make_reject("L'identificador de cursor no pot ser buit")
        if cursor_id not in self._cursors:
            return make_hold("Cursor no inicialitzat", meta={"cursor_id": cursor_id})
        return make_success({"cursor_id": cursor_id, "position": self._cursors[cursor_id]})

    def snapshot(self) -> dict[str, Any]:
        """Retorna una fotografia de tots els cursors.

        Returns:
            Un resultat canònic SUCCESS amb el diccionari de cursors.
        """
        return make_success(dict(self._cursors), meta={"count": len(self._cursors)})


class CheckpointStore:
    """Guarda i restaura checkpoints d'estat (§4.4.3)."""

    def __init__(self, event_log: Optional[EventLog] = None) -> None:
        """Inicialitza el magatzem de checkpoints.

        Args:
            event_log: Registre on persistir els checkpoints.
        """
        self.event_log = event_log if event_log is not None else EventLog()
        self._checkpoints: dict[str, dict[str, Any]] = {}

    def save(self, name: str, state: dict[str, Any]) -> dict[str, Any]:
        """Guarda un checkpoint amb el seu hash d'integritat.

        Args:
            name: Nom del checkpoint.
            state: Estat a guardar.

        Returns:
            Un resultat canònic SUCCESS amb el hash del checkpoint. REJECT si
            el nom és buit o l'estat no és un diccionari.
        """
        if not name:
            return make_reject("El nom del checkpoint no pot ser buit")
        if not isinstance(state, dict):
            return make_reject("L'estat d'un checkpoint ha de ser un diccionari")

        body = json.dumps(state, ensure_ascii=False, sort_keys=True, default=str)
        digest = sha256_hex(body.encode("utf-8"))
        self._checkpoints[name] = {"state": state, "hash": digest}
        self.event_log.append("checkpoint_save", {"name": name, "hash": digest})
        logger.info("checkpoint_save", name=name, hash=digest)
        return make_success({"name": name, "hash": digest})

    def restore(self, name: str) -> dict[str, Any]:
        """Restaura un checkpoint verificant-ne el hash.

        Args:
            name: Nom del checkpoint.

        Returns:
            Un resultat canònic SUCCESS amb l'estat, HOLD si no existeix,
            REJECT si el hash no coincideix amb el contingut.
        """
        if name not in self._checkpoints:
            return make_hold("Checkpoint inexistent", meta={"name": name})

        stored = self._checkpoints[name]
        body = json.dumps(stored["state"], ensure_ascii=False, sort_keys=True, default=str)
        if sha256_hex(body.encode("utf-8")) != stored["hash"]:
            return make_reject(
                "Checkpoint modificat: el hash no coincideix", meta={"name": name}
            )

        return make_success(stored["state"], meta={"name": name, "hash": stored["hash"]})

    def try_operation(self, name: str, operation: Any) -> dict[str, Any]:
        """Executa una operació amb recuperació per checkpoint (§4.4.3).

        Procés canònic: detecció -> diagnòstic -> localització -> recuperació
        -> verificació -> represa -> registre.

        Args:
            name: Nom del checkpoint associat a l'operació.
            operation: Funció sense arguments que executa l'operació.

        Returns:
            Un resultat canònic SUCCESS amb el resultat i si hi ha hagut
            represa. FAILURE si l'operació llança una excepció.
        """
        recovery_point = self.restore(name)
        resumed_from = recovery_point["data"] if recovery_point["status"] == "SUCCESS" else None

        try:
            outcome = operation()
            return make_success(
                {"result": outcome, "resumed_from": resumed_from},
                meta={"checkpoint": name},
            )
        except Exception as exception:  # noqa: BLE001 - contracte FAILURE és explícit
            self.event_log.append("operation_failed", {"name": name, "error": str(exception)})
            logger.critical("operation_failed", name=name, error=str(exception))
            return make_failure(
                f"Operació fallida: {exception}",
                meta={
                    "exception_type": type(exception).__name__,
                    "recovery_point": resumed_from,
                },
            )
