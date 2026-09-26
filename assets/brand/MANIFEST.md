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

## 3. Discrepància de paleta — verd del lliurament vs. verd del document

**MESURAT a nivell de píxel.**

El lliurament AAA declara la variant A com a verd `#056445`. La paleta oficial de §1.2.3 fixa el
fil verd principal a **`#005C3F`**.

| Origen | Verd | Delta |
|---|---|---|
| §1.2.3 del document mestre | `#005C3F` | referència |
| README del lliurament AAA | `#056445` | declarat pel lliurament |
| **Píxel dominant a la imatge A** | **`(4,93,63)` = `#045D3F`** | mesurat |

El píxel dominant és `#045D3F`, que és pràcticament `#005C3F` (diferència de 4 unitats al canal
vermell, 1 al verd, idèntic al blau). La diferència ve de la textura desgastada: el verd pla
`#005C3F` apareix barrejat amb vores més fosques per l'antialiàsing de l'empremta.

**Conclusió:** el logotip SÍ que fa servir el verd de §1.2.3. El valor `#056445` del README és
una aproximació declarada, no el valor pintat. No hi ha discrepància de fons entre el lliurament
i el document en aquest punt.

**Acció:** cap. El registre queda tancat en aquest punt.

---

## 4. Joc A — verd

### 4.1 Fons transparent

| Fitxer | Mides reals | Alfa | Pes | Estat |
|---|---|---|---|---|
| `..._MASTER_4096px.png` | 2000 × 1224 | **0% transparent — fons NEGRE OPAC** | 1.828.434 B | **DEFECTUÓS (PO-7)** |
| `..._MASTER_4096px.jpg` | 2000 × 1224 | No | 205.578 B | OK per al seu rol |
| `..._WEB_2048px.png` | 2000 × 1224 | 54,4% transparent | 2.356.787 B | **Massa pesat (PO-2)** |
| `..._WEB_2048px.jpg` | 2000 × 1224 | No | 210.375 B | OK per al seu rol |

### 4.2 Fons blanc

**Cap fitxer rebut.** Els 7 fitxers del grup `A_VERDE_FONDO_BLANCO` existeixen al manifest
SHA-256 però no han arribat pel canal (vegeu §7).

---

## 5. Joc B — gris fosc / negre

### 5.1 Fons transparent

| Fitxer | Mides reals | Alfa | Pes | Tinta dominant |
|---|---|---|---|---|
| `..._MASTER_4096px.png` | 2000 × 1224 | 55,6% transparent | 1.728.932 B | `(21,21,21)` |
| `..._MASTER_4096px.jpg` | 2000 × 1224 | No | 99.835 B | — |
| `..._WEB_2048px.png` | 2000 × 1224 | 54,4% transparent | 1.822.735 B | `(21,21,21)` |
| `..._WEB_2048px.jpg` | 2000 × 1224 | No | 108.071 B | — |

La tinta dominant mesurada és `(21,21,21)` = `#151515`, pràcticament el `#161616` declarat al
README. La declaració del lliurament és correcta.

### 5.2 Fons blanc

| Fitxer | Mides reals | Alfa | Pes |
|---|---|---|---|
| `..._MASTER_4096px.png` | 2000 × 1224 | 100% opac (blanc pur) | 1.317.380 B |
| `..._MASTER_4096px.jpg` | 2000 × 1224 | No | 298.843 B |
| `..._MASTER_4096px.jpg` (2a còpia) | 2000 × 1224 | No | 296.999 B |
| `..._WEB_2048px.png` | 2000 × 1224 | 100% opac (blanc pur) | 1.357.570 B |
| `..._WEB_2048px.jpg` | 2000 × 1224 | No | 304.303 B |

---

## 6. Previsualització i PDFs

| Fitxer | Mides / Estat | Pes |
|---|---|---|
| `RLF_LOGO_AAA_4_VARIANTS_PREVIEW.jpg` | 2000 × 857 px, amb dos textos superposats (PO-5) | 299.095 B |
| `B_NEGRO_FONDO_TRANSPARENTE_PRINT_ON_WHITE_300dpi.pdf` | 1 pàgina, sense xifrar | 539.562 B |
| `B_NEGRO_FONDO_BLANCO_PRINT_300dpi.pdf` | 1 pàgina, sense xifrar | 539.532 B |

---

## 7. Canal de lliurament — límit important

El canal de xat accepta **PNG, JPG i PDF**. **No accepta TIFF, WebP ni SVG.**

Dels 24 fitxers binaris del manifest SHA-256, **16 no poden arribar per aquesta via** (8 TIFF,
8 WebP) i 4 més (SVG) tampoc. La seva absència aquí **no és cap incompliment del lliurament**.

Via correcta per a tots els binaris: la interfície web de GitHub.

---

## 8. Convenció de noms AAA

`RLF_LOGO_[VERSION]_[COLOR]_[BACKGROUND]_[ROLE]_[SIZE/FORMAT]`

Adoptada del lliurament. Substitueix la convenció inicial d'aquest repositori. El document
mestre no fixa cap convenció de noms d'arxiu: la decisió és de governança.

**Advertiment de lectura:** el camp `[SIZE]` **no descriu el contingut real** de cap fitxer
(PO-1). Fins que es corregeixi, s'ha de llegir com a declaració de la intenció de reescalat, no
com a mida. La mida real és 2000 × 1224 px a tots els fitxers.

---

## 9. Estructura prevista al repositori

```
assets/brand/
├── MANIFEST.md
├── PUNTS_OBERTS.md
├── SHA256_MANIFEST.txt
├── README_RLF_LOGO_AAA.txt
├── A_VERDE_FONDO_TRANSPARENTE/
├── A_VERDE_FONDO_BLANCO/
├── B_NEGRO_FONDO_TRANSPARENTE/
└── B_NEGRO_FONDO_BLANCO/
```

Les carpetes `green/` i `black/` creades anteriorment queden **superseded** per aquesta
estructura.

---

*Document derivat. Les dades de fitxer són inspecció directa declarada. Els punts oberts i les
seves resolucions són a `PUNTS_OBERTS.md`. Si hi ha discrepància, mana el document mestre.*
