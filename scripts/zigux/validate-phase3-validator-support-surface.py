#!/usr/bin/env python3
"""Validate the dedicated Phase 3 validator-support surface note."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
SHARED_REMINDER_GAP_PATH = Path("Documentation/zigux/phase3-shared-reminder-gap.md")

REQUIRED_NOTE_MARKERS = (
    "This note records the current validator-facing Phase 3 surface on live `master`.",
    "Documentation/zigux/phase3-abi-slice.md",
    "zigux/kernel/export_shim.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "Documentation/zigux/phase3-policy-slice.md",
    "include/zigux/abi.h",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    'It does not currently ship the broader export/UAPI survey, catalog, or shared Phase 3 replay packet that older reminder surfaces still name, even though the shared `scripts/zigux/validate-phase3.py` validator entrypoint and `scripts/zigux/check-phase3-abi.py` shared ABI checker are directly readable on current `master`.',
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/phase3_catalog.py",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    'Current `master` does still ship the separately readable shared validator entrypoint through `scripts/zigux/validate-phase3.py` together with the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, but those two shared validation surfaces should not be used here to imply that the broader validator-support, export/UAPI survey, catalog, or shared replay packet has returned.',
    'Current `master` does still ship the adjacent low-level-wrapper packet through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`, and it separately ships the adjacent export/UAPI layout replay pair through `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig`, but those separate wrapper and replay surfaces should not be used here to imply that the broader validator-support or export/UAPI survey packet has returned.',
    '`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root and tests-root reminders together while keeping scripts-root inventory work separate.',
    '`scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.',
    "records the separately landed low-level-wrapper packet without promoting it into broader validator support",
    "records the shared docs-root and tests-root reminders as aligned while keeping scripts-root inventory work separate",
)

REQUIRED_SHARED_GAP_MARKERS = (
    "PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, and the shared docs-root plus tests-root Phase 3 summaries now both reflect that return while scripts-root inventory work stays separate",
    "PHASE3_SHARED_REMINDER_NEXT_STEP=keep any future same-lane follow-through scoped to scripts/zigux/README.md inventory truthfulness, or rerun the shared-summary reread only if current master changes reopen Phase 3 reminder drift",
    '`Documentation/zigux/README.md` now keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py` explicit as returned packet-local shared reminder evidence instead of framing them as repo-reality gaps.',
    '`zigux/tests/README.md` now also keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py` explicit as returned tests-root evidence beside the starter, helper, policy, and layout-replay packet.',
    "The earlier shared-reminder drift is currently closed across the shared docs-root and tests-root summaries.",
)

SELF_TEST_NOTE_MARKERS = (
    "This note records the current validator-facing Phase 3 surface on live `master`.",
    "zigux/kernel/export_shim.zig",
    'It does not currently ship the broader export/UAPI survey, catalog, or shared Phase 3 replay packet that older reminder surfaces still name, even though the shared `scripts/zigux/validate-phase3.py` validator entrypoint and `scripts/zigux/check-phase3-abi.py` shared ABI checker are directly readable on current `master`.',
    'Current `master` does still ship the separately readable shared validator entrypoint through `scripts/zigux/validate-phase3.py` together with the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, but those two shared validation surfaces should not be used here to imply that the broader validator-support, export/UAPI survey, catalog, or shared replay packet has returned.',
    'Current `master` does still ship the adjacent low-level-wrapper packet through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`, and it separately ships the adjacent export/UAPI layout replay pair through `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig`, but those separate wrapper and replay surfaces should not be used here to imply that the broader validator-support or export/UAPI survey packet has returned.',
    '`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root and tests-root reminders together while keeping scripts-root inventory work separate.',
    '`scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.',
)

SELF_TEST_GAP_MARKERS = (
    "PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, and the shared docs-root plus tests-root Phase 3 summaries now both reflect that return while scripts-root inventory work stays separate",
    "PHASE3_SHARED_REMINDER_NEXT_STEP=keep any future same-lane follow-through scoped to scripts/zigux/README.md inventory truthfulness, or rerun the shared-summary reread only if current master changes reopen Phase 3 reminder drift",
    "The earlier shared-reminder drift is currently closed across the shared docs-root and tests-root summaries.",
)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing file: {path}") from exc


def validate_text(note_text: str, gap_text: str) -> list[str]:
    missing: list[str] = []
    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            missing.append(f"missing {NOTE_PATH.as_posix()} marker: {marker}")
    for marker in REQUIRED_SHARED_GAP_MARKERS:
        if marker not in gap_text:
            missing.append(
                f"missing {SHARED_REMINDER_GAP_PATH.as_posix()} marker: {marker}"
            )
    return missing


def remove_exact_line(text: str, marker: str) -> str:
    return "\n".join(line for line in text.splitlines() if line != marker)


def run_self_test() -> int:
    sample_note = "\n".join(REQUIRED_NOTE_MARKERS)
    sample_gap = "\n".join(REQUIRED_SHARED_GAP_MARKERS)

    missing = validate_text(sample_note, sample_gap)
    if missing:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("\n".join(missing))
        return 1

    for marker in SELF_TEST_NOTE_MARKERS:
        missing = validate_text(remove_exact_line(sample_note, marker), sample_gap)
        expected = f"missing {NOTE_PATH.as_posix()} marker: {marker}"
        if expected not in missing:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print(f"expected missing marker was not reported: {expected}")
            return 1

    for marker in SELF_TEST_GAP_MARKERS:
        missing = validate_text(sample_note, remove_exact_line(sample_gap, marker))
        expected = f"missing {SHARED_REMINDER_GAP_PATH.as_posix()} marker: {marker}"
        if expected not in missing:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print(f"expected missing marker was not reported: {expected}")
            return 1

    print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=pass")
    print(
        "PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST_CASE_COUNT="
        f"{1 + len(SELF_TEST_NOTE_MARKERS) + len(SELF_TEST_GAP_MARKERS)}"
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

    note_text = load_text(args.repo_root / NOTE_PATH)
    gap_text = load_text(args.repo_root / SHARED_REMINDER_GAP_PATH)
    missing = validate_text(note_text, gap_text)
    if missing:
        for marker in missing:
            print(marker, file=sys.stderr)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    print(f"validated {args.repo_root / SHARED_REMINDER_GAP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
