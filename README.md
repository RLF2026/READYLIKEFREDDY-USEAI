# READY LIKE FREDDY

## Repositori canònic de projecte — `RLF2026/READYLIKEFREDDY-USEAI`

---

## Avís de governança

Aquest repositori **no és la font de veritat** del sistema RLF. La font de veritat única és `docs/RLF_Document_Mestre_v2.5.0.md` (R12, §0.1 del document mestre: davant de qualsevol contradicció entre el document i qualsevol altre artefacte — conversa, nota, correu, record, codi — **guanya el document**, i l'artefacte es corregeix).

Aquest README i la resta de fitxers d'aquest repositori són **artefactes derivats**: descriuen, referencien i preserven. No redefineixen res. Si aquest README contradiu el document mestre, el README és el que s'ha de corregir.

Funció d'aquest repositori, segons l'arquitectura del document: **RLF-BACKUP/1.0 (§4.4.4)** — "la conversa no és la infraestructura; la infraestructura ha de poder sobreviure a la conversa".

---

## 1. Versió del sistema

**La font única de versió dins aquest repositori és `docs/VERSIO.md`.** Cap fitxer d'aquí declara una versió pel seu compte.

| Camp | Valor |
|---|---|
| Versió del document | **2.5.0** |
| Data d'emissió | 2026-09-25 |
| Sistema | RLF REAL SYSTEMS |
| Esquema | SemVer 2.0.0 — `MAJOR.MINOR.PATCH` |

El valor prové de la capçalera del document mestre. La fila `2.2.0` de §6.5.6 **no és una versió en conflicte**: és el registre del valor que la capçalera portava quan aquella fila es va verificar. Explicació completa, i totes les versions que apareixen al document amb el seu abast real, a `docs/VERSIO.md`.

---

## 2. Dades canòniques de la capçalera del document mestre

Dades transcrites literalment de la capçalera de `docs/RLF_Document_Mestre_v2.5.0.md`. Tota la resta de dades de projecte són dins del document mestre, no aquí.

| Camp | Valor |
|---|---|
| Document | RLF — Document Mestre Canònic Únic |
| Sistema | RLF REAL SYSTEMS |
| Versió del document | 2.5.0 |
| Data d'emissió | 2026-09-25 |
| Autor i propietari intel·lectual | Jordi Figueras Soler (NIF 36521331E) |
| Domini oficial | readylikefreddy.shop |
| Correu operatiu | freddy@readylikefreddy.shop |
| Correu automàtic (mailings, factures, newsletters, campanyes) | no-reply@readylikefreddy.shop |
| Registrador de domini i correu | Nominalia |
| Hosting | IONOS (pla senzill, 200 GB, WordPress) |
| Base de dades de producció | MySQL inclosa a IONOS (§6.7.1: única font de veritat de dades) |
| Seu (HQ) | C/ Santa Eulàlia, 236. Baixos. 08902 L'Hospitalet de Llobregat |
| Passarel·la de pagament | Stripe (§3.12.1, §8.5) — única prevista per al llançament |
| Plataforma de botiga | WordPress + WooCommerce (§2.3.1 bloc 8, §6.8, §8.6) |

---

## 3. Estat dels gates de preinauguració (§5.3.A)

Cap d'aquests gates es pot satisfer manualment des del dashboard (§5.3.A, nota final). Cap es tanca amb una decisió de governança: es tanquen fent la feina real (§6.3.4, nota).

| Gate | Condició dura | Font de recompte | Estat |
|---|---|---|---|
| Suppliers | `supplier_prelaunch_validated >= 10000` | Snapshot SQL immutable | **OBERT** |
| KB | `kb_prelaunch_full_certified >= 15000` | Snapshot SQL immutable | **OBERT** |
| Operativa | 60 dies consecutius d'operativa estable amb ≥1 venda/setmana (§1.9) | Registre d'operació | **OBERT** |

R15: "No es compten projeccions, mostres, registres parcials ni aproximacions."

---

## 4. Estructura d'aquest repositori

L'arbre deriva de les rutes físiques de §2.3.6 del document mestre.

```
README.md                        Aquest fitxer. Acta del repositori.
docs/                            Documentació canònica i registres de governança.
  RLF_Document_Mestre_v2.5.0.md  Font de veritat única. Còpia íntegra, sense modificar.
  VERSIO.md                      Font única de versió del repositori.
  ARQUITECTURA.md                Arbre del sistema segons §2.3.
  GOVERNANCA_OP.md               Registre de les decisions de governança (OP).
  GATES_PREINAUGURACIO.md        Estat dels gates de §5.3.A.
  REGISTRE.md                    Registre append-only d'esdeveniments del repositori.
assets/brand/                    Actius d'identitat visual (§1.2, §1.3).
  MANIFEST.md                    Inventari verificat dels fitxers + convenció de noms.
  PUNTS_OBERTS.md                Resolució dels punts oberts, amb mesures.
  SHA256_MANIFEST.txt            Manifest SHA-256 del lliurament AAA.
  README_RLF_LOGO_AAA.txt        README del lliurament AAA.
  A_VERDE_FONDO_TRANSPARENTE/    Joc A, fons transparent.
  A_VERDE_FONDO_BLANCO/          Joc A, fons blanc.
  B_NEGRO_FONDO_TRANSPARENTE/    Joc B, fons transparent.
  B_NEGRO_FONDO_BLANCO/          Joc B, fons blanc.
shared/rlf_core/                 RLF CORE: primitives reutilitzables (§2.2.4).
projects/rlf_suppliers_eu27/     Actiu principal 1 (§2.2.3).
projects/rlf_fred_perry_kb_visor/ Actiu principal 2 (§2.2.3).
data/                            Dades.
governance/                      Contractes de governança (§4.4).
deployment/                      Desplegament (§8): hosting, domini, correus, stripe, storefront.
marketing/                       Màrqueting (§9): social, newsletter, fanzine. Fase 11.
tests/                           Proves.
```

Les carpetes de codi i de dades (`shared/`, `projects/`, `data/`, `governance/`, `deployment/`, `marketing/`, `tests/`) contenen **només un `README.md`** que descriu què hi ha d'anar segons el document mestre. No contenen codi: el codi encara no existeix i aquest repositori no l'inventa (NO FAKES, §5.2.2; R14, zero simulacions).

---

## 5. Actius d'identitat visual — estat

El logo viu a §1.2–§1.3 del document mestre: el bloc verbal "READY LIKE FREDDY" i la corona de llorer apareixen **sempre junts**, com a brodat verd fosc sobre piqué blanc cru, excepte dins d'una fotografia real (§1.3).

Hi ha un lliurament complet de quatre grups (A/B × blanc/transparent). L'inventari complet, les mides reals mesurades i l'estat de cada fitxer són a `assets/brand/MANIFEST.md`; la resolució dels punts oberts, amb les xifres, a `assets/brand/PUNTS_OBERTS.md`.

**Resum de l'estat:**

- **Verificat a nivell de píxel:** tots els binaris fan **2000 × 1224 px**. Cap fa 4096 px ni 2048 px, malgrat el que diuen els noms.
- **Defecte real (PO-7):** `A_VERDE_FONDO_TRANSPARENTE_MASTER_4096px.png` **no és transparent** — 100% opac, fons negre pur.
- **Marge de seguretat (PO-3):** 64–67 px reals contra els 600 px que exigeix §1.3.
- **Paleta:** el verd pintat és `(4,93,63)` ≈ `#005C3F`, el verd de §1.2.3. No hi ha discrepància.
- **Oberts per decisió de governança:** mides als noms (PO-1), regenerar la previsualització (PO-5), estat de la variant B dins el sistema visual (PO-6).

Els fitxers binaris s'han de carregar per la interfície web de GitHub: el canal de xat no accepta TIFF, WebP ni SVG.

---

## 6. Regla de treball d'aquest repositori

1. **El document mestre mana.** Qualsevol fitxer d'aquí que el contradigui es corregeix.
2. **Append-only (§5.2.6).** Els canvis s'afegeixen; no es reescriu la història.
3. **Zero invencions (§5.2.2, R14).** Cap dada, xifra, codi ni fitxer s'inventa per omplir una carpeta buida. Una carpeta buida és informació correcta: diu que la feina no s'ha fet.
4. **Traçabilitat (§5.2.4).** Cada afirmació d'aquest repositori porta referència de secció del document mestre o bé és el resultat d'una inspecció directa declarada com a tal.
5. **Els punts oberts es registren, no es tapen (§5.2.2, R5).** Els que queden oberts ho estan fins que governança els tanqui.
6. **La versió s'escriu en un sol lloc.** `docs/VERSIO.md`.

---

*Repositori creat com a artefacte RLF-BACKUP/1.0. Cap dada d'aquest fitxer substitueix el document mestre. Autor del sistema i propietari intel·lectual: Jordi Figueras Soler.*
