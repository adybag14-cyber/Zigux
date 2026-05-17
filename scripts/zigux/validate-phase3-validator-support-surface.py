#!/usr/bin/env python3
"""Validate the dedicated Phase 3 validator-support surface note."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")

REQUIRED_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "zigux/uapi/dev_t.zig",
    "zigux/uapi/version.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "include/zigux/abi.h",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "zigux/kernel/export_shim.zig",
    "scripts/zigux/README.md still carries a broader Phase 3 packet summary and should be narrowed in a follow-on truthfulness repair",
    "zigux/tests/README.md still carries a broader Phase 3 packet summary and should be narrowed in a follow-on truthfulness repair",
    "Documentation/zigux/review-checklist.md still carries a broader Phase 3 packet prompt and should be narrowed in a follow-on truthfulness repair",
    "keep the current starter `dev_t` packet explicit here instead of implying the broader exported UAPI and validator routes",
    "future Phase 3 follow-up should land one directly readable validator, replay, or binding slice at a time",
)

SELF_TEST_CASES = (
    (("Documentation/zigux/phase3-abi-slice.md",), "Documentation/zigux/phase3-abi-slice.md"),
    (("include/linux/zigux.h",), "include/linux/zigux.h"),
    (("zigux/tests/phase3_dev_t_starter_packet_build.zig",), "zigux/tests/phase3_dev_t_starter_packet_build.zig"),
    (("scripts/zigux/validate-phase3-export-uapi-survey.py",), "scripts/zigux/validate-phase3-export-uapi-survey.py"),
    (("zigux/kernel/export_shim.zig",), "zigux/kernel/export_shim.zig"),
    (
        ("Documentation/zigux/review-checklist.md still carries a broader Phase 3 packet prompt and should be narrowed in a follow-on truthfulness repair",),
        "Documentation/zigux/review-checklist.md still carries a broader Phase 3 packet prompt and should be narrowed in a follow-on truthfulness repair",
    ),
    (
        ("future Phase 3 follow-up should land one directly readable validator, replay, or binding slice at a time",),
        "future Phase 3 follow-up should land one directly readable validator, replay, or binding slice at a time",
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


def _remove_exact_marker_lines(markers: tuple[str, ...], removed_markers: tuple[str, ...]) -> str:
    marker_lines = list(markers)
    for removed_marker in removed_markers:
        marker_lines.remove(removed_marker)
    return "\n".join(marker_lines)


def run_self_test() -> int:
    sample = "\n".join(REQUIRED_MARKERS)
    missing = validate_text(sample)
    if missing:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("\n".join(missing))
        return 1

    for removed_markers, expected_missing in SELF_TEST_CASES:
        broken = validate_text(_remove_exact_marker_lines(REQUIRED_MARKERS, removed_markers))
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
