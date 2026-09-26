"""RLF SUPPLIER ENGINE — nucli del motor de proveidors.

Objectiu: registrar, verificar, validar i classificar proveidors de segona ma
que venguin Fred Perry o marques britaniques relacionades, de 1952 a 2026-09-16.

R14: aquest motor NO inventa dades. Sense evidencia, l'entrada queda REBUTJADA.
El motor es deterministic: la mateixa entrada dona sempre el mateix resultat.
"""
from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from enum import Enum
from typing import Any, Iterable

DATA_LIMIT_INFERIOR = 1952
DATA_LIMIT_SUPERIOR = date(2026, 9, 16)
OBJECTIU_PROVEIDORS = 10000
MOTOR_VERSIO = "supplier-engine/1.0"


class EstatVerificacio(str, Enum):
    PENDENT = "PENDENT"
    VERIFICAT = "VERIFICAT"
    REBUTJAT = "REBUTJAT"
    HOLD = "HOLD"


class Classificacio(str, Enum):
    ESPECIALISTA_FRED_PERRY = "ESPECIALISTA_FRED_PERRY"
    MARQUES_BRITANIQUES = "MARQUES_BRITANIQUES"
    VINTAGE_GENERALISTA = "VINTAGE_GENERALISTA"
    SEGONA_MA_FOCALITZADA = "SEGONA_MA_FOCALITZADA"
    DESCARTAT = "DESCARTAT"


class MotiuRebuig(str, Enum):
    SENSE_FONT = "SENSE_FONT"
    SENSE_URL = "SENSE_URL"
    FORA_TEMPORAL = "FORA_TEMPORAL"
    NO_ES_BOTIGA_PRELOVED = "NO_ES_BOTIGA_PRELOVED"
    DUPLICAT = "DUPLICAT"
    DADES_INCOMPLETES = "DADES_INCOMPLETES"


