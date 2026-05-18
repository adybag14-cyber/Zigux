#!/usr/bin/env python3
"""Validate the dedicated Phase 3 validator-support surface note."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")

REQUIRED_MARKERS = (
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
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` now all reflect that bounded three-slice posture",
    "`Documentation/zigux/phase3-shared-reminder-gap.md` now records that the earlier shared-reminder sentence drift is closed on current `master`.",
    "`scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.",
    "Keep any remaining follow-up focused on separate scripts-root inventory drift if that broader surface changes again.",
    "This note is limited to the current validator-support posture for Phase 3.",
    "records the separately landed low-level-wrapper packet without promoting it into broader validator support",
)

SELF_TEST_CASES = (
    (
        "This note records the current validator-facing Phase 3 surface on live `master`.",
        "This note records the current validator-facing Phase 3 surface on live `master`.",
    ),
    (
        "zigux/kernel/export_shim.zig",
        "zigux/kernel/export_shim.zig",
    ),
    (
        "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
        "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
    ),
    (
        "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
        "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    ),
    (
        "scripts/zigux/check-phase3-abi.py",
        "scripts/zigux/check-phase3-abi.py",
    ),
    (
        "scripts/zigux/validate-phase3-export-uapi-survey.py",
        "scripts/zigux/validate-phase3-export-uapi-survey.py",
    ),
    (
        "scripts/zigux/validate-phase3-abi-header-family-survey.py",
        "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    ),
    (
        "Documentation/zigux/phase3-abi-header-family-survey.md",
        "Documentation/zigux/phase3-abi-header-family-survey.md",
    ),
    (
        "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
        "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    ),
    (
        "Current `master` does still ship the adjacent low-level-wrapper packet through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`, and it separately ships the adjacent export/UAPI layout replay pair through `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig`, but those separate wrapper and replay surfaces should not be used here to imply that the broader validator-support or export/UAPI survey packet has returned.",
        "Current `master` does still ship the adjacent low-level-wrapper packet through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`, and it separately ships the adjacent export/UAPI layout replay pair through `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig`, but those separate wrapper and replay surfaces should not be used here to imply that the broader validator-support or export/UAPI survey packet has returned.",
    ),
    (
        "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` now all reflect that bounded three-slice posture",
        "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` now all reflect that bounded three-slice posture",
    ),
    (
        "`Documentation/zigux/phase3-shared-reminder-gap.md` now records that the earlier shared-reminder sentence drift is closed on current `master`.",
        "`Documentation/zigux/phase3-shared-reminder-gap.md` now records that the earlier shared-reminder sentence drift is closed on current `master`.",
    ),
    (
        "`scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.",
        "`scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.",
    ),
    (
        "Keep any remaining follow-up focused on separate scripts-root inventory drift if that broader surface changes again.",
        "Keep any remaining follow-up focused on separate scripts-root inventory drift if that broader surface changes again.",
    ),
    (
        "records the separately landed low-level-wrapper packet without promoting it into broader validator support",
        "records the separately landed low-level-wrapper packet without promoting it into broader validator support",
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


def _remove_exact_marker_lines(markers: tuple[str, ...], removed_marker: str) -> str:
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
        broken = validate_text(_remove_exact_marker_lines(REQUIRED_MARKERS, removed_marker))
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
