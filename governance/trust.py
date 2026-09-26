"""Contracte de governanca RLF-TRUST/1.0 - quin estat es de confianca.

Implementa §4.4.1 del document mestre canonic v2.6.0.

La pregunta fonamental del contracte es *quin estat es de confianca?* i la
resposta canonica es que ho es l'estat que pot ser verificat contra els
artefactes canonics. Sense artefactes verificables no hi ha confianca: hi ha
HOLD, perque el sistema es fail-closed.

Els set tipus d'artefacte canonic son manifests, versions, checkpoints, hashes,
estat, migracions i releases. Les transicions TRUST_EPOCH son canvis formals
de context i es produeixen per sis causes: migracio de versio, canvi d'entorn,
canvi d'operador, publicacio de release, resolucio d'inconsistencia i auditoria.
"""

from typing import Any, Optional

from shared.rlf_core.contract.return_contract import (
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

CONTRACT_NAME: str = "RLF-TRUST/1.0"

ARTEFACT_MANIFESTS: str = "manifests"
ARTEFACT_VERSIONS: str = "versions"
ARTEFACT_CHECKPOINTS: str = "checkpoints"
ARTEFACT_HASHES: str = "hashes"
ARTEFACT_STATE: str = "state"
ARTEFACT_MIGRATIONS: str = "migrations"
ARTEFACT_RELEASES: str = "releases"

CANONICAL_ARTEFACT_TYPES: tuple[str, ...] = (
    ARTEFACT_MANIFESTS,
    ARTEFACT_VERSIONS,
    ARTEFACT_CHECKPOINTS,
    ARTEFACT_HASHES,
    ARTEFACT_STATE,
    ARTEFACT_MIGRATIONS,
    ARTEFACT_RELEASES,
)

EPOCH_VERSION_MIGRATION: str = "version_migration"
EPOCH_ENVIRONMENT_CHANGE: str = "environment_change"
EPOCH_OPERATOR_CHANGE: str = "operator_change"
EPOCH_RELEASE_PUBLICATION: str = "release_publication"
EPOCH_INCONSISTENCY_RESOLUTION: str = "inconsistency_resolution"
EPOCH_AUDIT: str = "audit"

EPOCH_CAUSES: tuple[str, ...] = (
    EPOCH_VERSION_MIGRATION,
    EPOCH_ENVIRONMENT_CHANGE,
    EPOCH_OPERATOR_CHANGE,
    EPOCH_RELEASE_PUBLICATION,
    EPOCH_INCONSISTENCY_RESOLUTION,
    EPOCH_AUDIT,
)

TRUST_TRUSTED: str = "trusted"
TRUST_UNVERIFIED: str = "unverified"
TRUST_BROKEN: str = "broken"

logger = get_logger(__name__)


def is_trusted_state(artefacts_present: dict[str, bool]) -> dict[str, Any]:
    """Determina si un estat es de confianca segons els artefactes presents.

    Un estat nomes es de confianca si pot ser verificat contra els artefactes
    canonics. Sense cap artefacte, no hi ha confianca fiable i la decisio es
    HOLD. Un tipus d'artefacte que no sigui canonic es REJECT.

    Args:
        artefacts_present: Presencia de cada tipus d'artefacte canonic, amb el
            nom del tipus com a clau i un boolea com a valor.

    Returns:
        Un resultat canonic SUCCESS amb el veredicte, el nombre d'artefactes
        presents i els que falten. HOLD si no hi ha cap artefacte verificable.
        REJECT si apareix un tipus d'artefacte que no es canonic.
    """
    if not isinstance(artefacts_present, dict) or not artefacts_present:
        return make_hold(
            "Cap artefacte canonic present: l'estat no es verificable",
            meta={"required_types": CANONICAL_ARTEFACT_TYPES},
        )

    unknown = [n for n in artefacts_present if n not in CANONICAL_ARTEFACT_TYPES]
    if unknown:
        return make_reject(
            "Tipus d'artefacte no canonic", meta={"unknown_types": sorted(unknown)}
        )

    missing = [n for n in CANONICAL_ARTEFACT_TYPES if not artefacts_present.get(n)]
    present_count = len(CANONICAL_ARTEFACT_TYPES) - len(missing)

    if present_count == 0:
        return make_hold(
            "Cap dels set tipus d'artefacte es present", meta={"missing": missing}
        )

    verdict = TRUST_TRUSTED if not missing else TRUST_UNVERIFIED
    return make_success(
        {
            "trust": verdict,
            "artefacts_present": present_count,
            "missing": missing,
            "total_types": len(CANONICAL_ARTEFACT_TYPES),
        },
        meta={"contract": CONTRACT_NAME, "source": "S4.4.1"},
    )


def declare_trust_epoch(cause: str, detail: Optional[str] = None) -> dict[str, Any]:
    """Declara una transicio TRUST_EPOCH, segons §4.4.1.

    Una transicio d'epoca es un canvi formal de context del sistema i nomes es
    pot declarar per una de les sis causes canoniques.

    Args:
        cause: Causa formal de la transicio, una de les sis canoniques.
        detail: Detall addicional per a la traçabilitat.

    Returns:
        Un resultat canonic SUCCESS amb la transicio declarada. REJECT si la
        causa no es cap de les sis canoniques.
    """
    if cause not in EPOCH_CAUSES:
        return make_reject(
            "Causa de TRUST_EPOCH no canonica",
            meta={"cause": cause, "allowed": EPOCH_CAUSES},
        )

    logger.info("trust_epoch_declared", cause=cause)
    payload: dict[str, Any] = {"cause": cause, "contract": CONTRACT_NAME}
    if detail:
        payload["detail"] = detail
    return make_success(payload, meta={"source": "S4.4.1"})


def verify_state_against_artefacts(
    state: dict[str, Any],
    artefacts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Verifica un estat declarat contra els seus artefactes canonics.

    Un artefacte sense estructura verificable es una contradiccio i per tant
    REJECT. Un artefacte sense hash no es comprovable i per tant porta a HOLD.

    Args:
        state: Estat declarat pel sistema.
        artefacts: Artefactes amb identitat, versio i hash.

    Returns:
        Un resultat canonic SUCCESS amb el veredicte de confianca i el nombre
        d'artefactes verificats. HOLD si falta informacio per verificar.
        REJECT si hi ha un artefacte amb estructura no verificable.
    """
    if not isinstance(state, dict) or not isinstance(artefacts, dict):
        return make_reject("L'estat i els artefactes han de ser diccionaris")

    if not artefacts:
        return make_hold("Sense artefactes no hi ha verificacio possible")

    inconsistencies: list[str] = []
    unverified: list[str] = []

    for name, artefact in artefacts.items():
        if not isinstance(artefact, dict):
            inconsistencies.append(name)
            continue
        if not artefact.get("hash"):
            unverified.append(name)

    if inconsistencies:
        return make_reject(
            "Artefacte sense estructura verificable",
            meta={"artefacts": sorted(inconsistencies)},
        )

    if unverified:
        return make_hold(
            "Artefactes sense hash: no verificables",
            meta={"unverified": sorted(unverified)},
        )

    return make_success(
        {"trust": TRUST_TRUSTED, "verified_artefacts": len(artefacts)},
        meta={"contract": CONTRACT_NAME},
    )


def trust_epoch_history(causes: list[str]) -> dict[str, Any]:
    """Resumeix l'historial de transicions d'epoca.

    Args:
        causes: Causes declarades, en ordre cronologic.

    Returns:
        Un resultat canonic SUCCESS amb el recompte per causa i el total.
        REJECT si alguna causa de l'historial no es canonica.
    """
    unknown = [c for c in causes if c not in EPOCH_CAUSES]
    if unknown:
        return make_reject(
            "Causa de TRUST_EPOCH no canonica a l'historial",
            meta={"unknown": sorted(set(unknown))},
        )

    counts: dict[str, int] = {c: 0 for c in EPOCH_CAUSES}
    for cause in causes:
        counts[cause] += 1

    return make_success(
        {"counts": counts, "total": len(causes)}, meta={"contract": CONTRACT_NAME}
    )
