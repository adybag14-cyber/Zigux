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
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
    "scripts/zigux/check-phase3-xarray-slot.py",
    "Documentation/zigux/phase3-idr-slot-slice.md",
    "zigux/helpers/idr_slot_view.zig",
    "zigux/tests/phase3_idr_slot_starter_packet.zig",
    "zigux/tests/phase3_idr_slot_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_idr_slot_manifest.json",
    "scripts/zigux/check-phase3-idr-slot-starter-packet.py",
    "zigux/tests/phase3_idr_slot_dump.zig",
    "zigux/tests/phase3_idr_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_idr_slot/expected.json",
    "scripts/zigux/check-phase3-idr-slot.py",
    "one focused helper-local `idr_slot` classifier slice with both starter-packet and fixture-backed dump parity coverage",
    "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
    "scripts/zigux/check-phase3-bitmap-cpumask.py",
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test",
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "Documentation/zigux/phase3-list-hlist-slice.md",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "zigux/tests/phase3_list_hlist_starter_packet.zig",
    "zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_list_hlist_manifest.json",
    "scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "zigux/tests/phase3_list_hlist_dump.zig",
    "zigux/tests/phase3_list_hlist_dump_build.zig",
    "zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c",
    "zigux/tests/fixtures/phase3_list_hlist/expected.json",
    "scripts/zigux/check-phase3-list-hlist.py",
    "python3 scripts/zigux/check-phase3-list-hlist.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc",
    "zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig",
    "Documentation/zigux/phase3-policy-slice.md",
    "include/zigux/abi.h",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "scripts/zigux/check-phase3-policy-dump.py",
    "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-dump.py",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "one focused helper-local `xarray_slot` classifier slice with both starter-packet and fixture-backed dump parity coverage",
    "one bounded helper-local `bitmap` / `cpumask` starter slice with manifest-backed replay coverage",
    "one bounded helper-local `list_head` / `hlist` starter-plus-dump slice with dedicated replay coverage",
    "It now separately ships the dedicated `Documentation/zigux/phase3-abi-header-family-survey.md` note together with `scripts/zigux/validate-phase3-abi-header-family-survey.py` as bounded header-family follow-through, plus the focused `Documentation/zigux/phase3-abi-h-boundary-next-step.md` note as the packet-local `include/zigux/abi.h` companion. It does not currently ship the broader shared Phase 3 replay packet itself, even though the shared `scripts/zigux/validate-phase3.py` validator entrypoint and `scripts/zigux/check-phase3-abi.py` shared ABI checker are directly readable on current `master`, current `master` also directly serves the bounded catalog helper at `scripts/zigux/phase3_catalog.py` together with the shared ABI manifest at `zigux/tests/fixtures/phase3_abi_manifest.json`, and the aligned docs-root, review-checklist, tests-root, and scripts-root reminder surfaces now keep that broader shared-summary drift closed.",
    "Current `master` also directly serves the returned `Documentation/zigux/phase3-linux-zigux-header-governance.md` ownership note beside that adjacent export/UAPI layout replay pair, so the bounded Linux-facing relay is reviewable without turning this validator-support packet into the semantic owner of the separately landed header-family survey follow-through.",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/phase3_catalog.py",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Keep the shared Phase 3 reminder packet anchored to those seven current-tree-backed slices until additional broader export/UAPI survey or shared replay proof lands.",
    "Current `master` also directly serves the focused `Documentation/zigux/phase3-abi-h-boundary-next-step.md` note as the packet-local `include/zigux/abi.h` companion beside the dedicated `Documentation/zigux/phase3-abi-header-family-survey.md` plus `scripts/zigux/validate-phase3-abi-header-family-survey.py` follow-through and `Documentation/zigux/phase3-linux-zigux-header-governance.md`, but those returned same-family surfaces should not be used here to imply that the broader shared Phase 3 replay packet has returned.",
    "Current `master` does still ship the separately readable shared validator entrypoint through `scripts/zigux/validate-phase3.py` together with the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, and it also directly serves `scripts/zigux/phase3_catalog.py` together with `zigux/tests/fixtures/phase3_abi_manifest.json`, but those shared validation, catalog, and manifest surfaces should not be used here to imply that the broader validator-support or shared replay packet has returned beyond that bounded survey-plus-next-step companion packet already enumerated here.",
    "Current `master` also keeps this note's dedicated packet-local validator explicit through `scripts/zigux/validate-phase3-validator-support-surface.py`, and that validator should stay aligned with this note rather than being left implicit behind the broader shared `scripts/zigux/validate-phase3.py` entrypoint.",
    "Current `master` does still ship the adjacent low-level-wrapper packet through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/helpers/unsafe_policy.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`, and it separately ships the adjacent export/UAPI layout replay pair through `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig`, but those separate wrapper and replay surfaces should not be used here to imply that the broader validator-support or export/UAPI survey packet has returned.",
    "Current `master` also directly serves the same focused policy slice through the reviewer-readable dump route at `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/fixtures/phase3_policy_dump_expected.txt`, and `scripts/zigux/check-phase3-policy-dump.py`, so the bounded policy packet now exposes both its starter replay and its focused dump companion without widening this note into MMIO, low-level-wrapper, or broader runtime-shim ownership.",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
    "That adjacent low-level-wrapper packet now keeps `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `make -C zigux phase3-low-level-wrappers-test` directly readable on current `master`, but those returned wrapper-local surfaces should stay adjacent here instead of being promoted into broader validator support.",
    "`Documentation/zigux/README.md` now keeps the validator-support, `err_ptr` / `xarray`, bitmap/cpumask, list/hlist, `xarray_slot`, shared catalog companion, and bounded export/UAPI plus header-family reminder surfaces explicit beside the starter, policy, low-level-wrapper, and layout-replay packet, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.",
    "`zigux/tests/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the packet-local export/UAPI survey note, validator, focused export/UAPI layout replay, and direct C smoke companion family, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.",
    "`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root, review-checklist, tests-root, and scripts-root summaries, keeps the returned header-family survey follow-through explicit as a same-family companion, and records that no same-lane shared-summary drift remains on current `master`.",
    "`scripts/zigux/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the shared ABI manifest companion, export/UAPI layout replay pair, named Linux-side boundary-header helper family, and direct C smoke proof, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.",
    "records the separately landed linux-header governance note without promoting it into broader validator support",
    "records the separately landed low-level-wrapper packet without promoting it into broader validator support",
    "records the aligned docs-root, review-checklist, tests-root, and scripts-root summaries together with the closed shared-summary drift while keeping any future scripts-root inventory follow-through separate",
    "records the separately landed header-family survey follow-through without promoting it into broader validator support",
)

