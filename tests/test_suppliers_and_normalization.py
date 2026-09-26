RETIRAT PER INCOMPLIMENT DE R14.

Aquesta suite fabricava context de domini: codis de pais inventats, un domini
d'invencio, noms de ciutat i codis de model posats com a valors de comprovacio de
la elegibilitat de venedors i de la normalitzacio de producte.

R14 es literal: "Cap prova, verificacio o xifra es fa amb dades sintetiques
presentades com a reals, mocks que substitueixin el sistema provat ni resultats
inventats." Aquesta suite incomplia la regla.

Es important distingir els dos casos, perque no tots els moduls son iguals:

INCOMPLEIXEN R14, perque fabriquen context de domini:
  - test_suppliers_and_normalization.py (aquest fitxer)
  - test_sourcing.py (retirat abans)

COMPLEIXEN R14, perque son sobre funcions pures i no afirmen res sobre cap
entitat del mon real: el contracte de retorn, el principi fail-closed, la
maquina d'estats, el hashing, la validacio, els manifests i el monitoratge
(aquest ultim contra servidors HTTP locals reals).

El que cal per poder reescriure aquestes proves be:

  - per a la elegibilitat de venedors: venedors reals, descoberts per la recerca
  - per a la normalitzacio de producte: fitxes reals de producte Fred Perry
  - per al motor de sourcing: el protocol de cerques i les cent localitats

Els moduls que aquesta suite pretenia cobrir segueixen al repositori i
completament operatius:

  - projects/rlf_suppliers_eu27/verification/supplier_eligibility.py
  - shared/rlf_core/normalization/product_values.py

Aquest fitxer es pot esborrar del repositori sense cap efecte.
