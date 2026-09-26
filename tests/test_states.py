import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.rlf_core.state.states import (  # noqa: E402
    ALL_STATES,
    ALLOWED_TRANSITIONS,
    CANONICAL_STATES,
    PERMITTED_OPERATIONS,
    STATE_AVAILABLE,
    STATE_ELIGIBLE,
    STATE_HOLD,
    STATE_INTERESTING,
    STATE_KNOWN,
    STATE_OUT,
    STATE_PHYSICAL_STOCK,
    STATE_REJECT,
    STATE_SELECTED,
    STATE_STALE,
    guard_for,
    guards,
    is_operation_permitted,
    is_transition_reversible,
    transition,
)


def guards_for(origin: str, destination: str):
    return tuple(g for g in guards() if g.origin == origin and g.destination == destination)


def test_six_canonical_states_exist() -> None:
    assert len(CANONICAL_STATES) == 6
    assert set(CANONICAL_STATES) == {
        STATE_KNOWN, STATE_AVAILABLE, STATE_ELIGIBLE,
        STATE_INTERESTING, STATE_SELECTED, STATE_PHYSICAL_STOCK,
    }


def test_four_auxiliary_states_exist() -> None:
    assert ALL_STATES == set(CANONICAL_STATES) | {
        STATE_STALE, STATE_HOLD, STATE_REJECT, STATE_OUT
    }


def test_twenty_four_transition_guards_are_registered() -> None:
    assert len(guards()) == 24
    assert sorted(guard.case_id for guard in guards()) == list(range(1, 25))


def test_every_permitted_transition_has_a_guard() -> None:
    for origin, destinations in ALLOWED_TRANSITIONS.items():
        for destination in destinations:
            covering = guards_for(origin, destination)
            assert covering, f"Transicio sense guarda: {origin} -> {destination}"


def test_known_can_become_available_with_confirmed_signal() -> None:
    result = transition(STATE_KNOWN, STATE_AVAILABLE, {"availability_confirmed": True})
    assert result["status"] == "SUCCESS"
    assert result["data"]["executed"] is True
    assert result["data"]["case_id"] == 1


def test_known_to_available_is_reversible() -> None:
    assert is_transition_reversible(STATE_KNOWN, STATE_AVAILABLE) is True


def test_missing_data_produces_hold_not_reject() -> None:
    result = transition(STATE_KNOWN, STATE_AVAILABLE, {})
    assert result["status"] == "HOLD"
    assert 1 in result["meta"]["held_cases"]


def test_hold_to_eligible_is_the_canonical_resolution() -> None:
    result = transition(
        STATE_HOLD, STATE_ELIGIBLE, {"uncertainty_resolved_favourably": True}
    )
    assert result["data"]["executed"] is True
    assert result["data"]["case_id"] == 15
    assert result["data"]["reversible"] is True


def test_hold_to_reject_closes_the_uncertainty() -> None:
    result = transition(STATE_HOLD, STATE_REJECT, {"review_confirms_failure": True})
    assert result["data"]["executed"] is True
    assert result["data"]["case_id"] == 16


def test_reject_to_out_is_unconditional() -> None:
    result = transition(STATE_REJECT, STATE_OUT, {})
    assert result["status"] == "SUCCESS"
    assert result["data"]["executed"] is True


def test_transition_outside_the_table_is_rejected() -> None:
    result = transition(STATE_PHYSICAL_STOCK, STATE_KNOWN, {})
    assert result["status"] == "REJECT"


def test_physical_stock_only_goes_out() -> None:
    assert ALLOWED_TRANSITIONS[STATE_PHYSICAL_STOCK] == frozenset({STATE_OUT})


def test_out_is_terminal() -> None:
    assert ALLOWED_TRANSITIONS[STATE_OUT] == frozenset()


def test_selected_withdrawal_is_distinct_from_staleness() -> None:
    withdrawal = transition(
        STATE_SELECTED, STATE_INTERESTING, {"withdrawal_by_reevaluation": True}
    )
    stale = transition(STATE_SELECTED, STATE_STALE, {"availability_unresolved": True})
    assert withdrawal["data"]["case_id"] == 22
    assert stale["data"]["case_id"] == 21


def test_stale_persistence_thresholds_are_encoded() -> None:
    guard = guard_for(10)
    assert guard is not None
    assert "3 reconsultes" in guard.condition
    assert "15 min" in guard.condition


def test_operations_permitted_by_state() -> None:
    assert is_operation_permitted(STATE_KNOWN, "verify_availability") is True
    assert is_operation_permitted(STATE_KNOWN, "sell") is False
    assert is_operation_permitted(STATE_SELECTED, "sell") is True
    assert is_operation_permitted(STATE_PHYSICAL_STOCK, "ship") is True
    assert "return_to_product_pool" not in PERMITTED_OPERATIONS[STATE_PHYSICAL_STOCK]


def test_guard_metadata_is_traceable() -> None:
    for guard in guards():
        assert guard.case_id >= 1
        assert guard.condition
        assert guard.source.startswith("S")


if __name__ == "__main__":
    tests = [v for n, v in sorted(globals().items()) if n.startswith("test_")]
    for test in tests:
        test()
    print(f"OK: {len(tests)} proves passades")
