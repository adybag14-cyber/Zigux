#!/usr/bin/env python3
"""Track the bounded Phase 2 Makefile toolchain fallback gap."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "zigux" / "Makefile"
NOTE = ROOT / "Documentation" / "zigux" / "phase2-makefile-toolchain-fallback-gap.md"

ACTUAL_GAP_LINE = "ZIG_LOCAL_TOOLCHAIN := $(ZIG_PINNED_TOOLCHAIN)"
EXPECTED_FALLBACK_LINE = (
    "ZIG_LOCAL_TOOLCHAIN := $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),"
    "$(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig "
    "$(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig)))"
)

NOTE_MARKERS = (
    "The live `zigux/Makefile` line is:",
    ACTUAL_GAP_LINE,
    "The existing Phase 2 pin-scope checker expects:",
    EXPECTED_FALLBACK_LINE,
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
)


def validate_gap(makefile_text: str, note_text: str) -> list[str]:
    issues: list[str] = []

    if ACTUAL_GAP_LINE not in makefile_text:
        issues.append("Makefile no longer exposes the documented current gap line.")

    if EXPECTED_FALLBACK_LINE in makefile_text:
        issues.append("Makefile already contains the expected fallback line; retire or rewrite the gap note.")

    for marker in NOTE_MARKERS:
        if marker not in note_text:
            issues.append(f"Gap note is missing marker: {marker}")

    return issues


def run_self_test() -> int:
    gap_makefile = "\n".join(
        (
            "ZIG_PINNED_CHANNEL := 0.17.0-dev.758+748e7c5e3",
            ACTUAL_GAP_LINE,
            'ZIG ?= $(if $(ZIG_LOCAL_TOOLCHAIN),$(ZIG_LOCAL_TOOLCHAIN),zig)',
        )
    )
    note_text = "\n".join(NOTE_MARKERS)
    resolved_makefile = gap_makefile.replace(ACTUAL_GAP_LINE, EXPECTED_FALLBACK_LINE)

    cases = (
        ("gap-present", gap_makefile, note_text, []),
        (
            "resolved-needs-note-update",
            resolved_makefile,
            note_text,
            ["Makefile no longer exposes the documented current gap line.", "Makefile already contains the expected fallback line; retire or rewrite the gap note."],
        ),
        (
            "note-missing-marker",
            gap_makefile,
            note_text.replace("make -C zigux phase2-validate", ""),
            ["Gap note is missing marker: make -C zigux phase2-validate"],
        ),
    )

    for name, makefile_text, note_body, expected in cases:
        actual = validate_gap(makefile_text, note_body)
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
        description="Keep the bounded Phase 2 Makefile toolchain fallback gap note aligned with current repo reality."
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

    issues = validate_gap(
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
    print("PHASE2_MAKEFILE_TOOLCHAIN_FALLBACK_GAP_STATUS=documented")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
