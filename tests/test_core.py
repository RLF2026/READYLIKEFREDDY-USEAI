"""Proves de SPEC-CODE-001 del contracte de retorn i del principi fail-closed.

Proves sobre funcions pures: verificació determinista, sense recursos externs.
Les proves que necessiten un servidor HTTP real són a `test_monitoring.py`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.rlf_core.contract.return_contract import (  # noqa: E402
    CANONICAL_STATUSES,
    is_canonical,
    make_failure,
    make_hold,
    make_reject,
    make_skipped,
    make_success,
    unwrap,
)
from shared.rlf_core.contract.fail_closed import (  # noqa: E402
    DECISION_ACCEPT,
    DECISION_HOLD,
    DECISION_REJECT,
    apply_fail_closed,
    assert_no_blanks,
    decide,
)


def test_success_shape_is_canonical() -> None:
    """Un resultat SUCCESS compleix el contracte i no porta motiu."""
    result = make_success({"value": 1})
    assert is_canonical(result)
    assert result["status"] == "SUCCESS"
    assert result["reason"] is None
    assert result["data"] == {"value": 1}


def test_every_constructor_yields_a_canonical_result() -> None:
    """Els constructors produeixen resultats canònics."""
    results = [
        make_success({"a": 1}),
        make_skipped("no aplicable"),
        make_hold("falta evidència"),
        make_reject("contradicció"),
        make_failure("excepció", meta={"exception_type": "ValueError"}),
    ]
    for result in results:
        assert result["status"] in CANONICAL_STATUSES
        assert is_canonical(result)


def test_non_success_results_carry_no_data() -> None:
    """Cap estat que no sigui SUCCESS pot portar data."""
    for result in (make_skipped("x"), make_hold("x"), make_reject("x")):
        assert result["data"] is None


def test_unwrap_returns_data_only_on_success() -> None:
    """unwrap extreu la dada del SUCCESS i refusa la resta."""
    assert unwrap(make_success({"ok": True})) == {"ok": True}
    try:
        unwrap(make_hold("pendent"))
    except ValueError:
        pass
    else:
        raise AssertionError("unwrap hauria d'haver llançat sobre un HOLD")


def test_fail_closed_rejects_on_contradiction() -> None:
    """Una contradicció guanya sobre qualsevol altra condició."""
    result = apply_fail_closed(
        evidence={"source": "A"},
        contradictions=["A diu disponible, B diu venut"],
        missing_fields=["price"],
        validation_passed=False,
    )
    assert result["data"]["decision"] == DECISION_REJECT
    assert result["data"]["rule_applied"] == 3


def test_fail_closed_holds_on_missing_evidence() -> None:
    """Sense evidència, la decisió és HOLD i no REJECT."""
    result = apply_fail_closed(evidence=None, contradictions=[], validation_passed=True)
    assert result["data"]["decision"] == DECISION_HOLD
    assert "evidence" in result["data"]["details"]["missing_fields"]


def test_fail_closed_accepts_only_with_evidence_and_validation() -> None:
    """Amb evidència i validació passada, la decisió és ADVANCE."""
    result = apply_fail_closed(
        evidence={"price": 25, "source": "seller"},
        contradictions=[],
        missing_fields=[],
        validation_passed=True,
    )
    assert result["data"]["decision"] == DECISION_ACCEPT
    assert result["data"]["rule_applied"] == 4


def test_decide_returns_hold_on_internal_failure() -> None:
    """decide() no propaga mai una excepció: retorna HOLD."""
    assert decide(evidence={"x": 1}, validation_passed=True) == DECISION_ACCEPT
    assert decide(evidence=None, validation_passed=True) == DECISION_HOLD


def test_assert_no_blanks_flags_unknown_and_tbd() -> None:
    """R17: UNKNOWN i TBD són buits prohibits en un registre certificat."""
    result = assert_no_blanks(
        {"name": "The Fred Perry Shirt", "material": "UNKNOWN", "era": "TBD"},
        ["name", "material", "era"],
    )
    assert result["status"] == "HOLD"
    assert set(result["meta"]["blanks"]) == {"material", "era"}


def test_assert_no_blanks_passes_a_complete_record() -> None:
    """Un registre complet passa la comprovació de buits."""
    result = assert_no_blanks(
        {"name": "The Fred Perry Shirt", "material": "100% Cotton"},
        ["name", "material"],
    )
    assert result["status"] == "SUCCESS"


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"OK: {len(tests)} proves passades")
