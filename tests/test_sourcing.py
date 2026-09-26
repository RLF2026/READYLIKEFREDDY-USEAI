"""Proves del motor de sourcing: cua, finestres, orquestrador i Laurel Ledger.

Cada prova cita la seccio del document mestre que verifica. Les proves usen
recursos reals: la cua, les finestres i la matriu son objectes reals del
sistema, no simulacres que el substitueixin (R14).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from projects.rlf_suppliers_eu27.laurel_ledger.ledger import (  # noqa: E402
    EU27_COUNTRIES,
    LaurelLedger,
)
from projects.rlf_suppliers_eu27.sourcing.orchestrator import (  # noqa: E402
    CANONICAL_PHASES,
    PHASE_ASSIGNMENT,
    PHASE_COLLECTION,
    Orchestrator,
    Worker,
)
from projects.rlf_suppliers_eu27.sourcing.territorial_windows import (  # noqa: E402
    EXHAUSTION_EXHAUSTED as WINDOW_EXHAUSTED,
    TerritorialWindows,
)
from projects.rlf_suppliers_eu27.sourcing.work_queue import (  # noqa: E402
    STATUS_CLAIMED,
    STATUS_DONE,
    STATUS_PENDING,
    WorkQueue,
)
from shared.rlf_core.lanes.lane_assigner import (  # noqa: E402
    LANE_COUNT,
    LAUREL_LEDGER_UNITS,
    PriorityQueue,
    assign_lane,
)


def test_work_queue_is_append_only_and_open_ended() -> None:
    """§3.3.4: la cua es oberta i sense sostre fix."""
    queue = WorkQueue()
    for index in range(50):
        queue.append("discover", "DE", str(index))
    stats = queue.statistics()
    assert stats["data"]["total"] == 50
    assert stats["data"]["counts"][STATUS_PENDING] == 50
    assert stats["meta"]["has_fixed_ceiling"] is False


def test_work_queue_assigns_a_lane_to_every_item() -> None:
    """Cada unitat de treball porta la seva lane de §3.3.4."""
    queue = WorkQueue()
    result = queue.append("discover", "FR", "0")
    assert 1 <= result["data"]["lane"] <= LANE_COUNT


def test_work_queue_idempotency_keys_have_no_duplicates() -> None:
    """Les claus d'idempotencia de §3.3.10 no es repeteixen entre unitats."""
    queue = WorkQueue()
    for index in range(30):
        queue.append("discover", "ES", str(index))
    meta = queue.idempotency_keys()["meta"]
    assert meta["duplicates"] == 0
    assert meta["unique"] == meta["total"]


def test_work_queue_lifecycle() -> None:
    """El cicle de vida d'una unitat es pendent, reclamada i completada."""
    queue = WorkQueue()
    sequence = queue.append("discover", "IT", "0")["data"]["sequence"]
    assert queue.claim(sequence)["data"]["status"] == STATUS_CLAIMED
    assert queue.complete(sequence, {"found": 3})["data"]["status"] == STATUS_DONE


def test_work_queue_hold_on_reclaim() -> None:
    """Reclamar una unitat ja reclamada es HOLD, no REJECT."""
    queue = WorkQueue()
    sequence = queue.append("discover", "NL", "0")["data"]["sequence"]
    queue.claim(sequence)
    assert queue.claim(sequence)["status"] == "HOLD"


def test_territorial_window_requires_the_full_protocol() -> None:
    """§3.3.3: una ciutat nomes queda explorada amb el protocol complet."""
    windows = TerritorialWindows(["vintage fred perry", "second hand polo"])
    windows.add("DE", "Berlin")
    window = windows._windows["DE::Berlin"]

    window.run_search("vintage fred perry", [])
    assert window.exhaustion != WINDOW_EXHAUSTED

    window.run_search("second hand polo", [])
    assert window.exhaustion == WINDOW_EXHAUSTED


def test_territorial_window_counts_a_search_with_no_results() -> None:
    """§3.3.3: l'esgotament depen del protocol, no dels resultats."""
    windows = TerritorialWindows(["cerca unica"])
    windows.add("FR", "Lyon")
    window = windows._windows["FR::Lyon"]
    window.run_search("cerca unica", [])
    assert window.exhaustion == WINDOW_EXHAUSTED
    assert window.results == []


