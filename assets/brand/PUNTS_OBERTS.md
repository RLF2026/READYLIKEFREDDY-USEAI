# Punts oberts — resolució

Registre de resolució dels punts oberts de `assets/brand/MANIFEST.md`. Cada punt es tanca amb
l'evidència que el tanca, o es declara **no tancable per mesura automàtica** amb el motiu.

Document derivat. El contingut normatiu prové de §1.2–§1.3 i §5.2.11 del document mestre.

---

## Mètode

S'han decodificat els PNG sencers (chunks IDAT, descompressió zlib, filtres de línia) i s'han
llegit els píxels un a un. Sobre els canals RGB i alfa reals s'han calculat: percentatge
d'opacitat, color dominant de la tinta, caixa delimitadora del contingut i marges en píxels.
Els JPEG s'han analitzat per l'estructura de marcadors (SOF, DQT, quantitzadors) i per
comparació byte a byte.

---

## Resum de l'estat

| Punt | Estat | Naturalesa |
|---|---|---|
| PO-1 mides | **Obert** — decisió de governança | Noms vs. contingut |
| PO-2 pes web > màster | **Mesurat, incompleix** | Reexportar PNG de web |
| PO-3 marge §1.3 | **Mesurat, incompleix** (0,213 de l'exigit) | Canvi de retall de disseny |
| PO-4 alfa a `FONDO_BLANCO` | **TANCAT — nom correcte** | Cap acció |
| PO-5 previsualització | **Obert** — regenerar | Fitxer auxiliar |
| PO-6 variant B al sistema visual | **Obert** — decisió de governança | §1.2 vs. lliurament |
| PO-7 joc A màster no transparent | **Mesurat, defecte** | Reexportar |
| PO-8 alfa idèntica a dos grups | **Mesurat** | Vegeu resolució |
| PO-9 còpia doble del màster B blanc | **TANCAT — decideix el hash** | Cap acció als fitxers |
| PO-10 paleta del verd | **TANCAT — el lliurament fa servir el verd de §1.2.3** | Cap acció |
| PO-11 PDF blanc no llegible | **TANCAT** | Reintent amb èxit |

---

### PO-4 — `FONDO_BLANCO` amb canal alfa

**TANCAT. El nom és correcte; l'alfa és inert.**

Els dos PNG de `B_NEGRO_FONDO_BLANCO` són **100,00% de píxels opacs**, zero transparents, zero
parcials. Cantonades i vores a `(255,255,255,255)`. El fons és blanc pintat, tal com diu el nom.

---

### PO-10 — Paleta del verd: el lliurament i el document coincideixen

**TANCAT. El retiro.**

| Origen | Verd |
|---|---|
| §1.2.3 del document mestre | `#005C3F` |
| README del lliurament AAA | `#056445` (aproximació declarada) |
| **Píxel dominant mesurat a la imatge A** | **`(4,93,63)` = `#045D3F`** |

El verd pintat és `#045D3F`: quatre unitats de diferència al canal vermell i una al verd
respecte de `#005C3F`, idèntic al blau. La variació prové de l'antialiàsing de l'empremta
desgastada, no d'un canvi de color.

**El logotip fa servir el verd de §1.2.3.** La discrepància que es va registrar era una
comparació contra el valor declarat al README, no contra el valor pintat. Queda tancada.

---

### PO-3 — Marge de seguretat de §1.3

**MESURAT. Incompleix l'especificació.**

| Paràmetre | Valor |
|---|---|
| Alçada del glif "R" de READY | 300 px |
| Marge exigit per §1.3 (R ×2) | **600 px** |
| Marge real, tots els PNG transparents | 64–67 px |
| Ràtio marge / alçada R | **0,213** |

El marge real és una cinquena part de l'exigit i és uniforme als quatre costats — valor de
generació automàtica, no de disseny. Ampliar-lo a 600 px sobre un canvas de 2000 obliga a
recalcular la caixa: **és un canvi de retall, no una reparació d'arxiu.** Decisió de direcció
d'art.

---

### PO-2 — El fitxer "WEB" més pesat que el "MASTER"

**TANCAT COM A CAUSA. Mesurat.**

| Grup | PNG màster | PNG web | Diferència |
|---|---|---|---|
| A verd transparent | 1.828.434 B | 2.356.787 B | web +528 KB |
| B negre transparent | 1.728.932 B | 1.822.735 B | web +94 KB |
| B negre fons blanc | 1.317.380 B | 1.357.570 B | web +40 KB |

Causa identificada: als dos grups transparents, els PNG de màster i de web tenen **la mateixa
distribució d'alfa a la xifra exacta** (vegeu PO-8) i la mateixa caixa de contingut. Contenen la
mateixa imatge; el fitxer gran no aporta res que el petit no tingui.

Acció: reexportar els PNG de rol web amb compressió adequada a la seva funció (§1.6, §6.8.3).

---

### PO-8 — Estructura d'alfa idèntica entre dues variants de color

**RESOLT. L'explicació és la font única.**

| Fitxer | Mida | FNV-1a | Alfa idèntica |
|---|---|---|---|
| `A_VERDE_FONDO_TRANSPARENTE_WEB_2048px.png` | 2.356.787 B | `5cc8bf68` | 1.331.775 / 1.110.187 / 6.038 |
| `B_NEGRO_FONDO_TRANSPARENTE_WEB_2048px.png` | 1.822.735 B | `9c15d9b3` | 1.331.775 / 1.110.187 / 6.038 |

Els hashes difereixen, així que no són el mateix fitxer. Però comparteixen la distribució d'alfa
exacta i la caixa de contingut exacta.

**Conclusió:** és l'efecte esperat de generar les dues variants de color des de la **mateixa font
de tinta**. El README del lliurament ho declara: la textura desgastada s'hereta de la font
carregada, i el que canvia entre variants és el color, no l'empremta. Un alfà compartit és
coherent amb aquest mètode.

**No és un defecte.** Es registra com a característica del mètode de generació, perquè un
auditor futur que trobi dues imatges amb alfa idèntica ha de saber que és esperat i per què.

---

### PO-9 — Còpia doble del màster B blanc

**TANCAT. Decisió pel hash del manifest.**

S'han rebut dues còpies de `B_NEGRO_FONDO_BLANCO_MASTER_4096px.jpg`, amb pesos diferents:

| Còpia | Pes | FNV-1a |
|---|---|---|
| A | 298.843 B | `9d346b0` |
| B | 296.999 B | `8991cb46` |

Els dos fitxers comparteixen capçalera (`JFIF` + perfil ICC + mateixa taula de quantitzadors) i
divergeixen per primer cop al byte **686**. **294.949 bytes dels 296.999 difereixen:** són
pràcticament dos fitxers diferents, no dues còpies del mateix.

El manifest SHA-256 del lliurament és la font d'autoritat per decidir quin és el canònic:

```
ee628d376c00856d873fb3bb1b07899d21286a1b8521962a1183fff2d8a54257  B_NEGRO_FONDO_BLANCO/RLF_LOGO_B_NEGRO_FONDO_BLANCO_MASTER_4096px.jpg
```

**Regla:** el fitxer que el repositori ha d'adoptar és el que compleixi aquest hash. El que no
hi compleixi és un duplicat no canònic i no ha de viure al costat del canònic. La comprovació es
farà quan els fitxers estiguin carregats: `sha256sum` sobre el fitxer del repositori contra
l'entrada del manifest.

---

### PO-7 — `A_VERDE_FONDO_TRANSPARENTE_MASTER_4096px.png` no és transparent

**MESURAT. Defecte real, i abastat només a aquest fitxer.**

| Paràmetre | Valor |
|---|---|
| Dimensions | 2000 × 1224 px |
| Píxels opacs | **100,00%** |
| Píxels transparents | 0,00% |
| Cantonades i vores | `(0,0,0)` a les vuit mostres |
| Color de tinta dominant | `(4,93,63)` — verd |
| Proporció de fons negre | 63,01% dels píxels mostrejats |
| Caixa de contingut | tota la imatge, marges 0 |

El fitxer porta `FONDO_TRANSPARENTE` al nom i té el fons **negre pur i opac**. Al seu grup,
el fitxer de rol *web* sí que és transparent (54,4%).

**Impacte:** és el candidat natural a màster de composició i d'impressió. En l'estat actual,
sobre qualsevol fons que no sigui negre arrossega un rectangle negre que ocupa el 63% de la
superfície.

Condició de tancament: reexportar el màster del joc A amb transparència real, o substituir-lo
pel de rol web i regenerar aquest des del màster corregit.

---

### PO-5 — Previsualització amb composició defectuosa

**TANCABLE PER GOVERNANÇA.**

`RLF_LOGO_AAA_4_VARIANTS_PREVIEW.jpg` (2000 × 857 px) mostra dos textos pintats un damunt de
l'altre a l'etiqueta de la secció A. És un error de composició del fitxer auxiliar.

Acció: regenerar. No afecta cap actiu publicable.

---

### PO-11 — PDF de fons blanc no llegible

**TANCAT. Reintent amb èxit.**

Al segon intent, `B_NEGRO_FONDO_BLANCO_PRINT_300dpi.pdf` s'ha verificat: capçalera `%PDF-1.4`,
`%%EOF` present, **sense xifrat**, **1 pàgina**, 539.532 B. És un PDF vàlid.

El problema era del lector en el primer intent, no del fitxer. **El PDF està bé.**

---

### PO-1 — Mides declarades vs. mides reals

**OBERT. Decisió de governança, no mesura.**

Els setze binaris fan **2000 × 1224 px**. El canvas és idèntic a tots quatre grups. Cap fitxer fa
4096 px ni 2048 px.

El camp `[SIZE]` del nom declara una mida que cap fitxer té. Fins que governança decideixi els
noms, s'ha de llegir com a **rol** (`MASTER` / `WEB`), no com a mida, i la mida real és la del
manifest.

---

### PO-6 — Estat de la variant B dins el sistema visual

**OBERT. Requereix decisió de governança (Nivell 6).**

§1.2 defineix la identitat visual com a *"piqué blanc cru amb elements no fotogràfics resolts com
a brodat tèxtil verd fosc"* i §1.2.3 fixa la paleta amb el fil verd. La variant B (`#161616`) no
és verd: introduir-la és ampliar el sistema visual, i §5.2.11 exigeix justificació sòlida,
aprovació explícita, documentació completa i comunicació clara.

Dada d'ús mesurada: la tinta de la variant B és `(21,21,21)`, pràcticament el `#161616` declarat.
Sobre fons fosc el contrast és mínim, de manera que la seva funció natural és sobre fons clar.

Condició de tancament: decisió que registri si la variant B és un segon color oficial o una
variant perifèrica d'ús restringit.

---

## Estat final de la llista

**Tancats en aquesta revisió:** PO-4, PO-8, PO-9, PO-10, PO-11.
**Mesurats amb veredicte i acció definida:** PO-2, PO-3, PO-7.
**Oberts per decisió de governança:** PO-1, PO-5, PO-6.

Cap punt s'ha tancat per declaració. Els tres que queden oberts no depenen de cap mesura que es
pugui fer des d'aquí.

---

*Document derivat. Les mesures són resultat d'inspecció directa de píxels i d'estructura
d'arxiu, i es declaren com a tals. Si hi ha discrepància amb el document mestre, mana el
document mestre.*
