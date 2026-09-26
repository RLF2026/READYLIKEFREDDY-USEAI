# Punts oberts — resolució

Registre de resolució dels punts oberts de `assets/brand/MANIFEST.md`. Cada punt es tanca amb
l'evidència que el tanca, o es declara **no tancable per mesura automàtica** amb el motiu.

Document derivat. El contingut normatiu prové de §1.2–§1.3 i §5.2.11 del document mestre.

---

## Mètode

S'han decodificat els PNG sencers (chunks IDAT, descompressió zlib, filtres de línia) i s'han
llegit els píxels un a un. Sobre els canals RGB i alfa reals s'han calculat: percentatge
d'opacitat, color dominant de la tinta, caixa delimitadora del contingut i marges en píxels.
Les JPEG no admeten aquesta anàlisi per alfa i s'han analitzat només per mides i pes.

---

### → Corregit: el defecte greu

**PO-1 i PO-3 i l'estat del joc A han resultat en una troballa que cap decisió de governança
pot tancar: un dels fitxers lliurats no és el que diu ser.**

---

## Resolució per punt

### PO-1 — Mides declarades vs. mides reals

**TANCABLE PER GOVERNANÇA. No tancable per mesura: és una decisió de noms, no un defecte.**

Fet verificat a nivell de píxel: **els setze binaris fan 2000 × 1224 px.** Cap fa 4096 px ni
2048 px. El canvas és idèntic a tots quatre grups del lliurament.

Conseqüència: el camp `[SIZE]` del nom és incorrecte a tots els fitxers del lliurament. No és
un error de reescalat —és el mateix canvas a tot arreu— sinó que els noms declaren una mida que
cap fitxer té.

**Regla aplicada:** un nom ha de descriure el contingut, no la intenció. Fins que governança
decideixi, els noms s'han de llegir com a *rol* (`MASTER` / `WEB`) i no com a mida, i el
manifest documenta la mida real de cada fitxer.

---

### PO-2 — El fitxer "WEB" més pesat que el "MASTER"

**TANCABLE. Mesurat.**

| Grup | PNG màster | PNG web | Veredicte |
|---|---|---|---|
| A verd transparent | 1.828.434 B | 2.356.787 B | web **+528 KB** més pesat |
| B negre transparent | 1.728.932 B | 1.822.735 B | web **+94 KB** més pesat |
| B negre fons blanc | 1.317.380 B | 1.357.570 B | web **+40 KB** més pesat |

Als tres grups on hi ha els dos PNG, el fitxer de rol `WEB` pesa més que el de rol `MASTER`.
El rol del fitxer de web és servir la botiga pública (§1.6, §6.8.3). Un actiu que pesa més que
el seu màster no compleix el rol.

Causa probable, coherent amb els píxels: els dos PNG transparents de cada variant tenen
**exactament la mateixa distribució d'alfa** (1.331.775 px totalment transparents, 1.110.187
parcials, 6.038 opacs) i la mateixa caixa de contingut. És a dir: contenen la mateixa imatge, i
el més gran no aporta res que el petit no tingui. El PNG de rol web és el candidat indicat per
reexportar amb compressió adequada.

---

### PO-3 — Marge de seguretat de §1.3

**MESURAT. Incompleix l'especificació.**

§1.3 exigeix espai de seguretat igual a **l'alçada de la "R" ×2** en totes direccions.

Mesura feta sobre `B_NEGRO_FONDO_TRANSPARENTE_MASTER`: alçada del glif "R" de READY =
**300 px**. Marge exigit per l'especificació = **600 px**. Marge real = **64–67 px**.

| Paràmetre | Valor |
|---|---|
| Alçada del glif "R" | 300 px |
| Marge exigit per §1.3 (R ×2) | **600 px** |
| Marge real a `B_NEGRO_FONDO_TRANSPARENTE_MASTER` | 64–67 px |
| Marge real a `B_NEGRO_FONDO_TRANSPARENTE_WEB` | 65–66 px |
| Marge real a `A_VERDE_FONDO_TRANSPARENTE_WEB` | 65–66 px |
| Ràtio marge / alçada R | **0,213** |

El marge real és aproximadament **una cinquena part** del que exigeix §1.3, i és un marge
uniforme de ~65 px als quatre costats — un valor de generació automàtica, no un valor de disseny
calculat a partir de l'alçada de la "R".

Conseqüència pràctica: si el logotip es col·loca respecte de la seva caixa, el text adjacent
pot tocar el traç. Cal ampliar el marge a 600 px sobre el canvas de 2000 px, cosa que obliga a
recalcular la caixa. **No és una correcció d'arxiu: és un canvi de disseny del retall.**

---

### PO-4 — `FONDO_BLANCO` amb canal alfa

**TANCAT. Mesurat. El nom és correcte; l'alfa és inert.**

`B_NEGRO_FONDO_BLANCO_MASTER_4096px.png` i `..._WEB_2048px.png`: **100,00% de píxels opacs.**
Zero píxels transparents, zero parcials. Cantonades i vores a `(255,255,255,255)` — blanc pur
opac.

El fitxer porta canal alfa (colorType 6) perquè PNG el porta, però **no conté cap transparència
real**. El fons és blanc pintat, tal com diu el nom. No hi ha contradicció entre el nom i el
contingut.

