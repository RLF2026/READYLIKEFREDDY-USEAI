from typing import Any

from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

STATE_KNOWN: str = "CONEGUT"
STATE_AVAILABLE: str = "DISPONIBLE"
STATE_ELIGIBLE: str = "ELEGIBLE"
STATE_INTERESTING: str = "INTERESSANT"
STATE_SELECTED: str = "SELECCIONAT"
STATE_PHYSICAL_STOCK: str = "STOCK FISIC"

STATE_STALE: str = "STALE"
STATE_HOLD: str = "HOLD"
STATE_REJECT: str = "REJECT"
STATE_OUT: str = "FORA"

CANONICAL_STATES: tuple[str, ...] = (
    STATE_KNOWN,
    STATE_AVAILABLE,
    STATE_ELIGIBLE,
    STATE_INTERESTING,
    STATE_SELECTED,
    STATE_PHYSICAL_STOCK,
)

AUXILIARY_STATES: tuple[str, ...] = (STATE_STALE, STATE_HOLD, STATE_REJECT, STATE_OUT)

ALL_STATES: frozenset[str] = frozenset(CANONICAL_STATES + AUXILIARY_STATES)

ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    STATE_KNOWN: frozenset({STATE_AVAILABLE, STATE_STALE, STATE_REJECT, STATE_OUT}),
    STATE_AVAILABLE: frozenset({STATE_ELIGIBLE, STATE_STALE, STATE_REJECT, STATE_OUT}),
    STATE_STALE: frozenset({STATE_AVAILABLE, STATE_KNOWN, STATE_OUT}),
    STATE_ELIGIBLE: frozenset({STATE_INTERESTING, STATE_HOLD, STATE_STALE, STATE_REJECT}),
    STATE_HOLD: frozenset({STATE_ELIGIBLE, STATE_REJECT}),
    STATE_INTERESTING: frozenset({STATE_SELECTED, STATE_STALE, STATE_REJECT}),
    STATE_SELECTED: frozenset({STATE_PHYSICAL_STOCK, STATE_STALE, STATE_INTERESTING}),
    STATE_PHYSICAL_STOCK: frozenset({STATE_OUT}),
    STATE_REJECT: frozenset({STATE_OUT}),
    STATE_OUT: frozenset(),
}

REVERSIBLE_TRANSITIONS: frozenset[tuple[str, str]] = frozenset(
    {
        (STATE_KNOWN, STATE_AVAILABLE),
        (STATE_AVAILABLE, STATE_KNOWN),
        (STATE_AVAILABLE, STATE_STALE),
        (STATE_STALE, STATE_AVAILABLE),
        (STATE_KNOWN, STATE_STALE),
        (STATE_STALE, STATE_KNOWN),
        (STATE_ELIGIBLE, STATE_HOLD),
        (STATE_HOLD, STATE_ELIGIBLE),
        (STATE_SELECTED, STATE_INTERESTING),
    }
)

PERMITTED_OPERATIONS: dict[str, tuple[str, ...]] = {
    STATE_KNOWN: ("verify_availability", "discard"),
    STATE_AVAILABLE: ("verify_eligibility", "mark_stale"),
    STATE_ELIGIBLE: ("valuate", "mark_hold"),
    STATE_INTERESTING: ("select", "reserve"),
    STATE_SELECTED: ("sell", "materialise", "withdraw"),
    STATE_PHYSICAL_STOCK: ("ship", "return"),
}

PROHIBITED_OPERATIONS: dict[str, tuple[str, ...]] = {
    STATE_KNOWN: ("offer", "sell", "buy"),
    STATE_AVAILABLE: ("offer_without_verification",),
    STATE_ELIGIBLE: ("offer_without_valuation",),
    STATE_INTERESTING: ("offer_without_selection",),
    STATE_SELECTED: ("sell_when_availability_stale",),
    STATE_PHYSICAL_STOCK: ("return_to_product_pool",),
}

POLICY_FAIL_CLOSED: str = "RLF_PLUS_LAUREL_LEDGER_FAIL_CLOSED"

logger = get_logger(__name__)


class TransitionGuard:
    def __init__(self, case_id, origin, destination, condition, source, predicate) -> None:
        self.case_id = case_id
        self.origin = origin
        self.destination = destination
        self.condition = condition
        self.source = source
        self.predicate = predicate

    def evaluate(self, context: dict[str, Any]) -> dict[str, Any]:
        try:
            outcome = self.predicate(context)
            if outcome is None:
                return make_hold(
                    f"Dada absent per a la guarda del cas {self.case_id}",
                    meta={"case_id": self.case_id, "source": self.source},
                )
            if not outcome:
                return make_success(
                    {"allowed": False, "case_id": self.case_id},
                    meta={"source": self.source},
                )
            return make_success(
                {"allowed": True, "case_id": self.case_id},
                meta={"source": self.source},
            )
        except Exception as exception:
            logger.critical("guard_unexpected", case=self.case_id, error=str(exception))
            return make_failure(
                f"Excepcio inesperada: {exception}",
                meta={"case_id": self.case_id, "exception_type": type(exception).__name__},
            )


