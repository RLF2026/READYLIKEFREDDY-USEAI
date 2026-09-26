# `data/`

Directori de dades del sistema (§2.3.6).

## Regla de font de veritat (R12, §6.7)

La **base de dades SQL de producció** (MySQL a IONOS) és l'única font de veritat del sistema.
Tot artefacte d'aquest directori que mostri les mateixes dades és una **vista derivada de
lectura** i mai s'edita com a origen (§6.7.2, §6.7.4).

## Regla de no-invenció

Aquest directori **no conté cap dada**. No s'inventen registres per omplir-lo (NO FAKES,
§5.2.2; R14, zero simulacions).

Una carpeta de dades buida és informació correcta: diu que les dades encara no existeixen o
que viuen a la base de dades de producció, no aquí.

## Nota sobre dades personals

Qualsevol dada de client o de comanda que hi arribi en el futur queda subjecta a RGPD i a la
governança de §3.11. En aquest repositori no s'hi allotja cap dada personal.
