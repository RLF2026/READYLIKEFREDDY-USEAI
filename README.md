# READY LIKE FREDDY

## Repositori canònic de projecte — `RLF2026/READYLIKEFREDDY-USEAI`

---

## Avís de governança

Aquest repositori **no és la font de veritat** del sistema RLF. La font de veritat única és
`docs/RLF_Document_Mestre_v2.5.0.md` (R12, §0.1 del document mestre: davant de qualsevol
contradicció entre el document i qualsevol altre artefacte — conversa, nota, correu, record,
codi — **guanya el document**, i l'artefacte es corregeix).

Aquest README i la resta de fitxers d'aquest repositori són **artefactes derivats**: descriuen,
referencien i preserven. No redefineixen res. Si aquest README contradiu el document mestre,
el README és el que s'ha de corregir.

Funció d'aquest repositori, segons l'arquitectura del document: **RLF-BACKUP/1.0 (§4.4.4)** —
"la conversa no és la infraestructura; la infraestructura ha de poder sobreviure a la conversa".

---

## 1. Dades canòniques de la capçalera del document mestre

Dades transcrites literalment de la capçalera de `docs/RLF_Document_Mestre_v2.5.0.md`.
Tota la resta de dades de projecte són dins del document mestre, no aquí.

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

## 2. Contradicció oberta registrada — versió del sistema

**Estat: PUNT OBERT. Requereix decisió de governança (Nivell 6, §2.2.7). No resolt per aquest repositori.**

| Ubicació | Valor |
|---|---|
| Capçalera del document mestre | `Versió del document: 2.5.0` |
| §6.5.6 (Taula de versions) | `RLF REAL SYSTEMS` = **2.2.0** |

El mateix document registra dues versions del sistema. §0.1 diu que les contradiccions es
resolen a favor del document, però aquí la contradicció és **interna** al document: no hi ha
cap artefacte extern que pugui desempatar. Condició de tancament (§6.3.5): decisió de
governança que ratifiqui quin dels dos valors és el canònic, i correcció de l'altre.

Fins que es tanqui, aquest repositori **no afirma cap versió del sistema**. Qualsevol agent
que hagi de citar una versió cita les dues i assenyala el punt obert.

---

## 3. Estat dels gates de preinauguració (§5.3.A)

Cap d'aquests gates es pot satisfer manualment des del dashboard (§5.3.A, nota final).
Cap es tanca amb una decisió de governança: es tanquen fent la feina real (§6.3.4, nota).

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
  ARQUITECTURA.md                Arbre del sistema segons §2.3.
  GOVERNANCA_OP.md               Registre de les decisions de governança (OP).
  GATES_PREINAUGURACIO.md        Estat dels tres gates de §5.3.A.
  REGISTRE.md                    Registre append-only d'esdeveniments del repositori.
assets/brand/                    Actius d'identitat visual (§1.2, §1.3).
  MANIFEST.md                    Inventari verificat dels fitxers + convenció de noms.
  green/                         Joc verd — fons transparent.
  black/                         Joc negre — buit, pendent de lliurament.
shared/rlf_core/                 RLF CORE: primitives reutilitzables (§2.2.4).
projects/rlf_suppliers_eu27/     Actiu principal 1 (§2.2.3).
projects/rlf_fred_perry_kb_visor/ Actiu principal 2 (§2.2.3).
data/                            Dades.
governance/                      Contractes de governança (§4.4).
deployment/                      Desplegament (§8): hosting, domini, correus, stripe, storefront.
marketing/                       Màrqueting (§9): social, newsletter, fanzine. Fase 11.
tests/                           Proves.
```

Les carpetes de codi i de dades (`shared/`, `projects/`, `data/`, `governance/`,
`deployment/`, `marketing/`, `tests/`) contenen **només un `README.md`** que descriu què hi ha
d'anar segons el document mestre. No contenen codi: el codi encara no existeix i aquest
repositori no l'inventa (NO FAKES, §5.2.2; R14, zero simulacions).

---

## 5. Actius d'identitat visual — estat

El logo viu a §1.2–§1.3 del document mestre: el bloc verbal "READY LIKE FREDDY" i la corona
de llorer apareixen **sempre junts**, com a brodat verd fosc sobre piqué blanc cru, excepte
dins d'una fotografia real (§1.3).

Hi ha un joc de fitxers verd de fons transparent **lliurat** (4 fitxers) i un joc negre
**anunciat i encara no lliurat**.

Mides i propietats verificades per inspecció directa dels bytes:

| Fitxer | Mides reals | Canal alfa | Pes |
|---|---|---|---|
| `rlf-logo-a-green-transparent-master.png` | 2000 × 1224 px | Sí (RGBA, colorType 6, sense tRNS) | 1.828.434 B |
| `rlf-logo-a-green-master.jpg` | 2000 × 1224 px | No (JPEG no admet alfa) | 205.578 B |
| `rlf-logo-a-green-transparent-web.png` | 2000 × 1224 px | Sí (RGBA, colorType 6, sense tRNS) | 2.356.787 B |
| `rlf-logo-a-green-web.jpg` | 2000 × 1224 px | No | 210.375 B |

**Tres desviacions detectades respecte del que els noms dels fitxers declaren.** Es registren
com a punts a resoldre abans de publicar; no s'han corregit ni s'han amagat:

1. **Els quatre fitxers fan la mateixa mida en píxels, 2000 × 1224.** Els noms diuen
   "MASTER 4096px" i "WEB 2048px", però no existeix cap fitxer de 4096 px ni de 2048 px.
2. **El fitxer "WEB" és el més pesat dels quatre** (2,36 MB, més que el "MASTER"). Un actiu
   de web no pot ser el més pesat del joc. Contradiu l'ús previst a §1.6 i §6.8.3.
3. **Marge de seguretat no verificable.** §1.3 exigeix espai de seguretat igual a l'alçada
   de la "R" ×2 en totes direccions, i mida mínima de 25 mm en impressió / 70 px en pantalla.
   No s'ha pogut comprovar el marge contra el fitxer; cal una comprovació explícita abans
   de publicar.

Detall complet i convenció de noms a `assets/brand/MANIFEST.md`.

---

## 6. Regla de treball d'aquest repositori

1. **El document mestre mana.** Qualsevol fitxer d'aquí que el contradigui es corregeix.
2. **Append-only (§5.2.6).** Els canvis s'afegeixen; no es reescriu la història.
3. **Zero invencions (§5.2.2, R14).** Cap dada, xifra, codi ni fitxer s'inventa per omplir
   una carpeta buida. Una carpeta buida és informació correcta: diu que la feina no s'ha fet.
4. **Traçabilitat (§5.2.4).** Cada afirmació d'aquest repositori porta referència de secció
   del document mestre o bé és el resultat d'una inspecció directa declarada com a tal.
5. **Els punts oberts es registren, no es tapen (§5.2.2, R5).** Els de §2 i §5 d'aquest
   fitxer són oberts i així es queden fins que governança els tanqui.

---

*Repositori creat com a artefacte RLF-BACKUP/1.0. Cap dada d'aquest fitxer substitueix el
document mestre. Autor del sistema i propietari intel·lectual: Jordi Figueras Soler.*
