#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FIXDEP_GATE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-fixdep-gate.py"
FIXDEP_DIFF_CHECKER = ROOT / "scripts" / "zigux" / "check-fixdep-diff.py"
PHASE2_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
PHASE2_CROSS_SELFTEST_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
)
PHASE2_KCONFIG_SELFTEST_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py"
)
PHASE2_TOOL_MANIFEST_PACKET_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest-packets.py"
)
TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
TESTS_README_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
)
KCONFIG_README_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-readme-alignment.py"
)

PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_MARKER = "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass"
PHASE2_TOOLCHAIN_PIN_SCOPE_MARKER = "PHASE2_TOOLCHAIN_PIN_SCOPE=pass"
PHASE2_VALIDATION_COMMAND_SPECS = (
    (TESTS_README_ALIGNMENT_CHECKER, "--self-test"),
    (TESTS_README_ALIGNMENT_CHECKER,),
    (KCONFIG_README_ALIGNMENT_CHECKER, "--self-test"),
    (KCONFIG_README_ALIGNMENT_CHECKER,),
    (PHASE2_KCONFIG_SELFTEST_ALIGNMENT_CHECKER, "--self-test"),
    (PHASE2_KCONFIG_SELFTEST_ALIGNMENT_CHECKER,),
    (FIXDEP_GATE_CHECKER, "--self-test"),
    (FIXDEP_GATE_CHECKER,),
    (FIXDEP_DIFF_CHECKER, "--self-test"),
    (FIXDEP_DIFF_CHECKER,),
    (PHASE2_CROSS_CHECKER, "--self-test"),
    (PHASE2_CROSS_CHECKER,),
    (PHASE2_CROSS_SELFTEST_ALIGNMENT_CHECKER, "--self-test"),
    (PHASE2_CROSS_SELFTEST_ALIGNMENT_CHECKER,),
    (PHASE2_TOOL_MANIFEST_PACKET_CHECKER, "--self-test"),
    (PHASE2_TOOL_MANIFEST_PACKET_CHECKER,),
    (TOOLCHAIN_PIN_SCOPE_CHECKER, "--self-test"),
    (TOOLCHAIN_PIN_SCOPE_CHECKER,),
)
PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT = 18


def build_validation_commands() -> list[list[str]]:
    return [[sys.executable, str(spec[0]), *spec[1:]] for spec in PHASE2_VALIDATION_COMMAND_SPECS]


def collect_command_inventory_issues() -> list[str]:
    issues: list[str] = []
    commands = build_validation_commands()
    if len(commands) != PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT:
        issues.append(
            "phase2_validation_commands:count="
            f"{len(commands)}:expected={PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT}"
        )

    tails = []
    for command in commands:
        tail_parts: list[str] = []
        for part in command[1:]:
            path = Path(part)
            if path.is_absolute():
                try:
                    tail_parts.append(str(path.relative_to(ROOT)))
                    continue
                except ValueError:
                    pass
            tail_parts.append(part)
        tails.append(" ".join(tail_parts))
    if len(set(tails)) != len(tails):
        issues.append("phase2_validation_commands:duplicate_command_tail")

    expected_tails = {
        "scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test",
        "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-fixdep-gate.py --self-test",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py --self-test",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/check-phase2-cross.py --self-test",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
        "scripts/zigux/check-phase2-tool-manifest-packets.py",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    }
    for tail in sorted(expected_tails):
        if tail not in tails:
            issues.append(f"phase2_validation_commands:missing:{tail}")
    return issues


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
        description="Validate the current live Phase 2 deterministic gate packet on current master."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Check that the live Phase 2 validator packet is present.",
    )
    args = parser.parse_args()

    required = [
        ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
        ROOT / "Documentation" / "zigux" / "README.md",
        ROOT / "Documentation" / "zigux" / "phase2-closure.md",
        ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md",
        ROOT / "Documentation" / "zigux" / "review-checklist.md",
        ROOT / "scripts" / "zigux" / "README.md",
        ROOT / "scripts" / "zigux" / "check-phase2-cross.py",
        ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
        ROOT / "scripts" / "zigux" / "check-phase2-fixdep-gate.py",
        ROOT / "scripts" / "zigux" / "check-phase2-kconfig-readme-alignment.py",
        ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
        ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
        ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest-packets.py",
        ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py",
        ROOT / "scripts" / "zigux" / "check-fixdep-diff.py",
        ROOT / "scripts" / "zigux" / "check-zig-toolchain.py",
        ROOT / "scripts" / "zigux" / "fixdep.zig",
        ROOT / "scripts" / "zigux" / "install-zig.py",
        ROOT / "scripts" / "zigux" / "validate-phase2-closure.py",
        ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json",
        ROOT / "zigux" / "Makefile",
        ROOT / "zigux" / "tests" / "README.md",
        ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
        ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
        ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json",
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

    command_issues = collect_command_inventory_issues()
    if command_issues:
        label = "PHASE2_VALIDATION_SELF_TEST" if args.self_test else "PHASE2_VALIDATION"
        print(f"{label}=fail")
        for issue in command_issues:
            print(issue)
        return 1

    if args.self_test:
        print("PHASE2_VALIDATION_SELF_TEST=pass")
        print(f"PHASE2_VALIDATION_SELF_TEST_REQUIRED_FILE_COUNT={len(required)}")
        print(
            "PHASE2_VALIDATION_SELF_TEST_COMMAND_COUNT="
            f"{PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT}"
        )
        print(PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_MARKER)
        print(PHASE2_TOOLCHAIN_PIN_SCOPE_MARKER)
        return 0

    commands = build_validation_commands()
    for command in commands:
        if run(command) != 0:
            print("PHASE2_VALIDATION=fail")
            print(f"PHASE2_VALIDATION_FAILED_COMMAND={' '.join(command[1:])}")
            return 1

    print("PHASE2_VALIDATION=pass")
    print(f"PHASE2_VALIDATION_COMMAND_COUNT={PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
