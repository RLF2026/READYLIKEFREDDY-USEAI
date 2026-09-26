RETIRAT PER INCOMPLIMENT DE R14.

Aquesta suite passava valors inventats (codis de pais, noms de ciutat, etiquetes
com "locality-0") al motor de sourcing i hi assertia a sobre com si fossin la
matriu canonica del Laurel Ledger. No ho son: la matriu canonica son les cent
localitats reals creuades amb els vint-i-set estats, i el protocol de cerques es
una decisio de governanca que encara no esta presa.

R14 es literal: "Cap prova, verificacio o xifra es fa amb dades sintetiques
presentades com a reals, mocks que substitueixin el sistema provat ni resultats
inventats." Aquesta suite incomplia la regla.

Les proves del motor de sourcing es reescriuran quan existeixin les dades reals
sobre les quals han de correr:

  - les cent localitats canoniques (punt obert PO-C del pla de la megarecerca)
  - el protocol de cerques aprovat (punt obert PO-A)
  - la sectoritzacio definida per a cada poblacio

Fins que aquestes dades no existeixin, aquest fitxer no ha de tenir contingut.

Els moduls que aquesta suite pretenia cobrir segueixen al repositori i segueixen
completament operatius:

  - projects/rlf_suppliers_eu27/sourcing/work_queue.py
  - projects/rlf_suppliers_eu27/sourcing/territorial_windows.py
  - projects/rlf_suppliers_eu27/sourcing/orchestrator.py
  - projects/rlf_suppliers_eu27/laurel_ledger/ledger.py
  - projects/rlf_suppliers_eu27/monitoring/availability.py
  - projects/rlf_suppliers_eu27/verification/supplier_eligibility.py

Aquest fitxer es pot esborrar del repositori sense cap efecte.
