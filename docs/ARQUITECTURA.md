# Arquitectura del sistema RLF

Transcripció estructurada de §2.3 del document mestre canònic
(`RLF_Document_Mestre_v2.5.0.md`). Cap element d'aquest fitxer és una decisió pròpia:
tot prové del document.

---

## 1. Blocs del sistema (§2.3.1)

```
READY LIKE FREDDY

0. PROPÒSIT / ESTRATÈGIA

1. BUSINESS SYSTEMS
   ├─ RLF Suppliers EU27 (motor de sourcing 100 lanes, Laurel Ledger 2.700 lanes,
   │                      registre de venedors)
   └─ RLF Fred Perry KB + Visor (KB, identitats, visor forense, evidència)

2. RLF CORE
   identitat, normalització, deduplicació, estat, cursors, hashing, manifests,
   validació, logging, recovery, configuració, integritat

3. OPERATIONAL ENGINE
   orchestrator, work queue, territorial windows, lanes, workers

4. DATA PIPELINES
   discovery, normalization, entity resolution, deduplication, validation,
   evidence, classification, persistence

5. COMMERCIAL ENGINE
   product pool, pricing, margin, selection, sale, backup, orders,
   anonymous purchasing, fulfilment

6. KNOWLEDGE ENGINE

7. GOVERNANCE (8 contractes)

8. STOREFRONT (WordPress + WooCommerce + Stripe; integració §6.8)

9. DEPLOYMENT (fase final)

10. MARKETING (fase final)
```

## 2. Dependències (§2.3.2)

- Business systems i motor operatiu depenen del CORE.
- Pipelines, del motor operatiu.
- Motor comercial, dels pipelines.
- Motor de coneixement, del CORE i del pipeline.
- Governança és transversal.
- Desplegament depèn de tot l'anterior; màrqueting, del desplegament.

## 3. Fluxos de dades (§2.3.3)

1. Descoberta → verificació → Product Pool.
2. Product Pool → scoring → selecció → Sale/Backup.
3. Producte → KB → identitat.
4. Monitoratge → disponibilitat → actualització d'estat.
5. Comanda → compra anònima → recepció → inspecció → enviament (§3.14).
6. Estat → checkpoint → backup.

## 4. Fluxos de control (§2.3.4)

Orquestrador → Work Queue → Workers → Validació → Estat.
TRUST i INTEGRITY són transversals. RECOVERY actua sobre l'estat. TURN controla el cicle.

## 5. Punts d'integració (§2.3.5)

- CORE ↔ Business Systems
- Pipeline ↔ KB
- KB ↔ Sistema comercial
- Motor de sourcing ↔ Laurel Ledger
- Motor comercial ↔ Botiga pública (WooCommerce, §6.8)

## 6. Rutes físiques (§2.3.6)

```
shared/rlf_core/                    { logging, contract, hashing, state, pipeline,
                                      configuration, ... }
projects/rlf_suppliers_eu27/        { sourcing, pool, monitoring, sync, seo,
                                      verification, laurel_ledger }
projects/rlf_fred_perry_kb_visor/   { kb, visor, evidence }
data/
governance/
deployment/                         { hosting, domain, emails, stripe, storefront }
marketing/                          { social, newsletter, fanzine }
docs/
tests/
```

Aquestes són les rutes canòniques. L'arbre d'aquest repositori les reprodueix literalment.

---

## 7. Spec de codi vinculant — SPEC-CODE-001 (§6.1)

Tot mòdul del sistema compleix SPEC-CODE-001. Cap mòdul queda exempt (R7).

Contracte de retorn canònic de tot mòdul (§6.1.6, §6.6.1):

```python
{
    "status": str,  # "SUCCESS" | "SKIPPED" | "HOLD" | "REJECT" | "ERROR" | "FAILURE"
    "reason": Optional[str],
    "data": Optional[object],
    "meta": Optional[dict],
}
```

| Estat | Significat | `data` |
|---|---|---|
| SUCCESS | Completat | Resultat |
| SKIPPED | No processat | None |
| HOLD | Ajornat | None |
| REJECT | Rebutjat | None |
| ERROR | Error d'entorn | None |
| FAILURE | Error inesperat | None |

Nomenclatura (§6.1.2): mòduls i paquets `snake_case`; classes `PascalCase`; funcions i
variables `snake_case`; constants `SCREAMING_SNAKE_CASE`. Docstrings en català.
Imports en ordre: biblioteca estàndard, tercers, locals.

---

## 8. Font de veritat de dades (§6.7)

Jerarquia de fonts. Només el nivell 1 és editable, i només via els mòduls del sistema.

| Nivell | Artefacte | Naturalesa | Editable directament? |
|---|---|---|---|
| 1 | Base de dades SQL de producció (MySQL a IONOS) | Font de veritat | Sí, només via els mòduls del sistema (§6.1) |
| 2 | `CERVELL_AUTENTIFICADOR.xlsx` (§6.2) | Vista derivada de lectura | No |
| 3 | Dashboard (§4.5) | Vista derivada de lectura | No |
| 4 | Exportacions (CSV, informes) | Vista derivada puntual | No |

La sincronització és sempre unidireccional: base de dades → vistes derivades (§6.7.4).

---

*Tot el contingut d'aquest fitxer prové de §2.3, §6.1 i §6.7 del document mestre. Si hi ha
discrepància, mana el document mestre.*
