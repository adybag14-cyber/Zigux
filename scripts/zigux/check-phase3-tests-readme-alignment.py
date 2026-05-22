#!/usr/bin/env python3
"""Fail-close the current Phase 3 tests-root reminder alignment packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


README_PATH = Path("zigux/tests/README.md")
GAP_PATH = Path("Documentation/zigux/phase3-shared-reminder-gap.md")

REQUIRED_MARKERS = {
    README_PATH: (
        "Keep the returned bounded bitmap/cpumask packet explicit too through `Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `zigux/helpers/bitmap_view.zig`, `zigux/helpers/cpumask_view.zig`, `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`, and `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`.",
        "Keep the returned bounded list/hlist packet explicit too through `Documentation/zigux/phase3-list-hlist-slice.md`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/tests/phase3_list_hlist_starter_packet.zig`, and `zigux/tests/phase3_list_hlist_starter_packet_build.zig`.",
        "Keep the returned focused xarray-slot packet explicit too through `Documentation/zigux/phase3-xarray-slot-slice.md`, `zigux/helpers/xarray_slot_view.zig`, `zigux/tests/phase3_xarray_slot_starter_packet.zig`, `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`, `zigux/tests/phase3_xarray_slot_dump.zig`, `zigux/tests/phase3_xarray_slot_dump_build.zig`, `zigux/tests/fixtures/phase3_xarray_slot/expected.json`, `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`, and `scripts/zigux/check-phase3-xarray-slot.py`.",
    ),
    GAP_PATH: (
        "PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the dedicated ABI header-family survey follow-through, the focused abi.h next-step note, the shared ABI catalog helper plus manifest-backed inventory companion, the bounded bitmap/cpumask and list/hlist helper slices, the shared tests-root export/UAPI layout route, and the direct C smoke proof; the remaining same-lane gap is no longer missing landed helper-local code, replay surfaces, or tests-root summary coverage, but shared-summary truthfulness across the docs-root and scripts-root reminder family",
        "Documentation/zigux/README.md now stays aligned on the returned validator-support, xarray-slot, shared catalog, and bounded export/UAPI plus header-family reminder surfaces, but it still needs a smaller same-lane refresh before the returned bitmap/cpumask and list/hlist slices are named there with the same explicitness as this note.",
        "zigux/tests/README.md now keeps the returned packet-local export/UAPI survey note and validator explicit beside the starter, helper, policy, layout-replay, bitmap/cpumask, list/hlist, and xarray-slot packets, so the remaining same-lane reminder drift is no longer in the tests root.",
        "scripts/zigux/README.md remains a separate scripts-root reminder surface, and its current Phase 3 inventory aligns with the directly readable shared ABI manifest companion at `zigux/tests/fixtures/phase3_abi_manifest.json` plus the shared export/UAPI layout surfaces, but it still does not restate the returned direct C smoke pair or the returned bitmap/cpumask and list/hlist slices.",
        "No additional wider same-lane code or replay member needs to be called out here; the remaining same-lane gap is the narrower shared-summary sync for already-landed bitmap/cpumask and list/hlist wording in the docs root together with the scripts-root direct-C-smoke and helper-slice reminder.",
        "The earlier shared-reminder drift is now closed for the packet-local export/UAPI survey, the dedicated header-family and abi.h follow-through, the manifest-backed catalog packet, the landed helper-local interop slices themselves, and the tests-root reminder wording, but the shared docs-root and scripts-root summaries still undercount parts of that returned reminder family.",
        "The next same-lane follow-through is now a shared-summary refresh outside the tests root, not another slice-local implementation step: docs-root wording still needs to count the returned bitmap/cpumask and list/hlist packets honestly, and scripts-root still needs its own separate inventory-local direct-C-smoke plus helper-slice follow-through.",
    ),
}

SELF_TEST_CASES = tuple(
    (relative_path, marker)
    for relative_path, markers in REQUIRED_MARKERS.items()
    for marker in markers
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_tests_readme_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_TESTSREADME_ALIGNMENT_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_TESTSREADME_ALIGNMENT_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_TESTSREADME_ALIGNMENT_SELF_TEST=pass")
    print(
        "PHASE3_TESTSREADME_ALIGNMENT_SELF_TEST_CASE_COUNT="
        f"{1 + len(SELF_TEST_CASES)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 tests-root reminder alignment packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 tests-root reminder packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_TESTSREADME_ALIGNMENT=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / README_PATH}")
    print("PHASE3_TESTSREADME_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
