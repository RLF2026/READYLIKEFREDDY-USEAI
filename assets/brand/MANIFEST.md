# Actius d'identitat visual — inventari i convenció

Actius de marca segons §1.2–§1.3 del document mestre canònic
(`docs/RLF_Document_Mestre_v2.5.0.md`).

---

## 1. Regla del logotip (§1.3)

- El bloc verbal **"READY LIKE FREDDY"** i la **corona de llorer** apareixen **sempre junts**.
  No existeix isotip separat ni versió simplificada.
- Apareixen sempre com a **brodat verd fosc sobre piqué blanc cru**, excepte dins una
  fotografia real.
- Tagline **"PRE-LOVED FRED PERRY SPECIALIST"** a mida completa dins el marc inferior.
- Espai de seguretat: alçada de la "R" ×2 en totes direccions.
- Mida mínima: **25 mm en impressió, 70 px en pantalla**.
- Interlineat sòlid (1,0); tracking −10 a READY i FREDDY.

**Prohibit (§1.3):** logotip en blanc pur, pla sense textura, glossy, metàl·lic, com a
sticker, inclinat, o amb la corona separada del bloc verbal.

**Regla del logotip de tercers (§1.3):** cap logotip de Fred Perry solt (ni la corona de
llorer de la marca) s'usa com a element gràfic de RLF fora del logotip oficial de RLF. La
marca Fred Perry només s'usa de manera nominativa per identificar la peça revenuda.

**Decisió de governança OP-008 (TANCAT, §1.3):** la compatibilitat de la corona de llorer
amb els drets de marca de tercers **no s'ha sotmès a revisió legal prèvia**. La governança
assumeix aquest risc de manera explícita i informada, i el disseny actual s'usa des del dia 1
sense modificació ni bloqueig.

---

## 2. Paleta (§1.2.3, VERIFICAT)

| Color | Codi | Ús |
|---|---|---|
| Piqué blanc cru | `#F2EBDD` / `#F4EFE6` | 85% — fons, contenidors, targetes, fitxes, footer. **Mai blanc pur.** |
| Fil verd principal | `#005C3F` | 12% — logotip, titulars, botons, marcs, icones, separadors, preus, badges. |
| Ombra de fil | `#003B2B` | Microrelleu, profunditat de puntada, text llarg. |
| Llum de fil | `#0A6F50` | Ressalt tèxtil subtil. Només decoratiu o text gran. |
| Fotografia / accents funcionals | — | 3% màxim, sempre dins marc brodat. |

**Prohibit (§1.2.3):** blanc pur `#FFFFFF` com a fons, daurat, neó, degradat digital, ombra
web moderna, glossy, metall, plàstic, cartolina, sticker, mockup digital, acabat corporatiu.

---

## 3. Joc verd lliurat — verificació directa

Els quatre fitxers d'aquest joc s'han inspeccionat llegint-ne els bytes
(capçalera PNG/JPEG i chunks). Les dades són el resultat d'aquesta inspecció, no una
transcripció del nom del fitxer.

| Fitxer al repositori | Mides reals | Canal alfa | Pes |
|---|---|---|---|
| `green/rlf-logo-a-green-transparent-master.png` | 2000 × 1224 px | Sí — RGBA (colorType 6), sense chunk `tRNS` | 1.828.434 B |
| `green/rlf-logo-a-green-master.jpg` | 2000 × 1224 px | No — JPEG no admet alfa | 205.578 B |
| `green/rlf-logo-a-green-transparent-web.png` | 2000 × 1224 px | Sí — RGBA (colorType 6), sense chunk `tRNS` | 2.356.787 B |
| `green/rlf-logo-a-green-web.jpg` | 2000 × 1224 px | No | 210.375 B |

Noms originals dels fitxers lliurats:

```
RLF_LOGO_A_VERDE_FONDO_TRANSPARENTE_MASTER_4096px.png
RLF_LOGO_A_VERDE_FONDO_TRANSPARENTE_MASTER_4096px.jpg
RLF_LOGO_A_VERDE_FONDO_TRANSPARENTE_WEB_2048px.png
RLF_LOGO_A_VERDE_FONDO_TRANSPARENTE_WEB_2048px.jpg
```

