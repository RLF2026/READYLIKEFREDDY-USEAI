import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.rlf_core.deduplication.deduplication import (  # noqa: E402
    BLOOM_DEFAULT_CAPACITY,
    BLOOM_DEFAULT_ERROR_RATE,
    BloomFilter,
    LSHIndex,
    check_minhash_separation,
    deduplicate,
    jaccard,
    minhash_signature,
    minhash_similarity,
    optimal_bloom_parameters,
)
from shared.rlf_core.identity.canonical_identity import (  # noqa: E402
    CATEGORY_NOT_APPLICABLE,
    SCOPE_1940S,
    SCOPE_BRAND,
    canonical_key,
    identity_completeness,
    not_applicable_is_valid,
    same_identity,
    temporal_scope,
)
from shared.rlf_core.state.hold_resolution import (  # noqa: E402
    HOLD_SOURCES,
    RESOLVABLE_HUMAN,
    RESOLVABLE_NEVER,
    RESOLVABLE_SYSTEM,
    assert_never_resolvable,
    build_resolution,
    classify_holds,
    hold,
    hold_rate_kpi,
)


def test_bloom_parameters_match_the_document_measurement() -> None:
    result = optimal_bloom_parameters(BLOOM_DEFAULT_CAPACITY, BLOOM_DEFAULT_ERROR_RATE)
    assert result["status"] == "SUCCESS"
    assert result["data"]["bytes"] == 11982
    assert result["data"]["k"] == 7


def test_bloom_has_no_false_negatives() -> None:
    bloom = BloomFilter(capacity=1000)
    for index in range(1000):
        bloom.add(f"key-{index}")
    for index in range(1000):
        assert bloom.contains(f"key-{index}")["data"]["possibly_present"] is True


def test_bloom_flags_a_positive_as_a_suspicion() -> None:
    bloom = BloomFilter(capacity=100)
    bloom.add("present")
    assert bloom.contains("present")["data"]["requires_full_check"] is True


def test_bloom_rejects_empty_items() -> None:
    assert BloomFilter().add("")["status"] == "REJECT"


def test_jaccard_extremes() -> None:
    assert jaccard({"a", "b"}, {"a", "b"}) == 1.0
    assert jaccard({"a"}, {"b"}) == 0.0
    assert jaccard(set(), set()) == 0.0


def test_minhash_similarity_is_higher_for_identical_sets() -> None:
    tokens = [f"token-{i}" for i in range(40)]
    other = [f"token-{i}" for i in range(40, 80)]
    sig_a = minhash_signature(tokens, 128)["data"]["signature"]
    sig_b = minhash_signature(tokens, 128)["data"]["signature"]
    sig_c = minhash_signature(other, 128)["data"]["signature"]
    identical = minhash_similarity(sig_a, sig_b)["data"]["estimated_jaccard"]
    different = minhash_similarity(sig_a, sig_c)["data"]["estimated_jaccard"]
    assert identical > different


def test_minhash_requires_tokens() -> None:
    assert minhash_signature([])["status"] == "REJECT"


def test_lsh_returns_candidates_for_a_similar_signature() -> None:
    tokens = [f"t{i}" for i in range(64)]
    signature = minhash_signature(tokens, 64)["data"]["signature"]
    index = LSHIndex(bands=16)
    index.add("item-a", signature)
    candidates = index.candidates(signature)["data"]["candidates"]
    assert any(c["identifier"] == "item-a" for c in candidates)


def test_dedup_separates_duplicates_from_unique_items() -> None:
    items = [
        {"canonical_key": "k1", "tokens": ["polo", "navy", "m12", "cotton"]},
        {"canonical_key": "k2", "tokens": ["polo", "navy", "m12", "cotton"]},
        {"canonical_key": "k3", "tokens": ["jacket", "nylon", "j2660", "blue"]},
    ]
    result = deduplicate(items, tolerance=0.8, permutations=64)
    assert result["status"] == "SUCCESS"
    assert result["data"]["duplicates"] >= 1


def test_dedup_holds_when_an_item_lacks_its_key() -> None:
    assert deduplicate([{"tokens": ["a"]}])["status"] == "HOLD"


def test_minhash_separation_check_matches_the_document() -> None:
    result = check_minhash_separation()
    assert result["data"]["same_item"] == 0.727
    assert result["data"]["different_item"] == 0.156
    assert result["data"]["separation_possible"] is True


