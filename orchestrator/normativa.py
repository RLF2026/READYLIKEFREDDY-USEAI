"""RLF ORCHESTRATOR — NORMATIVA DEL SISTEMA.

AQUEST MODUL ES LA LLEI EXECUTABLE DEL SISTEMA.

Prelacio de la norma:
  1. RLF Document Mestre Canonnic Unic. ES LA NORMA PRINCIPAL I MANA EN TOT.
  2. EXCEPCIONS: nomes les que l'operador dicta. Cap agent no se n'inventa cap.

--------------------------------------------------------------------------------
EXCEPCIONS DICTADES PER L'OPERADOR
--------------------------------------------------------------------------------
[AQUI NO HI HA CAP EXCEPCIO VIGENT]  (buit a 2026-09-26)

Mentre aquesta seccio sigui buida, s'aplica el mestre sencer, sense retallar.
--------------------------------------------------------------------------------
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


OBJECTIU_PROVEIDORS = 10000
LOCALITATS_PER_PAIS = 100
TOTAL_CARRILS = 27
UNITATS_TERRITORIALS = LOCALITATS_PER_PAIS * TOTAL_CARRILS

DATA_INFERIOR = 1952
DATA_SUPERIOR = date(2026, 9, 16)

CRITERI_ESGOTAMENT_RECERQUES = 15

VERSIO_NORMATIVA = "normativa/1.0"
DATA_RATIFICACIO = "2026-09-26"


class EstatCarril(str, Enum):
    PENDENT = "PENDENT"
    EN_CURS = "EN_CURS"
    COMPLET = "COMPLET"
    BLOQUEJAT = "BLOQUEJAT"


class MotiuBloqueig(str, Enum):
    SENSE_FONT_VALIDA = "SENSE_FONT_VALIDA"
    SENSE_EVIDENCIA = "SENSE_EVIDENCIA"
    RATE_LIMIT = "RATE_LIMIT"
    ERROR_TRANSPORT = "ERROR_TRANSPORT"


@dataclass
class Carril:
    """Un carril = un pais. Independent de tots els altres."""

    index: int
    pais: str
    codi_operatiu: str
    estat: EstatCarril = EstatCarril.PENDENT
    localitats_completades: int = 0
    localitat_en_curs: str = ""
    sector_en_curs: str = ""
    recerques_sense_resultat: int = 0
    proveidors_registrats: int = 0
    bloqueig: str = ""

    @property
    def progres_pct(self) -> float:
        return round(100.0 * self.localitats_completades / LOCALITATS_PER_PAIS, 4)

    @property
    def acabat(self) -> bool:
        return self.localitats_completades >= LOCALITATS_PER_PAIS

    @property
    def te_pendent(self) -> bool:
        return not self.acabat

    def tanca_localitat(self, proveidors: int = 0) -> "Carril":
        self.localitats_completades += 1
        self.proveidors_registrats += proveidors
        self.localitat_en_curs = ""
        self.sector_en_curs = ""
        self.recerques_sense_resultat = 0
        self.estat = EstatCarril.COMPLET if self.acabat else EstatCarril.EN_CURS
        return self

    def pot_obrir_sector(self) -> bool:
        return self.recerques_sense_resultat >= CRITERI_ESGOTAMENT_RECERQUES


def carrils_canonics() -> list[Carril]:
    """Els 27 carrils, un per pais de la UE-27, tots independents."""
    paisos = [
        ("Alemanya", "DE"), ("Àustria", "AT"), ("Bèlgica", "BE"), ("Bulgària", "BG"),
        ("Croàcia", "HR"), ("Dinamarca", "DK"), ("Eslovàquia", "SK"), ("Eslovènia", "SI"),
        ("Espanya", "ES"), ("Estònia", "EE"), ("Finlàndia", "FI"), ("França", "FR"),
        ("Grècia", "GR"), ("Hongria", "HU"), ("Irlanda", "IE"), ("Itàlia", "IT"),
        ("Letònia", "LV"), ("Lituània", "LT"), ("Luxemburg", "LU"), ("Malta", "MT"),
        ("Països Baixos", "NL"), ("Polònia", "PL"), ("Portugal", "PT"), ("Romania", "RO"),
        ("Suècia", "SE"), ("Txèquia", "CZ"), ("Xipre", "CY"),
    ]
    if len(paisos) != TOTAL_CARRILS:
        raise AssertionError(f"calen {TOTAL_CARRILS} carrils, n'hi ha {len(paisos)}")
    return [Carril(index=i + 1, pais=p, codi_operatiu=c) for i, (p, c) in enumerate(paisos)]


def carril_alemanya() -> Carril:
    return Carril(index=1, pais="Alemanya", codi_operatiu="DE")


@dataclass
class Verificacio:
    ok: bool
    motius: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.ok


def comprova_entrada(*, nom: str, url: str, extracte: str, data_consulta: str, anys: list[int] | None = None) -> Verificacio:
    """Cap dada entra sense prova documental real (R14)."""
    motius: list[str] = []
    if not nom or not nom.strip():
        motius.append("nom buit")
    if not url or not url.startswith(("http://", "https://")):
        motius.append("url no valida o absent")
    if not extracte or len(extracte.strip()) < 20:
        motius.append("extracte massa curt per ser evidencia")
    if not data_consulta or len(str(data_consulta)) < 10:
        motius.append("data de consulta absent")
    if anys and not any(DATA_INFERIOR <= a <= DATA_SUPERIOR.year for a in anys):
        motius.append(f"cap any dins la finestra {DATA_INFERIOR}-{DATA_SUPERIOR.isoformat()}")
    return Verificacio(ok=not motius, motius=motius)


def comprova_objectiu(registrats: int) -> Verificacio:
    motius: list[str] = []
    if registrats < 0:
        motius.append("recompte negatiu")
    if registrats > OBJECTIU_PROVEIDORS:
        motius.append(f"recompte per sobre de l'objectiu ({OBJECTIU_PROVEIDORS})")
    return Verificacio(ok=not motius, motius=motius)


def sector_esgotat(recerques_sense_resultat: int) -> bool:
    return recerques_sense_resultat >= CRITERI_ESGOTAMENT_RECERQUES


def comprova_avanc(carril: Carril) -> Verificacio:
    if not carril.pot_obrir_sector():
        return Verificacio(
            ok=False,
            motius=[f"{carril.pais}: sector no esgotat ({carril.recerques_sense_resultat}/{CRITERI_ESGOTAMENT_RECERQUES})"],
        )
    return Verificacio(ok=True)
