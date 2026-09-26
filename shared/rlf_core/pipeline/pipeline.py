from typing import Any, Callable, Optional

from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.contract.fail_closed import apply_fail_closed
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

STAGE_DISCOVERY: str = "discovery"
STAGE_NORMALIZATION: str = "normalization"
STAGE_ENTITY_RESOLUTION: str = "entity_resolution"
STAGE_DEDUPLICATION: str = "deduplication"
STAGE_VALIDATION: str = "validation"
STAGE_EVIDENCE: str = "evidence"
STAGE_CLASSIFICATION: str = "classification"
STAGE_PERSISTENCE: str = "persistence"

STAGES: tuple[str, ...] = (
    STAGE_DISCOVERY,
    STAGE_NORMALIZATION,
    STAGE_ENTITY_RESOLUTION,
    STAGE_DEDUPLICATION,
    STAGE_VALIDATION,
    STAGE_EVIDENCE,
    STAGE_CLASSIFICATION,
    STAGE_PERSISTENCE,
)

STAGE_NUMBERS: dict[str, int] = {name: index + 1 for index, name in enumerate(STAGES)}

logger = get_logger(__name__)


class Stage:
    def __init__(
        self,
        name: str,
        handler: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
    ) -> None:
        if name not in STAGE_NUMBERS:
            raise ValueError(f"Etapa no canonica: {name!r}")
        self.name = name
        self.number = STAGE_NUMBERS[name]
        self.handler = handler


class Pipeline:
    def __init__(self, stages: Optional[list[Stage]] = None) -> None:
        self.stages: list[Stage] = list(stages or [])
        self._by_name: dict[str, Stage] = {stage.name: stage for stage in self.stages}

    def add_stage(self, stage: Stage) -> dict[str, Any]:
        if stage.name in self._by_name:
            return make_reject("Etapa duplicada al pipeline", meta={"stage": stage.name})

        expected_next = len(self.stages) + 1
        if stage.number != expected_next:
            return make_reject(
                "Les etapes s'encadenen en l'ordre canonic de S3.4.2",
                meta={
                    "expected_number": expected_next,
                    "given_number": stage.number,
                    "given_stage": stage.name,
                },
            )

        self.stages.append(stage)
        self._by_name[stage.name] = stage
        return make_success({"stage": stage.name, "number": stage.number})

    def is_complete(self) -> bool:
        return tuple(stage.name for stage in self.stages) == STAGES

    def run(
        self,
        element: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        try:
            if not isinstance(element, dict) or not element:
                return make_reject("L'element d'entrada no es un diccionari amb contingut")

            shared = dict(context or {})
            current = dict(element)
            trail: list[dict[str, Any]] = []

            for stage in self.stages:
                outcome = stage.handler(current, shared)
                status = outcome.get("status")

                if status == "FAILURE":
                    return outcome
                if status == "REJECT":
                    trail.append(
                        {"stage": stage.name, "number": stage.number, "status": "REJECT"}
                    )
                    return make_reject(
                        f"Refusat a l'etapa {stage.number} ({stage.name})",
                        meta={"reason": outcome.get("reason"), "trail": trail},
                    )
                if status == "HOLD":
                    trail.append(
                        {"stage": stage.name, "number": stage.number, "status": "HOLD"}
                    )
                    return make_hold(
                        f"Ajornat a l'etapa {stage.number} ({stage.name})",
                        meta={"reason": outcome.get("reason"), "trail": trail},
                    )

                if isinstance(outcome.get("data"), dict):
                    current = outcome["data"]
                trail.append(
                    {"stage": stage.name, "number": stage.number, "status": "SUCCESS"}
                )

            logger.info("pipeline_completed", stages=len(trail))
            return make_success(
                {"element": current, "trail": trail},
                meta={"stages_executed": len(trail), "fail_closed": True},
            )
        except Exception as exception:
            logger.critical("pipeline_unexpected", error=str(exception))
            return make_failure(
                f"Excepcio inesperada: {exception}",
                meta={"exception_type": type(exception).__name__},
            )


def discovery_stage(
    discover: Callable[[dict[str, Any]], Optional[dict[str, Any]]]
) -> Stage:
    def handler(element: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        found = discover(element)
        if found is None:
            return make_hold("Discovery sense resultat", meta={"stage": STAGE_DISCOVERY})
        merged = dict(element)
        merged.update(found)
        return make_success(merged)

    return Stage(STAGE_DISCOVERY, handler)


def validation_stage(
    validate: Callable[[dict[str, Any]], tuple[bool, list[str], list[str]]]
) -> Stage:
    def handler(element: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        passed, missing, contradictions = validate(element)
        decision = apply_fail_closed(
            evidence=element,
            contradictions=contradictions,
            missing_fields=missing,
            validation_passed=passed,
        )
        if decision["status"] != "SUCCESS":
            return decision

        chosen = decision["data"]["decision"]
        if chosen == "reject":
            return make_reject("Contradiccio a la validacio", meta=decision["data"]["details"])
        if chosen == "hold":
            return make_hold("Validacio incompleta", meta=decision["data"]["details"])
        return make_success(element)

    return Stage(STAGE_VALIDATION, handler)


def passthrough_stage(name: str) -> Stage:
    def handler(element: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        return make_success(element)

    return Stage(name, handler)
