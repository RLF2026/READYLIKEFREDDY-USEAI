"""Registre estructurat d'esdeveniments del sistema RLF.

Implementa el logging de SPEC-CODE-001 §6.1.8.

Format de línia, un esdeveniment per línia:

    {timestamp_utc} | {level} | {logger} | {event} | {clau=valor; ...}

El registre és append-only (§5.2.6) i no depèn de cap entorn extern.
"""

import json
import sys
from datetime import datetime, timezone
from typing import Any, Optional, TextIO

VERSION: str = "1.0"

LEVEL_DEBUG: str = "DEBUG"
LEVEL_INFO: str = "INFO"
LEVEL_WARNING: str = "WARNING"
LEVEL_ERROR: str = "ERROR"
LEVEL_CRITICAL: str = "CRITICAL"

_LEVEL_ORDER: dict[str, int] = {
    LEVEL_DEBUG: 10,
    LEVEL_INFO: 20,
    LEVEL_WARNING: 30,
    LEVEL_ERROR: 40,
    LEVEL_CRITICAL: 50,
}


def _utc_now_iso() -> str:
    """Retorna el moment actual en ISO 8601 amb zona UTC.

    Returns:
        Cadena de data i hora, amb sufix Z.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _serialise_value(value: Any) -> str:
    """Serialitza un valor per a la línia de registre.

    Args:
        value: Valor arbitrari.

    Returns:
        Representació textual simple, o JSON compacte per a estructures.
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return str(value)
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    except (TypeError, ValueError):
        return repr(value)


class Logger:
    """Registrador estructurat amb nivell mínim i stream configurables."""

    def __init__(
        self,
        name: str,
        level: str = LEVEL_INFO,
        stream: Optional[TextIO] = None,
    ) -> None:
        """Inicialitza el registrador.

        Args:
            name: Nom del mòdul o component.
            level: Nivell mínim a emetre.
            stream: Destinació de les línies. Per defecte, sys.stderr.

        Raises:
            ValueError: Si el nivell no és cap dels cinc canònics.
        """
        if level not in _LEVEL_ORDER:
            raise ValueError(f"Nivell de log no canònic: {level!r}")
        self.name = name
        self.level = level
        self.stream = stream if stream is not None else sys.stderr

    def _enabled(self, level: str) -> bool:
        """Indica si un nivell s'ha d'emetre."""
        return _LEVEL_ORDER[level] >= _LEVEL_ORDER[self.level]

    def _emit(self, level: str, event: str, **context: Any) -> None:
        """Escriu una línia de registre si el nivell la permet."""
        if not self._enabled(level):
            return
        parts = [f"{k}={_serialise_value(v)}" for k, v in sorted(context.items())]
        suffix = f" | {'; '.join(parts)}" if parts else ""
        self.stream.write(f"{_utc_now_iso()} | {level} | {self.name} | {event}{suffix}\n")

    def debug(self, event: str, **context: Any) -> None:
        """Registra un esdeveniment de depuració."""
        self._emit(LEVEL_DEBUG, event, **context)

    def info(self, event: str, **context: Any) -> None:
        """Registra un esdeveniment informatiu."""
        self._emit(LEVEL_INFO, event, **context)

    def warning(self, event: str, **context: Any) -> None:
        """Registra un advertiment."""
        self._emit(LEVEL_WARNING, event, **context)

    def error(self, event: str, **context: Any) -> None:
        """Registra un error d'entorn."""
        self._emit(LEVEL_ERROR, event, **context)

    def critical(self, event: str, **context: Any) -> None:
        """Registra un error crític."""
        self._emit(LEVEL_CRITICAL, event, **context)


_LOGGERS: dict[str, Logger] = {}


def get_logger(name: str, level: str = LEVEL_INFO) -> Logger:
    """Retorna el registrador d'un nom, creant-lo si cal.

    Args:
        name: Nom del mòdul o component.
        level: Nivell mínim, només s'aplica en crear-lo.

    Returns:
        Una instància de Logger per a aquell nom.
    """
    if name not in _LOGGERS:
        _LOGGERS[name] = Logger(name, level)
    return _LOGGERS[name]
