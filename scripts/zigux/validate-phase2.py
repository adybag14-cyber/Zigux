#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
TESTS_README_ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
KCONFIG_README_ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-kconfig-readme-alignment.py"

PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_MARKER = "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass"
PHASE2_TOOLCHAIN_PIN_SCOPE_MARKER = "PHASE2_TOOLCHAIN_PIN_SCOPE=pass"


def run(cmd: list[str]) -> int:
    completed = subprocess.run(cmd, cwd=ROOT, check=False)
    return completed.returncode


def require_files(paths: list[Path]) -> list[str]:
    missing: list[str] = []
    for path in paths:
        if not path.exists():
            missing.append(str(path.relative_to(ROOT)))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current live Phase 2 reminder packet on current master."
    )
    parser.add_argument("--self-test", action="store_true", help="Check that the live Phase 2 validator packet is present.")
    args = parser.parse_args()

    required = [
        TOOLCHAIN_PIN_SCOPE_CHECKER,
        TESTS_README_ALIGNMENT_CHECKER,
        KCONFIG_README_ALIGNMENT_CHECKER,
    ]
    missing = require_files(required)
    if missing:
        label = "PHASE2_VALIDATION_SELF_TEST" if args.self_test else "PHASE2_VALIDATION"
        print(f"{label}=fail")
        print("PHASE2_VALIDATION_MISSING_FILES_START")
        for item in missing:
            print(item)
        print("PHASE2_VALIDATION_MISSING_FILES_END")
        return 1

    if args.self_test:
        print("PHASE2_VALIDATION_SELF_TEST=pass")
        print("PHASE2_VALIDATION_SELF_TEST_CHECKER_COUNT=3")
        print(PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_MARKER)
        print(PHASE2_TOOLCHAIN_PIN_SCOPE_MARKER)
        return 0

    commands = [
        [sys.executable, str(TESTS_README_ALIGNMENT_CHECKER), "--self-test"],
        [sys.executable, str(TESTS_README_ALIGNMENT_CHECKER)],
        [sys.executable, str(KCONFIG_README_ALIGNMENT_CHECKER), "--self-test"],
        [sys.executable, str(KCONFIG_README_ALIGNMENT_CHECKER)],
        [sys.executable, str(TOOLCHAIN_PIN_SCOPE_CHECKER), "--self-test"],
        [sys.executable, str(TOOLCHAIN_PIN_SCOPE_CHECKER)],
    ]
    for command in commands:
        if run(command) != 0:
            print("PHASE2_VALIDATION=fail")
            print(f"PHASE2_VALIDATION_FAILED_COMMAND={' '.join(command[1:])}")
            return 1

    print("PHASE2_VALIDATION=pass")
    print("PHASE2_VALIDATION_COMMAND_COUNT=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