def _flag(context: dict[str, Any], key: str):
    value = context.get(key)
    if value is None:
        return None
    return bool(value)


def guards() -> tuple[TransitionGuard, ...]:
    return (
        TransitionGuard(1, STATE_KNOWN, STATE_AVAILABLE,
            "La reconsulta confirma disponibilitat amb senyal positiu.", "S3.8.4",
            lambda c: _flag(c, "availability_confirmed")),
        TransitionGuard(2, STATE_KNOWN, STATE_STALE,
            "La reconsulta falla o no retorna senyal concloent.", "S3.8.4",
            lambda c: _flag(c, "availability_unresolved")),
        TransitionGuard(3, STATE_KNOWN, STATE_OUT,
            "Duplicat exacte: el candidat ja existeix com a identitat canonica.",
            "S3.2.2.A cas 3 (OP-020)", lambda c: _flag(c, "exact_duplicate")),
        TransitionGuard(4, STATE_KNOWN, STATE_REJECT,
            "Criteri explicitament incomplert o contradiccio a l'elegibilitat.", "S3.3.8",
            lambda c: _flag(c, "criteria_explicitly_failed")),
        TransitionGuard(5, STATE_AVAILABLE, STATE_ELIGIBLE,
            "Compleix tots els criteris d'elegibilitat de S3.3.8.", "S3.3.8",
            lambda c: _flag(c, "eligible_criteria_met")),
        TransitionGuard(6, STATE_AVAILABLE, STATE_STALE,
            "La disponibilitat deixa de confirmar-se.", "S3.8.4",
            lambda c: _flag(c, "availability_unresolved")),
        TransitionGuard(7, STATE_AVAILABLE, STATE_REJECT,
            "Criteri d'elegibilitat incomplert de manera concloent.", "S3.3.8",
            lambda c: _flag(c, "criteria_explicitly_failed")),
        TransitionGuard(8, STATE_STALE, STATE_AVAILABLE,
            "Una reconsulta posterior confirma disponibilitat amb senyal positiu.", "S3.8.4",
            lambda c: _flag(c, "availability_reconfirmed")),
        TransitionGuard(9, STATE_STALE, STATE_KNOWN,
            "La pagina canvia d'estructura o identitat (OP-021).",
            "S3.2.2.A cas 9 (OP-021)", lambda c: _flag(c, "page_structure_changed")),
        TransitionGuard(10, STATE_STALE, STATE_OUT,
            "No-disponibilitat concloent, o STALE persistent: 3 reconsultes consecutives "
            "en Sale+Backup (aprox 15 min) o 2 en Pool (aprox 12 h) (OP-022).",
            "S3.2.2.A cas 10 (OP-022)", lambda c: _flag(c, "stale_persistence_exceeded")),
        TransitionGuard(11, STATE_ELIGIBLE, STATE_INTERESTING,
            "Els quatre filtres obligatoris i simultanis de S3.9.1 son PASS, inclosa "
            "competencia observable, i benefici_net_real dins la zona 40-90 EUR.",
            "S3.9.1-S3.9.6", lambda c: _flag(c, "four_filters_pass")),
        TransitionGuard(12, STATE_ELIGIBLE, STATE_HOLD,
            "Dada o evidencia obligatoria absent o no determinable en qualsevol dels "
            "quatre filtres, inclosa la competencia observable, o en el cost complet.",
            "S3.2.4 S4.1", lambda c: _flag(c, "mandatory_data_missing")),
        TransitionGuard(13, STATE_ELIGIBLE, STATE_STALE,
            "La disponibilitat deixa de confirmar-se durant l'avaluacio.", "S3.8.4",
            lambda c: _flag(c, "availability_unresolved")),
        TransitionGuard(14, STATE_ELIGIBLE, STATE_REJECT,
            "Contradiccio clara en les dades d'elegibilitat o economiques.", "S3.9.6",
            lambda c: _flag(c, "data_contradiction")),
        TransitionGuard(15, STATE_HOLD, STATE_ELIGIBLE,
            "Evidencia addicional o revisio (humana o de nova font) resol la incertesa "
            "a favor del compliment dels criteris de S3.3.8.", "S3.3.8 S3.7.7",
            lambda c: _flag(c, "uncertainty_resolved_favourably")),
        TransitionGuard(16, STATE_HOLD, STATE_REJECT,
            "La revisio confirma un criteri explicitament incomplert o una contradiccio.",
            "S3.3.8", lambda c: _flag(c, "review_confirms_failure")),
        TransitionGuard(17, STATE_INTERESTING, STATE_SELECTED,
            "El candidat queda dins les 1.100 places (Sale+Backup) un cop aplicat "
            "l'ordre per score i les quotes de diversificacio, i la disponibilitat es "
            "verificada en el moment de la seleccio.", "S3.8.6 S3.10",
            lambda c: _flag(c, "within_selection_slots")),
        TransitionGuard(18, STATE_INTERESTING, STATE_STALE,
            "La disponibilitat deixa de confirmar-se abans de la seleccio.", "S3.8.4",
            lambda c: _flag(c, "availability_unresolved")),
        TransitionGuard(19, STATE_INTERESTING, STATE_REJECT,
            "Un recalculo amb dades actualitzades fa benefici_net_real < 25 EUR de "
            "manera concloent, no per manca de dades.", "S3.9.6",
            lambda c: _flag(c, "recalculated_below_net_minimum")),
        TransitionGuard(20, STATE_SELECTED, STATE_PHYSICAL_STOCK,
            "La comanda associada arriba a REBUDA_A_SEU: RLF posseeix fisicament la peca.",
            "S3.13.4", lambda c: _flag(c, "order_at_hq")),
        TransitionGuard(21, STATE_SELECTED, STATE_STALE,
            "La comprovacio just-in-time o el monitoratge de Sale/Backup detecta "
            "indisponibilitat abans que existeixi una comanda que comprometi la compra.",
            "S3.14.3 S3.8.4", lambda c: _flag(c, "availability_unresolved")),
        TransitionGuard(22, STATE_SELECTED, STATE_INTERESTING,
            "Decisio de retirada per reavaluacio de scoring o diversificacio, SENSE "
            "indisponibilitat detectada.", "S3.8.3 S3.8.6",
            lambda c: _flag(c, "withdrawal_by_reevaluation")),
        TransitionGuard(23, STATE_PHYSICAL_STOCK, STATE_OUT,
            "Enviament generat i lliurat al transportista (estat de comanda ENVIADA).",
            "S3.13.4", lambda c: _flag(c, "shipment_delivered_to_carrier")),
        TransitionGuard(24, STATE_REJECT, STATE_OUT,
            "Transicio automatica i incondicional un cop registrada la decisio REJECT.",
            "S3.2.3", lambda c: True),
    )