REQUIRED_SHARED_GAP_MARKERS = (
    "PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the dedicated ABI header-family survey follow-through, the focused abi.h next-step note, the shared ABI catalog helper plus manifest-backed inventory companion, the bounded bitmap/cpumask and list/hlist helper slices, the shared tests-root export/UAPI layout route, the named Linux-side boundary-header helper family plus validation relay, and the direct C smoke proof; the docs-root reminder, shared review checklist, tests-root reminder, and scripts-root reminder are now aligned on those already-returned helper-local slices, and no same-lane shared-summary drift remains on current master`",
    "PHASE3_SHARED_REMINDER_NEXT_STEP=keep this note parked unless a fresh current-master reread shows a smaller one-file shared-summary drift around the returned export/UAPI, bitmap/cpumask, list/hlist, shared tests-root layout, named boundary-header helper, or direct C smoke packet`",
    "`Documentation/zigux/README.md` now stays aligned on the returned bitmap/cpumask, list/hlist, xarray-slot, validator-support, shared catalog, policy, low-level-wrapper, and bounded export/UAPI plus header-family reminder surfaces.",
    "`Documentation/zigux/review-checklist.md` now keeps the returned bitmap/cpumask and list/hlist helper-slice wording explicit beside the bounded export/UAPI, xarray-slot, policy, low-level-wrapper, and shared-catalog packet, so the checklist no longer carries an open same-lane summary gap.",
    "`zigux/tests/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the packet-local export/UAPI survey note, validator, focused export/UAPI layout replay, and direct C smoke companion family, so the tests-root reminder no longer carries a same-lane summary gap.",
    "`scripts/zigux/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the shared ABI manifest companion, export/UAPI layout replay pair, named Linux-side boundary-header helper family, and direct C smoke proof, so the scripts-root reminder no longer carries a same-lane summary gap.",
    "The earlier shared-reminder drift is now closed for the packet-local export/UAPI survey, the dedicated header-family and abi.h follow-through, the manifest-backed catalog packet, the landed helper-local interop slices themselves, and the shared docs-root, review-checklist, tests-root, and scripts-root reminder surfaces. No smaller same-lane shared-summary drift is visible on current `master` right now.",
)

