#!/bin/sh
# Executa totes les suites de proves del sistema RLF.
#
# No depen de cap servei extern, de cap credencial i de cap eina addicional:
# nomes necessita Python 3. El modul de monitoratge aixeca servidors HTTP
# locals reals, tal com exigeix R14 (zero simulacions).
#
# Us:  sh tests/run.sh
# Retorna 0 si tot passa i 1 si alguna prova falla.

set -e
cd "$(dirname "$0")/.."

echo "RLF REAL SYSTEMS - comprovacio de sintaxi"
python3 -m compileall -q shared projects governance tests

echo "RLF REAL SYSTEMS - execucio de suites"
python3 tests/run_all.py
