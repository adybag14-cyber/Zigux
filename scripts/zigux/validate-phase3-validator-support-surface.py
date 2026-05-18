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
    "one focused helper-local policy slice with a reusable layout guard and bounded narrow-surface cross-check, and one adjacent export/UAPI layout replay pair.",
    "It does not currently ship the broader export/UAPI survey, catalog, or shared Phase 3 replay packet that older reminder surfaces still name, even though the shared `scripts/zigux/validate-phase3.py` validator entrypoint is directly readable on current `master`.",
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
    "Do not treat the current starter packet, its manifest-backed replay guard, its direct Zig compile replay, its starter export shim companion, its helper-local fixture-backed parity packet, the focused policy slice, the directly readable shared validator entrypoint, or the adjacent export/UAPI layout replay pair as evidence that the broader Phase 3 ABI substrate",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/phase3_catalog.py",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Current `master` does still ship the separately readable shared validator entrypoint through `scripts/zigux/validate-phase3.py`, but that single entrypoint should not be used here to imply that the broader validator-support, export/UAPI survey, catalog, or shared replay packet has returned.",
    "Current `master` does still ship the adjacent low-level-wrapper packet through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`, and it separately ships the adjacent export/UAPI layout replay pair through `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig`, but those separate wrapper and replay surfaces should not be used here to imply that the broader validator-support or export/UAPI survey packet has returned.",
    "`Documentation/zigux/README.md` now reflects that bounded three-slice posture together with the returned notifier binding companion and adjacent export/UAPI layout replay, and should stay aligned with `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and this note.",
    "`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root and tests-root shared reminder packet while keeping scripts-root inventory follow-through separate.",
    "`scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.",
    "Keep any remaining follow-up focused on separate scripts-root inventory drift or a fresh shared-summary reread only if that broader surface changes again. This note should not be used to imply that the broader Phase 3 ABI substrate, export/UAPI survey packet, catalog wiring, IDR/IDA family, or shared replay routes have returned.",
    "This note is limited to the current validator-support posture for Phase 3.",
    "records the separately landed low-level-wrapper packet without promoting it into broader validator support",
    "records the shared docs-root and tests-root reminders as aligned while keeping scripts-root follow-through separate",
)

REQUIRED_SHARED_GAP_MARKERS = (
    "PHASE3_SHARED_REMINDER_GAP=current master keeps the docs-root and tests-root Phase 3 summaries aligned with the landed notifier binding companion, bounded kernel-export-shim note, focused export/UAPI layout replay, low-level-wrapper reminder packet, and separately readable shared validator entrypoint",
    "PHASE3_SHARED_REMINDER_NEXT_STEP=leave future same-lane follow-through parked unless a fresh reread shows a different bounded Phase 3 reminder surface changed again",
    "`Documentation/zigux/README.md` is now aligned with the bounded current packet: it keeps `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `zigux/bindings/notifier_abi.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, and the low-level-wrapper helper-and-build surfaces explicit while still framing `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json` as repo-reality gaps.",
    "`zigux/tests/README.md` is now aligned on the returned notifier-binding, kernel-export-shim, focused export/UAPI layout replay, low-level-wrapper reminder packet, and separately readable shared validator entrypoint instead of keeping `scripts/zigux/validate-phase3.py` inside the broader repo-reality-gap list.",
    "The earlier shared-reminder drift is now closed on both the shared docs-root and tests-root summaries.",
)