def test_canonical_key_is_deterministic() -> None:
    first = canonical_key("M12", None, "Navy", "Polo Shirts", 1990)
    second = canonical_key("M12", None, "Navy", "Polo Shirts", 1990)
    assert first["data"]["canonical_key"] == second["data"]["canonical_key"]


def test_canonical_key_requires_an_identifier() -> None:
    assert canonical_key(None, None, "Navy", "Polo Shirts")["status"] == "REJECT"


def test_canonical_key_separator_avoids_collisions() -> None:
    a = canonical_key("M12", "X", "Navy", "Polo Shirts")
    b = canonical_key("M12X", None, "Navy", "Polo Shirts")
    assert a["data"]["canonical_key"] != b["data"]["canonical_key"]


def test_temporal_scope_excludes_the_1940s_from_brand_products() -> None:
    result = temporal_scope(1945)
    assert result["data"]["scope"] == SCOPE_1940S
    assert result["data"]["counts_as_brand_product"] is False


def test_temporal_scope_includes_products_from_1952() -> None:
    result = temporal_scope(1952)
    assert result["data"]["scope"] == SCOPE_BRAND
    assert result["data"]["counts_as_brand_product"] is True


def test_temporal_scope_holds_when_era_is_unknown() -> None:
    assert temporal_scope(None)["status"] == "HOLD"


def test_identity_completeness_flags_unknown_fields() -> None:
    result = identity_completeness({"model": "M12", "colour": "UNKNOWN"}, ["model", "colour"])
    assert result["status"] == "HOLD"
    assert result["meta"]["missing"] == ["colour"]


def test_not_applicable_requires_a_category_rule_and_justification() -> None:
    assert not_applicable_is_valid(CATEGORY_NOT_APPLICABLE, False, "x")["status"] == "REJECT"
    assert not_applicable_is_valid(CATEGORY_NOT_APPLICABLE, True, None)["status"] == "REJECT"
    assert (
        not_applicable_is_valid(CATEGORY_NOT_APPLICABLE, True, "categoria sense talla")["status"]
        == "SUCCESS"
    )


def test_same_identity_compares_keys() -> None:
    assert same_identity({"canonical_key": "abc"}, {"canonical_key": "abc"})["data"]["same_identity"] is True
    assert same_identity({"canonical_key": "abc"}, {})["status"] == "HOLD"


def test_nine_hold_sources_are_registered() -> None:
    assert len(HOLD_SOURCES) == 9


def test_every_hold_declares_its_resolution() -> None:
    for key, source in HOLD_SOURCES.items():
        assert source["resolution"], f"HOLD sense resolucio: {key}"
        assert source["resolvable_by"] in {RESOLVABLE_SYSTEM, RESOLVABLE_HUMAN, RESOLVABLE_NEVER}
        assert source["reference"]


def test_hold_carries_its_resolution_block() -> None:
    result = hold("public_purchase", ["checkout_verified"])
    assert result["status"] == "HOLD"
    resolution = result["meta"]["resolution"]
    assert resolution["resolvable_by"] == RESOLVABLE_SYSTEM
    assert resolution["missing"] == ["checkout_verified"]


def test_unknown_hold_key_is_rejected() -> None:
    assert build_resolution("nonexistent")["status"] == "REJECT"


def test_brand_unlisted_hold_is_a_human_decision() -> None:
    assert build_resolution("brand_unlisted")["data"]["resolvable_by"] == RESOLVABLE_HUMAN


def test_blocked_domain_is_never_resolved() -> None:
    assert assert_never_resolvable("domain_blocked") is True
    assert assert_never_resolvable("public_purchase") is False


def test_holds_are_classified_by_resolution_path() -> None:
    holds = [
        hold("public_purchase", ["checkout"]),
        hold("brand_unlisted", ["brand"]),
        hold("domain_blocked", ["access"]),
    ]
    result = classify_holds(holds)
    assert result["data"]["by_system"] == ["public_purchase"]
    assert result["data"]["by_human"] == ["brand_unlisted"]
    assert result["data"]["never"] == ["domain_blocked"]


def test_hold_rate_kpi_threshold() -> None:
    assert hold_rate_kpi(30, 100)["data"]["within_threshold"] is True
    assert hold_rate_kpi(50, 100)["data"]["within_threshold"] is False


def test_hold_rate_kpi_holds_on_zero_denominator() -> None:
    assert hold_rate_kpi(0, 0)["status"] == "HOLD"


if __name__ == "__main__":
    tests = [v for n, v in sorted(globals().items()) if n.startswith("test_")]
    for test in tests:
        test()
    print(f"OK: {len(tests)} proves passades")