def _normalitza(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("_normalitza espera un str")
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(t.lower().split())


def clau_canonica(nom: str, localitat: str, pais: str) -> str:
    base = f"{_normalitza(nom)}|{_normalitza(localitat)}|{_normalitza(pais)}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def empremta(obj: Any) -> str:
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EntradaProveidor:
    nom: str
    localitat: str
    sector: str
    pais: str
    url: str
    font: str
    data_consulta: str

    def clau(self) -> str:
        return clau_canonica(self.nom, self.localitat, self.pais)

    def camps_buits(self) -> list[str]:
        return [c for c, v in asdict(self).items() if not isinstance(v, str) or not v.strip()]


@dataclass
class Evidencia:
    tipus: str
    url: str
    data_consulta: str
    extracte: str

    def valida(self) -> bool:
        return bool(self.extracte.strip() and len(self.extracte.strip()) >= 20 and self.url.startswith(("http://", "https://")))


@dataclass
class Proveidor:
    clau: str
    nom: str
    localitat: str
    sector: str
    pais: str
    url: str
    font: str
    data_consulta: str
    estat: EstatVerificacio
    classificacio: Classificacio
    evidencies: list[Evidencia] = field(default_factory=list)
    motius: list[str] = field(default_factory=list)
    marques_detectades: list[str] = field(default_factory=list)
    anys_detectats: list[int] = field(default_factory=list)
    empremta_entrada: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["estat"] = self.estat.value
        d["classificacio"] = self.classificacio.value
        return d


MARQUES_BRITANIQUES = ("fred perry", "ben sherman", "lonsdale", "baracuta", "gabba", "pretty green", "luke 1977", "aquascutum", "burberry")
TERMES_PRELOVED = ("preloved", "pre-loved", "second hand", "secondhand", "segona ma", "vintage", "thrift", "consignment", "recommerce")
SENYALS_CLASSIFICACIO = {
    Classificacio.ESPECIALISTA_FRED_PERRY: ("fred perry specialist", "fred perry only", "solo fred perry"),
    Classificacio.MARQUES_BRITANIQUES: ("british brands", "marcas britanicas", "heritage british"),
}


def te_evidencia_suficient(evidencies: Iterable[Evidencia]) -> bool:
    return any(e.valida() for e in evidencies)


def any_de_la_linia(any_observat: int) -> bool:
    return DATA_LIMIT_INFERIOR <= any_observat <= DATA_LIMIT_SUPERIOR.year


def es_preloved(text: str) -> bool:
    t = _normalitza(text)
    return any(terme in t for terme in TERMES_PRELOVED)


def marques_en_text(text: str) -> list[str]:
    t = _normalitza(text)
    return [m for m in MARQUES_BRITANIQUES if m in t]


def anys_en_text(text: str) -> list[int]:
    trobats = []
    for paraula in text.replace("-", " ").split():
        net = "".join(c for c in paraula if c.isdigit())
        if len(net) == 4 and net.isdigit():
            any_ = int(net)
            if 1900 <= any_ <= 2030:
                trobats.append(any_)
    return sorted(set(trobats))


def classifica(marques: list[str], text: str, evidencies: list[Evidencia]) -> Classificacio:
    t = _normalitza(text)
    for cat, senyals in SENYALS_CLASSIFICACIO.items():
        if any(s in t for s in senyals):
            return cat
    if "fred perry" in marques:
        return Classificacio.ESPECIALISTA_FRED_PERRY
    if marques:
        return Classificacio.MARQUES_BRITANIQUES
    if es_preloved(text):
        return Classificacio.SEGONA_MA_FOCALITZADA
    return Classificacio.VINTAGE_GENERALISTA


class MotorProveidors:
    """Processa entrades reals i les converteix en proveidors registrats."""

    def __init__(self) -> None:
        self._per_clau: dict[str, Proveidor] = {}
        self._descartades: list[dict] = []

    def processa(self, entrada: EntradaProveidor, evidencies: list[Evidencia]) -> Proveidor:
        buits = entrada.camps_buits()
        if buits:
            return self._rebutja(entrada, MotiuRebuig.DADES_INCOMPLETES, f"camps buits: {', '.join(buits)}")
        if not entrada.url.startswith(("http://", "https://")):
            return self._rebutja(entrada, MotiuRebuig.SENSE_URL, "url no valida")
        if not te_evidencia_suficient(evidencies):
            return self._rebutja(entrada, MotiuRebuig.SENSE_FONT, "cap evidencia valida")
        clau = entrada.clau()
        if clau in self._per_clau:
            return self._rebutja(entrada, MotiuRebuig.DUPLICAT, f"clau ja registrada: {clau[:16]}")
        corpus = " ".join(e.extracte for e in evidencies)
        marques = marques_en_text(corpus)
        anys = anys_en_text(corpus)
        if anys and not any(any_de_la_linia(a) for a in anys):
            return self._rebutja(entrada, MotiuRebuig.FORA_TEMPORAL, f"anys detectats: {anys}")
        if not marques and not es_preloved(corpus):
            return self._rebutja(entrada, MotiuRebuig.NO_ES_BOTIGA_PRELOVED, "ni marques ni senyals preloved")
        prov = Proveidor(
            clau=clau, nom=entrada.nom, localitat=entrada.localitat, sector=entrada.sector,
            pais=entrada.pais, url=entrada.url, font=entrada.font, data_consulta=entrada.data_consulta,
            estat=EstatVerificacio.VERIFICAT, classificacio=classifica(marques, corpus, evidencies),
            evidencies=list(evidencies), marques_detectades=marques, anys_detectats=anys,
            empremta_entrada=empremta(asdict(entrada)),
        )
        self._per_clau[clau] = prov
        return prov

    def _rebutja(self, entrada: EntradaProveidor, motiu: MotiuRebuig, detall: str) -> Proveidor:
        clau = entrada.clau() if (entrada.nom and entrada.localitat and entrada.pais) else "sense-clau"
        prov = Proveidor(
            clau=clau, nom=entrada.nom, localitat=entrada.localitat, sector=entrada.sector,
            pais=entrada.pais, url=entrada.url, font=entrada.font, data_consulta=entrada.data_consulta,
            estat=EstatVerificacio.REBUTJAT, classificacio=Classificacio.DESCARTAT,
            motius=[f"{motiu.value}: {detall}"], empremta_entrada=empremta(asdict(entrada)),
        )
        self._descartades.append({"clau": clau, "motiu": motiu.value, "detall": detall})
        return prov

    @property
    def registrats(self) -> list[Proveidor]:
        return list(self._per_clau.values())

    @property
    def descartats(self) -> list[dict]:
        return list(self._descartades)

    def total(self) -> int:
        return len(self._per_clau)

    def per_classificacio(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for p in self._per_clau.values():
            out[p.classificacio.value] = out.get(p.classificacio.value, 0) + 1
        return out

    def per_pais(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for p in self._per_clau.values():
            out[p.pais] = out.get(p.pais, 0) + 1
        return out

    def progres_objectiu(self) -> dict:
        t = self.total()
        return {"registrats": t, "objectiu": OBJECTIU_PROVEIDORS, "percentatge": round(100.0 * t / OBJECTIU_PROVEIDORS, 4), "descartats": len(self._descartades)}

    def exporta(self) -> dict:
        return {
            "motor": MOTOR_VERSIO,
            "generat": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "progres": self.progres_objectiu(),
            "classificacio": self.per_classificacio(),
            "paisos": self.per_pais(),
            "proveidors": [p.to_dict() for p in self.registrats],
            "descartats": self.descartats,
            "empremta": empremta([p.to_dict() for p in self.registrats]),
        }