SELF_TEST_NOTE_MARKERS = (
    REQUIRED_NOTE_MARKERS[0],
    "one focused helper-local `xarray_slot` classifier slice with both starter-packet and fixture-backed dump parity coverage",
    "one focused helper-local `idr_slot` classifier slice with both starter-packet and fixture-backed dump parity coverage",
    "Documentation/zigux/phase3-idr-slot-slice.md",
    "zigux/helpers/idr_slot_view.zig",
    "scripts/zigux/check-phase3-idr-slot.py",
    "one bounded helper-local `bitmap` / `cpumask` starter slice with manifest-backed replay coverage",
    "one bounded helper-local `list_head` / `hlist` starter-plus-dump slice with dedicated replay coverage",
    "Keep the shared Phase 3 reminder packet anchored to those seven current-tree-backed slices until additional broader export/UAPI survey or shared replay proof lands.",
    "Current `master` also directly serves the same focused policy slice through the reviewer-readable dump route at `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/fixtures/phase3_policy_dump_expected.txt`, and `scripts/zigux/check-phase3-policy-dump.py`, so the bounded policy packet now exposes both its starter replay and its focused dump companion without widening this note into MMIO, low-level-wrapper, or broader runtime-shim ownership.",
    "Current `master` also keeps this note's dedicated packet-local validator explicit through `scripts/zigux/validate-phase3-validator-support-surface.py`, and that validator should stay aligned with this note rather than being left implicit behind the broader shared `scripts/zigux/validate-phase3.py` entrypoint.",
    "That adjacent low-level-wrapper packet now keeps `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `make -C zigux phase3-low-level-wrappers-test` directly readable on current `master`, but those returned wrapper-local surfaces should stay adjacent here instead of being promoted into broader validator support.",
    "`Documentation/zigux/README.md` now keeps the validator-support, `err_ptr` / `xarray`, bitmap/cpumask, list/hlist, `xarray_slot`, shared catalog companion, and bounded export/UAPI plus header-family reminder surfaces explicit beside the starter, policy, low-level-wrapper, and layout-replay packet, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.",
    "`scripts/zigux/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the shared ABI manifest companion, export/UAPI layout replay pair, named Linux-side boundary-header helper family, and direct C smoke proof, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.",
    "records the separately landed linux-header governance note without promoting it into broader validator support",
    "records the separately landed low-level-wrapper packet without promoting it into broader validator support",
    "records the separately landed header-family survey follow-through without promoting it into broader validator support",
)

SELF_TEST_GAP_MARKERS = REQUIRED_SHARED_GAP_MARKERS


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


def remove_first_occurrence(text: str, marker: str) -> str:
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    sample_note = "\n".join(REQUIRED_NOTE_MARKERS)
    sample_gap = "\n".join(REQUIRED_SHARED_GAP_MARKERS)

    missing = validate_text(sample_note, sample_gap)
    if missing:
        print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
        print("\n".join(missing))
        return 1

    for marker in SELF_TEST_NOTE_MARKERS:
        missing = validate_text(remove_first_occurrence(sample_note, marker), sample_gap)
        expected = f"missing {NOTE_PATH.as_posix()} marker: {marker}"
        if expected not in missing:
            print("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=fail")
            print(f"expected missing marker was not reported: {expected}")
            return 1

    for marker in SELF_TEST_GAP_MARKERS:
        missing = validate_text(sample_note, remove_first_occurrence(sample_gap, marker))
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
