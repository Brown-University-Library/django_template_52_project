"""
Runs unittests for this repository.

Usage examples:
    (all) uv run ./run_tests.py -v
    (app) uv run ./run_tests.py -v foo_app
    (file) uv run ./run_tests.py -v tests.test_environment_checks
    (class) uv run ./run_tests.py -v tests.test_environment_checks.TestEnvironmentChecks
    (method) uv run ./run_tests.py -v tests.test_environment_checks.TestEnvironmentChecks.test_check_branch_non_main_raises
"""

import argparse
import os
import sys
from pathlib import Path

import django
from django.conf import settings  # type: ignore
from django.test.utils import get_runner  # type: ignore


def main() -> None:
    """
    Discover and run unittests for this repository.
    - Uses standard library unittest (per AGENTS.md)
    - Uses Django's test runner so app-based tests (e.g., `foo_app/tests/`) are discovered
    - Sets top-level directory to the repository root so `lib/` is importable
    """
    ## set up argparser ---------------------------------------------
    parser = argparse.ArgumentParser(description='Run repository unittests')
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Increase verbosity (equivalent to unittest verbosity=2)',
    )
    parser.add_argument(
        'targets',
        nargs='*',
        help=(
            'Optional dotted test targets to run, e.g. '
            '(app) `foo_app` or '
            '(module) `foo_app.tests.test_error_check` or '
            '(class/method) dotted paths under app tests'
        ),
    )
    ## parse args ---------------------------------------------------
    args = parser.parse_args()
    ## Ensure repository root is importable (adds 'lib/', etc) ------
    repo_root = Path(__file__).parent
    sys.path.insert(0, str(repo_root))
    ## Change working directory to repo root so relative discovery works
    os.chdir(repo_root)
    ## Initialize Django and use Django's test runner -----------------
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    verbosity = 2 if args.verbose else 1
    test_labels: list[str] = list(args.targets) if args.targets else []
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity, interactive=False)
    failures = test_runner.run_tests(test_labels)
    sys.exit(0 if failures == 0 else 1)


if __name__ == '__main__':
    main()
