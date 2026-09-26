"""Integritat i manifests d'artefactes del sistema RLF.

Implementa §4.4.1 (TRUST) i §4.4.2 (INTEGRITY) del document mestre canònic.

Cinc components per artefacte: identitat, versió, hash, relació amb manifest,
estat.

Cinc tipus de problema detectats: modificació, versió incorrecta, artefacte
obsolet, fitxer absent, inconsistència.
"""

from pathlib import Path
from typing import Any, Iterable, Sequence

from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.hashing.idempotency import sha256_file_hex
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

STATE_CURRENT: str = "current"
STATE_OBSOLETE: str = "obsolete"
STATE_MISSING: str = "missing"

PROBLEM_MODIFIED: str = "modified"
PROBLEM_WRONG_VERSION: str = "wrong_version"
PROBLEM_OBSOLETE: str = "obsolete"
PROBLEM_ABSENT: str = "absent"
PROBLEM_INCONSISTENT: str = "inconsistent"

GENERATED_NOTE: str = "Fitxer generat. No editar a mà."

logger = get_logger(__name__)


def build_manifest(
    root: str,
    relative_paths: Sequence[str],
    include_header: bool = True,
) -> dict[str, Any]:
    """Construeix un manifest SHA-256 d'un conjunt de fitxers.

    Args:
        root: Directori arrel.
        relative_paths: Rutes relatives a incloure.
        include_header: Si cal afegir la nota de fitxer generat.

    Returns:
        Un resultat canònic SUCCESS amb el text del manifest i les entrades.
        HOLD si algun fitxer falta. FAILURE si apareix una excepció.
    """
    try:
        base = Path(root)
        entries: list[dict[str, str]] = []
        absent: list[str] = []

        for relative in sorted(relative_paths):
            target = base / relative
            if not target.is_file():
                absent.append(relative)
                continue
            entries.append({"hash": sha256_file_hex(str(target)), "path": relative})

        if absent:
            return make_hold("Fitxers del manifest absents al disc", meta={"absent": absent})

        lines: list[str] = []
        if include_header:
            lines.append(f"# {GENERATED_NOTE}")
            lines.append("")
        for entry in entries:
            lines.append(f"{entry['hash']}  {entry['path']}")

        return make_success(
            {"text": "\n".join(lines) + "\n", "entries": entries},
            meta={"count": len(entries)},
        )
    except Exception as exception:  # noqa: BLE001 - contracte FAILURE és explícit
        logger.critical("manifest_unexpected", root=root, error=str(exception))
        return make_failure(
            f"Excepció inesperada: {exception}",
            meta={"exception_type": type(exception).__name__},
        )


def verify_file(path: str, expected_sha256: str) -> dict[str, Any]:
    """Verifica un fitxer contra el seu hash esperat (§4.4.2).

    Args:
        path: Ruta del fitxer.
        expected_sha256: Hash esperat, en hexadecimal.

    Returns:
        Un resultat canònic SUCCESS si coincideix. HOLD si el fitxer no
        existeix (absent). REJECT si el hash no coincideix (modificació).
    """
    target = Path(path)
    if not target.is_file():
        logger.warning("integrity_absent", path=path)
        return make_hold("Fitxer absent", meta={"problem": PROBLEM_ABSENT, "path": path})

    actual = sha256_file_hex(path)
    if actual != expected_sha256:
        logger.error("integrity_modified", path=path)
        return make_reject(
            "El hash no coincideix: el fitxer s'ha modificat",
            meta={
                "problem": PROBLEM_MODIFIED,
                "path": path,
                "expected": expected_sha256,
                "actual": actual,
            },
        )

    return make_success({"path": path, "sha256": actual})


def verify_role_sizes(
    master_path: str,
    web_path: str,
) -> dict[str, Any]:
    """Comprova que el fitxer de rol web no pesa més que el de rol master.

    Escenari d'ús: al lliurament d'actius, el fitxer de rol `web` serveix la
    botiga pública (§1.6, §6.8.3). Un actiu de web que pesa més que el seu
    màster no compleix la seva funció.

    Args:
        master_path: Ruta del fitxer de rol master.
        web_path: Ruta del fitxer de rol web.

    Returns:
        Un resultat canònic SUCCESS amb els pesos. HOLD si falta algun fitxer.
        REJECT si el web pesa més que el màster.
    """
    master = Path(master_path)
    web = Path(web_path)

    if not master.is_file() or not web.is_file():
        missing = [str(p) for p in (master, web) if not p.is_file()]
        return make_hold("Fitxers de comparació absents", meta={"absent": missing})

    master_bytes = master.stat().st_size
    web_bytes = web.stat().st_size

    if web_bytes > master_bytes:
        return make_reject(
            "El fitxer de rol web pesa més que el de rol màster",
            meta={
                "problem": PROBLEM_INCONSISTENT,
                "master_bytes": master_bytes,
                "web_bytes": web_bytes,
                "excess_bytes": web_bytes - master_bytes,
            },
        )

    return make_success({"master_bytes": master_bytes, "web_bytes": web_bytes})


def summarise(paths: Iterable[str]) -> dict[str, Any]:
    """Resumeix un conjunt de fitxers amb mida i hash.

    Args:
        paths: Rutes a resumir.

    Returns:
        Un resultat canònic SUCCESS amb una entrada per fitxer existent i la
        llista dels absents.
    """
    present: list[dict[str, Any]] = []
    absent: list[str] = []

    for path in paths:
        target = Path(path)
        if not target.is_file():
            absent.append(path)
            continue
        present.append(
            {"path": path, "bytes": target.stat().st_size, "sha256": sha256_file_hex(path)}
        )

    meta: dict[str, Any] = {"count": len(present)}
    if absent:
        meta["absent"] = absent
    return make_success({"present": present}, meta=meta)


def release_manifest_object(
    entries: Sequence[dict[str, Any]],
    version: str,
    author: str,
) -> dict[str, Any]:
    """Construeix l'objecte de manifest d'una release (§4.4.8).

    Args:
        entries: Entrades del manifest, amb path i hash.
        version: Versió de la release.
        author: Autor o responsable de la publicació.

    Returns:
        Un resultat canònic SUCCESS amb l'objecte de manifest. REJECT si falta
        la versió o l'autor, o si no hi ha cap entrada.
    """
    if not version:
        return make_reject("Una release requereix versió")
    if not author:
        return make_reject("Una release requereix autor")
    if not entries:
        return make_reject("Una release requereix un manifest amb entrades")

    return make_success(
        {
            "version": version,
            "author": author,
            "artefacts": list(entries),
            "count": len(entries),
            "note": GENERATED_NOTE,
        }
    )
