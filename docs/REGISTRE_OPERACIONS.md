# Registre d'operacions del repositori

Aquest fitxer anota exactament què s'ha fet al repositori i quan. És l'únic
lloc on es registra l'activitat. No es reescriu mai: s'hi afegeix.

---

## 2026-09-26 — Sessió de neteja i normalització

### Situació de partida

El repositori contenia fitxers de diverses sessions sense nomenclatura comuna i
amb duplicitats: dues còpies del document mestre, un fitxer de dades de
sectors amb regles no traçables al mestre, un motor paral·lel construït sense
verificació, i dos scripts d'auditoria d'ús puntual.

### Què s'ha fet

1. **Esborrats per no ser traçables al mestre ni verificables:**
   - `orchestrator/normativa.py` — contenia regles inventades (carrils de país,
sectorització per districtes, ordre alfabètic) que no són al document mestre.
   - `data/sectors_eu27.json` — sectorització de ciutats alemanyes per districtes;
el mestre no sectoritza ciutats (la unitat és país → regió → ciutat).
   - `data/localities_eu27.json` — contenia codis ISO interns i llistes
parcials amb restes de treball anterior.
   - `projects/rlf_suppliers_eu27/engine/` — motor paral·lel que duplicava el
motor ja existent i sense proves executades.
   - `tests/test_supplier_engine.py` — proves del motor anterior, mai executades.
   - `docs/AUDITORIA_REPO.md` — document d'auditoria d'ús puntual.
   - `docs/METODE_EXECUCIO.md` — mètode inventat, no traçable al mestre.

2. **Es manté, perquè és feina verificada i traçable:**
   - `docs/RLF_Document_Mestre_v2.5.0.md` — font de veritat única.
   - `docs/PLA_MEGARECERCA_SUPPLIERS.md` — pla derivat del mestre.
   - `projects/rlf_suppliers_eu27/sourcing/orchestrator.py` — §2.2.5, §3.3.6, §3.3.7.
   - `projects/rlf_suppliers_eu27/laurel_ledger/ledger.py` — §3.3.9, §3.3.13.
   - `shared/rlf_core/` — primitives del nucli.
   - `tests/` — proves de les primitives.

### Estat del projecte després de la neteja

- Comptador de proveïdors validats: **0**. Inici net, sense dades anteriors.
- No hi ha cap checkpoint anterior al sistema.
- Fase 2 (motor de sourcing): completa.
- Fase 3 (pipeline de vuit etapes): pendent.
- Fase 4 (identitat canònica): pendent.

### Punts oberts que bloquegen l'execució

- **PO-A** — El protocol de cerques concret no està definit.
- **PO-B** — La llista de marques afins no està tancada.
- **PO-C** — Les 100 localitats base no estan aprovades.
- **PO-D** — La capacitat de workers no està dimensionada.

Els quatre són decisions de governança (Nivell 6). Cap no es pot resoldre
des del sistema.
