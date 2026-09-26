# Registre d'esdeveniments d'aquest repositori

Registre append-only (§5.2.6). Les entrades s'afegeixen; no es reescriuen.

---

## 2026-09-26 — Obertura del repositori i estructura inicial

El repositori `RLF2026/READYLIKEFREDDY-USEAI` era completament buit, sense branca per defecte. Primera càrrega de contingut.

---

## 2026-09-26 — Lliurament AAA de logotip

Arribada del lliurament `LOGO DELIVERY AAA`. Creat el manifest, el manifest SHA-256 i el README del lliurament.

---

## 2026-09-26 — Resolució dels punts oberts d'actius

Decodificats els PNG sencers i llegits els píxels un a un. Tancats PO-4, PO-8, PO-9, PO-10 i PO-11 amb evidència. Mesurats amb veredicte PO-2, PO-3 i PO-7.

---

## 2026-09-26 — Versió del sistema reconciliada a 2.6.0

Eliminada la fila històrica 2.2.0 de §6.5.6, capçalera unificada a 2.6.0, i creat `docs/VERSIO.md` com a font única de versió del repositori.

---

## 2026-09-26 — Fase 1 i Fase 2 del sistema

Fase 1 (RLF CORE): contracte de retorn, fail-closed, logging, hashing i idempotència, estat persistent, cursors, checkpoints, configuració, integritat, normalització, identitat canònica, deduplicació, màquina d'estats amb les 24 guardes, resolució de HOLDs, validació i els contractes RLF-TRUST/1.0 i RLF-RESILIENCE/1.0.

Fase 2 (motor de sourcing): work queue, finestres territorials, orquestrador, workers i Laurel Ledger.

---

## 2026-09-26 — Pla de la megarecerca de proveïdors

Creat `docs/PLA_MEGARECERCA_SUPPLIERS.md` amb els quinze elements de VALIDAT, els vuit criteris d'elegibilitat, el protocol de cerques, les regles de cortesia i els quatre punts oberts.

---

## 2026-09-26 — Correcció de compliment de R14: retirades dues suites

**Motiu.** Governança va recordar que les dades de prova són una simulació i que R14 les prohibeix sense excepció. Revisió de totes les suites del repositori contra la regla.

**Retirades, per fabricar context de domini:**

- `tests/test_sourcing.py` — passava codis de país, noms de ciutat i etiquetes inventades al motor de sourcing i hi assertia com si fossin la matriu canònica del Laurel Ledger.
- `tests/test_suppliers_and_normalization.py` — fabricava codis de país, un domini d'invenció i codis de model com a valors de comprovació.

**Mantingudes, perquè compleixen R14:**

- `test_core.py`, `test_states.py`, `test_identity_dedup_hold.py`, `test_validation_governance.py` — proves sobre funcions pures; no afirmen res sobre cap entitat del món real.
- `test_state_and_integrity.py` — funcions pures i fitxers reals en directoris temporals.
- `test_monitoring.py` — servidors HTTP locals reals, tal com R14 exigeix.

**També corregit:**

- `tests/README.md` reescrit: la versió anterior deia «Estat: Buid» mentre hi havia set suites al repositori.
- `tests/run_all.py` actualitzat: retirades les suites inexistents de la llista i afegida la detecció de suites retirades per R14.
- `tests/.github-workflow-tests.yml` marcat com a retirat; era una còpia temporal amb nom enganyós.
- `/A_VERDE_FONDO_BLANCO`, `/A_VERDE_FONDO_TRANSPARENTE`, `/B_NEGRO_FONDO_BLANCO`, `/B_NEGRO_FONDO_TRANSPARENTE` a l'arrel: la meva simplificació incorrecta. El lliurament viu sencer sota `assets/brand/`; aquestes carpetes de l'arrel són duplicat.

**Conseqüència de fons.** Les proves dels mòduls de domini no es poden escriure fins que existeixin les dades reals: el protocol de cerques (PO-A), les cent localitats canòniques (PO-C) i la sectorització per població. Els mòduls segueixen al repositori i operatius; el que no existeix és la matèria real sobre la qual provar-los.

---

*Registre append-only. Autor del sistema i propietari intel·lectual: Jordi Figueras Soler.*
