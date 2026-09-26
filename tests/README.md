# Tests

El sistema RLF usa **nomes la biblioteca estandard** de Python. No hi ha
`requirements.txt` perque no hi ha cap dependencia externa (R7).

---

## Com executar les proves

```bash
python3 tests/run_all.py
```

El retorn es 0 si tot passa i 1 si alguna falla. El runner descobreix
automaticament totes les funcions `test_*` de cada suite; no cal pytest.

---

## Suites

| Suite | Cobreix |
|---|---|
| `test_core.py` | Contracte de retorn (S6.1.6) i fail-closed (S4.1) |
| `test_states.py` | Sis estats, taula de transicions i les 24 guardes (S3.2.2.A) |
| `test_identity_dedup_hold.py` | Clau canonica (S3.3.4), Bloom i MinHash (S3.3.10), resolucio de HOLDs (S3.2.2 cas 15) |
| `test_monitoring.py` | Disponibilitat per URL (S3.8.4) contra servidors HTTP locals reals (R14) |
| `test_validation_governance.py` | Validacio (S6.1), RLF-TRUST/1.0 (S4.4.1) i RLF-RESILIENCE/1.0 (S4.4.5) |
| `test_state_and_integrity.py` | Idempotencia (S4.3.2), estats, checkpoints i manifests (S4.4.2) |
| `test_suppliers_and_normalization.py` | Elegibilitat de venedors (S3.3.8) i normalitzacio (S3.5.8) |

---

## Convencio

Cada prova cita **la seccio del document mestre** a la docstring, perque una
auditoria pugui rastrejar que es prova i contra que. Una prova sense referencia
de seccio no serveix per a S6.1.11.

## Recursos reals (R14)

Cap prova usa simulacres que substitueixin el sistema provat. Les proves de
monitoratge aixequen **servidors HTTP reals** sobre `http.server` i fan
peticions HTTP de veritat a `127.0.0.1`. Les de manifest i integritat
construeixen **fitxers reals** en directoris temporals i en calculen el SHA-256.

## Integracio continua

Per executar les suites automaticament a cada push sense instal·lar res a
maquina local, es pot afegir el flux de treball de GitHub Actions indicat a la
documentacio del repositori. El runner `run_all.py` es autocontingut i no
depen de cap servei.
