# Versió del sistema — font única dins el repositori

Aquest fitxer és **l'única font de versió del repositori**. Cap altre fitxer declara una versió pel seu compte: tots hi apunten.

Document derivat. El valor prové de la capçalera del document mestre, que és la font de veritat única (§0.1). Si hi ha discrepància, mana el document mestre.

---

## Versió vigent

| Camp | Valor |
|---|---|
| **Versió del document** | **2.5.0** |
| Data d'emissió | 2026-09-25 |
| Sistema | RLF REAL SYSTEMS |
| Esquema de versionament | SemVer 2.0.0 — `MAJOR.MINOR.PATCH` (§4.4.8, §6.1.12) |

---

## Per què hi ha més d'un número al document, i no és cap contradicció

§6.5.6 es titula **"Taula de versions"** i conté aquesta fila:

```
| RLF REAL SYSTEMS (capçalera del document) | 2.2.0 | VERIFICAT |
```

**Aquesta fila no declara la versió del sistema.** El parèntesi és literal i és la clau: diu *"RLF REAL SYSTEMS (capçalera del document)"*, és a dir, **el valor que portava la capçalera del document en el moment en què aquesta fila es va verificar**. És un registre de procedència de la taula de versions, no una declaració de la versió vigent.

La capçalera ha avançat de 2.2.0 a 2.5.0 en tres revisions MINOR —compatible, sense canvi incompatible, exactament el que SemVer preveu per a una MINOR. La fila de §6.5.6 descriu un estat anterior, verificat i correcte en el seu moment.

**Conclusió: no hi ha dues versions del sistema en conflicte. Hi ha una fila de taula que descriu un estat històric i que no s'ha de sobreescriure.**

---

## Regla de coherència

1. **La capçalera del document mestre és l'autoritat.** El seu valor és la versió vigent.
2. **§6.5.6 no es modifica sobreescrivint.** El seu valor és un registre `VERIFICAT`; canviar-lo seria falsificar una verificació (R2, R19). Si s'ha d'afegir la versió actual, s'afegeix una fila nova, no se'n reescriu cap.
3. **Cap fitxer d'aquest repositori declara una versió pròpia.** Tots apunten a aquest fitxer.
4. **Una versió futura s'incorpora així:** s'actualitza la capçalera del document mestre (governança), i aquest fitxer reflecteix el nou valor. La fila de §6.5.6 es manté.

---

## Valors de versió que apareixen al document, amb el seu abast

| Valor | On | Què és | És la versió del sistema? |
|---|---|---|---|
| `2.5.0` | Capçalera del document mestre | Versió vigent del document i del sistema | **Sí** |
| `2.2.0` | §6.5.6, fila "RLF REAL SYSTEMS (capçalera del document)" | Valor que la capçalera portava en verificar-se aquella fila | No — registre històric |
| `2.0.0` (SemVer) | §4.4.8, §6.1.12 | *Esquema* de versionament, no una versió | No — és el format |
| `RLF-RELEASE-MANIFEST/2.0` | §2.2.6, §4.4.8 | Versió del **contracte** de governança | No — versió d'un contracte |
| `RLF-TRUST/1.0`, `RLF-INTEGRITY/1.0`, `RLF-RECOVERY/1.0`, `RLF-BACKUP/1.0`, `RLF-RESILIENCE/1.0`, `RLF-PORTABLE/1.0`, `RLF-TURN/1.0` | §2.2.6 | Versió de cada contracte | No — versió d'un contracte |
| `cervell_sync 1.0`, `lane_assigner 1.1`, `rlf_normalization 1.0` | §6.5.6 | Versió de components tècnics individuals | No — versió de component |

**Nota sobre l'últim bloc:** les versions de component a §6.5.6 inclouen `lane_assigner 1.1`, i §3.3.4 esmenta la clau `lane_assigner/1.1` dins la fórmula d'assignació de lanes. Coincideixen, i per tant no hi ha incoherència entre la taula i la fórmula.

---

## Prohibicions

- No declarar cap versió del sistema fora d'aquest fitxer i de la capçalera del document mestre.
- No sobreescriure cap fila `VERIFICAT` de §6.5.6 per fer-la quadrar amb la capçalera.
- No presentar les versions de contracte (`RLF-*/1.0`) com si fossin la versió del sistema.
- No derivar una versió del nom d'un fitxer.

---

*Font única de versió del repositori. El valor vigent prové de la capçalera del document mestre. Si el document mestre canvia de versió, aquest fitxer s'actualitza i cap altre.*