def guard_for(case_id: int):
    for guard in guards():
        if guard.case_id == case_id:
            return guard
    return None


def guards_for(origin: str, destination: str) -> tuple[TransitionGuard, ...]:
    return tuple(
        g for g in guards() if g.origin == origin and g.destination == destination
    )


def is_transition_allowed(origin: str, destination: str) -> bool:
    return destination in ALLOWED_TRANSITIONS.get(origin, frozenset())


def is_transition_reversible(origin: str, destination: str) -> bool:
    return (origin, destination) in REVERSIBLE_TRANSITIONS


def transition(origin: str, destination: str, context: dict[str, Any]) -> dict[str, Any]:
    if origin not in ALL_STATES or destination not in ALL_STATES:
        return make_reject(
            "Estat no canonic", meta={"origin": origin, "destination": destination}
        )

    if not is_transition_allowed(origin, destination):
        return make_reject(
            "Transicio no permesa per la taula de S3.2.2",
            meta={"origin": origin, "destination": destination},
        )

    applicable = guards_for(origin, destination)
    if not applicable:
        return make_reject(
            "La transicio es permesa pero cap guarda de S3.2.2.A la cobreix",
            meta={"origin": origin, "destination": destination},
        )

    held: list[int] = []
    for guard in applicable:
        outcome = guard.evaluate(context)
        if outcome["status"] == "FAILURE":
            return outcome
        if outcome["status"] == "HOLD":
            held.append(guard.case_id)
            continue
        if outcome["data"]["allowed"]:
            return make_success(
                {
                    "origin": origin,
                    "destination": destination,
                    "executed": True,
                    "case_id": guard.case_id,
                    "reversible": is_transition_reversible(origin, destination),
                },
                meta={"source": guard.source},
            )

    if held:
        return make_hold(
            "Transicio ajornada: cap guarda satisfeta i alguna depen de dada absent",
            meta={"origin": origin, "destination": destination, "held_cases": held},
        )

    return make_success(
        {
            "origin": origin,
            "destination": destination,
            "executed": False,
            "reason": "cap guarda satisfeta",
        }
    )


def is_operation_permitted(state: str, operation: str) -> bool:
    return operation in PERMITTED_OPERATIONS.get(state, ())
