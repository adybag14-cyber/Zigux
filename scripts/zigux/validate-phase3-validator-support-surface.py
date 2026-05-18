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
    "Current `master` now carries one bounded `dev_t` starter packet with paired `dev_t` and version bindings plus a directly readable export shim companion,",
    "one focused helper-local `err_ptr` / `xarray` interop slice with both starter-packet and fixture-backed parity coverage,",
    "one focused helper-local policy slice, and one adjacent export/UAPI layout replay pair.",
    "It does not currently ship the broader validator, export/UAPI survey, catalog, or shared Phase 3 replay packet that older reminder surfaces still name.",
    "Documentation/zigux/phase3-abi-slice.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "Documentation/zigux/phase3-policy-slice.md",
    "include/zigux/abi.h",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "Do not treat the current starter packet, its manifest-backed replay guard, its direct Zig compile replay, its starter export shim companion, its helper-local fixture-backed parity packet, the focused policy slice, or the adjacent export/UAPI layout replay pair as evidence that the broader Phase 3 ABI substrate",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/phase3_catalog.py",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Current `master` does still ship the adjacent low-level-wrapper packet through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`, and it separately ships the adjacent export/UAPI layout replay pair through `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig`, but those separate wrapper and replay surfaces should not be used here to imply that the broader validator-support or export/UAPI survey packet has returned.",
    "`Documentation/zigux/README.md` now reflects that bounded three-slice posture together with the returned notifier binding companion and adjacent export/UAPI layout replay, and should stay aligned with `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and this note.",
    "`Documentation/zigux/phase3-shared-reminder-gap.md` now records that remaining tests-root drift and keeps scripts-root inventory follow-through separate.",
    "`scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.",
    "Keep any remaining follow-up focused on the tests-root reminder surface or separate scripts-root inventory drift if that broader surface changes again. This note should not be used to imply that the broader Phase 3 ABI substrate, export/UAPI survey packet, catalog wiring, IDR/IDA family, or shared replay routes have returned.",
    "This note is limited to the current validator-support posture for Phase 3.",
    "records the separately landed low-level-wrapper packet without promoting it into broader validator support",
    "records the docs-root reminder as aligned while keeping the tests-root reminder drift explicit",
)

REQUIRED_SHARED_GAP_MARKERS = (
    "PHASE3_SHARED_REMINDER_GAP=current master now keeps the landed notifier binding companion plus one focused export-or-UAPI layout replay explicit in the dedicated ABI note, and the shared docs-root Phase 3 summary now reflects that returned surface, but the tests-root Phase 3 summary still undercounts it, so the earlier shared-reminder sentence drift is only partially closed",
    "PHASE3_SHARED_REMINDER_NEXT_STEP=refresh only the shared Phase 3 tests-root summary in zigux/tests/README.md so it explicitly includes zigux/bindings/notifier_abi.zig, the starter export shim companion, and zigux/tests/phase3_export_uapi_layout.zig plus zigux/tests/phase3_export_uapi_layout_build.zig, while keeping the broader validator, catalog, and survey routes framed as gaps",
    "`Documentation/zigux/README.md` now reflects that returned shared Phase 3 surface from the docs root.",
    "`zigux/tests/README.md` still needs the same tests-root Phase 3 summary refresh so it stops treating `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, and the focused export/UAPI layout replay as broader gaps.",
)

