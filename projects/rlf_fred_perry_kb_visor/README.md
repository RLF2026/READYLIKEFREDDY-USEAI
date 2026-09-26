# `projects/rlf_fred_perry_kb_visor/` — RLF Fred Perry Canonical KB + Visor

Actiu principal 2 (§2.2.3): sistema de coneixement de referència per identificar, normalitzar
i verificar producte Fred Perry preloved.

## Contingut previst (§2.3.6)

```
projects/rlf_fred_perry_kb_visor/
├── kb/         Knowledge Base canònica (§3.6)
├── visor/      Visor forense: interfície de coneixement visual (§3.7)
└── evidence/   Evidència
```

## Regles que governen aquest actiu

- **Cobertura objectiu:** ≥15.000 productes únics Fred Perry **FULL-CERTIFIED** (§3.6.2).
  El recompte és d'identitats canòniques, no d'anuncis, talles ni exemplars duplicats.
- **Abast temporal (R20):** antecedents dels anys 1940 (capa històrica, **no** compten com a
  productes Fred Perry de la marca) + productes de marca des de 1952 fins al tall de
  congelació. Una data futura mai es declara coberta abans que arribi.
- **Fotografies per producte (§3.6.3):** 4 bàsiques obligatòries (frontal/hero, posterior,
  detall de Laurel Wreath o element de marca, etiqueta de coll/manufactura) + Forensic
  Profile complet (2–10 forenses per identitat).
- **Zero buits (R17, §3.6.5):** un registre FULL-CERTIFIED no conté buits. `NOT_APPLICABLE`
  només amb regla de categoria explícita i justificació persistent.
- **Imatges reals i traçables (R18):** no es generen, pinten, reconstrueixen ni completen
  vistes amb IA. Una imatge certificada és una fotografia real d'una font permesa, amb
  origen, data d'accés, hash, classificació i estat de drets.
- **Factory Registry (§3.6.6):** entitat pròpia amb `factory_id`, estat
  (`VERIFIED_ACTIVE` / `VERIFIED_HISTORICAL` / `UNRESOLVED`) i evidència. Una menció de país
  no es transforma automàticament en una fàbrica. Si la fàbrica és material i no es pot
  resoldre, el producte no compta entre els 15.000.
- **Saturació (§3.6.4):** el dataset només es declara saturat després de **dues passades
  independents consecutives** sense cap nova identitat que pugui arribar a FULL-CERTIFIED.
  La saturació **no substitueix** el gate de 15.000.

## Estat

**Buid.** No hi ha codi en aquest repositori.
