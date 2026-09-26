"""RLF SUPPLIER ENGINE — primera passada de descobriment.

Converteix resultats de cerca web REALS en candidates de proveidor. No inventa
res: sense URL i extracte literal, no en surt cap entrada.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict

from supplier_engine import EntradaProveidor, Evidencia, _normalitza


@dataclass(frozen=True)
class ResultatCerca:
    url: str
    titol: str
    extracte: str
    consulta: str
    data_consulta: str


@dataclass
class Candidat:
    nom: str
    localitat: str
    sector: str
    pais: str
    url: str
    font: str
    data_consulta: str
    extracte: str


EXCLOSOS = (
    "wikipedia.org", "facebook.com", "instagram.com", "twitter.com", "x.com",
    "youtube.com", "pinterest.", "linkedin.com", "amazon.", "ebay.",
    "tiktok.com", "reddit.com", "google.com",
)

SENYALS_BOTIGA = (
    "shop", "store", "boutique", "tienda", "botiga", "vintage", "preloved",
    "pre-loved", "second hand", "secondhand", "thrift", "consignment",
    "fred perry", "ben sherman", "baracuta", "lonsdale",
)


def _domini(url: str) -> str:
    m = re.match(r"https?://([^/]+)", url)
    return m.group(1).lower() if m else ""


def _nom_del_domini(url: str) -> str:
    d = _domini(url).replace("www.", "")
    base = d.split(".")[0] if d else ""
    return base.replace("-", " ").replace("_", " ").strip() or d


def _sembla_botiga(r: ResultatCerca) -> bool:
    blob = _normalitza(r.titol + " " + r.extracte + " " + r.url)
    if not r.url.startswith(("http://", "https://")):
        return False
    if any(e in _domini(r.url) for e in EXCLOSOS):
        return False
    return any(s in blob for s in SENYALS_BOTIGA)


def candidats_de_resultats(resultats: list[ResultatCerca], localitat: str, pais: str, sector: str = "") -> list[Candidat]:
    out: list[Candidat] = []
    for r in resultats:
        if not _sembla_botiga(r):
            continue
        if len(r.extracte.strip()) < 40:
            continue
        nom = r.titol.strip()[:120] or _nom_del_domini(r.url)
        out.append(
            Candidat(
                nom=nom, localitat=localitat, sector=sector, pais=pais, url=r.url,
                font=f"cerca-web:{r.consulta}", data_consulta=r.data_consulta,
                extracte=r.extracte.strip()[:2000],
            )
        )
    return out


def candidats_a_entrades(cands: list[Candidat]) -> tuple[list[EntradaProveidor], dict[str, list[Evidencia]]]:
    entrades: list[EntradaProveidor] = []
    evidencies: dict[str, list[Evidencia]] = {}
    for c in cands:
        e = EntradaProveidor(
            nom=c.nom, localitat=c.localitat, sector=c.sector, pais=c.pais,
            url=c.url, font=c.font, data_consulta=c.data_consulta,
        )
        k = f"{c.nom}|{c.localitat}|{c.pais}"
        evidencies.setdefault(k, []).append(
            Evidencia(tipus="resultat-cerca", url=c.url, data_consulta=c.data_consulta, extracte=c.extracte)
        )
        entrades.append(e)
    return entrades, evidencies


def desa_candidats(path: str, cands: list[Candidat]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"candidats": [asdict(c) for c in cands]}, fh, ensure_ascii=False, indent=2)