SELF_TEST_CASES = (
    ("note", "This note records the current validator-facing Phase 3 surface on live `master`.", f"missing {NOTE_PATH.as_posix()} marker: This note records the current validator-facing Phase 3 surface on live `master`."),
    ("note", "zigux/kernel/export_shim.zig", f"missing {NOTE_PATH.as_posix()} marker: zigux/kernel/export_shim.zig"),
    ("note", "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig", f"missing {NOTE_PATH.as_posix()} marker: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"),
    ("note", "`Documentation/zigux/README.md` now reflects that bounded three-slice posture together with the returned notifier binding companion and adjacent export/UAPI layout replay, and should stay aligned with `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and this note.", f"missing {NOTE_PATH.as_posix()} marker: `Documentation/zigux/README.md` now reflects that bounded three-slice posture together with the returned notifier binding companion and adjacent export/UAPI layout replay, and should stay aligned with `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and this note."),
    ("note", "`Documentation/zigux/phase3-shared-reminder-gap.md` now records that remaining tests-root drift and keeps scripts-root inventory follow-through separate.", f"missing {NOTE_PATH.as_posix()} marker: `Documentation/zigux/phase3-shared-reminder-gap.md` now records that remaining tests-root drift and keeps scripts-root inventory follow-through separate."),
    ("note", "Keep any remaining follow-up focused on the tests-root reminder surface or separate scripts-root inventory drift if that broader surface changes again. This note should not be used to imply that the broader Phase 3 ABI substrate, export/UAPI survey packet, catalog wiring, IDR/IDA family, or shared replay routes have returned.", f"missing {NOTE_PATH.as_posix()} marker: Keep any remaining follow-up focused on the tests-root reminder surface or separate scripts-root inventory drift if that broader surface changes again. This note should not be used to imply that the broader Phase 3 ABI substrate, export/UAPI survey packet, catalog wiring, IDR/IDA family, or shared replay routes have returned."),
    ("note", "records the docs-root reminder as aligned while keeping the tests-root reminder drift explicit", f"missing {NOTE_PATH.as_posix()} marker: records the docs-root reminder as aligned while keeping the tests-root reminder drift explicit"),
    ("gap", "PHASE3_SHARED_REMINDER_GAP=current master now keeps the landed notifier binding companion plus one focused export-or-UAPI layout replay explicit in the dedicated ABI note, and the shared docs-root Phase 3 summary now reflects that returned surface, but the tests-root Phase 3 summary still undercounts it, so the earlier shared-reminder sentence drift is only partially closed", f"missing {SHARED_REMINDER_GAP_PATH.as_posix()} marker: PHASE3_SHARED_REMINDER_GAP=current master now keeps the landed notifier binding companion plus one focused export-or-UAPI layout replay explicit in the dedicated ABI note, and the shared docs-root Phase 3 summary now reflects that returned surface, but the tests-root Phase 3 summary still undercounts it, so the earlier shared-reminder sentence drift is only partially closed"),
    ("gap", "`Documentation/zigux/README.md` now reflects that returned shared Phase 3 surface from the docs root.", f"missing {SHARED_REMINDER_GAP_PATH.as_posix()} marker: `Documentation/zigux/README.md` now reflects that returned shared Phase 3 surface from the docs root."),
    ("gap", "`zigux/tests/README.md` still needs the same tests-root Phase 3 summary refresh so it stops treating `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, and the focused export/UAPI layout replay as broader gaps.", f"missing {SHARED_REMINDER_GAP_PATH.as_posix()} marker: `zigux/tests/README.md` still needs the same tests-root Phase 3 summary refresh so it stops treating `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, and the focused export/UAPI layout replay as broader gaps."),
)

EXPECTED_SELF_TEST_CASE_COUNT = len(SELF_TEST_CASES) + 1


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


def _remove_exact_marker_line(text: str, marker: str) -> str:
    return "\n".join(line for line in text.splitlines() if line != marker)


def run_self_test() -> int:
    sample_note = "\n".join(REQUIRED_NOTE_MARKERS)
    sample_gap = "\n".join(REQUIRED_SHARED_GAP_MARKERS)

    missing = validate_text(sample_note, sample_gap)
    if missing:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("\n".join(missing))
        return 1

    for target, removed_marker, expected_missing in SELF_TEST_CASES:
        note_text = sample_note
        gap_text = sample_gap
        if target == "note":
            note_text = _remove_exact_marker_line(note_text, removed_marker)
        else:
            gap_text = _remove_exact_marker_line(gap_text, removed_marker)
        missing = validate_text(note_text, gap_text)
        if expected_missing not in missing:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print(f"expected missing marker was not reported: {expected_missing}")
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