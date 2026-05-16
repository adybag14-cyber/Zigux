#!/usr/bin/env python3
"""Validate the dedicated Phase 3 validator-support surface note."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")

REQUIRED_MARKERS = (
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/phase3_check_lib.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/run-phase3-checks.py",
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "make -C zigux phase3-validate",
    "make -C zigux phase3-selftest",
    "make -C zigux phase3-export-uapi-layout-test",
    "make -C zigux phase3-low-level-wrappers-test",
    "make -C zigux phase3",
    "shipped helper entrypoints on current `master`",
)

SELF_TEST_CASES = (
    (
        "scripts/zigux/validate-phase3-validator-support-surface.py",
        "scripts/zigux/validate-phase3-validator-support-surface.py",
    ),
    (
        "scripts/zigux/check-phase3-abi-dump-gate.py",
        "scripts/zigux/check-phase3-abi-dump-gate.py",
    ),
    (
        "scripts/zigux/validate-phase3-export-uapi-survey.py",
        "scripts/zigux/validate-phase3-export-uapi-survey.py",
    ),
    (
        "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
        "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    ),
    (
        "scripts/zigux/validate-phase3-abi-header-family-survey.py",
        "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    ),
    (
        "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
        "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    ),
    (
        "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
        "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    ),
    (
        "scripts/zigux/check-phase3-abi.py",
        "scripts/zigux/check-phase3-abi.py",
    ),
    (
        "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
        "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    ),
    (
        "Documentation/zigux/phase3-kernel-export-shim-governance.md",
        "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    ),
    (
        "zigux/tests/phase3_low_level_wrappers.zig",
        "zigux/tests/phase3_low_level_wrappers.zig",
    ),
    (
        "zigux/tests/phase3_low_level_wrappers_build.zig",
        "zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    (
        "make -C zigux phase3-low-level-wrappers-test",
        "make -C zigux phase3-low-level-wrappers-test",
    ),
    (
        "make -C zigux phase3-validate",
        "make -C zigux phase3-validate",
    ),
    (
        "make -C zigux phase3-selftest",
        "make -C zigux phase3-selftest",
    ),
    (
        "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
        "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    ),
)
EXPECTED_SELF_TEST_CASE_COUNT = len(SELF_TEST_CASES) + 1


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing note: {path}") from exc


def validate_text(text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def _remove_exact_marker_line(markers: tuple[str, ...], removed_marker: str) -> str:
    marker_lines = list(markers)
    marker_lines.remove(removed_marker)
    return "\n".join(marker_lines)


def run_self_test() -> int:
    sample = "\n".join(REQUIRED_MARKERS)
    missing = validate_text(sample)
    if missing:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("\n".join(missing))
        return 1

    for removed_marker, expected_missing in SELF_TEST_CASES:
        broken = validate_text(_remove_exact_marker_line(REQUIRED_MARKERS, removed_marker))
        if expected_missing not in broken:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print(f"expected missing marker was not reported: {expected_missing}")
            return 1

    observed_case_count = len(SELF_TEST_CASES) + 1
    if observed_case_count != EXPECTED_SELF_TEST_CASE_COUNT:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print(
            "unexpected self-test case count: "
            f"{observed_case_count} != {EXPECTED_SELF_TEST_CASE_COUNT}"
        )
        return 1

    print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=pass")
    print(
        "PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST_CASE_COUNT="
        f"{EXPECTED_SELF_TEST_CASE_COUNT}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains Documentation/zigux/",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in validator coverage without reading repo files",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    note_path = args.repo_root / NOTE_PATH
    text = load_text(note_path)
    missing = validate_text(text)
    if missing:
        for marker in missing:
            print(f"missing marker: {marker}", file=sys.stderr)
        return 1

    print(f"validated {note_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())