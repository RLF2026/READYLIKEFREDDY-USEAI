# Registre d'esdeveniments d'aquest repositori

Registre append-only (§5.2.6). Les entrades s'afegeixen; no es reescriuen.

---

## 2026-09-26 — Obertura del repositori i estructura inicial

El repositori `RLF2026/READYLIKEFREDDY-USEAI` era completament buit, sense branca per defecte. Primera càrrega de contingut.

**Creat:** `README.md`; `docs/` (document mestre íntegre, arquitectura, governança OP, gates, registre); `assets/brand/` (manifest); els README de `shared/rlf_core/`, `projects/rlf_suppliers_eu27/`, `projects/rlf_fred_perry_kb_visor/`, `governance/`, `deployment/`, `marketing/`, `data/`, `tests/`.

---

## 2026-09-26 — Lliurament AAA de logotip

Arribada del lliurament `LOGO DELIVERY AAA` (variants A i B, fons blanc i transparent).

**Creat:** `assets/brand/MANIFEST.md`, `assets/brand/SHA256_MANIFEST.txt`, `assets/brand/README_RLF_LOGO_AAA.txt`.

Convenció de noms adoptada del lliurament: `RLF_LOGO_[VERSION]_[COLOR]_[BACKGROUND]_[ROLE]_[SIZE/FORMAT]`.

---

## 2026-09-26 — Resolució dels punts oberts d'actius

Decodificats els PNG sencers (IDAT, zlib, filtres de línia) i llegits els píxels un a un; JPEG analitzats per marcadors i comparació byte a byte.

**Creat:** `assets/brand/PUNTS_OBERTS.md`.

**Tancats amb evidència:** PO-4 (alfa inert a `FONDO_BLANCO`), PO-8 (alfa compartida = efecte esperat de font única), PO-9 (decideix el hash del manifest), PO-10 (el verd pintat és `(4,93,63)` ≈ `#005C3F` de §1.2.3 — alerta prèvia retirada), PO-11 (PDF blanc vàlid).

**Mesurats amb veredicte:** PO-2, PO-3 (marge 64–67 px contra 600 exigits), PO-7 (`A_VERDE..._MASTER` no transparent).

**Oberts per decisió de governança:** PO-1, PO-5, PO-6.

---

## 2026-09-26 — Versió del sistema reconciliada a 2.6.0

**Autoritzat per governança (Nivell 6).** Canvi aplicat al document mestre:

- **Eliminada** la fila `| RLF REAL SYSTEMS (capçalera del document) | 2.2.0 | VERIFICAT |` de §6.5.6.
- **Capçalera** unificada a **2.6.0**, data d'emissió 2026-09-26.
- **Afegida** nota de versió 2.6.0 a la capçalera, que separa explícitament la versió del sistema de l'esquema SemVer, de les versions de contracte i de les versions de component.
- **Afegida** nota d'abast sota la taula §6.5.6: registra versions de component, no la versió del sistema.
- **Afegit** punter de versió a la portada, sota el títol.

**Fitxers renombats:** `docs/RLF_Document_Mestre_v2.5.0.md` → `docs/RLF_Document_Mestre_v2.6.0.md`.

**Retirada una meva lectura anterior:** havia registrat la diferència 2.5.0 vs. 2.2.0 com una contradicció interna que requeria decisió de governança. Governança ha decidit eliminar la fila per coherència de lectura. Fet.

---

## 2026-09-26 — Codi del sistema (fases inicials)

**Creat:** `shared/rlf_core/` amb contract, logging, hashing, state, config i integrity; `projects/rlf_suppliers_eu27/verification/supplier_eligibility.py` i `monitoring/availability.py`; proves a `tests/`.

Tot el codi compleix **SPEC-CODE-001** (§6.1): contracte de retorn canònic, nomenclatura, type hints, docstrings en català.

---

*Registre append-only. Autor del sistema i propietari intel·lectual: Jordi Figueras Soler.*
