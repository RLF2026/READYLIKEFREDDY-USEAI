# Registre d'esdeveniments d'aquest repositori

Registre append-only (§5.2.6) de l'obertura i la construcció inicial d'aquest repositori.
Les entrades s'afegeixen; no es reescriuen.

---

## 2026-09-26 — Obertura del repositori i estructura inicial

**Context.** El repositori `RLF2026/READYLIKEFREDDY-USEAI` existia i era completament buit
(GitHub: *"Git Repository is empty"*), sense branca per defecte. Aquesta entrada registra la
primera càrrega de contingut.

**Què s'ha creat.**

| Ruta | Naturalesa |
|---|---|
| `README.md` | Acta del repositori; dades canòniques de capçalera; punts oberts |
| `docs/RLF_Document_Mestre_v2.5.0.md` | Font de veritat única, còpia íntegra |
| `docs/ARQUITECTURA.md` | Arbre del sistema (§2.3, §6.1, §6.7) |
| `docs/GOVERNANCA_OP.md` | Registre dels OP tancats i dels 8 contractes |
| `docs/GATES_PREINAUGURACIO.md` | Estat dels gates de §5.3.A |
| `docs/REGISTRE.md` | Aquest fitxer |
| `assets/brand/MANIFEST.md` | Inventari dels actius de marca (PO-1 a PO-4) |
| `assets/brand/green/README.md` | Joc verd: què hi ha d'anar |
| `assets/brand/black/README.md` | Joc negre: pendent de lliurament |
| `shared/rlf_core/README.md` | RLF CORE segons §2.2.4, §2.3.6 |
| `projects/rlf_suppliers_eu27/README.md` | Actiu 1 segons §2.2.3, §3.3 |
| `projects/rlf_fred_perry_kb_visor/README.md` | Actiu 2 segons §2.2.3, §3.6 |
| `projects/README.md`, `shared/README.md` | Contenidors |
| `governance/README.md` | Contractes de Nivell 5 i funció RLF-BACKUP/1.0 |
| `deployment/README.md` | Part 8 i checklist §8.7 |
| `marketing/README.md` | Part 9, Fase 11, no activada |
| `data/README.md` | Regla de font de veritat (R12, §6.7) |
| `tests/README.md` | Proves del document (§3.3.10, §6.5.5) |

**Què NO s'ha creat, i per què.**

- **Cap fitxer binari.** Els quatre actius del joc verd (PNG/JPEG, 1,7 MB i 2,2 MB els PNG)
  no s'han pogut carregar: les eines de fitxer disponibles en aquesta execució treballen amb
  contingut de text i el camí per llegir-ne els bytes crus ha estat bloquejat. **Els binaris
  han d'entrar per la interfície web de GitHub.** Cap fitxer parcial ni corrupte s'ha deixat
  al repositori.
- **Cap codi.** El codi del sistema no existeix encara; no s'ha simulat (NO FAKES, R14).

**Punts oberts registrats en aquesta obertura.**

- **PO-VERSIÓ** — contradicció interna: capçalera 2.5.0 vs. §6.5.6 `RLF REAL SYSTEMS` 2.2.0.
  Requereix decisió de governança (Nivell 6).
- **PO-1** — els noms dels quatre fitxers declaren 4096 px / 2048 px; les mides reals són
  2000 × 1224 px en tots quatre.
- **PO-2** — el PNG marcat "WEB" és el més pesat del joc (2,36 MB > 1,83 MB del "MASTER").
- **PO-3** — marge de seguretat de §1.3 no verificat contra els fitxers.
- **PO-4** — joc negre pendent de lliurament.

**Estat dels gates.** Suppliers, KB i operativa: tots oberts. Cap s'ha tocat.

**Governança.** Cap decisió nova. Aquest registre no afegeix autoritat a res: el document
mestre continua manant (§0.1).

---

*Registre append-only. Autor del sistema i propietari intel·lectual: Jordi Figueras Soler.*
