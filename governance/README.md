# `governance/` — Contractes de governança

Els vuit contractes formals de Nivell 5 (§2.2.6), en ordre canònic. Són transversals al
sistema. Detall i referències: `docs/GOVERNANCA_OP.md`.

| Ordre | Contracte | Pregunta |
|---|---|---|
| 1 | RLF-TRUST/1.0 | Quin estat és de confiança |
| 2 | RLF-INTEGRITY/1.0 | Els artefactes són els que creiem |
| 3 | RLF-RECOVERY/1.0 | Com es torna a l'estat bo |
| 4 | RLF-BACKUP/1.0 | Com sobreviu el projecte fora de la sessió |
| 5 | RLF-RESILIENCE/1.0 | Com tolera errors sense caure sencer |
| 6 | RLF-PORTABLE/1.0 | Com es transporta i es reconstrueix |
| 7 | RLF-TURN/1.0 | Cicle d'execució |
| 8 | RLF-RELEASE-MANIFEST/2.0 | Què és una versió del sistema |

## Funció d'aquest repositori dins la governança

Aquest repositori exerceix **RLF-BACKUP/1.0 (§4.4.4)**: "la conversa no és la infraestructura;
la infraestructura ha de poder sobreviure a la conversa". És la còpia de projecte que
sobreviu fora de qualsevol sessió.

## Regla d'escriptura del sistema (§5.2.6, APPEND-ONLY)

Les dades només s'afegeixen, mai es modifiquen ni s'esborren directament. Els canvis es fan
afegint noves entrades; l'estat es pot reconstruir llegint la seqüència.

## Estat

**Buid.** Els contractes es desenvolupen a §4.4 del document mestre; aquí no se n'hi afegeix
cap versió pròpia.
