# Gates de preinauguració — estat

Transcripció de §5.3.A i §0.2 (R15) del document mestre canònic, amb l'estat real declarat
com a obert. **Cap gate es pot satisfer manualment des del dashboard** (§5.3.A, nota final).

---

## 1. Taula de gates (§5.3.A)

| Gate | Condició dura | Font de recompte | Estat |
|---|---|---|---|
| Suppliers | `supplier_prelaunch_validated >= 10000` | Snapshot SQL immutable | **OBERT** |
| KB | `kb_prelaunch_full_certified >= 15000` | Snapshot SQL immutable | **OBERT** |
| Camps KB | 100% obligatoris plens i verificats | Validator + auditoria | **OBERT** |
| Imatges | 4/4 bàsiques + 100% forenses aplicables | Image ledger | **OBERT** |
| Factories | `factory_id` resolt quan és material | Factory Registry | **OBERT** |
| Duplicats | 0 duplicats oberts al conjunt certificat | Dedup ledger | **OBERT** |
| Evidència | 100% dels camps crítics amb evidència | Evidence ledger | **OBERT** |
| Freeze | Manifest + SHA-256 + snapshot revalidats | Release manifest | **OBERT** |
| Operativa | 60 dies consecutius amb ≥1 venda/setmana (§1.9) | Registre d'operació | **OBERT** |

**Conseqüència operativa directa (R15, §0.2):** la inauguració queda bloquejada fins que
existeixin simultàniament ≥10.000 venedors VALIDATS i ≥15.000 productes KB FULL-CERTIFIED.
"No es compten projeccions, mostres, registres parcials ni aproximacions."

**Les fases 10 i 11 no s'inicien fins que la resta estigui al 100%** (R9, §0.2).

---

## 2. Per què aquests gates no són decisions de governança (§6.3.4)

El document ho diu explícitament: *"El requisit de ≥10.000 proveïdors VALIDATS i el de
≥15.000 productes KB FULL-CERTIFIED són gates operatius de preinauguració, no OP de
governança; el mateix val per als 60 dies d'operativa estable amb ≥1 venda/setmana. Aquests
tres gates només es tanquen fent la feina real, no amb una decisió de governança."*

Per tant: cap d'aquests gates es pot tancar des d'aquí, ni amb una ordre, ni amb una
declaració, ni editant aquest fitxer. Es tanquen amb un snapshot SQL immutable que confirmi
el llindar (§6.3.5, condició de tancament tipus "Gate preinauguració").

---

## 3. Definició de VALIDAT (§3.3.12)

Un venedor compta per al mínim preinauguració **només quan té a la base SQL**:

1. identitat canònica única
2. domini propi
3. país i ciutat/zona
4. pertinença UE-27
5. activitat professional de segona mà
6. criteri de marca complert
7. compra pública verificable sense crear una comanda de pagament
8. condicions de compra/devolució i enviament documentades
9. compatibilitat de monitoratge
10. font principal
11. data de verificació
12. snapshot/hash d'evidència
13. decisió ELEGIBLE
14. deduplicació PASS
15. auditoria persistent

**VALIDAT ≠ descobert ≠ HOLD ≠ elegible provisional.** El comptador
`supplier_prelaunch_validated` només incrementa quan la transacció de persistència i totes
les validacions han estat confirmades.

---

## 4. Re-validació de frescor abans del freeze (OP-025, §3.3.15)

Un registre VALIDAT amb data de verificació anterior a **30 dies** respecte del moment de
calcular el snapshot immutable de preinauguració es reencua automàticament per a una segona
comprovació abans de comptar en el recompte final. Si la comprovació de compra pública o les
condicions publicades ja no es poden reproduir, el registre passa a HOLD i **no compta** dins
dels 10.000.

---

## 5. Planificació de volum (§3.3.12)

`candidats_requerits = ceil((10000 − VALIDATS_actuals) / max(p_Wilson_lower, ε))`

on `p_Wilson_lower` és la cota inferior de confiança de Wilson al 95% sobre una mostra real.
Aquesta xifra és un **pressupost de treball, no un gate**. Si `p_Wilson_lower` és molt baix,
el sistema continua ampliant fonts i territori; **no relaxa els criteris d'elegibilitat**.

---

*Transcripció de §5.3.A, §0.2 (R9, R15), §3.3.12 i §3.3.15. Si hi ha discrepància, mana el
document mestre. Aquest fitxer no tanca cap gate.*
