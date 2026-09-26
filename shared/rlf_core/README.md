# `shared/rlf_core/` — RLF CORE

Primitives reutilitzables compartides (§2.2.4, §2.3.6).

## Contingut previst (§2.3.6)

```
shared/rlf_core/
├── logging/         Registre estructurat d'esdeveniments (§6.1.8)
├── contract/        Contracte de retorn canònic (§6.1.6, §6.6)
├── hashing/         SHA-256, idempotència (§3.3.10, §4.3.2)
├── state/           Estat persistent (§3.4.2)
├── pipeline/        Primitiva de pipeline
├── configuration/   Configuració
└── ...
```

Primitives canonitzades a §2.2.4: identitat, normalització, deduplicació, estat, cursors,
hashing, manifests, validació, logging, recovery, configuració, integritat.

## Estat

**Buid.** No hi ha codi en aquest repositori. El codi no s'inventa per omplir una carpeta
(NO FAKES, §5.2.2; R14).

Tot mòdul que s'hi afegeixi compleix **SPEC-CODE-001** (§6.1). Cap mòdul queda exempt (R7).
Contracte de retorn canònic i nomenclatura: vegeu `docs/ARQUITECTURA.md` §7.
