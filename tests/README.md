# Tests

El sistema RLF usa **nomes la biblioteca estandard** de Python. No hi ha
`requirements.txt` perque no hi ha cap dependencia externa (R7: cap dependencia
no justificada).

---

## La regla que governa aquest directori

**R14, zero simulacions**, es literal:

> *"Cap prova, verificacio o xifra es fa amb dades sintetiques presentades com a
> reals, mocks que substitueixin el sistema provat ni resultats inventats. Les
> proves usen recursos reals (servidor HTTP local real, fitxer xlsx real, base de
> dades real)."*

Consequencies practiques per a aquest repositori:

1. **Cap prova fabrica context de domini.** Ni codis de pais, ni noms de ciutat,
   ni identificadors de venedor, ni SKU, ni cap valor que afirmi res sobre el món
   real. Si una prova necessita context de domini, vol dir que les dades reals ja
   han d'existir.
2. **Les proves dels moduls de domini no existeixen fins que hi hagi dades.** El
   motor de sourcing, el pipeline, la KB i el visor forense no es poden provar
   fins que existeixin el protocol de cerques, les cent localitats canoniques i
   els productes reals.
3. **Les proves dels moduls del CORE si que existeixen**, perque son sobre
   funcions pures: el contracte de retorn, el principi fail-closed, la maquina
   d'estats, el hashing, la validacio. Cap d'aquestes no afirma res sobre cap
   entitat del món real.
4. **Cap xifra de producció es presenta com a mesurada** si no ho es.

---

## Execucio

```bash
python3 tests/run_all.py
```

El retorn es 0 si tot passa i 1 si alguna prova falla. El runner descobreix
automaticament totes les funcions `test_*` de cada suite; no cal pytest.

Alternatives:

```bash
sh tests/run.sh      # sintaxi i suites
make verify          # sintaxi i suites, via Makefile
```

---

## Suites del CORE

| Suite | Cobreix | Naturalesa |
|---|---|---|
| `test_contract_and_fail_closed.py` | Contracte de retorn (S6.1.6) i fail-closed (S4.1) | Funcions pures |
| `test_states.py` | Sis estats, taula de transicions i les 24 guardes (S3.2.2.A) | Funcions pures |
| `test_hashing_and_integrity.py` | Idempotencia (S4.3.2), estats, checkpoints i manifests (S4.4.2) | Funcions pures i fitxers reals |
| `test_validation_and_governance.py` | Validacio (S6.1), RLF-TRUST/1.0 (S4.4.1) i RLF-RESILIENCE/1.0 (S4.4.5) | Funcions pures |
| `test_monitoring.py` | Disponibilitat per URL (S3.8.4) | Servidors HTTP locals reals |

---

## Convencio

Cada prova cita **la seccio del document mestre** a la docstring, perque una
auditoria pugui rastrejar que es prova i contra que. Una prova sense referencia
de seccio no serveix per a S6.1.11.

## Recursos reals

Cap prova usa simulacres que substitueixin el sistema provat. Les proves de
monitoratge aixequen **servidors HTTP reals** sobre `http.server` i fan
peticions HTTP de veritat a `127.0.0.1`. Les de manifest i integritat
construeixen **fitxers reals** en directoris temporals i en calculen el SHA-256.

## El que falta, i per que

Les proves dels moduls de domini **no estan escrites i no ho poden estar** fins
que existeixin les dades reals:

| Modul | Dada real que necessita | Punt obert |
|---|---|---|
| Motor de sourcing | Protocol de cerques aprovat | PO-A |
| Motor de sourcing | Les cent localitats canoniques | PO-C |
| Motor de sourcing | Sectoritzacio per poblacio | Pendent de definicio |
| Elegibilitat de venedors | Els vuit criteris sobre venedors reals | Requereix la recerca |
| Pipeline de vuit etapes | Pagines reals de venedors | Requereix la recerca |
| KB i Visor forense | Productes Fred Perry reals i fotografies reals | Requereix la recerca |

Aquestes mancances no son un forat: son la consequencia correcta d'aplicar R14.
