"""Motor de comprovació d'elegibilitat de venedors (§3.3.8).

Implementa els vuit criteris acumulatius d'elegibilitat del document mestre
canònic.

Decisions canòniques:
- Dades absents -> HOLD.
- Marca *similar* no llistada -> HOLD (decisió humana, que pot ampliar la llista).
- Criteri explícitament incomplert -> REJECT.
- Contradicció -> REJECT.

Nota d'abast (OP-003, TANCAT): les marques afins només amplien **l'univers de
descoberta de proveïdors**. Mai entren al catàleg comercial, ni a la Knowledge
Base de productes venibles, ni al circuit de venda.
"""

from typing import Any, Optional, Sequence

from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

DECISION_ELEGIBLE: str = "ELEGIBLE"
DECISION_HOLD: str = "HOLD"
DECISION_REJECT: str = "REJECT"

EU27_COUNTRIES: frozenset[str] = frozenset(
    {
        "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
        "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
        "SI", "ES", "SE",
    }
)

EXCLUDED_COUNTRY: str = "GB"

GENERALIST_MARKETPLACES: frozenset[str] = frozenset(
    {
        "ebay", "wallapop", "vinted", "depop", "etsy", "amazon", "allegro",
        "marktplaats", "subito", "leboncoin", "kleinanzeigen", "todocoleccion",
    }
)

BRAND_FRED_PERRY: str = "fred perry"

ADJACENT_BRANDS: frozenset[str] = frozenset(
    {
        "stone island",
        "cp company",
        "c.p. company",
        "lyle & scott",
        "diadora",
        "sergio tacchini",
        "fila",
        "lonsdale",
        "ben sherman",
        "peaceful hooligan",
    }
)

logger = get_logger(__name__)


def check_country(country_code: str) -> dict[str, Any]:
    """Comprova el criteri 2: pertinença a la UE-27, Regne Unit exclòs.

    Args:
        country_code: Codi de país ISO de dues lletres.

    Returns:
        Un resultat canònic amb la decisió del criteri.
    """
    if not country_code or not country_code.strip():
        return make_hold("Codi de país absent: no es pot avaluar la pertinença UE-27")

    code = country_code.strip().upper()
    if code == EXCLUDED_COUNTRY:
        return make_reject("El Regne Unit queda fora del perímetre (decisió estratègica, §2.1.6)")
    if code not in EU27_COUNTRIES:
        return make_reject(f"El país {code} és fora de la UE-27", meta={"country": code})

    return make_success({"country": code, "criterion": "eu27"})


def check_not_generalist_marketplace(domains: Sequence[str]) -> dict[str, Any]:
    """Comprova el criteri 4: no ser un marketplace generalista.

    Args:
        domains: Dominis associats al venedor.

    Returns:
        Un resultat canònic amb la decisió.
    """
    if not domains:
        return make_hold("Sense dominis informats: no es pot avaluar el criteri 4")

    found = [
        domain
        for domain in domains
        if any(marketplace in domain.lower() for marketplace in GENERALIST_MARKETPLACES)
    ]
    if found:
        return make_reject(
            "Marketplace generalista: exclòs del registre canònic (§2.2.3, §3.3.8)",
            meta={"domains": found},
        )

    return make_success({"domains": list(domains), "criterion": "not_generalist_marketplace"})


def check_brand(stocked_brands: Sequence[str]) -> dict[str, Any]:
    """Comprova el criteri 5: marca Fred Perry o preloved seriós de marques afins.

    L'encaix en marques afins limita l'univers de descoberta de proveïdors; no
    amplia en cap cas el catàleg comercial (§3.3.8, OP-003 TANCAT).

    Args:
        stocked_brands: Marques que el venedor estoca.

    Returns:
        Un resultat canònic amb la decisió.
    """
    if not stocked_brands:
        return make_hold("Sense marques informades: no es pot avaluar el criteri 5")

    surfaced = [brand.strip().lower() for brand in stocked_brands if brand and brand.strip()]
    if not surfaced:
        return make_hold("Marques informades però buides: criteri 5 no avaluable")

    has_fred_perry = any(BRAND_FRED_PERRY in brand for brand in surfaced)
    adjacent_hits = [
        brand
        for brand in surfaced
        if any(adjacent == brand or adjacent in brand for adjacent in ADJACENT_BRANDS)
    ]

    if has_fred_perry:
        return make_success(
            {
                "criterion": "brand",
                "fred_perry_stocked": True,
                "adjacent_brands": adjacent_hits,
                "catalogue_scope_unchanged": True,
            }
        )

    if adjacent_hits:
        return make_success(
            {
                "criterion": "brand",
                "fred_perry_stocked": False,
                "adjacent_brands": adjacent_hits,
                "discovery_only": True,
                "catalogue_scope_unchanged": True,
                "note": "Marca afina admesa per a descobriment; el catàleg comercial no s'amplia.",
            }
        )

    return make_hold(
        "Marca no llistada: possible ampliació de la llista per decisió humana",
        meta={"brands": surfaced, "adjacent_brands": sorted(ADJACENT_BRANDS)},
    )


