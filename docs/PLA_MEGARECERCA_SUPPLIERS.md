# Pla de la megarecerca — 10.000 proveïdors VALIDATS

Document derivat de **§3.3** (motor de sourcing), **§3.3.8** (elegibilitat),
**§3.3.12** (gate i definició de VALIDAT), **§3.3.13–§3.3.15** (priorització,
descoberta creuada i frescor), **§7.8.A** (producció de dades preinauguració) i
**§2.4.3** (regles de cortesia) del document mestre canònic v2.6.0.

**Naturalesa d'aquest document.** És un pla d'execució, no una regla nova. Cap
criteri d'aquest document no és meu: tots són transcripcions del document mestre.
Si hi ha discrepància, mana el document mestre (§0.1).

---

## 1. Quan s'engega, i per què no és una fase

La recerca **no és cap de les onze fases**. §7.8.A la defineix com una **línia
d'execució paral·lela**:

> *"Aquesta línia s'executa en paral·lel després que les Fases 2–6 proporcionin
> els components necessaris."*

I R16 ho confirma:

> *"La producció de Suppliers i KB s'executa en paral·lel tan aviat com
> existeixen els components necessaris. No cal acabar un actiu abans de començar
> l'altre."*

**Conseqüència operativa:** la recerca de proveïdors es pot engegar tan bon punt
les fases 2, 3 i 4 estiguin completes. La Fase 2 ja ho està; falten la 3
(pipeline) i la 4 (sistema de producte).

| Component necessari | Fase | Estat |
|---|---|---|
| Lanes, Laurel Ledger, orquestrador, workers, cua | 2 | Complet |
| Pipeline de vuit etapes | 3 | Pendent |
| Identitat canònica i normalització en 5 idiomes | 4 | Pendent |
| KB i Visor forense | 5, 6 | No necessaris per a aquesta recerca |

---

## 2. L'objectiu, amb la seva xifra exacta

**`supplier_prelaunch_validated >= 10000`** (§3.3.12).

Regla literal del document, i no admet interpretació:

> *"'gairebé 10.000' o 'gairebé 15.000' no és un estat admissible de
> preinauguració."*

I **VALIDAT no és descobert, ni HOLD, ni elegible provisional.** El comptador
només incrementa quan la transacció de persistència i totes les validacions han
estat confirmades.

---

## 3. La definició de VALIDAT — els quinze elements de §3.3.12

Un venedor compta per al mínim **només quan té a la base SQL** els quinze
elements següents. Si en falta un, queda en HOLD i **no compta**.

| # | Element | Com es verifica |
|---|---|---|
| 1 | Identitat canònica única | Clau canònica construïda i deduplicada globalment |
| 2 | Domini propi | El venedor té botiga pròpia, no un perfil de marketplace |
| 3 | País i ciutat o zona | Dada territorial registrada |
| 4 | Pertinença UE-27 | Codi de país dins els 27; Regne Unit exclòs |
| 5 | Activitat professional de segona mà | Negoci identificable amb activitat sostinguda |
| 6 | Criteri de marca complert | Fred Perry, o marca afina de la llista (§3.3.8 punt 5) |
| 7 | Compra pública verificable | Navegació/cistella/checkout **sense comprar ni gastar** |
| 8 | Condicions documentades | Política de devolucions i costos d'enviament visibles |
| 9 | Compatibilitat de monitoratge | `robots.txt` no prohibeix el monitoratge de producte |
| 10 | Font principal | Origen de la descoberta registrat |
| 11 | Data de verificació | Timestamp de la comprovació |
| 12 | Snapshot o hash d'evidència | Captura o hash de la pàgina verificada |
| 13 | Decisió ELEGIBLE | Resultat de l'avaluació dels vuit criteris de §3.3.8 |
| 14 | Deduplicació PASS | Cap duplicat global: una empresa no compta dues vegades |
| 15 | Auditoria persistent | Registre de qui i quan ho ha verificat |

