"""Punt d'entrada del paquet `shared.rlf_core`.

RLF CORE és la infraestructura comuna compartida (§2.2.4). Aquest mòdul només
exposa les primitives i la seva versió de component; no conté lògica pròpia.
"""

VERSION: str = "1.0"

COMPONENT_NAME: str = "rlf_core"

COMPONENT_VERSIONS: dict[str, str] = {
    "rlf_core": "1.0",
    "lane_assigner": "1.1",
    "rlf_normalization": "1.0",
}

PRIMITIVES: tuple[str, ...] = (
    "identity",
    "normalization",
    "deduplication",
    "state",
    "cursors",
    "hashing",
    "manifests",
    "validation",
    "logging",
    "recovery",
    "configuration",
    "integrity",
)


def component_versions() -> dict[str, str]:
    """Retorna les versions dels components del CORE.

    Returns:
        Un diccionari component -> versió. Cap d'aquests valors és la versió
        del sistema; la versió del sistema viu a la capçalera del document
        mestre.
    """
    return dict(COMPONENT_VERSIONS)
