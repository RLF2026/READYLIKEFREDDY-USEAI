"""Runner de proves del sistema RLF.

Executor propi que descobreix i executa totes les suites de `tests/` sense
poder dependre de pytest ni de cap eina externa. Us:

    python3 tests/run_all.py

Retorna codi de sortida 0 si totes les proves passen, 1 si alguna falla.

Nota sobre l'abast (R14, zero simulacions). Aquest runner nomes conte les
suites que proven funcions pures o recursos reals. Les suites dels moduls de
domini no hi son i no hi poden ser fins que existeixin les dades reals sobre
les quals han de correr: el protocol de cerques, les cent localitats canoniques,
els venedors reals i els productes Fred Perry reals.
"""

import importlib.util
import sys
import traceback
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent

# Nomes suites que compleixen R14.
SUITES: tuple[str, ...] = (
    "test_core.py",
    "test_states.py",
    "test_identity_dedup_hold.py",
    "test_monitoring.py",
    "test_validation_governance.py",
    "test_state_and_integrity.py",
)


def load_suite(path: Path):
    """Carrega una suite de proves com a modul.

    Args:
        path: Ruta del fitxer de la suite.

    Returns:
        El modul carregat.

    Raises:
        ImportError: Si la suite no es pot carregar.
    """
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No s'ha pogut carregar la suite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


def discover_tests(module) -> list[tuple[str, object]]:
    """Descobreix les funcions de prova d'un modul.

    Args:
        module: Modul de la suite.

    Returns:
        Una llista de parells nom i funcio, ordenada pel nom.
    """
    found: list[tuple[str, object]] = []
    for name in sorted(dir(module)):
        if not name.startswith("test_"):
            continue
        candidate = getattr(module, name)
        if callable(candidate):
            found.append((name, candidate))
    return found


def main() -> int:
    """Executa totes les suites i informa del resultat.

    Returns:
        0 si tot passa, 1 si hi ha alguna fallada.
    """
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    total_passed = 0
    total_failed = 0
    failures: list[tuple[str, str, str]] = []
    suite_report: list[tuple[str, int, int]] = []

    print("=" * 70)
    print("RLF REAL SYSTEMS - execucio de proves")
    print("=" * 70)

    for suite_name in SUITES:
        suite_path = TESTS_DIR / suite_name
        if not suite_path.is_file():
            print(f"\n[ ABSENT ] {suite_name}")
            total_failed += 1
            failures.append((suite_name, "<suite>", "suite no trobada al disc"))
            continue

        # Una suite pot haver estat retirada per R14 i contenir nomes una nota.
        raw = suite_path.read_text(encoding="utf-8")
        if "RETIRAT PER INCOMPLIMENT DE R14" in raw:
            print(f"\n[ RETIRADA ] {suite_name}")
            continue

        print(f"\n[ SUITE ] {suite_name}")
        try:
            module = load_suite(suite_path)
        except Exception as exception:
            print(f"  ERROR de carrega: {exception}")
            total_failed += 1
            failures.append((suite_name, "<load>", str(exception)))
            continue

        tests = discover_tests(module)
        if not tests:
            print("  Cap prova descoberta")
            continue

        passed = 0
        failed = 0
        for name, function in tests:
            try:
                function()
                passed += 1
            except Exception as exception:
                failed += 1
                detail = traceback.format_exc(limit=3).strip().splitlines()[-1]
                print(f"  FALLA  {name}")
                print(f"         {exception}")
                failures.append((suite_name, name, detail))

        total_passed += passed
        total_failed += failed
        suite_report.append((suite_name, passed, failed))
        print(f"  {passed} passades, {failed} fallades")

    print("\n" + "=" * 70)
    print("RESUM")
    print("=" * 70)
    for suite_name, passed, failed in suite_report:
        mark = "OK " if failed == 0 else "FAIL"
        print(f"  [{mark}] {suite_name:<40} {passed:>3} passades  {failed:>3} fallades")
    print("-" * 70)
    print(f"  TOTAL: {total_passed} passades, {total_failed} fallades")

    if failures:
        print("\nFALLADES:")
        for suite_name, test_name, detail in failures:
            print(f"  {suite_name} :: {test_name}")
            print(f"    {detail}")

    print("=" * 70)
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
