# Versió del sistema — font única dins el repositori

Aquest fitxer és **l'única font de versió del repositori**. Cap altre fitxer declara una versió pel seu compte: tots hi apunten.

Document derivat. El valor prové de la capçalera del document mestre, que és la font de veritat única (§0.1). Si hi ha discrepància, mana el document mestre.

---

## Versió vigent

| Camp | Valor |
|---|---|
| **Versió del sistema** | **2.6.0** |
| Data d'emissió | 2026-09-26 |
| Sistema | RLF REAL SYSTEMS |
| Esquema de versionament | SemVer 2.0.0 — `MAJOR.MINOR.PATCH` (§4.4.8, §6.1.12) |

La versió viu **en un sol lloc**: la capçalera de `docs/RLF_Document_Mestre_v2.6.0.md`. Aquest fitxer la reflecteix.

---

## Canvi 2.6.0 (2026-09-26) — reconciliació de versió

**Fet:** eliminada la fila `| RLF REAL SYSTEMS (capçalera del document) | 2.2.0 | VERIFICAT |` de §6.5.6, per decisió de governança.

**Motiu:** aquella fila registrava el valor que la capçalera portava quan la taula es va verificar, i coexistia amb la capçalera 2.5.0. Tenir dos números de sistema vius alhora és una incoherència de lectura, no una dada útil: la taula §6.5.6 existeix per registrar **versions de component**, no la versió del sistema.

**Resultat:** una sola versió de sistema al document. La taula §6.5.6 conserva les seves tres files de component i duu una nota d'abast.

---

## Valors de versió que apareixen al document, amb el seu abast

| Valor | On | Què és | És la versió del sistema? |
|---|---|---|---|
| `2.6.0` | Capçalera del document mestre | Versió vigent | **Sí — l'única** |
| `2.0.0` (SemVer) | §4.4.8, §6.1.12 | *Esquema* de versionament, no una versió | No — és el format |
| `RLF-RELEASE-MANIFEST/2.0` | §2.2.6, §4.4.8 | Versió del contracte de governança | No — contracte |
| `RLF-TRUST/1.0`, `RLF-INTEGRITY/1.0`, `RLF-RECOVERY/1.0`, `RLF-BACKUP/1.0`, `RLF-RESILIENCE/1.0`, `RLF-PORTABLE/1.0`, `RLF-TURN/1.0` | §2.2.6 | Versió de cada contracte | No — contracte |
| `cervell_sync 1.0`, `lane_assigner 1.1`, `rlf_normalization 1.0` | §6.5.6 | Versió de components tècnics | No — component |

`lane_assigner 1.1` de §6.5.6 coincideix amb la clau `lane_assigner/1.1` de la fórmula d'assignació de lanes (§3.3.4): no hi ha incoherència entre la taula i la fórmula.

---

## Regla de coherència

1. **La capçalera del document mestre és l'autoritat.** El seu valor és la versió vigent.
2. **Cap fitxer d'aquest repositori declara una versió pròpia.** Tots apunten a aquest fitxer.
3. **Una versió futura s'incorpora així:** la governança actualitza la capçalera del document mestre, i aquest fitxer reflecteix el nou valor. No s'obre cap segon lloc on declarar-la.
4. **Les versions de contracte i de component no es presenten mai com la versió del sistema.**

---

## Prohibicions

- No declarar cap versió del sistema fora de la capçalera del document mestre.
- No reintroduir files de versió de sistema a §6.5.6.
- No presentar les versions de contracte (`RLF-*/1.0`) com si fossin la versió del sistema.
- No derivar una versió del nom d'un fitxer.

---

*Font única de versió del repositori. El valor vigent prové de la capçalera del document mestre. Si el document mestre canvia de versió, aquest fitxer s'actualitza i cap altre.*
