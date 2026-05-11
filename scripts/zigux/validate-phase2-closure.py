#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
CHECK_PHASE2_TESTS_README_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
CHECK_PHASE2_KCONFIG_README_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-kconfig-readme-alignment.py"
PHASE2_CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_MAKEFILE = ROOT / "zigux" / "Makefile"

PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
]

PHASE2_FIXDEP_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_FIXDEP_EMBEDDED_NUL_GUARD=fixdep.zig truncates depfile parsing at the first embedded NUL and keeps dep parsing skips bytes after the first embedded NUL as the bounded parser guard",
]

PHASE2_GENKSYMS_REQUIRED_SOURCE_MARKERS = [
    "shared genksyms bridge selftest-alignment self-test: `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test`",
    "shared genksyms bridge selftest-alignment gate: `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py`",
    "direct genksyms bridge self-test: `python3 scripts/zigux/check-genksyms-bridge.py --self-test`",
    "direct genksyms bridge gate: `python3 scripts/zigux/check-genksyms-bridge.py`",
    "the dedicated Phase 2 `genksyms` bridge packet remains the live `27-case` bridge surface under `zigux/tests/fixtures/genksyms_bridge/`",
]

PHASE2_MAKEFILE_RUN_COUNTS = {
    "scripts/zigux/check-zig-toolchain.py": 1,
    "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
    "scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-kconfig-readme-alignment.py": 1,
}


def require_files(paths: list[Path]) -> list[str]:
    missing: list[str] = []
    for path in paths:
        if not path.exists():
            missing.append(str(path.relative_to(ROOT)))
    return missing


def validate_required_markers(text: str, markers: list[str], label: str) -> list[str]:
    return [f"{label}:missing:{marker}" for marker in markers if marker not in text]


def validate_exact_makefile_runs(makefile_text: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in makefile_text.splitlines()]
    for command, expected in PHASE2_MAKEFILE_RUN_COUNTS.items():
        expected_line = f"cd $(ZIGUX_ROOT) && $(PYTHON) {command}"
        count = sum(1 for line in lines if line == expected_line)
        if count != expected:
            issues.append(f"makefile:exact_count:{command}:count={count}:expected={expected}")
    return issues


def run(cmd: list[str]) -> int:
    completed = subprocess.run(cmd, cwd=ROOT, check=False)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current live Phase 2 closure packet on current master."
    )
    parser.add_argument("--self-test", action="store_true", help="Run closure-validator self coverage.")
    args = parser.parse_args()

    required = [
        CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE,
        CHECK_PHASE2_TESTS_README_ALIGNMENT,
        CHECK_PHASE2_KCONFIG_README_ALIGNMENT,
        PHASE2_CLOSURE_DOC,
        PHASE2_MAKEFILE,
    ]
    missing = require_files(required)
    if missing:
        label = "PHASE2_CLOSURE_VALIDATION_SELF_TEST" if args.self_test else "PHASE2_CLOSURE_VALIDATION"
        print(f"{label}=fail")
        print("PHASE2_CLOSURE_VALIDATION_MISSING_FILES_START")
        for item in missing:
            print(item)
        print("PHASE2_CLOSURE_VALIDATION_MISSING_FILES_END")
        return 1

    closure_text = PHASE2_CLOSURE_DOC.read_text(encoding="utf-8")
    makefile_text = PHASE2_MAKEFILE.read_text(encoding="utf-8")

    issues: list[str] = []
    issues.extend(
        validate_required_markers(
            closure_text,
            PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS,
            "phase2_closure",
        )
    )
    issues.extend(
        validate_required_markers(
            closure_text,
            PHASE2_FIXDEP_REQUIRED_SOURCE_MARKERS,
            "phase2_closure",
        )
    )
    issues.extend(
        validate_required_markers(
            closure_text,
            PHASE2_GENKSYMS_REQUIRED_SOURCE_MARKERS,
            "phase2_closure",
        )
    )
    issues.extend(validate_exact_makefile_runs(makefile_text))

    if args.self_test:
        if issues:
            print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=fail")
            for issue in issues:
                print(issue)
            return 1
        print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
        print("PHASE2_CLOSURE_VALIDATION_SELF_TEST_CHECK_COUNT=15")
        return 0

    if issues:
        print("PHASE2_CLOSURE_VALIDATION=fail")
        for issue in issues:
            print(issue)
        return 1

    commands = [
        [sys.executable, str(CHECK_PHASE2_TESTS_README_ALIGNMENT)],
        [sys.executable, str(CHECK_PHASE2_KCONFIG_README_ALIGNMENT)],
        [sys.executable, str(CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE)],
    ]
    for command in commands:
        if run(command) != 0:
            print("PHASE2_CLOSURE_VALIDATION=fail")
            print(f"PHASE2_CLOSURE_VALIDATION_FAILED_COMMAND={' '.join(command[1:])}")
            return 1

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print("PHASE2_CLOSURE_VALIDATION_COMMAND_COUNT=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
