# Registre d'esdeveniments d'aquest repositori

Registre append-only (§5.2.6). Les entrades s'afegeixen; no es reescriuen.

---

## 2026-09-26 — Obertura del repositori i estructura inicial

El repositori `RLF2026/READYLIKEFREDDY-USEAI` era completament buit, sense branca per defecte.
Primera càrrega de contingut.

**Creat:** `README.md`; `docs/` (document mestre íntegre, arquitectura, governança OP, gates,
registre); `assets/brand/` (manifest, joc verd i negre reservat); els README de
`shared/rlf_core/`, `projects/rlf_suppliers_eu27/`, `projects/rlf_fred_perry_kb_visor/`,
`governance/`, `deployment/`, `marketing/`, `data/`, `tests/`.

**No creat:** cap fitxer binari ni cap codi. Motiu registrat al seu moment.

---

## 2026-09-26 — Lliurament AAA de logotip

Arribada del lliurament `LOGO DELIVERY AAA` (variants A i B, fons blanc i transparent).

**Creat:** `assets/brand/MANIFEST.md`, `assets/brand/SHA256_MANIFEST.txt`,
`assets/brand/README_RLF_LOGO_AAA.txt`.

La convenció de noms adoptada és la del lliurament:
`RLF_LOGO_[VERSION]_[COLOR]_[BACKGROUND]_[ROLE]_[SIZE/FORMAT]`.

---

## 2026-09-26 — Resolució dels punts oberts

S'han decodificat els PNG sencers (IDAT, zlib, filtres de línia) i llegit els píxels un a un;
s'han analitzat els JPEG per estructura de marcadors i comparació byte a byte.

**Creat:** `assets/brand/PUNTS_OBERTS.md`.

**Tancats amb evidència:**

- **PO-4** — els PNG `FONDO_BLANCO` són 100% opacs; el nom és correcte i l'alfa és inert.
- **PO-8** — l'alfa idèntica entre variants és l'efecte esperat de generar-les des de la mateixa
  font de tinta. No és defecte.
- **PO-9** — les dues còpies del màster B blanc difereixen en 294.949 bytes; decideix el hash del
  manifest.
- **PO-10** — el verd pintat és `(4,93,63)` ≈ `#005C3F`. El lliurament SÍ que fa servir el verd
  de §1.2.3. L'alerta anterior es retira.
- **PO-11** — el PDF de fons blanc és vàlid: `%PDF-1.4`, `%%EOF`, sense xifrat, 1 pàgina. El
  problema era del lector al primer intent.

**Mesurats amb veredicte:**

- **PO-2** — causa identificada: màster i web comparteixen imatge; el gran no aporta res.
- **PO-3** — marge real 64–67 px contra 600 px exigits per §1.3; ràtio 0,213. És un canvi de
  retall, no una reparació d'arxiu.
- **PO-7** — **`A_VERDE_FONDO_TRANSPARENTE_MASTER_4096px.png` no és transparent:** 100% opac,
  fons negre pur, 63% de la superfície. Defecte real.

**Oberts per decisió de governança:** PO-1 (mides als noms), PO-5 (regenerar previsualització),
PO-6 (estat de la variant B dins el sistema visual).

**Governança:** cap decisió nova presa des d'aquí. Els tres punts oberts són de Nivell 6.

---

*Registre append-only. Autor del sistema i propietari intel·lectual: Jordi Figueras Soler.*
