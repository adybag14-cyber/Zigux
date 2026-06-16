#!/usr/bin/env python3
"""Verify the resolved Phase 2 Makefile toolchain fallback contract."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "zigux" / "Makefile"
NOTE = ROOT / "Documentation" / "zigux" / "phase2-makefile-toolchain-fallback-gap.md"

EXPECTED_FALLBACK_LINE = (
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig "
    "$(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))"
)
EXPECTED_PINNED_LINE = "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))"

NOTE_MARKERS = (
    "**Status: resolved on current `master`.**",
    EXPECTED_FALLBACK_LINE,
    EXPECTED_PINNED_LINE,
    "zig test scripts/zigux/toolchain_policy.zig",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
)


def validate_resolved(makefile_text: str, note_text: str) -> list[str]:
    issues: list[str] = []

    if EXPECTED_FALLBACK_LINE not in makefile_text:
        issues.append("Makefile is missing the repo-local .zig-toolchain fallback line.")

    if EXPECTED_PINNED_LINE not in makefile_text:
        issues.append("Makefile is missing the pinned-then-local toolchain selection line.")

    for marker in NOTE_MARKERS:
        if marker not in note_text:
            issues.append(f"Gap note is missing marker: {marker}")

    return issues


def run_self_test() -> int:
    resolved_makefile = "\n".join(
        (
            "ZIG_PINNED_CHANNEL := 0.17.0-dev.877+a3ae499dc",
            EXPECTED_FALLBACK_LINE,
            EXPECTED_PINNED_LINE,
            'ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)',
        )
    )
    note_text = "\n".join(NOTE_MARKERS)

    cases = (
        ("resolved-present", resolved_makefile, note_text, []),
        (
            "makefile-missing-fallback",
            resolved_makefile.replace(EXPECTED_FALLBACK_LINE, ""),
            note_text,
            ["Makefile is missing the repo-local .zig-toolchain fallback line."],
        ),
        (
            "note-missing-marker",
            resolved_makefile,
            note_text.replace("make -C zigux phase2-validate", ""),
            ["Gap note is missing marker: make -C zigux phase2-validate"],
        ),
    )

    for name, makefile_text, note_body, expected in cases:
        actual = validate_resolved(makefile_text, note_body)
        if actual != expected:
            print("PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP_SELF_TEST=fail")
            print(f"CASE={name}")
            print(f"EXPECTED={expected!r}")
            print(f"ACTUAL={actual!r}")
            return 1

    print("PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP_SELF_TEST=pass")
    print("PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP_SELF_TEST_CASES=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the resolved Phase 2 Makefile toolchain fallback note aligned with current repo reality."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = [path for path in (MAKEFILE, NOTE) if not path.exists()]
    if missing:
        print("PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP=fail")
        print("MISSING_PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP_FILES_START")
        for path in missing:
            print(path.relative_to(ROOT))
        print("MISSING_PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP_FILES_END")
        return 1

    issues = validate_resolved(
        MAKEFILE.read_text(encoding="utf-8"),
        NOTE.read_text(encoding="utf-8"),
    )
    if issues:
        print("PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP=fail")
        print("PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP_ISSUES_END")
        return 1

    print("PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP=present")
    print("PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP_STATUS=resolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())