def check_public_purchase(reachable: Optional[bool], checkout_verified: Optional[bool]) -> dict[str, Any]:
    """Comprova el criteri 6 i la prova de compra pública (§3.3.12).

    La prova és una comprovació de navegació/cistella/checkout que **no obliga
    a comprar ni gastar diners**.

    Args:
        reachable: Si s'ha pogut arribar a la botiga pública.
        checkout_verified: Si s'ha verificat l'accés públic a la compra.

    Returns:
        Un resultat canònic amb la decisió.
    """
    if reachable is None or checkout_verified is None:
        return make_hold("Comprovació de compra pública no completada")
    if not reachable:
        return make_reject("La botiga pública no és accessible")
    if not checkout_verified:
        return make_hold("Accés públic a la compra no verificat: el venedor queda en HOLD")
    return make_success({"criterion": "public_purchase", "checkout_verified": True})


def check_monitoring_allowed(robots_verdict: Optional[str]) -> dict[str, Any]:
    """Comprova el criteri 8: el web no prohibeix el monitoratge de producte.

    Fail-closed per designació (§3.8.4): si `robots.txt` no es pot llegir
    (5xx, xarxa, 401/403), es tracta com a **no permès**.

    Args:
        robots_verdict: `allowed`, `disallowed` o `unreadable`.

    Returns:
        Un resultat canònic amb la decisió.
    """
    if not robots_verdict:
        return make_hold("Veredicte de robots.txt absent")
    verdict = robots_verdict.strip().lower()
    if verdict == "disallowed":
        return make_reject("El web prohibeix el monitoratge de pàgines de producte")
    if verdict == "unreadable":
        return make_hold(
            "robots.txt no llegible: es tracta com a no permès (fail-closed, §3.8.4)"
        )
    if verdict != "allowed":
        return make_hold(
            "Veredicte de robots.txt no reconegut", meta={"verdict": robots_verdict}
        )
    return make_success({"criterion": "monitoring_allowed", "verdict": verdict})


def _as_verdict(criterion: str, result: dict[str, Any]) -> dict[str, Any]:
    """Converteix el resultat d'una comprovació de criteri en un veredicte.

    Args:
        criterion: Nom del criteri.
        result: Resultat canònic d'una funció `check_*`.

    Returns:
        Un dict amb criteri, decisió i motiu opcional.
    """
    status = result.get("status")
    if status == "SUCCESS":
        return {"criterion": criterion, "decision": DECISION_ELEGIBLE}
    if status == "HOLD":
        return {"criterion": criterion, "decision": DECISION_HOLD, "reason": result.get("reason")}
    return {"criterion": criterion, "decision": DECISION_REJECT, "reason": result.get("reason")}


