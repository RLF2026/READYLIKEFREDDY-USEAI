"""RLF SUPPLIER ENGINE — capa de font.

El motor processa entrades; aquesta capa les OBTE. Cap adaptador no pot
fabricar una entrada: si la font no dona nom, URL, evidencia i data, falla.
"""
from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path

from supplier_engine import EntradaProveidor, Evidencia

CAMPS_OBLIGATORIS_CSV = ("nom", "localitat", "sector", "pais", "url", "font", "data_consulta")


class FontInvalida(Exception):
    """La font no te el format esperat o li falten camps obligatoris."""


@dataclass
class ResultatLectura:
    entrades: list[EntradaProveidor]
    evidencies: dict[str, list[Evidencia]]
    files_llegides: int
    files_descartades: int
    errors: list[str]


def _clau(nom: str, localitat: str, pais: str) -> str:
    return f"{nom.strip()}|{localitat.strip()}|{pais.strip()}"


def _valida_capcaleres(camps: list[str], origen: str) -> None:
    falten = [c for c in CAMPS_OBLIGATORIS_CSV if c not in camps]
    if falten:
        raise FontInvalida(f"{origen}: falten columnes obligatories: {', '.join(falten)}")


def llegeix_csv(contingut: str, origen: str = "csv") -> ResultatLectura:
    lector = csv.DictReader(io.StringIO(contingut))
    if not lector.fieldnames:
        raise FontInvalida(f"{origen}: CSV buit o sense capcalera")
    _valida_capcaleres(lector.fieldnames, origen)
    entrades: list[EntradaProveidor] = []
    evidencies: dict[str, list[Evidencia]] = {}
    errors: list[str] = []
    descartades = 0
    for n, fila in enumerate(lector, start=2):
        try:
            e = EntradaProveidor(
                nom=fila["nom"].strip(), localitat=fila["localitat"].strip(),
                sector=fila["sector"].strip(), pais=fila["pais"].strip(),
                url=fila["url"].strip(), font=fila["font"].strip(),
                data_consulta=fila["data_consulta"].strip(),
            )
        except (KeyError, AttributeError) as exc:
            errors.append(f"{origen}: fila {n}: {exc}")
            descartades += 1
            continue
        ev_url = (fila.get("evidencia_url") or "").strip()
        ev_ext = (fila.get("evidencia_extracte") or "").strip()
        k = _clau(e.nom, e.localitat, e.pais)
        if ev_url and ev_ext:
            evidencies.setdefault(k, []).append(
                Evidencia(tipus=fila.get("evidencia_tipus", "font"), url=ev_url, data_consulta=e.data_consulta, extracte=ev_ext)
            )
        entrades.append(e)
    return ResultatLectura(entrades, evidencies, len(entrades), descartades, errors)


def llegeix_json(contingut: str, origen: str = "json") -> ResultatLectura:
    try:
        dades = json.loads(contingut)
    except json.JSONDecodeError as exc:
        raise FontInvalida(f"{origen}: JSON invalid: {exc}") from exc
    if "proveidors" not in dades:
        raise FontInvalida(f"{origen}: falta la clau 'proveidors'")
    entrades: list[EntradaProveidor] = []
    evidencies: dict[str, list[Evidencia]] = {}
    errors: list[str] = []
    descartades = 0
    for n, item in enumerate(dades["proveidors"], start=1):
        try:
            e = EntradaProveidor(
                nom=item["nom"], localitat=item["localitat"], sector=item.get("sector", ""),
                pais=item["pais"], url=item["url"], font=item["font"], data_consulta=item["data_consulta"],
            )
        except (KeyError, TypeError) as exc:
            errors.append(f"{origen}: registre {n}: {exc}")
            descartades += 1
            continue
        entrades.append(e)
    for k, llista in (dades.get("evidencies") or {}).items():
        evidencies[k] = [
            Evidencia(tipus=x.get("tipus", "font"), url=x["url"], data_consulta=x["data_consulta"], extracte=x["extracte"])
            for x in llista
        ]
    return ResultatLectura(entrades, evidencies, len(entrades), descartades, errors)


def llegeix_fitxer(ruta: str) -> ResultatLectura:
    p = Path(ruta)
    if not p.exists():
        raise FontInvalida(f"no existeix: {ruta}")
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".csv":
        return llegeix_csv(text, str(p))
    if p.suffix.lower() == ".json":
        return llegeix_json(text, str(p))
    raise FontInvalida(f"extensio no suportada: {p.suffix}")
