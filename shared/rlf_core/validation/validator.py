from typing import Any, Callable, Iterable, Optional, Sequence

from shared.rlf_core.contract.return_contract import (
    CANONICAL_STATUSES,
    make_failure,
    make_hold,
    make_reject,
    make_success,
    is_canonical,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

RULE_REQUIRED: str = "required"
RULE_TYPE: str = "type"
RULE_RANGE: str = "range"
RULE_ENUM: str = "enum"
RULE_PATTERN: str = "pattern"
RULE_LENGTH: str = "length"

BLANK_MARKERS: frozenset[str] = frozenset({"", "UNKNOWN", "TBD"})

DEFAULT_COVERAGE_TARGETS: dict[str, float] = {
    "public_functions": 1.0,
    "return_statuses": 1.0,
    "conditional_branches": 0.80,
}

logger = get_logger(__name__)


class FieldRule:
    """Una regla de validacio aplicada a un camp d'un registre."""

    def __init__(
        self,
        field: str,
        rule: str,
        value: Any = None,
        allow_not_applicable: bool = False,
        justification: Optional[str] = None,
    ) -> None:
        """Inicialitza una regla de validacio.

        Args:
            field: Nom del camp sobre el qual s'aplica.
            rule: Tipus de regla, un dels sis permesos.
            value: Parametre de la regla, com el tipus, el rang, el conjunt o
                la longitud admesa.
            allow_not_applicable: Si NOT_APPLICABLE es admissible en aques camp.
            justification: Justificacio persistent que exigeix R17 quan el camp
                es declara NOT_APPLICABLE.

        Raises:
            ValueError: Si el tipus de regla no es cap dels coneguts.
        """
        known = {RULE_REQUIRED, RULE_TYPE, RULE_RANGE, RULE_ENUM, RULE_PATTERN, RULE_LENGTH}
        if rule not in known:
            raise ValueError(f"Tipus de regla desconegut: {rule!r}")
        self.field = field
        self.rule = rule
        self.value = value
        self.allow_not_applicable = allow_not_applicable
        self.justification = justification


def validate_required(value: Any) -> Optional[str]:
    """Comprova que un camp obligatori no es buit, segons R17.

    Args:
        value: Valor del camp.

    Returns:
        None si el valor es valid, o el motiu del rebuig.
    """
    if value is None:
        return "camp absent"
    if isinstance(value, str) and value.strip().upper() in BLANK_MARKERS:
        return "camp buit o no resolt (R17)"
    return None


def validate_type(value: Any, expected: Any) -> Optional[str]:
    """Comprova el tipus d'un valor.

    Args:
        value: Valor del camp.
        expected: Tipus esperat.

    Returns:
        None si el tipus es correcte, o el motiu del rebuig.
    """
    if value is None:
        return None
    if not isinstance(value, expected):
        return "tipus incorrecte: s'esperava " + str(getattr(expected, "__name__", expected))
    return None


def validate_range(value: Any, limits: Sequence[float]) -> Optional[str]:
    """Comprova que un valor numeric es dins d'un interval.

    Args:
        value: Valor del camp.
        limits: Parell de minim i maxim.

    Returns:
        None si el valor es dins l'interval, o el motiu del rebuig.
    """
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return "rang sobre un valor no numeric"
    if len(limits) != 2:
        return "el rang requereix minim i maxim"
    low, high = limits
    if not low <= float(value) <= high:
        return f"fora de rang [{low}, {high}]"
    return None


def validate_enum(value: Any, allowed: Iterable[Any]) -> Optional[str]:
    """Comprova que un valor pertany a un conjunt permes.

    Args:
        value: Valor del camp.
        allowed: Valors admesos.

    Returns:
        None si el valor es admissible, o el motiu del rebuig.
    """
    if value is None:
        return None
    if value not in set(allowed):
        return "valor fora del conjunt permes"
    return None


def validate_length(value: Any, limits: Sequence[int]) -> Optional[str]:
    """Comprova la longitud d'una cadena o d'una col·leccio.

    Args:
        value: Valor del camp.
        limits: Parell de minim i maxim.

    Returns:
        None si la longitud es dins l'interval, o el motiu del rebuig.
    """
    if value is None:
        return None
    if not hasattr(value, "__len__"):
        return "longitud sobre un valor sense longitud"
    if len(limits) != 2:
        return "la longitud requereix minim i maxim"
    low, high = limits
    if not low <= len(value) <= high:
        return f"longitud fora de [{low}, {high}]"
    return None


def _apply_rule(rule: FieldRule, value: Any) -> Optional[str]:
    """Aplica una regla concreta a un valor.

    Args:
        rule: Regla a aplicar.
        value: Valor del camp.

    Returns:
        None si el valor passa la regla, o el motiu del rebuig.
    """
    if rule.rule == RULE_REQUIRED:
        return validate_required(value)
    if rule.rule == RULE_TYPE:
        return validate_type(value, rule.value)
    if rule.rule == RULE_RANGE:
        return validate_range(value, rule.value)
    if rule.rule == RULE_ENUM:
        return validate_enum(value, rule.value)
    if rule.rule == RULE_LENGTH:
        return validate_length(value, rule.value)
    return None


def validate_record(
    record: dict[str, Any],
    rules: Sequence[FieldRule],
) -> dict[str, Any]:
    """Valida un registre contra un conjunt de regles.

    Args:
        record: Registre a validar.
        rules: Regles a aplicar sobre els camps del registre.

    Returns:
        Un resultat canonic SUCCESS amb els camps validats, o HOLD si algun
        camp no passa. REJECT si el registre no es un diccionari. FAILURE si
        apareix una excepcio inesperada.
    """
    try:
        if not isinstance(record, dict):
            return make_reject("El registre no es un diccionari")

        failures: list[dict[str, str]] = []
        passed: list[str] = []

        for rule in rules:
            value = record.get(rule.field)

            if (
                rule.allow_not_applicable
                and isinstance(value, str)
                and value.strip().upper() == "NOT_APPLICABLE"
            ):
                if not rule.justification or not rule.justification.strip():
                    failures.append(
                        {
                            "field": rule.field,
                            "reason": "NOT_APPLICABLE sense justificacio (R17)",
                        }
                    )
                else:
                    passed.append(rule.field)
                continue

            reason = _apply_rule(rule, value)
            if reason:
                failures.append({"field": rule.field, "reason": reason})
            else:
                passed.append(rule.field)

        if failures:
            logger.info("validation_hold", failures=len(failures))
            return make_hold(
                "Validacio incompleta: camps que no passen",
                meta={"failures": failures, "passed": passed},
            )

        return make_success(
            {"validated_fields": sorted(passed)},
            meta={"rule_count": len(rules)},
        )
    except Exception as exception:
        logger.critical("validation_unexpected", error=str(exception))
        return make_failure(
            f"Excepcio inesperada: {exception}",
            meta={"exception_type": type(exception).__name__},
        )


def find_contradictions(
    claims: Sequence[dict[str, Any]],
    key_field: str = "field",
    value_field: str = "value",
) -> dict[str, Any]:
    """Detecta contradiccions entre afirmacions sobre el mateix camp.

    Una contradiccio es REJECT i no HOLD, perque dues fonts que es neguen ja
    son informacio i no ignorancia, segons la regla tercera de S4.1.4.

    Args:
        claims: Afirmacions amb camp i valor.
        key_field: Nom del camp que identifica la materia.
        value_field: Nom del camp que porta el valor declarat.

    Returns:
        Un resultat canonic SUCCESS amb les contradiccions trobades i un
        indicador de si n'hi ha. REJECT si el format no es l'esperat.
    """
    if not isinstance(claims, Sequence):
        return make_reject("Les afirmacions han de ser una sequencia")

    by_field: dict[str, set[str]] = {}
    for claim in claims:
        if not isinstance(claim, dict):
            return make_reject("Una afirmacio no es un diccionari")
        subject = claim.get(key_field)
        value = claim.get(value_field)
        if subject is None or value is None:
            continue
        by_field.setdefault(str(subject), set()).add(str(value))

    contradictions = [
        {"field": field, "values": sorted(values)}
        for field, values in by_field.items()
        if len(values) > 1
    ]

    return make_success(
        {"contradictions": contradictions, "has_contradiction": bool(contradictions)},
        meta={"claims": len(claims)},
    )


def validate_module_output(result: Any) -> dict[str, Any]:
    """Comprova que la sortida d'un modul compleix SPEC-CODE-001 (S6.1.6).

    Args:
        result: Valor retornat per un modul.

    Returns:
        Un resultat canonic SUCCESS si la forma es correcta, o REJECT si no ho
        es o si porta dada amb un estat que no sigui SUCCESS.
    """
    if not is_canonical(result):
        return make_reject(
            "La sortida no compleix el contracte de retorn de SPEC-CODE-001",
            meta={"received_type": type(result).__name__},
        )

    if result["status"] not in CANONICAL_STATUSES:
        return make_reject("Estat no canonic", meta={"status": result["status"]})

    if result["status"] != "SUCCESS" and result["data"] is not None:
        return make_reject("Un estat que no es SUCCESS no pot portar data")

    return make_success({"status": result["status"]})


def coverage_report(
    covered: dict[str, int],
    totals: dict[str, int],
    targets: Optional[dict[str, float]] = None,
) -> dict[str, Any]:
    """Calcula la cobertura de proves contra els objectius de S6.1.11.

    Args:
        covered: Elements coberts per categoria.
        totals: Elements totals per categoria.
        targets: Objectius per categoria. Per defecte, els de S6.1.11.

    Returns:
        Un resultat canonic SUCCESS amb la cobertura i la llista de mancances.
        HOLD si alguna categoria no te elements totals.
    """
    threshold = dict(targets or DEFAULT_COVERAGE_TARGETS)

    for category, total in totals.items():
        if total <= 0:
            return make_hold(
                f"Categoria sense elements totals: {category}",
                meta={"category": category},
            )

    report: dict[str, Any] = {}
    shortfalls: list[str] = []

    for category, total in totals.items():
        achieved = covered.get(category, 0) / total
        target = threshold.get(category, 1.0)
        meets = achieved >= target
        report[category] = {
            "covered": covered.get(category, 0),
            "total": total,
            "ratio": round(achieved, 4),
            "target": target,
            "meets": meets,
        }
        if not meets:
            shortfalls.append(category)

    return make_success(
        {"coverage": report, "shortfalls": shortfalls, "complete": not shortfalls},
        meta={"source": "S6.1.11"},
    )


def assert_spec_code_compliant(module_name: str, checks: dict[str, bool]) -> dict[str, Any]:
    """Comprova els requisits de SPEC-CODE-001 d'un modul (S6.1).

    Args:
        module_name: Nom del modul.
        checks: Resultats de les comprovacions individuals.

    Returns:
        Un resultat canonic SUCCESS si totes passen, o REJECT amb la llista de
        comprovacions fallides.
    """
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        return make_reject(
            f"El modul {module_name} incompleix SPEC-CODE-001",
            meta={"failed_checks": sorted(failed), "source": "S6.1"},
        )
    return make_success(
        {"module": module_name, "checks_passed": len(checks)},
        meta={"source": "S6.1"},
    )
