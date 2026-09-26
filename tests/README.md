# `tests/` — Proves

Les proves del sistema usen **recursos reals**: servidor HTTP local real, fitxer xlsx real,
base de dades real. Cap prova s'executa amb dades sintètiques presentades com a reals, ni amb
mocks que substitueixin el sistema provat (R14, zero simulacions).

## Proves esmentades pel document mestre

| Prova | Mesura | Referència |
|---|---|---|
| `tests/test_core.py` | Bloom filter: 10.000 claus, p = 1% → 11.982 bytes (11,70 KiB), k = 7, 0 falsos negatius, 0,998% de falsos positius sobre 100.000 sondes | §3.3.10 |
| MinHash + LSH | Jaccard 0,727 (mateixa peça) vs. 0,156 (peça diferent) | §6.5.5 |
| Perceptual hashing | Hamming 0 (còpia +8% brillantor) vs. 32 (imatges no relacionades) | §6.5.5 |
| Claus d'idempotència | applied / replayed-noop, zero duplicacions | §6.5.5 |
| Backup adreçat per contingut | 35,9% / 57% / 68% menys bytes (2/3/4 snapshots) | §6.5.5 |
| Monitoratge de disponibilitat | Servidor HTTP local real | §3.8.4 |

Les mesures de la taula són **MESURAT** segons el document: resultat d'una prova documentada i
reproduïble. Aquest repositori les transcriu, no les reclama com a pròpies ni les reprodueix.

## Estat

**Buid.** No hi ha codi de prova en aquest repositori.