def test_territorial_window_rejects_a_search_outside_the_protocol() -> None:
    """Una cerca que no es del protocol es REJECT."""
    windows = TerritorialWindows(["cerca a"])
    windows.add("BE", "Bruges")
    window = windows._windows["BE::Bruges"]
    assert window.run_search("cerca inventada", [])["status"] == "REJECT"


def test_territorial_windows_statistics_and_fingerprint() -> None:
    """Les finestres resumeixen el seu estat i el del protocol."""
    windows = TerritorialWindows(["a", "b"])
    windows.add("DE", "Berlin")
    windows.add("FR", "Paris")
    assert windows.statistics()["data"]["total"] == 2
    assert len(windows.protocol_fingerprint()["data"]["fingerprint"]) == 64


def test_laurel_ledger_builds_the_canonical_matrix() -> None:
    """§3.3.9: cent localitats per vint-i-set estats son dues mil set-centes unitats."""
    ledger = LaurelLedger()
    result = ledger.build([f"locality-{index}" for index in range(100)])
    assert result["status"] == "SUCCESS"
    assert result["data"]["units"] == LAUREL_LEDGER_UNITS == 2700
    assert result["data"]["countries"] == 27


def test_laurel_ledger_rejects_more_than_one_hundred_localities() -> None:
    """La matriu canonica admet com a maxim cent localitats."""
    ledger = LaurelLedger()
    assert ledger.build([f"l-{index}" for index in range(101)])["status"] == "REJECT"


def test_laurel_ledger_rejects_duplicate_localities() -> None:
    """Les localitats duplicades son REJECT."""
    ledger = LaurelLedger()
    assert ledger.build(["Paris", "Paris"])["status"] == "REJECT"


def test_laurel_ledger_all_countries_can_work_simultaneously() -> None:
    """§3.3.9: els vint-i-set paisos poden tenir treball actiu alhora."""
    ledger = LaurelLedger()
    ledger.build(["Berlin"])
    assert ledger.statistics()["data"]["countries_with_work"] == 27
    assert ledger.statistics()["meta"]["all_countries_can_work_simultaneously"] is True


def test_laurel_ledger_priority_update() -> None:
    """§3.3.13: la cota inferior de Wilson s'actualitza per unitat."""
    ledger = LaurelLedger()
    ledger.build(["Berlin"])
    assert ledger.update_priority("DE::Berlin", 0.42)["data"]["wilson_lower"] == 0.42
    assert ledger.update_priority("DE::Berlin", 1.5)["status"] == "REJECT"


def test_laurel_ledger_unknown_unit_is_hold() -> None:
    """Una unitat que no existeix es HOLD, no REJECT."""
    ledger = LaurelLedger()
    ledger.build(["Berlin"])
    assert ledger.get("XX::Nowhere")["status"] == "HOLD"


def test_orchestrator_phases_follow_the_canonical_order() -> None:
    """§3.3.7: el cicle te fases canoniques i no es pot retrocedir."""
    orchestrator = Orchestrator()
    assert orchestrator.advance_phase(PHASE_ASSIGNMENT)["status"] == "SUCCESS"
    assert orchestrator.advance_phase(CANONICAL_PHASES[0])["status"] == "REJECT"
    assert orchestrator.advance_phase("inventada")["status"] == "REJECT"


def test_orchestrator_assigns_work_to_workers() -> None:
    """L'orquestrador reparteix unitats entre els workers disponibles."""
    orchestrator = Orchestrator([Worker("w1", capacity=2)])
    items = [
        {"sequence": 1, "action": "discover", "country": "DE", "cursor": "0"},
        {"sequence": 2, "action": "discover", "country": "FR", "cursor": "0"},
    ]
    result = orchestrator.assign_work(items)
    assert result["status"] == "SUCCESS"
    assert len(result["data"]["assigned"]) == 2