**La prova de compra pública (element 7) és el punt més delicat.** El document
diu literalment que és *"una comprovació de navegació/cistella/checkout que no
obliga a comprar ni gastar diners"*. Si no es pot completar, el venedor queda en
HOLD. És una comprovació d'accessibilitat, no una transacció.

---

## 4. Els vuit criteris d'elegibilitat de §3.3.8

Acumulatius: calen tots vuit. Les decisions davant de dubte:

| Criteri | Contingut | Davant de dubte |
|---|---|---|
| 1 | Professional: negoci identificable, activitat sostinguda, botiga pròpia | Dada absent, HOLD |
| 2 | UE-27, Regne Unit exclòs | Fora del perímetre, REJECT |
| 3 | Segona mà com a activitat | Dada absent, HOLD |
| 4 | No és marketplace generalista | eBay, Wallapop, Vinted i equivalents, REJECT |
| 5 | Fred Perry o marca afina de la llista | Marca similar no llistada, **HOLD i decisió humana** |
| 6 | Compra pública sense relació | No verificable, HOLD |
| 7 | Condicions publicades | Falta política o enviament, HOLD |
| 8 | `robots.txt` permet monitoratge | No llegible, HOLD (fail-closed) |

**Criteri 5, la distinció que importa.** §3.3.8 diu que aquest criteri *"limita
l'univers de descoberta de proveïdors; no amplia en cap cas el catàleg
comercial"*. I OP-003 ho tanca: les marques afins *"mai entren al catàleg
comercial, ni a la Knowledge Base de productes venibles, ni al circuit de
venda"*.

**Per tant:** un venedor amb Stone Island però sense Fred Perry **es valida com a
venedor**. Si en una remesa futura rep Fred Perry, ja és dins del registre i les
seves peces entren al pipeline normal. El seu producte no-Fred-Perry no entra mai
al catàleg.

Llista de marques afins admeses (§3.3.8 punt 5): Stone Island, CP Company, Lyle &
Scott, Diadora, Sergio Tacchini, Fila, Lonsdale, Ben Sherman, Peaceful Hooligan
*i similars*. La llista es pot ampliar per decisió humana (Nivell 6).

---

## 5. L'estructura de la recerca

### 5.1 Les 2.700 unitats territorials

§3.3.9: **100 localitats per 27 estats UE, o sigui 2.700 unitats**. Totes
independents, totes posables en cua alhora. **Els 27 països poden tenir treball
actiu simultàniament**, subjecte a la capacitat real de workers i a les regles de
cortesia per domini.

Cada unitat porta: país, localitat, conjunt de consultes, cursor, estat
d'esgotament, resultats, fonts consultades, errors, checkpoint i darrera
actualització.

### 5.2 La unitat i la seva lane

§3.3.2: **país, regió, ciutat, conjunt de cerques, lane, resultat**. L'assignació
de lane és determinista per la fórmula de §3.3.4, i **dues lanes no consumeixen
mai el mateix espai de treball** (§3.3.6).

### 5.3 La metodologia d'esgotament

§3.3.3, literal: *"una ciutat es considera explorada quan ha completat el
protocol de cerques, **amb independència dels resultats**."*

Una cerca que no troba res **compta igual** que una que en troba vint. El que es
mesura és el protocol completat, no el rendiment.

### 5.4 El protocol de cerques per unitat

El document fixa l'estructura però no enumera les cerques concretes. El protocol
s'ha de definir i registrar, i totes les unitats han de seguir el mateix patró
(per això el mòdul calcula una empremta SHA-256 del protocol).

**Eixos de cerca que el document obliga a cobrir** (§3.3.8 punts 3 i 5, §3.3.14):

| Eix | Cerques |
|---|---|
| Terme de producte | *fred perry*, *fred perry vintage*, *fred perry preloved*, *fred perry second hand* |
| Categoria | *polo fred perry*, *harrington fred perry*, *track jacket fred perry*, *fred perry knitwear* |
| Condició | *second hand*, *preloved*, *vintage*, *used* |
| Idioma local | Equivalent en l'idioma del país (CA, ES, EN, FR, DE i els altres) |

