#!/usr/bin/env python3
"""Fail-close the shared Phase 3 xarray-slot reminder packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

DOCS_README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
SLICE_NOTE_PATH = Path("Documentation/zigux/phase3-xarray-slot-slice.md")
VALIDATOR_SUPPORT_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")

REQUIRED_MARKERS = {
    DOCS_README_PATH: (
        "Documentation/zigux/phase3-xarray-slot-slice.md",
        "Documentation/zigux/phase3-validator-support-surface.md",
        "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
        "scripts/zigux/check-phase3-xarray-slot.py",
        "zigux/helpers/xarray_slot_view.zig",
        "zigux/tests/phase3_xarray_slot_starter_packet.zig",
        "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
        "current `master` directly serves the focused `xarray_slot` packet through `zigux/helpers/xarray_slot_view.zig`, `zigux/tests/phase3_xarray_slot_starter_packet.zig`, `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`, `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`, `zigux/tests/phase3_xarray_slot_dump.zig`, `zigux/tests/phase3_xarray_slot_dump_build.zig`, `zigux/tests/fixtures/phase3_xarray_slot/expected.json`, and `scripts/zigux/check-phase3-xarray-slot.py`, so keep those helper-local slices explicit here instead of leaving them parked only inside packet-local validator wording.",
    ),
    REVIEW_CHECKLIST_PATH: (
        "Documentation/zigux/phase3-xarray-slot-slice.md",
        "Documentation/zigux/phase3-validator-support-surface.md",
        "scripts/zigux/validate-phase3-validator-support-surface.py",
        "scripts/zigux/check-phase3-selftest-surface.py",
        "scripts/zigux/check-phase3-readme-tooling-inventory.py",
        "scripts/zigux/validate-phase3-abi-header-family-survey.py",
        "Documentation/zigux/phase3-abi-header-family-survey.md",
        "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
        "if the change touches the shared Phase 3 ABI/runtime packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-xarray-slot-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase3-selftest-surface.py`, `scripts/zigux/check-phase3-readme-tooling-inventory.py`, `scripts/zigux/validate-phase3-validator-support-surface.py`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/phase3_catalog.py`, `scripts/zigux/check-phase3-catalog-selftest.py`, `scripts/zigux/generate-phase3-check-wrappers.py`, `zigux/tests/fixtures/phase3_abi_manifest.json`, and `zigux/tests/phase3_export_uapi_layout.zig` still agree on the current bounded starter, helper, policy, validator-support, export/UAPI, layout-replay, low-level-wrapper, catalog, manifest-backed inventory, linux-header-governance, returned header-family survey follow-through, and wrapper-retirement packet, keep `scripts/zigux/validate-phase3-abi-header-family-survey.py` and `Documentation/zigux/phase3-abi-header-family-survey.md` explicit as the current dedicated header-family survey companion beside `Documentation/zigux/phase3-linux-zigux-header-governance.md`, keep `Documentation/zigux/phase3-abi-h-boundary-next-step.md` explicit as the current focused abi.h next-step companion beside that dedicated survey and governance note, and keep any broader shared replay or broader header-family completion claims framed as repo-reality gaps until current `master` materializes them again?",
    ),
    TESTS_README_PATH: (
        "Documentation/zigux/phase3-xarray-slot-slice.md",
        "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
        "scripts/zigux/check-phase3-xarray-slot.py",
        "zigux/tests/phase3_xarray_slot_starter_packet.zig",
        "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
        "zigux/tests/phase3_xarray_slot_dump.zig",
        "zigux/tests/phase3_xarray_slot_dump_build.zig",
        "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
        "keep the current docs-root Phase 3 reminder packet should stay parked on `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-xarray-slot-slice.md`",
    ),
    SCRIPTS_README_PATH: (
        "Documentation/zigux/phase3-xarray-slot-slice.md",
        "Documentation/zigux/phase3-validator-support-surface.md",
        "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
        "scripts/zigux/check-phase3-xarray-slot.py",
        "scripts/zigux/check-phase3-selftest-surface.py",
        "scripts/zigux/run-phase3-checks.py",
        "scripts/zigux/validate_phase3_selftest.py",
        "zigux/helpers/xarray_slot_view.zig",
        "Phase 3 flow - the current scripts-root ABI/runtime packet stays reviewable through the bounded `dev_t` starter packet, the focused helper-local `err_ptr` / `xarray` slice, the directly readable `xarray_slot` starter-and-checker packet, the focused policy slice with the returned notifier binding companion plus the dedicated policy-dump and policy-unsafe survey guards, the dedicated validator-support and selftest reminder guards, the adjacent low-level-wrapper packet, the packet-local export/UAPI survey note plus validator, the directly readable catalog helper, and the dedicated export/UAPI layout replay pair instead of rebuilding the broader export/UAPI, catalog-selftest, closure, or shared replay story from routes that current `master` still does not serve",
    ),
    SLICE_NOTE_PATH: (
        "Documentation/zigux/phase3-validator-support-surface.md",
        "zigux/helpers/xarray_slot_view.zig",
        "zigux/tests/phase3_xarray_slot_starter_packet.zig",
        "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
        "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
        "zigux/tests/phase3_xarray_slot_dump.zig",
        "zigux/tests/phase3_xarray_slot_dump_build.zig",
        "zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
        "scripts/zigux/check-phase3-xarray-slot.py",
        "The docs-root xarray-slot slice note is now landed, and `zigux/tests/fixtures/phase3_xarray_slot_manifest.json` keeps the remaining nearby repo-reality follow-up narrowed to `Documentation/zigux/phase3-validator-support-surface.md` and `scripts/zigux/validate-phase3.py`.",
    ),
    VALIDATOR_SUPPORT_PATH: (
        "Documentation/zigux/phase3-xarray-slot-slice.md",
        "zigux/helpers/xarray_slot_view.zig",
        "zigux/tests/phase3_xarray_slot_starter_packet.zig",
        "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
        "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
        "zigux/tests/phase3_xarray_slot_dump.zig",
        "zigux/tests/phase3_xarray_slot_dump_build.zig",
        "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
        "scripts/zigux/check-phase3-xarray-slot.py",
        "one focused helper-local `xarray_slot` classifier slice with both starter-packet and fixture-backed dump parity coverage",
        "Current `master` also keeps this note's dedicated packet-local validator explicit through `scripts/zigux/validate-phase3-validator-support-surface.py`, and that validator should stay aligned with this note rather than being left implicit behind the broader shared `scripts/zigux/validate-phase3.py` entrypoint.",
    ),
}

SELF_TEST_CASES = (
    (DOCS_README_PATH, REQUIRED_MARKERS[DOCS_README_PATH][-1]),
    (REVIEW_CHECKLIST_PATH, REQUIRED_MARKERS[REVIEW_CHECKLIST_PATH][-1]),
    (TESTS_README_PATH, "zigux/tests/phase3_xarray_slot_dump_build.zig"),
    (SCRIPTS_README_PATH, REQUIRED_MARKERS[SCRIPTS_README_PATH][0]),
    (SLICE_NOTE_PATH, REQUIRED_MARKERS[SLICE_NOTE_PATH][-1]),
    (VALIDATOR_SUPPORT_PATH, REQUIRED_MARKERS[VALIDATOR_SUPPORT_PATH][-1]),
)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing file: {path}") from exc


def validate_texts(texts: dict[Path, str]) -> list[str]:
    issues: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = texts.get(rel_path)
        if text is None:
            issues.append(f"missing phase3 xarray-slot shared-summary file: {rel_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(
                    "missing "
                    + rel_path.as_posix()
                    + " marker: "
                    + marker
                )
    return issues


def validate_repo(repo_root: Path) -> list[str]:
    texts = {rel_path: load_text(repo_root / rel_path) for rel_path in REQUIRED_MARKERS}
    return validate_texts(texts)


def run_self_test() -> int:
    sample_texts = {
        rel_path: "\n".join(markers)
        for rel_path, markers in REQUIRED_MARKERS.items()
    }

    issues = validate_texts(sample_texts)
    if issues:
        print("PHASE3_XARRAY_SLOT_SHARED_SUMMARY_SELF_TEST=fail")
        print("\n".join(issues))
        return 1

    for rel_path, marker in SELF_TEST_CASES:
        mutated = dict(sample_texts)
        mutated[rel_path] = mutated[rel_path].replace(marker, "", 1)
        issues = validate_texts(mutated)
        expected = f"missing {rel_path.as_posix()} marker: {marker}"
        if expected not in issues:
            print("PHASE3_XARRAY_SLOT_SHARED_SUMMARY_SELF_TEST=fail")
            print(f"expected missing marker was not reported: {expected}")
            return 1

    print("PHASE3_XARRAY_SLOT_SHARED_SUMMARY_SELF_TEST=pass")
    print(
        "PHASE3_XARRAY_SLOT_SHARED_SUMMARY_SELF_TEST_CASE_COUNT="
        f"{1 + len(SELF_TEST_CASES)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 3 xarray-slot reminder packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 reminder files",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_XARRAY_SLOT_SHARED_SUMMARY=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_XARRAY_SLOT_SHARED_SUMMARY=pass")
    print(f"validated {args.repo_root / DOCS_README_PATH}")
    print(f"validated {args.repo_root / REVIEW_CHECKLIST_PATH}")
    print(f"validated {args.repo_root / TESTS_README_PATH}")
    print(f"validated {args.repo_root / SCRIPTS_README_PATH}")
    print(f"validated {args.repo_root / SLICE_NOTE_PATH}")
    print(f"validated {args.repo_root / VALIDATOR_SUPPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
