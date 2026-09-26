# Joc negre — pendent de lliurament

Carpeta reservada per al joc de logotip en negre, anunciat i encara **no lliurat**.

## Convenció de noms prevista

```
black/rlf-logo-a-black-transparent-master.png
black/rlf-logo-a-black-master.jpg
black/rlf-logo-a-black-transparent-web.png
black/rlf-logo-a-black-web.jpg
```

Variant `a` com al joc verd. Si el joc negre és una variant de disseny diferent i no una
variant de color, el camp `variant` ho ha de reflectir.

## Restricció de marca a tenir en compte

§1.3 prohibeix el logotip **en blanc pur**, **pla sense textura**, **glossy** i **metàl·lic**.
El joc negre s'ha de verificar contra aquesta llista abans de publicar-lo, i contra la resta
de §1.3 (bloc verbal i corona junts, espai de seguretat, mides mínimes).

## En rebre els fitxers

Verificar, amb el mateix procediment que el joc verd:

1. Mides reals en píxels (no les que declari el nom).
2. Canal alfa real (llegir el colorType de la capçalera PNG, no confiar en el nom).
3. Pes del fitxer.
4. Que la mida final no baixi dels mínims de §1.3.
5. Marge de seguretat contra l'alçada de la "R" ×2.

Qualsevol desviació es registra com a punt obert a `../MANIFEST.md`, sense corregir-la en
silenci.