**Canal addicional de §3.3.14 (OP-024, TANCAT):** cada `factory_id` amb estat
`VERIFIED_ACTIVE` o `VERIFIED_HISTORICAL` al Factory Registry alimenta un canal de
descoberta creuada, amb cerques dirigides pel nom de la fàbrica, el model i el
`manufacturing_country`. Aquest canal **complementa, no substitueix** la cobertura
geogràfica, i els seus resultats entren pel mateix pipeline i queden subjectes als
mateixos criteris. Un venedor trobat per aquesta via **no rep cap tracte
diferenciat**.

---

## 6. L'ordre de consum — priorització dinàmica

§3.3.13 (OP-023, TANCAT). Cada unitat territorial porta la seva **cota inferior de
confiança de Wilson al 95%**, recalculada després de cada lot de resultats. Els
workers disponibles s'assignen primer a les unitats amb cota més alta i cursor no
esgotat.

**Condició de canvi de prioritat, ratificada pel propietari i transcrita
literalment:** *"el consum només es desplaça cap a la unitat territorial següent en
ordre de cota de Wilson un cop el cursor de la unitat (o del grup d'unitats) de
prioritat superior queda esgotat; mai s'abandona una unitat amb cursor actiu per
prioritzar-ne una altra només per rendiment puntual."*

**Objectiu d'aquesta regla:** reduir el temps fins a 10.000 VALIDATS **sense
relaxar cap criteri d'elegibilitat i sense saltar-se cap unitat**.

### La planificació de volum

§3.3.12:

```
p_hat = x / n
p_Wilson_lower = cota inferior de Wilson al 95%
candidats_requerits = ceil((10000 - VALIDATS_actuals) / max(p_Wilson_lower, epsilon))
```

**Aquesta xifra és un pressupost de treball, no un gate.** Si `p_Wilson_lower` és
molt baix, el sistema **amplia fonts i territori; no relaxa els criteris**.

**Advertència del document sobre el cas de Berlín (§3.3.11):** el checkpoint
DE_11000000_G22 registra 341 venedors verificats, 69 elegibles i 272 en HOLD, amb
una taxa d'elegibilitat del 20,23%. El document diu explícitament que **és una
observació de Berlín i no es projecta automàticament a tota la UE-27**. No es pot
planificar amb aquesta xifra.

---

## 7. Regles de cortesia — vinculants, no opcionals

§2.4.3 i §3.8.4. Totes cinc regles s'apliquen des de la primera petició:

1. **Pressupost per domini:** interval mínim configurable entre peticions al
   mateix host. Els URLs d'un venedor es reparteixen dins la finestra amb
   *jitter*; **mai en ràfega**.
2. **`robots.txt` es respecta:** si no es pot llegir (5xx, xarxa, 401/403), es
   tracta com a **no permès**. Fail-closed.
3. **Bloqueig o petició d'aturada:** 401, 403 o 429, el domini s'aparca, totes les
   seves peces passen a STALE, i s'escala. **Mai s'eludeix.**
4. **Senyal de disponibilitat, no només HTTP 200:** una pàgina que respon 200 pot
   dir "venut". Disponible només amb senyal positiu. Sense senyal, STALE.
5. **Identitat de les peticions:** peticions HTTP normals a pàgines públiques, com
   un client qualsevol. **Sense suplantar rastrejadors i sense eludir mesures
   tècniques.**

**Regla estructural que ho envolta tot (R11, §2.4):** davant dels venedors
d'origen, RLF és un client retail sense relació comercial privilegiada. Cap procés
del sistema pot dependre d'un acord, un contacte, una API, un feed privat, un preu
de majorista ni cap tracte especial.

---

## 8. La seqüència d'execució, en ordre

Cada pas té el seu mòdul. Cap pas es pot saltar.

| Pas | Acció | Mòdul |
|---|---|---|
| 1 | Construir la matriu de 2.700 unitats | `laurel_ledger/ledger.py` |
| 2 | Definir el protocol de cerques per unitat | `territorial_windows.py` |
| 3 | Encuar la feina a la Work Queue | `work_queue.py` |
| 4 | L'orquestrador assigna unitats a workers | `orchestrator.py` |
| 5 | Executar la descoberta respectant cortesia | `availability.py` |
| 6 | Avaluar els vuit criteris d'elegibilitat | `supplier_eligibility.py` |
| 7 | Verificar la compra pública sense comprar | pendent |
| 8 | Deduplicar globalment | `deduplication.py` |
| 9 | Persistir amb snapshot o hash d'evidència | pendent |
| 10 | Comptar només els que compleixen els 15 elements | `validated_record_complete()` |
| 11 | Recalcular la cota de Wilson i reprioritzar | `lane_assigner.PriorityQueue` |
| 12 | Re-validar frescor a 30 dies abans del freeze | pendent |

---

## 9. La re-validació de frescor abans del freeze

§3.3.15 (OP-025, TANCAT). Un registre VALIDAT amb data de verificació **anterior a
30 dies** respecte del moment de calcular el snapshot immutable de preinauguració
es reencua automàticament per a una segona comprovació.

- Si la comprovació de compra pública o les condicions publicades **no es poden
  reproduir**, el registre passa a HOLD i **no compta** dins dels 10.000.
- Si **es reprodueixen**, la data de verificació s'actualitza.

Aquesta regla **no altera el comptador durant la producció**; només el recompte
que es congela en el snapshot final. Redueix el risc de comptar venedors que han
tancat entre la validació i la inauguració.

---

## 10. El freeze

§7.8.A punts 4 i 5, i §3.3.12:

1. Congelar els snapshots quan els dos gates se superen
2. Reexecutar validators i deduplicació
3. Recalcular els comptadors
4. Generar el manifest SHA-256
5. **Només el snapshot revalidat pot passar a Fase 9.** Un recompte anterior al
   freeze no autoritza la inauguració.

I la regla del gate, literal: *"Superar temporalment 10.000 durant la producció no
substitueix el freeze: el recompte final es torna a calcular sobre un snapshot
immutable."*

---

## 11. Els punts oberts d'aquest pla

Cap d'aquests no és una decisió meva. Tots són qüestions que el document deixa a
la governança i que cal tancar abans que el motor corri.

### PO-A — El protocol de cerques concret

El document fixa l'estructura del protocol però no n'enumera les cerques. Cal una
llista aprovada abans d'encuar 2.700 unitats. Condició de tancament: decisió de
governança que fixi el protocol, registrat amb la seva empremta SHA-256.

### PO-B — La llista de marques afins

§3.3.8 en dona deu i diu *"i similars"*. Qualsevol ampliació és **decisió humana**
(Nivell 6). Condició de tancament: decisió que tanqui la llista o fixi el
procediment d'ampliació.

### PO-C — Les 100 localitats base

El document fixa la xifra, cent localitats, però no quines. Condició de tancament:
llista aprovada de les 100 localitats que es creuaran amb els 27 estats.

### PO-D — Capacitat de workers real

§3.3.9 diu que l'execució simultània dels 27 països està subjecta *"a la capacitat
real de workers i a les regles de cortesia per domini"*. Condició de tancament:
dimensionament aprovat de la capacitat inicial.

---

## 12. La finestra temporal de la segona recerca — aclariment

Ho deixo registrat perquè és una correcció d'una dada que s'ha expressat amb una
imprecisió.

**R20, literal:** *"L'abast històric cobreix els antecedents dels anys 1940 i els
productes de la marca des de 1952 fins a la data de congelació."*

Per tant la finestra de la **recerca KB**, que és la segona, no aquesta, és **1952
fins al 16 de setembre de 2026**, i no 1950. La marca Fred Perry es funda el 1952;
el 1950 i el 1951 no existeixen com a any de producte de marca. I els antecedents
dels anys 1940 són una **capa genealògica separada que no compta** com a producte
de la marca.

---

*Document derivat del document mestre v2.6.0. Totes les regles citades són
transcripcions literals o paràfrasis fidels de les seccions indicades. Si hi ha
discrepància, mana el document mestre. Autor del sistema i propietari
intel·lectual: Jordi Figueras Soler.*
