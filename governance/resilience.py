"""Contracte de governanca RLF-RESILIENCE/1.0 (S4.4.5)."""

from typing import Any, Callable, Optional

from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

CONTRACT_NAME: str = "RLF-RESILIENCE/1.0"

FAILURE_TRANSIENT: str = "transient"
FAILURE_PERMANENT: str = "permanent"
FAILURE_CRITICAL: str = "critical"

ACTION_RETRY: str = "retry"
ACTION_ISOLATE: str = "isolate"
ACTION_HALT: str = "halt"

MAX_RETRY_ATTEMPTS: int = 3

logger = get_logger(__name__)


def classify_failure(exception: BaseException) -> dict[str, Any]:
    transient_types = (TimeoutError, ConnectionError, OSError)
    critical_types = (MemoryError, SystemExit, KeyboardInterrupt)

    if isinstance(exception, critical_types):
        return make_success(
            {"classification": FAILURE_CRITICAL, "action": ACTION_HALT},
            meta={"notification": "escala a governanca humana"},
        )

    if isinstance(exception, transient_types):
        return make_success(
            {"classification": FAILURE_TRANSIENT, "action": ACTION_RETRY},
            meta={"max_attempts": MAX_RETRY_ATTEMPTS},
        )

    return make_success(
        {"classification": FAILURE_PERMANENT, "action": ACTION_ISOLATE},
        meta={"note": "no es reintenta: la condicio no canvia sola"},
    )


def with_retry(
    operation: Callable[[], Any],
    max_attempts: int = MAX_RETRY_ATTEMPTS,
) -> dict[str, Any]:
    if max_attempts <= 0:
        return make_reject("El nombre d'intents ha de ser positiu")

    last_error: Optional[BaseException] = None
    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        try:
            outcome = operation()
            return make_success(
                {"result": outcome, "attempts": attempts},
                meta={"contract": CONTRACT_NAME},
            )
        except Exception as exception:
            last_error = exception
            classified = classify_failure(exception)
            classification = classified["data"]["classification"]
            action = classified["data"]["action"]

            logger.warning(
                "operation_failed",
                attempt=attempts,
                classification=classification,
                error=str(exception),
            )

            if action == ACTION_HALT:
                return make_failure(
                    f"Fallada critica: {exception}",
                    meta={
                        "exception_type": type(exception).__name__,
                        "action": ACTION_HALT,
                        "attempts": attempts,
                    },
                )

            if action == ACTION_ISOLATE:
                return make_failure(
                    f"Fallada permanent: {exception}",
                    meta={
                        "exception_type": type(exception).__name__,
                        "action": ACTION_ISOLATE,
                        "attempts": attempts,
                    },
                )

            if attempts >= max_attempts:
                return make_hold(
                    f"Intents exhaurits despres de {attempts}: {exception}",
                    meta={
                        "exception_type": type(last_error).__name__ if last_error else None,
                        "attempts": attempts,
                        "max_attempts": max_attempts,
                    },
                )

    return make_hold("Intents exhaurits", meta={"attempts": attempts})


class ComponentIsolation:
    def __init__(self, failure_threshold: int = 3) -> None:
        if failure_threshold <= 0:
            raise ValueError("El llindar ha de ser positiu")
        self.failure_threshold = failure_threshold
        self._failures: dict[str, int] = {}
        self._isolated: set[str] = set()

    def record_failure(self, component: str) -> dict[str, Any]:
        if not component:
            return make_reject("El component no pot ser buit")

        count = self._failures.get(component, 0) + 1
        self._failures[component] = count

        just_isolated = False
        if count >= self.failure_threshold and component not in self._isolated:
            self._isolated.add(component)
            just_isolated = True
            logger.error("component_isolated", component=component, failures=count)

        return make_success(
            {
                "component": component,
                "failures": count,
                "isolated": component in self._isolated,
                "just_isolated": just_isolated,
            },
            meta={"contract": CONTRACT_NAME},
        )

    def record_success(self, component: str) -> dict[str, Any]:
        self._failures.pop(component, None)
        self._isolated.discard(component)
        return make_success({"component": component, "reset": True})

    def is_isolated(self, component: str) -> bool:
        return component in self._isolated

    def snapshot(self) -> dict[str, Any]:
        return make_success(
            {
                "failures": dict(self._failures),
                "isolated": sorted(self._isolated),
                "threshold": self.failure_threshold,
            },
            meta={"contract": CONTRACT_NAME},
        )


def degradation_verdict(
    isolated_components: list[str], total_components: int
) -> dict[str, Any]:
    if total_components <= 0:
        return make_reject("El nombre total de components ha de ser positiu")
    if len(isolated_components) > total_components:
        return make_reject(
            "Hi ha mes components aillats que components totals",
            meta={"isolated": len(isolated_components), "total": total_components},
        )

    ratio = len(isolated_components) / total_components
    if ratio == 0:
        state = "full"
    elif ratio < 0.5:
        state = "degraded-operational"
    else:
        state = "degraded-critical"

    return make_success(
        {
            "state": state,
            "isolated": len(isolated_components),
            "total": total_components,
            "ratio": round(ratio, 4),
            "system_alive": ratio < 1.0,
        },
        meta={"contract": CONTRACT_NAME, "source": "S4.4.5"},
    )
