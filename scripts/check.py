from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {
    ".agents",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
}


def discover_python_files() -> list[str]:
    files: list[str] = []

    for directory, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_DIRS]
        base = Path(directory)

        for filename in filenames:
            if filename.endswith(".py"):
                files.append(str((base / filename).relative_to(ROOT)))

    return sorted(files)


def discover_test_files() -> list[str]:
    tests_dir = ROOT / "tests"
    if not tests_dir.exists():
        return []

    return sorted(
        str(path.relative_to(ROOT))
        for path in tests_dir.rglob("*.py")
        if path.name.startswith("test_") or path.name.endswith("_test.py")
    )


def run(command: Sequence[str]) -> int:
    print("$ " + " ".join(command), flush=True)
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the project baseline checks.")
    parser.add_argument("--skip-lint", action="store_true", help="Skip ruff.")
    parser.add_argument("--skip-types", action="store_true", help="Skip mypy.")
    parser.add_argument("--skip-tests", action="store_true", help="Run lint and types only.")
    parser.add_argument(
        "--skip-contamination",
        action="store_true",
        help="Skip contamination scan.",
    )
    args = parser.parse_args(argv)

    commands: list[list[str]] = []

    if args.skip_lint:
        print("Skipping ruff by request.", flush=True)
    else:
        commands.append(["ruff", "check", "."])

    python_files = discover_python_files()
    if args.skip_types:
        print("Skipping mypy by request.", flush=True)
    elif python_files:
        commands.append(["mypy", *python_files])
    else:
        print("No Python files found; skipping mypy.", flush=True)

    test_files = discover_test_files()
    if args.skip_tests:
        print("Skipping pytest by request.", flush=True)
    elif test_files:
        commands.append(["pytest"])
    else:
        print("No pytest files found; skipping pytest.", flush=True)

    if args.skip_tests or args.skip_contamination:
        print("Skipping contamination scan by request.", flush=True)
    else:
        commands.append(["python", "scripts/check_contamination.py"])

    for command in commands:
        return_code = run(command)
        if return_code != 0:
            return return_code

    return 0


if __name__ == "__main__":
    sys.exit(main())