def evaluate_supplier(candidate: dict[str, Any]) -> dict[str, Any]:
    """Avalua l'elegibilitat d'un venedor contra els vuit criteris.

    Args:
        candidate: Diccionari amb els camps del venedor candidat:
            `is_professional`, `country`, `second_hand`, `domains`,
            `stocked_brands`, `reachable`, `checkout_verified`,
            `return_policy_published`, `shipping_cost_published`,
            `robots_verdict`.

    Returns:
        Un resultat canònic SUCCESS amb la decisió, els criteris avaluats i els
        motius de cada criteri no superat. FAILURE si apareix una excepció.
    """
    try:
        if not isinstance(candidate, dict) or not candidate:
            return make_reject("El candidat no és un diccionari amb contingut")

        verdicts: list[dict[str, Any]] = []

        is_professional = candidate.get("is_professional")
        if is_professional is None:
            verdicts.append(
                {"criterion": "professional", "decision": DECISION_HOLD, "reason": "Absent"}
            )
        elif not is_professional:
            verdicts.append(
                {
                    "criterion": "professional",
                    "decision": DECISION_REJECT,
                    "reason": "No és un negoci professional identificable",
                }
            )
        else:
            verdicts.append({"criterion": "professional", "decision": DECISION_ELEGIBLE})

        verdicts.append(_as_verdict("eu27", check_country(candidate.get("country", ""))))

        second_hand = candidate.get("second_hand")
        if second_hand is None:
            verdicts.append(
                {"criterion": "second_hand", "decision": DECISION_HOLD, "reason": "Absent"}
            )
        elif not second_hand:
            verdicts.append(
                {
                    "criterion": "second_hand",
                    "decision": DECISION_REJECT,
                    "reason": "La segona mà no és activitat del venedor",
                }
            )
        else:
            verdicts.append({"criterion": "second_hand", "decision": DECISION_ELEGIBLE})

        verdicts.append(
            _as_verdict(
                "not_generalist_marketplace",
                check_not_generalist_marketplace(candidate.get("domains", [])),
            )
        )
        verdicts.append(_as_verdict("brand", check_brand(candidate.get("stocked_brands", []))))
        verdicts.append(
            _as_verdict(
                "public_purchase",
                check_public_purchase(candidate.get("reachable"), candidate.get("checkout_verified")),
            )
        )

        has_return_policy = candidate.get("return_policy_published")
        has_shipping_cost = candidate.get("shipping_cost_published")
        if has_return_policy is None or has_shipping_cost is None:
            verdicts.append(
                {
                    "criterion": "published_conditions",
                    "decision": DECISION_HOLD,
                    "reason": "Condicions publicades no informades",
                }
            )
        elif has_return_policy and has_shipping_cost:
            verdicts.append({"criterion": "published_conditions", "decision": DECISION_ELEGIBLE})
        else:
            verdicts.append(
                {
                    "criterion": "published_conditions",
                    "decision": DECISION_HOLD,
                    "reason": "Falten condicions publicades de devolució o d'enviament",
                }
            )

        verdicts.append(
            _as_verdict(
                "monitoring_allowed",
                check_monitoring_allowed(candidate.get("robots_verdict")),
            )
        )

        rejects = [v for v in verdicts if v["decision"] == DECISION_REJECT]
        holds = [v for v in verdicts if v["decision"] == DECISION_HOLD]

        if rejects:
            final = DECISION_REJECT
        elif holds:
            final = DECISION_HOLD
        else:
            final = DECISION_ELEGIBLE

        logger.info(
            "supplier_evaluated",
            decision=final,
            criteria=len(verdicts),
            holds=len(holds),
            rejects=len(rejects),
        )
        return make_success(
            {
                "decision": final,
                "criterion_verdicts": verdicts,
                "rejected_criteria": [v["criterion"] for v in rejects],
                "held_criteria": [v["criterion"] for v in holds],
                "catalogue_scope_unchanged": True,
            },
            meta={"evaluated_criteria": len(verdicts)},
        )
    except Exception as exception:  # noqa: BLE001 - contracte FAILURE és explícit
        logger.critical("supplier_evaluation_unexpected", error=str(exception))
        return make_failure(
            f"Excepció inesperada: {exception}",
            meta={"exception_type": type(exception).__name__},
        )


def validated_record_complete(record: dict[str, Any]) -> dict[str, Any]:
    """Comprova si un venedor compleix la definició de VALIDAT (§3.3.12).

    Un venedor compta per al mínim preinauguració només quan té a la base SQL
    tots els quinze elements de §3.3.12.

    Args:
        record: Registre del venedor a la base.

    Returns:
        Un resultat canònic SUCCESS amb `counts_towards_gate` i la llista de
        camps que falten. HOLD si en falta cap. REJECT si el registre no és un
        diccionari.
    """
    if not isinstance(record, dict):
        return make_reject("El registre no és un diccionari")

    required: tuple[str, ...] = (
        "canonical_identity_unique",
        "own_domain",
        "country_and_city",
        "eu27_membership",
        "professional_second_hand",
        "brand_criterion_complete",
        "public_purchase_verifiable",
        "conditions_documented",
        "monitoring_compatible",
        "primary_source",
        "verification_date",
        "evidence_snapshot_hash",
        "decision_elegible",
        "deduplication_pass",
        "persistent_audit",
    )

    missing = [field for field in required if not record.get(field)]
    if missing:
        return make_hold(
            "El registre no compleix la definició de VALIDAT",
            meta={"missing": missing, "counts_towards_gate": False},
        )

    return make_success({"counts_towards_gate": True, "verified_fields": len(required)})