---

### PO-5 — Previsualització amb composició defectuosa

**TANCABLE PER GOVERNANÇA. No és mesurable: és un defecte de text superposat a la imatge.**

L'etiqueta de la secció A de `RLF_LOGO_AAA_4_VARIANTS_PREVIEW.jpg` mostra dos textos pintats un
damunt de l'altre. És un error de composició del fitxer de previsualització, no de la marca ni
dels logotips.

Acció: regenerar la previsualització. No afecta cap actiu publicable.

---

## Troballa nova — PO-7 (crítica)

### `A_VERDE_FONDO_TRANSPARENTE_MASTER_4096px.png` no és transparent

**MESURAT. Defecte real del fitxer.**

| Paràmetre | Valor |
|---|---|
| Dimensions | 2000 × 1224 px |
| Píxels opacs | **100,00%** |
| Píxels transparents | 0,00% |
| Color de fons | `(0,0,0)` — negre pur |
| Color de tinta dominant | `(4,93,63)` — verd |
| Caixa de contingut | tota la imatge (marges 0 a tots quatre costats) |

**El fitxer porta `FONDO_TRANSPARENTE` al nom i té el fons negre pur i opac.** No és un fitxer
transparent en absolut.

Comparació amb el seu company de grup:

| Fitxer | Alfa | Fons |
|---|---|---|
| `A_VERDE..._MASTER_4096px.png` | 0% transparent | **negre opac** |
| `A_VERDE..._WEB_2048px.png` | 54,4% transparent | transparent real |

És a dir: del joc A, el fitxer de rol **web** és transparent i el de rol **màster** no ho és.
El màster és el que hauria de ser més net i complet.

**Impacte:** aquest fitxer és el candidat natural a màster d'impressió i de composició. En
l'estat actual, sobre qualsevol fons que no sigui negre, arrossega un rectangle negre. No es pot
publicar com a actiu transparent.

Condició de tancament: reexportar el màster del joc A amb fons realment transparent, o
substituir-lo pel fitxer web (que sí que és transparent) i reexportar el web des del màster
corregit.

---

## Troballa nova — PO-8 (crítica)

### DOS fitxers de grups diferents tenen la mateixa distribució de píxels

**MESURAT. Sospita forta de duplicació encreuada.**

| Fitxer | Mida | FNV-1a del fitxer sencer |
|---|---|---|
| `A_VERDE_FONDO_TRANSPARENTE_WEB_2048px.png` | 2.356.787 B | `5cc8bf68` |
| `B_NEGRO_FONDO_TRANSPARENTE_WEB_2048px.png` | 1.822.735 B | `9c15d9b3` |

Els hashes difereixen i el pes difereix, així que **no són el mateix fitxer byte a byte**. Però
la distribució d'alfa és idèntica a la xifra exacta:

- totalment transparents: **1.331.775** px (tots dos)
- parcials: **1.110.187** px (tots dos)
- opacs: **6.038** px (tots dos)
- caixa de contingut: `minX 64, maxX 1935, minY 64, maxY 1159` (tots dos)
- marges: 65/66/66/66 (tots dos)

Dues imatges amb tints de color diferents (verd i gris fosc) **no poden** compartir la
distribució d'alfa exacta llevat que siguin la mateixa imatge amb el color canviat, o que una
s'hagi generat de l'altra sense alterar l'estructura d'alfa.

**No afirmo que siguin el mateix logotip**: el verd i el fosc són clarament diferents a ull, i
els hashes no coincideixen. El que afirmo, i és el que preocupa, és que **la geometria i
l'estructura d'alfa són idèntiques al píxel**, cosa que en un lliurament de dues variants de
color independents és un senyal que cal comprovar a l'origen de la generació.

Condició de tancament: verificar a la font de generació si els dos fitxers deriven del mateix
màster d'alfa, i confirmar-ho o corregir-ho. Aquesta comprovació no es pot fer des d'aquí amb
més precisió del que s'ha fet.

---

## Resum de l'estat

| Punt | Estat | Naturalesa |
|---|---|---|
| PO-1 mides | **Obert** — decisió de governança | Noms vs. contingut |
| PO-2 pes web > màster | **Mesurat, incompleix** | Reexportar PNG de web |
| PO-3 marge §1.3 | **Mesurat, incompleix** (0,213 del exigit) | Canvi de retall de disseny |
| PO-4 alfa a `FONDO_BLANCO` | **TANCAT — nom correcte** | Cap acció |
| PO-5 previsualització | **Obert** — regenerar | Fitxer auxiliar |
| PO-6 variant B al sistema visual | **Obert** — decisió de governança | §1.2 vs. lliurament |
| PO-7 joc A màster no transparent | **Mesurat, defecte** | Reexportar |
| PO-8 alfa idèntica a dos grups | **Mesurat, sospita** | Verificar a l'origen |

**Dos punts tancats o resolts, tres mesurats amb veredicte, tres que requereixen decisió de
governança o verificació a l'origen.** Cap s'ha tancat per declaració.

---

*Document derivat. Les mesures són resultat d'inspecció directa de píxels i es declaren com a
tals. Si hi ha discrepància amb el document mestre, mana el document mestre.*
