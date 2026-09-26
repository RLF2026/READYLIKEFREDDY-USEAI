# `deployment/` — Desplegament (Part 8)

Posada en producció del sistema. Detall complet: Part 8 del document mestre.

```
deployment/
├── hosting/      IONOS (pla senzill, 200 GB, WordPress)
├── domain/       readylikefreddy.shop — Nominalia
├── emails/       freddy@ i no-reply@readylikefreddy.shop
├── stripe/       Passarel·la de pagament (§3.12.1, §8.5)
└── storefront/   Botiga WordPress + WooCommerce (§6.8, §8.6)
```

## Estat dels elements, segons el que ha declarat la governança

| Element | Declarat | Estat al repositori |
|---|---|---|
| Domini `readylikefreddy.shop` | Contractat (Nominalia) | Sense registre tècnic aquí |
| Correu `freddy@readylikefreddy.shop` | Contractat (Nominalia) | Sense configuració aquí |
| Correu `no-reply@readylikefreddy.shop` | Contractat (Nominalia) | Sense configuració aquí |
| Hosting IONOS 200 GB + MySQL | Contractat | Sense configuració aquí |
| Stripe | Perfil obert | Sense claus ni configuració aquí — **mai s'hi posen credencials** |
| Botiga WordPress + WooCommerce | Prevista (§8.6) | No construïda |

## Advertiment de seguretat

En aquesta carpeta **no s'hi guarden mai credencials, claus d'API, tokens ni contrasenyes**.
El sistema és portable (§5.2.8) i la seva configuració no depèn de secrets allotjats al
repositori.

## Checklist de desplegament (§8.7)

Llista literal del document mestre. Cap casella es marca aquí.

- [ ] Hosting IONOS contractat i configurat.
- [ ] Domini readylikefreddy.shop apuntant a IONOS.
- [ ] Correu freddy@readylikefreddy.shop operatiu.
- [ ] Correu no-reply@readylikefreddy.shop operatiu.
- [ ] SPF, DKIM i DMARC configurats.
- [ ] Stripe en producció.
- [ ] Connector de sincronització operatiu (§6.8).
- [ ] Botiga publicada.
- [ ] KB migrada.
- [ ] Verificació del checkout en producció completada.
- [ ] Backups configurats.

## Nota d'ordre (R9)

Les fases 10 (desplegament) i 11 (màrqueting) **no s'inicien fins que la resta estigui al
100%**. Els gates de preinauguració continuen oberts: vegeu `docs/GATES_PREINAUGURACIO.md`.
