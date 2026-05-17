#!/usr/bin/env python3
"""Validate the dedicated Phase 3 shared-reminder gap note."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

NOTE_PATH = Path("Documentation/zigux/phase3-shared-reminder-gap.md")

REQUIRED_MARKERS = (
    "This note records the remaining shared-reminder drift for Phase 3 on live `master`.",
    "Current `master` already narrows the validator-facing Phase 3 packet to the bounded starter header-family and `dev_t` slice",
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "zigux/tests/README.md",
    "Documentation/zigux/review-checklist.md",
    "Those shared reminder surfaces still describe a wider validator, export/UAPI layout, low-level-wrapper, catalog, or shared replay packet",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/phase3_catalog.py",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/kernel/export_shim.zig",
    "include/zigux/abi.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/notifier_abi.zig",
    "Narrow the shared reminder surfaces above so they agree with the current starter packet",
    "This note is limited to the remaining shared-reminder truthfulness gap.",
)

SELF_TEST_CASES = tuple((marker, marker) for marker in REQUIRED_MARKERS)
EXPECTED_SELF_TEST_CASE_COUNT = len(SELF_TEST_CASES) + 1


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing note: {path}") from exc


def validate_text(text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def _remove_exact_marker_lines(markers: tuple[str, ...], removed_marker: str) -> str:
    marker_lines = list(markers)
    marker_lines.remove(removed_marker)
    return "\n".join(marker_lines)


def run_self_test() -> int:
    sample = "\n".join(REQUIRED_MARKERS)
    missing = validate_text(sample)
    if missing:
        print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
        print("\n".join(missing))
        return 1

    for removed_marker, expected_missing in SELF_TEST_CASES:
        broken = validate_text(_remove_exact_marker_lines(REQUIRED_MARKERS, removed_marker))
        if expected_missing not in broken:
            print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
            print(f"expected missing marker was not reported: {expected_missing}")
            return 1

    observed_case_count = len(SELF_TEST_CASES) + 1
    if observed_case_count != EXPECTED_SELF_TEST_CASE_COUNT:
        print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
        print(
            "unexpected self-test case count: "
            f"{observed_case_count} != {EXPECTED_SELF_TEST_CASE_COUNT}"
        )
        return 1

    print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=pass")
    print(
        "PHASE3_SHARED_REMINDER_GAP_SELF_TEST_CASE_COUNT="
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