def test_orchestrator_holds_when_capacity_is_insufficient() -> None:
    """Sense capacitat suficient, les unitats queden sense assignar i es HOLD."""
    orchestrator = Orchestrator([Worker("w1", capacity=1)])
    items = [
        {"sequence": 1, "action": "discover", "country": "DE", "cursor": "0"},
        {"sequence": 2, "action": "discover", "country": "FR", "cursor": "0"},
    ]
    result = orchestrator.assign_work(items)
    assert result["status"] == "HOLD"
    assert result["meta"]["unassigned"] == [2]


def test_orchestrator_execution_is_idempotent() -> None:
    """§4.3.2: executar dues vegades la mateixa unitat no duplica efectes."""
    orchestrator = Orchestrator([Worker("w1", capacity=1)])
    orchestrator.assign_work(
        [{"sequence": 1, "action": "discover", "country": "DE", "cursor": "0"}]
    )
    calls = {"count": 0}

    def operation() -> str:
        calls["count"] += 1
        return "fet"

    first = orchestrator.execute(1, operation)
    second = orchestrator.execute(1, operation)
    assert first["data"]["outcome"] == "applied"
    assert second["data"]["outcome"] == "replayed-noop"
    assert calls["count"] == 1


def test_orchestrator_execute_without_assignment_is_hold() -> None:
    """Executar una unitat sense worker assignat es HOLD."""
    orchestrator = Orchestrator()
    assert orchestrator.execute(99, lambda: None)["status"] == "HOLD"


def test_orchestrator_cursors_are_per_lane() -> None:
    """§3.3.6: cada lane te cursor independent."""
    orchestrator = Orchestrator()
    orchestrator.update_cursor(5, "position-5")
    orchestrator.update_cursor(17, "position-17")
    cursors = orchestrator.cursors()["data"]["cursors"]
    assert cursors[5] == "position-5"
    assert cursors[17] == "position-17"
    assert orchestrator.update_cursor(101, "x")["status"] == "REJECT"


def test_orchestrator_collect_reports_worker_state() -> None:
    """La recollida de §3.3.7 resumeix l'estat dels workers."""
    orchestrator = Orchestrator([Worker("w1"), Worker("w2")])
    orchestrator.assign_work(
        [{"sequence": 1, "action": "discover", "country": "DE", "cursor": "0"}]
    )
    collected = orchestrator.collect()
    assert collected["data"]["busy"] == 1
    assert collected["data"]["idle"] == 1
    assert orchestrator.phase == PHASE_COLLECTION


def test_priority_queue_never_abandons_an_active_cursor() -> None:
    """§3.3.13: una unitat amb cursor actiu no s'abandona per prioritzar-ne una altra."""
    queue = PriorityQueue()
    queue.add("unit-low", cursor_exhausted=False, wilson_lower=0.10)
    queue.add("unit-high", cursor_exhausted=False, wilson_lower=0.90)
    assert queue.next_unit()["data"]["selected"]["unit_id"] == "unit-high"

    queue.mark_exhausted("unit-high")
    assert queue.next_unit()["data"]["selected"]["unit_id"] == "unit-low"


def test_priority_queue_holds_when_all_cursors_are_exhausted() -> None:
    """Amb tots els cursors esgotats, la cua de prioritat es HOLD."""
    queue = PriorityQueue()
    queue.add("a", cursor_exhausted=True, wilson_lower=0.5)
    assert queue.next_unit()["status"] == "HOLD"


def test_lane_assignment_is_deterministic_across_calls() -> None:
    """La mateixa clau dona sempre la mateixa lane (§3.3.4)."""
    keys = ["DE::Berlin::discover", "FR::Paris::verify", "IT::Milano::discover"]
    assert [assign_lane(k) for k in keys] == [assign_lane(k) for k in keys]


def test_eu27_country_list_has_twenty_seven_entries() -> None:
    """El perimetre de §2.1.6 son vint-i-set estats, sense el Regne Unit."""
    assert len(EU27_COUNTRIES) == 27
    assert "GB" not in EU27_COUNTRIES


if __name__ == "__main__":
    tests = [v for n, v in sorted(globals().items()) if n.startswith("test_")]
    for test in tests:
        test()
    print(f"OK: {len(tests)} proves passades")