SELF_TEST_CASES = (
    ("note", "This note records the current validator-facing Phase 3 surface on live `master`.", f"missing {NOTE_PATH.as_posix()} marker: This note records the current validator-facing Phase 3 surface on live `master`."),
    ("note", "zigux/kernel/export_shim.zig", f"missing {NOTE_PATH.as_posix()} marker: zigux/kernel/export_shim.zig"),
    ("note", "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig", f"missing {NOTE_PATH.as_posix()} marker: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"),
    ("note", "Current `master` does still ship the separately readable shared validator entrypoint through `scripts/zigux/validate-phase3.py`, but that single entrypoint should not be used here to imply that the broader validator-support, export/UAPI survey, catalog, or shared replay packet has returned.", f"missing {NOTE_PATH.as_posix()} marker: Current `master` does still ship the separately readable shared validator entrypoint through `scripts/zigux/validate-phase3.py`, but that single entrypoint should not be used here to imply that the broader validator-support, export/UAPI survey, catalog, or shared replay packet has returned."),
    ("note", "`Documentation/zigux/README.md` now reflects that bounded three-slice posture together with the returned notifier binding companion and adjacent export/UAPI layout replay, and should stay aligned with `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and this note.", f"missing {NOTE_PATH.as_posix()} marker: `Documentation/zigux/README.md` now reflects that bounded three-slice posture together with the returned notifier binding companion and adjacent export/UAPI layout replay, and should stay aligned with `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and this note."),
    ("note", "`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root and tests-root shared reminder packet while keeping scripts-root inventory follow-through separate.", f"missing {NOTE_PATH.as_posix()} marker: `Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root and tests-root shared reminder packet while keeping scripts-root inventory follow-through separate."),
    ("note", "Keep any remaining follow-up focused on separate scripts-root inventory drift or a fresh shared-summary reread only if that broader surface changes again. This note should not be used to imply that the broader Phase 3 ABI substrate, export/UAPI survey packet, catalog wiring, IDR/IDA family, or shared replay routes have returned.", f"missing {NOTE_PATH.as_posix()} marker: Keep any remaining follow-up focused on separate scripts-root inventory drift or a fresh shared-summary reread only if that broader surface changes again. This note should not be used to imply that the broader Phase 3 ABI substrate, export/UAPI survey packet, catalog wiring, IDR/IDA family, or shared replay routes have returned."),
    ("note", "records the shared docs-root and tests-root reminders as aligned while keeping scripts-root follow-through separate", f"missing {NOTE_PATH.as_posix()} marker: records the shared docs-root and tests-root reminders as aligned while keeping scripts-root follow-through separate"),
    ("gap", "PHASE3_SHARED_REMINDER_GAP=current master keeps the docs-root and tests-root Phase 3 summaries aligned with the landed notifier binding companion, bounded kernel-export-shim note, focused export/UAPI layout replay, low-level-wrapper reminder packet, and separately readable shared validator entrypoint", f"missing {SHARED_REMINDER_GAP_PATH.as_posix()} marker: PHASE3_SHARED_REMINDER_GAP=current master keeps the docs-root and tests-root Phase 3 summaries aligned with the landed notifier binding companion, bounded kernel-export-shim note, focused export/UAPI layout replay, low-level-wrapper reminder packet, and separately readable shared validator entrypoint"),
    ("gap", "PHASE3_SHARED_REMINDER_NEXT_STEP=leave future same-lane follow-through parked unless a fresh reread shows a different bounded Phase 3 reminder surface changed again", f"missing {SHARED_REMINDER_GAP_PATH.as_posix()} marker: PHASE3_SHARED_REMINDER_NEXT_STEP=leave future same-lane follow-through parked unless a fresh reread shows a different bounded Phase 3 reminder surface changed again"),
    ("gap", "`Documentation/zigux/README.md` is now aligned with the bounded current packet: it keeps `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `zigux/bindings/notifier_abi.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, and the low-level-wrapper helper-and-build surfaces explicit while still framing `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json` as repo-reality gaps.", f"missing {SHARED_REMINDER_GAP_PATH.as_posix()} marker: `Documentation/zigux/README.md` is now aligned with the bounded current packet: it keeps `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `zigux/bindings/notifier_abi.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, and the low-level-wrapper helper-and-build surfaces explicit while still framing `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json` as repo-reality gaps."),
    ("gap", "`zigux/tests/README.md` is now aligned on the returned notifier-binding, kernel-export-shim, focused export/UAPI layout replay, low-level-wrapper reminder packet, and separately readable shared validator entrypoint instead of keeping `scripts/zigux/validate-phase3.py` inside the broader repo-reality-gap list.", f"missing {SHARED_REMINDER_GAP_PATH.as_posix()} marker: `zigux/tests/README.md` is now aligned on the returned notifier-binding, kernel-export-shim, focused export/UAPI layout replay, low-level-wrapper reminder packet, and separately readable shared validator entrypoint instead of keeping `scripts/zigux/validate-phase3.py` inside the broader repo-reality-gap list."),
    ("gap", "The earlier shared-reminder drift is now closed on both the shared docs-root and tests-root summaries.", f"missing {SHARED_REMINDER_GAP_PATH.as_posix()} marker: The earlier shared-reminder drift is now closed on both the shared docs-root and tests-root summaries."),
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