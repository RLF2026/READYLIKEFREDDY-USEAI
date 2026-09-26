"""RLF SUPPLIER ENGINE — CLI.

Us:
    python -m cli --entrada proveidors.csv --sortida registre.json --informe

Mai genera dades. Si el fitxer no existeix o li falten camps, falla clarament.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from font_adapters import FontInvalida, llegeix_fitxer
from supplier_engine import MotorProveidors


def _informe_text(motor: MotorProveidors, files_llegides: int, files_descartades: int, errors: list[str]) -> str:
    p = motor.progres_objectiu()
    linies = [
        "=" * 62,
        "RLF SUPPLIER ENGINE — INFORME",
        "=" * 62,
        f"Files llegides de la font : {files_llegides}",
        f"Files descartades a la font: {files_descartades}",
        f"Proveidors registrats     : {p['registrats']} / {p['objectiu']}",
        f"Progres                   : {p['percentatge']}%",
        f"Entrades rebutjades       : {p['descartats']}",
        "",
        "Classificacio:",
    ]
    for k, v in sorted(motor.per_classificacio().items()):
        linies.append(f"  {k:<28} {v}")
    linies.append("")
    linies.append("Paisos:")
    for k, v in sorted(motor.per_pais().items()):
        linies.append(f"  {k:<28} {v}")
    if errors:
        linies.append("")
        linies.append(f"Errors de lectura ({len(errors)}):")
        for e in errors[:20]:
            linies.append(f"  - {e}")
    linies.append("=" * 62)
    return "\n".join(linies)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Processa proveidors reals cap al registre RLF.")
    ap.add_argument("--entrada", required=True, help="Fitxer CSV o JSON de proveidors reals")
    ap.add_argument("--sortida", required=True, help="Fitxer JSON del registre processat")
    ap.add_argument("--informe", action="store_true", help="Escriu l'informe per stdout")
    args = ap.parse_args(argv)
    try:
        lectura = llegeix_fitxer(args.entrada)
    except FontInvalida as exc:
        print(f"ERROR de font: {exc}", file=sys.stderr)
        return 2
    motor = MotorProveidors()
    for entrada in lectura.entrades:
        clau = f"{entrada.nom.strip()}|{entrada.localitat.strip()}|{entrada.pais.strip()}"
        motor.processa(entrada, lectura.evidencies.get(clau, []))
    sortida = Path(args.sortida)
    sortida.parent.mkdir(parents=True, exist_ok=True)
    sortida.write_text(json.dumps(motor.exporta(), ensure_ascii=False, indent=2), encoding="utf-8")
    if args.informe:
        print(_informe_text(motor, lectura.files_llegides, lectura.files_descartades, lectura.errors))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
