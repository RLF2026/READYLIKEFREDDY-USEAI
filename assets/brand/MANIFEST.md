# Lliurament AAA de logotip — inventari i verificació

Registre del lliurament `LOGO DELIVERY AAA` de READY LIKE FREDDY. Document derivat: tot el
contingut normatiu prové de §1.2–§1.3 del document mestre; les dades de fitxer són el resultat
d'una inspecció directa dels bytes, declarada com a tal.

---

## 1. Què conté el lliurament

Segons el seu propi README:

- **Dos jocs de color:** A (verd, tinta original `#056445`) i B (gris fosc neutre `#161616`).
- **Dos fons per cada joc:** fons blanc i fons transparent.
- **Textura:** l'empremta desgastada/sellada prové de la font carregada. El paper s'elimina als
  màsters transparents i es substitueix per blanc pur a les versions de fons blanc.
- **Formats:** PNG (màster sense pèrdua), JPG (màster de fons blanc / compatibilitat), WebP
  (web/app), TIFF (300 dpi impressió), PDF (exportació d'impressió 300 dpi), SVG (contenidor
  SVG d'alta resolució amb PNG sense pèrdua incrustat, que preserva la textura).
- **Vector:** no s'inclou cap vector de traçat. El README ho justifica i ho declara
  explícitament: un traçat automàtic forçat modificaria o destruiria la microtextura
  desgastada de la font, i per tant no seria fidel a AAA. L'SVG es diu explícitament
  `RASTER_PRESERVADA` i **no es presenta com a vector de traçat natiu**.
- **Mides:** 4096 px màster i 2048 px web. El README declara que la imatge d'origen feia
  1280 px d'amplada, i que per tant els màsters de 4096 px són reescalats d'alta qualitat,
  **no detall addicional inventat**.

**Valoració d'aquest registre:** la declaració del README sobre la naturalesa de l'SVG és
coherent amb R18 i R14 (no es presenta com a cosa que no és) i amb NO FAKES (§5.2.2). La
declaració que els màsters són reescalats i no detall inventat és exactament el que R2 i R5
demanen. Tot això queda registrat com a declaració del lliurament, no com a verificació
pròpia.

---

## 2. Convenció de noms AAA

`RLF_LOGO_[VERSION]_[COLOR]_[BACKGROUND]_[ROLE]_[SIZE/FORMAT]`

Aquesta convenció **substitueix** la que es va proposar inicialment en aquest repositori
(`rlf-logo-[variant]-[colour]...`). El document mestre no fixa cap convenció de noms
d'arxiu, així que la decisió és de governança i s'adopta la del lliurament.

Conseqüència per a l'arbre del repositori: les carpetes `assets/brand/green/` i
`assets/brand/black/` s'han de reorganitzar en quatre carpetes, una per joc i fons, amb els
noms originals del lliurament. Vegeu §6.

---

## 3. Inventari del manifest SHA-256

El lliurament aporta `SHA256_MANIFEST.txt` amb **29 entrades**: 24 fitxers repartits en quatre
carpetes, més el README, la previsualització i el propi manifest.

| Grup | Fitxers | Format |
|---|---|---|
| A_VERDE_FONDO_TRANSPARENTE | 6 | TIFF, PNG (màster 4096, web 2048), WebP, PDF, SVG |
| A_VERDE_FONDO_BLANCO | 7 | TIFF, JPG (màster 4096, web 2048), PNG (màster 4096, web 2048), WebP, PDF, SVG |
| B_NEGRO_FONDO_TRANSPARENTE | 6 | TIFF, PNG (màster 4096, web 2048), WebP, PDF, SVG |
| B_NEGRO_FONDO_BLANCO | 7 | TIFF, JPG (màster 4096, web 2048), PNG (màster 4096, web 2048), WebP, PDF, SVG |

Els hashes SHA-256 aportats queden registrats a `assets/brand/SHA256_MANIFEST.txt` i són la
identitat de referència dels fitxers, tant si els bytes arriben al repositori com si no.

---

## 4. Verificació directa — 11 fitxers

Aquests són els fitxers que han arribat al canal i s'han inspeccionat llegint-ne la capçalera i
els chunks. **Les dades són el resultat d'aquesta inspecció, no una transcripció del nom.**

### Joc A — verd

| Fitxer | Mides reals | Alfa | Pes |
|---|---|---|---|
| `A_VERDE_FONDO_TRANSPARENTE_MASTER_4096px.png` | 2000 × 1224 px | Sí — RGBA (colorType 6), sense `tRNS` | 1.828.434 B |
| `A_VERDE_FONDO_TRANSPARENTE_MASTER_4096px.jpg` | 2000 × 1224 px | No | 205.578 B |
| `A_VERDE_FONDO_TRANSPARENTE_WEB_2048px.png` | 2000 × 1224 px | Sí — RGBA (colorType 6), sense `tRNS` | 2.356.787 B |
| `A_VERDE_FONDO_TRANSPARENTE_WEB_2048px.jpg` | 2000 × 1224 px | No | 210.375 B |

### Joc B — fons blanc

| Fitxer | Mides reals | Alfa | Pes |
|---|---|---|---|
| `B_NEGRO_FONDO_BLANCO_MASTER_4096px.jpg` | 2000 × 1224 px | No | 298.843 B |
| `B_NEGRO_FONDO_BLANCO_MASTER_4096px.jpg` (variant) | 2000 × 1224 px | No | 296.999 B |
| `B_NEGRO_FONDO_BLANCO_MASTER_4096px.png` | 2000 × 1224 px | Sí — RGBA (colorType 6) | 1.317.380 B |
| `B_NEGRO_FONDO_BLANCO_WEB_2048px.jpg` | 2000 × 1224 px | No | 304.303 B |
| `B_NEGRO_FONDO_BLANCO_WEB_2048px.png` | 2000 × 1224 px | Sí — RGBA (colorType 6) | 1.357.570 B |

### Joc B — fons transparent

| Fitxer | Mides reals | Alfa | Pes |
|---|---|---|---|
| `B_NEGRO_FONDO_TRANSPARENTE_MASTER_4096px.png` | 2000 × 1224 px | Sí — RGBA (colorType 6), sense `tRNS` | 1.728.932 B |
| `B_NEGRO_FONDO_TRANSPARENTE_MASTER_4096px.jpg` | 2000 × 1224 px | No | 99.835 B |
| `B_NEGRO_FONDO_TRANSPARENTE_WEB_2048px.png` | 2000 × 1224 px | Sí — RGBA (colorType 6), sense `tRNS` | 1.822.735 B |
| `B_NEGRO_FONDO_TRANSPARENTE_WEB_2048px.jpg` | 2000 × 1224 px | No | 108.071 B |

### Previsualització

| Fitxer | Mides reals | Pes |
|---|---|---|
| `RLF_LOGO_AAA_4_VARIANTS_PREVIEW.jpg` | 2000 × 857 px | 299.095 B |

### PDFs

| Fitxer | Capçalera | `%%EOF` | Xifrat | Pàgines | Pes | Estat |
|---|---|---|---|---|---|---|
| `B_NEGRO_FONDO_TRANSPARENTE_PRINT_ON_WHITE_300dpi.pdf` | `%PDF-1.4` | Sí | No | 1 | 539.562 B | **Vàlid, llegit** |
| `B_NEGRO_FONDO_BLANCO_PRINT_300dpi.pdf` | `%PDF-1.4` | Sí | No | 1 | 539.532 B | **No llegible en aquest entorn** |

Els dos PDF tenen la mateixa estructura i 30 bytes de diferència. El segon no ha estat llegible
pel lector d'aquest entorn malgrat tenir capçalera, `%%EOF`, cap xifrat i una pàgina. Es
registra com a **no verificat**; no s'afirma que estigui malmès ni que estigui bé.

---

## 5. Punts oberts — ampliació

### PO-1 — Els noms declaren mides que no existeixen

**Els setze fitxers binaris verificats fan 2000 × 1224 px.** Cap fa 4096 px ni 2048 px. Els
noms ho diuen; el contingut no ho compleix. Afecta tots dos jocs i tots dos fons.

Context: el README declara que la font feia 1280 px i que els màsters són reescalats. El
desajustament, doncs, no és entre 1280 i 4096, sinó entre el nom i el resultat real.

Condició de tancament: o bé es reexporta a les mides que els noms declaren, o bé els noms
declaren la mida real. Governança decideix quina.

### PO-2 — El fitxer "WEB" és més pesat que el "MASTER"

Passa al joc A transparent (2,36 MB vs 1,83 MB) i al joc B transparent (1,82 MB vs 1,73 MB).
El rol declarat del fitxer de web és servir la botiga pública (§1.6, §6.8.3); un actiu que pesa
més que el màster no compleix el seu rol.

Condició de tancament: reexportar els PNG de web amb compressió adequada a la funció.

### PO-3 — Marge de seguretat no verificat

§1.3 exigeix espai de seguretat igual a l'alçada de la "R" ×2 en totes direccions. La inspecció
feta verifica mides, canal alfa i pes, però **no verifica el marge**. No s'afirma que es
compleixi ni que no.

Condició de tancament: comprovació explícita del marge contra la mida de la "R".

### PO-4 — El nom `FONDO_BLANCO` conviu amb canal alfa

Els PNG de `B_NEGRO_FONDO_BLANCO` tenen **canal alfa real** (colorType 6) tot i que el nom
diu fons blanc. Si el fons blanc ja és pintat, l'alfa és inert; si l'alfa és efectiu, el fons no
és blanc sinó transparent i el nom enganya. No es pot resoldre sense inspeccionar els píxels, i
aquest registre no ho fa.

Condició de tancament: inspecció de píxels que determini si el fons és blanc opac o
transparent, i correcció del nom o del fitxer segons el resultat.

### PO-5 — Previsualització amb composició defectuosa

A `RLF_LOGO_AAA_4_VARIANTS_PREVIEW.jpg`, l'etiqueta de la secció A es llegeix com dos textos
superposats ("FONDO BLANCO" i "FONDO TRANSPARENTE" pintats un damunt de l'altre). És un error
de composició del fitxer de previsualització, no de la marca ni dels logotips.

Condició de tancament: regenerar la previsualització.

### PO-6 — Estat de la variant B dins el sistema visual

**Decisió de governança pendent (Nivell 6).**

§1.2 defineix la identitat visual única com a *"piqué blanc cru amb elements no fotogràfics
resolts com a brodat tèxtil verd fosc"*, i §1.2.3 fixa la paleta amb el fil verd `#005C3F`.
La variant B (`#161616`) **no és verd**. Introduir-la és ampliar el sistema visual, i §5.2.11
exigeix que un canvi així tingui justificació sòlida, aprovació explícita, documentació
completa i comunicació clara.

Observació d'ús, registrada com a observació i no com a decisió: sobre fons fosc la variant B
té un contrast mínim entre traç i fons —a la versió transparent el logotip gairebé no es
llegeix—, de manera que la seva funció natural és sobre fons clar.

Condició de tancament: decisió de governança que registri si la variant B és un segon color
oficial del sistema o una variant perifèrica d'ús restringit, amb la justificació corresponent.

---

## 6. Estructura prevista al repositori

Per rebre el lliurament sencer amb la seva pròpia convenció de noms:

```
assets/brand/
├── MANIFEST.md
├── SHA256_MANIFEST.txt
├── README_RLF_LOGO_AAA.txt
├── A_VERDE_FONDO_TRANSPARENTE/
├── A_VERDE_FONDO_BLANCO/
├── B_NEGRO_FONDO_TRANSPARENTE/
└── B_NEGRO_FONDO_BLANCO/
```

Cada carpeta rep els seus 6 o 7 fitxers amb els noms originals del lliurament. Les carpetes
`green/` i `black/` creades anteriorment queden **superseded** per aquesta estructura i
s'eliminen quan el lliurament estigui carregat, per no tenir dues convencions vives alhora.

---

## 7. Nota sobre el canal de lliurament

El canal de xat accepta PNG, JPG i PDF. **No accepta TIFF, WebP ni SVG**, que són 20 dels 24
fitxers del lliurament. Aquests formats no poden arribar per aquesta via per cap mitjà, i la
seva absència aquí **no és cap incompliment del lliurament**.

Via correcta per a tots els binaris: la interfície web de GitHub, que accepta els sis formats.

---

*Document derivat. El contingut normatiu prové de §1.2–§1.3 i §5.2.11 del document mestre. Les
dades de fitxer són inspecció directa declarada. Si hi ha discrepància, mana el document mestre.*
