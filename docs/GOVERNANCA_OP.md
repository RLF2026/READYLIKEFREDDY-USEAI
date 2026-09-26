# Registre de decisions de governança (OP)

Registre de les decisions de governança tancades del sistema RLF, transcrites de §6.3.4 del document mestre canònic. **Totes les entrades d'aquesta taula estan TANCADES** segons el document. Un OP tancat no es reobre sense una nova decisió de governança explícita.

| OP | Tipus | Matèria | Referència | Estat |
|---|---|---|---|---|
| OP-003 | Decisió de governança | Abast del catàleg: 100% Fred Perry, sense ampliació a perpetuïtat | §3.3.8 | Tancat |
| OP-004 | Decisió de governança | Calendari i pressupost d'activació de màrqueting (Fase 11) | §9.1.A | Tancat |
| OP-005 | Decisió de governança | Definició canònica del Product Pool (conjunt inclusiu ≈4.000) | §3.8.2 | Tancat |
| OP-006 | Decisió de governança | Escala de condició i zona de benefici 40–90 €; viabilitat via pilot | §3.8.5.A, §3.9, §3.15.6 | Tancat |
| OP-008 | Decisió de governança | Risc de marca de la corona de llorer assumit explícitament; logo s'usa des del dia 1 | §1.3 | Tancat |
| OP-009 | Decisió de governança | Logística: taula canònica per ruta, sense transportista únic universal | §3.12.3 | Tancat |
| OP-011 | Decisió de governança | Vigilància regulatòria del DPP (ESPR) | §9.8 | Tancat |
| OP-012 | Decisió de governança | Control de canvis legal-regulatori del DPP | §9.8 | Tancat |
| OP-015 | Decisió de governança | Enviament d'entrada (proveïdor → HQ) i sortida (HQ → client) com a costs independents | §3.12.3.B, §3.12.3.C | Tancat |
| OP-016 | Decisió de governança | Mesura física obligatòria per categoria | §3.12.3.A | Tancat |
| OP-018 | Decisió de governança | SOP legal de devolucions: 14 dies de desistiment, excepcions legals | §3.12.4 | Tancat |
| OP-019 | Decisió de governança | Protocol de comparació de serveis de transport per venda | §3.12.3 | Tancat |
| OP-020 a OP-031 | Decisió de governança | Bloc de decisions tancades | §6.3.4 | Tancat |
| OP-023 | Decisió de governança | Priorització dinàmica per rendiment (cota inferior de Wilson) | §3.3.13 | Tancat |
| OP-024 | Decisió de governança | Descoberta creuada via Factory Registry (canal additiu) | §3.3.14 | Tancat |
| OP-025 | Decisió de governança | Re-validació de frescor (30 dies) abans del freeze | §3.3.15 | Tancat |
| OP-029 | Decisió de governança | Límit epistemològic del Forensic Profile: no s'inventen punts per omplir quota | §3.7.7 | Tancat |
| OP-030 | Decisió de governança | Normalització de cada factor de scoring econòmic | §3.8.5.A | Tancat |
| OP-032 | Decisió de governança | Estàndard de valors normalitzats (polos) | §3.5.8 | Tancat |
| OP-033 | Decisió de governança | Extensió de l'estàndard de valors normalitzats a la resta de categories del catàleg | §3.5.8.9–§3.5.8.13 | Tancat |

**Nota del document (§6.3.4):** només resten oberts els gates que depenen d'execució real i els valors que encara no existeixin com a artefacte verificable. El requisit de ≥10.000 proveïdors VALIDATS, el de ≥15.000 productes KB FULL-CERTIFIED i els 60 dies d'operativa estable amb ≥1 venda/setmana **no són OP**: són gates operatius de preinauguració, i només es tanquen fent la feina real, no amb una decisió de governança.

---

## Contractes de governança (Nivell 5, §2.2.6)

Ordre canònic. Els vuit contractes són transversals al sistema.

| Ordre | Contracte | Propòsit | Desenvolupament |
|---|---|---|---|
| 1 | RLF-TRUST/1.0 | Quin estat és de confiança | §4.4.1 |
| 2 | RLF-INTEGRITY/1.0 | Com es verifica la integritat dels artefactes | §4.4.2 |
| 3 | RLF-RECOVERY/1.0 | Com es recupera l'estat després d'una interrupció | §4.4.3 |
| 4 | RLF-BACKUP/1.0 | Com es preserva el projecte fora de la sessió | §4.4.4 |
| 5 | RLF-RESILIENCE/1.0 | Com tolera errors sense caure sencer | §4.4.5 |
| 6 | RLF-PORTABLE/1.0 | Com es transporta i es reconstrueix | §4.4.6 |
| 7 | RLF-TURN/1.0 | Cicle d'execució (inici, pausa, represa, tancament) | §4.4.7 |
| 8 | RLF-RELEASE-MANIFEST/2.0 | Què és una versió del sistema | §4.4.8 |

**Nota de versions:** les versions dels contractes (`/1.0`, `/2.0`) són **versions de cada contracte**, no la versió del sistema. La versió del sistema és a `docs/VERSIO.md`.

---

## Jerarquia executiva — set nivells (§2.2)

| Nivell | Nom | Funció |
|---|---|---|
| 0 | Propòsit | Objectiu últim |
| 1 | Estratègia | Com s'assoleix |
| 2 | Dos actius | Suppliers EU27 + KB + Visor |
| 3 | Core | Primitives compartides |
| 4 | Motor operatiu | Execució |
| 5 | Governança | 8 contractes |
| 6 | Humà | Governança superior |

**Nivell 6 és humà.** Màquina = execució. Humà = governança: definir política, aprovar canvis, gestionar excepcions, revisar casos amb evidència insuficient, autoritzar migracions, supervisar releases, decidir estratègia, resoldre punts oberts (§2.2.7).

---

*Transcripció de §6.3.4, §2.2.6 i §2.2. Si hi ha discrepància, mana el document mestre. Aquest registre no afegeix, no reinterpreta i no tanca cap OP pel seu compte. La versió del sistema és a `docs/VERSIO.md`.*