---

## 4. Punts oberts d'aquest joc — a resoldre abans de publicar

Registrats com a punts oberts (R5). **No s'han corregit ni s'han amagat.**

### PO-1 — Els noms declaren mides que no existeixen

Els noms diuen "MASTER 4096px" i "WEB 2048px". La inspecció directa mostra que **els quatre
fitxers fan 2000 × 1224 px**. No existeix cap fitxer de 4096 px ni de 2048 px en aquest joc.

Condició de tancament: o bé es reexporten els màsters a les mides que els noms declaren, o bé
es renombren els fitxers perquè el nom reflecteixi la mida real. Governança decideix quina.

### PO-2 — El fitxer "WEB" és el més pesat dels quatre

`rlf-logo-a-green-transparent-web.png` pesa 2,36 MB — **més que el "MASTER"** (1,83 MB). Un
actiu destinat a la botiga pública no pot ser el més pesat del joc; contradiu l'ús previst de
§1.6 i la divisió de responsabilitats de §6.8.3 (WordPress allotja contingut públic).

Condició de tancament: reexportar el PNG de web amb compressió adequada a la seva funció, o
descartar-lo i generar-ne un de nou.

### PO-3 — Marge de seguretat no verificat

§1.3 exigeix espai de seguretat igual a l'alçada de la "R" ×2 en totes direccions. La
inspecció d'aquest pas ha verificat mides, canal alfa i pes, però **no ha verificat el marge
de seguretat** contra el fitxer. No s'afirma que compleixi ni que incompleixi.

Condició de tancament: comprovació explícita del marge contra la mida de la "R" del logotip.

### PO-4 — Joc negre pendent

El joc negre està anunciat i encara no lliurat. `black/` existeix i és buida.

Condició de tancament: lliurament dels fitxers i verificació amb el mateix procediment
d'aquest document.

---

## 5. Convenció de noms

Patró aplicat als fitxers d'aquest repositori:

```
rlf-logo-[variant]-[colour]-[transparency]-[size].[ext]
rlf-logo-[variant]-[colour]-[size].[ext]          # sense alfa (JPG)
```

| Camp | Valors |
|---|---|
| `variant` | `a` (variants futures: `b`, `c`) |
| `colour` | `green`, `black`, `white`, `mono` |
| `transparency` | `transparent` quan el fitxer porta alfa; s'omet quan no en porta |
| `size` | `master`, `web` (si el nom ha de declarar píxels, `[size]-[px]px`) |
| `ext` | `png`, `jpg`, `svg` |

Tot en minúscules, amb guions, sense accents ni espais — perquè els URLs siguin segurs a
qualsevol host i perquè les variants futures s'incorporin sense tocar les existents.

**Nota:** la convenció reflecteix el **contingut real** del fitxer, no la seva intenció.
És per això que els fitxers d'aquí no porten `4096px` ni `2048px` al nom: cap dels quatre té
aquesta mida (PO-1).

---

## 6. Ús per context

| Context | Fitxer |
|---|---|
| Web, sobre piqué o color | `green/rlf-logo-a-green-transparent-web.png` (un cop resolt PO-2) |
| Web, fons clar pla | `green/rlf-logo-a-green-web.jpg` |
| Impressió | `green/rlf-logo-a-green-master.jpg` |
| Impressió amb fons variable | `green/rlf-logo-a-green-transparent-master.png` |

**Verificació prèvia a qualsevol publicació:** comprovar que la mida final no baixa dels
mínims de §1.3 (25 mm impremta / 70 px pantalla) i que el marge de seguretat es conserva.

---

*Tot el contingut normatiu d'aquest fitxer prové de §1.2–§1.3 del document mestre. Les dades
de fitxers són el resultat d'una inspecció directa dels bytes, declarada com a tal. Si hi ha
discrepància, mana el document mestre.*
