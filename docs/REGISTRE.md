# Registre d'esdeveniments d'aquest repositori

Registre append-only (§5.2.6). Les entrades s'afegeixen; no es reescriuen.

---

## 2026-09-26 — Obertura del repositori i estructura inicial

El repositori `RLF2026/READYLIKEFREDDY-USEAI` era completament buit, sense branca per defecte. Primera càrrega de contingut.

**Creat:** `README.md`; `docs/` (document mestre íntegre, arquitectura, governança OP, gates, registre); `assets/brand/` (manifest, joc verd i negre reservat); els README de `shared/rlf_core/`, `projects/rlf_suppliers_eu27/`, `projects/rlf_fred_perry_kb_visor/`, `governance/`, `deployment/`, `marketing/`, `data/`, `tests/`.

**No creat:** cap fitxer binari ni cap codi. Motiu registrat al seu moment.

---

## 2026-09-26 — Lliurament AAA de logotip

Arribada del lliurament `LOGO DELIVERY AAA` (variants A i B, fons blanc i transparent).

**Creat:** `assets/brand/MANIFEST.md`, `assets/brand/SHA256_MANIFEST.txt`, `assets/brand/README_RLF_LOGO_AAA.txt`.

La convenció de noms adoptada és la del lliurament: `RLF_LOGO_[VERSION]_[COLOR]_[BACKGROUND]_[ROLE]_[SIZE/FORMAT]`.

---

## 2026-09-26 — Resolució dels punts oberts

S'han decodificat els PNG sencers (IDAT, zlib, filtres de línia) i llegit els píxels un a un; s'han analitzat els JPEG per estructura de marcadors i comparació byte a byte.

**Creat:** `assets/brand/PUNTS_OBERTS.md`.

**Tancats amb evidència:** PO-4 (alfa inert a `FONDO_BLANCO`), PO-8 (alfa compartida = efecte esperat de font única), PO-9 (decideix el hash del manifest), PO-10 (el verd del lliurament SÍ que és el de §1.2.3; alerta retirada), PO-11 (el PDF blanc és vàlid).

**Mesurats amb veredicte:** PO-2 (causa identificada), PO-3 (marge 64–67 px contra 600 exigits), PO-7 (`A_VERDE..._MASTER` no és transparent).

**Oberts per decisió de governança:** PO-1, PO-5, PO-6.

---

## 2026-09-26 — Reconciliació de versió

S'ha revisat la presumpta incoherència entre la capçalera del document (2.5.0) i §6.5.6 (2.2.0).

**Conclusió: no hi ha dues versions del sistema en conflicte.** La fila de §6.5.6 diu literalment *"RLF REAL SYSTEMS (capçalera del document) | 2.2.0 | VERIFICAT"*: és el registre del valor que la capçalera portava quan aquella fila es va verificar, no una declaració de la versió vigent. Sota SemVer (§4.4.8, §6.1.12), 2.5.0 és un avanç de tres revisions MINOR des de 2.2.0 — compatible i previst per l'esquema.

**La meva lectura anterior queda corregida:** ho havia registrat com una contradicció interna que requeria decisió de governança; requereix una correcció de coherència, no una decisió.

**Què NO s'ha fet:** no s'ha editat el document mestre. La fila diu `VERIFICAT` i sobreescriure-la per fer-la quadrar amb la capçalera seria falsificar un registre de verificació (R2, R19). Si s'hi ha d'afegir la versió vigent, s'afegeix una fila nova.

**Què S'ha fet:** `docs/VERSIO.md` com a font única de versió del repositori, amb totes les versions que apareixen al document i el seu abast real. El README hi apunta i ja no declara cap versió pel seu compte.

---

*Registre append-only. Autor del sistema i propietari intel·lectual: Jordi Figueras Soler.*
