# `projects/rlf_suppliers_eu27/` — RLF Suppliers EU27

Actiu principal 1 (§2.2.3): registre de venedors professionals de producte preloved de la
UE-27. **No és una xarxa**: no hi ha relació amb els venedors (§2.4, R11).

## Contingut previst (§2.3.6)

```
projects/rlf_suppliers_eu27/
├── sourcing/         Motor de sourcing (100 lanes, §3.3.4)
├── pool/             Product Pool, reavaluació (§3.8.2, §3.8.3)
├── monitoring/       Monitoratge de disponibilitat per URL (§3.8.4)
│                     availability.py
├── sync/             Sincronització
├── seo/              SEO
├── verification/     Verificació
│                     supplier_eligibility.py (§3.3.8)
└── laurel_ledger/    Laurel Ledger: 100 localitats × 27 estats UE = 2.700 unitats (§3.3.9)
```

## Regles que governen aquest actiu

- **Elegibilitat de venedors (§3.3.8):** vuit criteris acumulatius. Dades absents → HOLD;
  marca similar no llistada → HOLD (decisió humana); criteri incomplert → REJECT;
  contradicció → REJECT.
- **Gate de preinauguració:** ≥10.000 venedors VALIDATS. Vegeu
  `docs/GATES_PREINAUGURACIO.md`.
- **Lanes:** `lane = (SHA-256("lane_assigner/1.1" + "|" + clau_canònica) mod 100) + 1`.
  100 lanes són una partició de concurrència i persistència, **no** una quota de cobertura.
- **Marketplaces generalistes** (eBay, Wallapop, Vinted i equivalents) queden fora del
  registre canònic (§2.2.3, §3.3.8).
- **Regles de cortesia (§2.4.3, §3.8.4):** respectar `robots.txt` (fail-closed si no es pot
  llegir); pressupost per domini; mai en ràfega; 401/403/429 → el domini s'aparca i s'escala;
  mai eludir mesures tècniques.

## Estat

**Buid.** No hi ha codi en aquest repositori.
