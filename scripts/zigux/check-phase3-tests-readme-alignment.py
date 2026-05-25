#!/usr/bin/env python3
"""Fail-close the current Phase 3 tests-root reminder alignment packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


README_PATH = Path("zigux/tests/README.md")
GAP_PATH = Path("Documentation/zigux/phase3-shared-reminder-gap.md")

README_MARKERS = (
    "Keep the focused helper and starter packet explicit through `zigux/helpers/err_ptr.zig`, `zigux/helpers/xa_value.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`, `zigux/tests/phase3_xarray_slot_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, and `zigux/tests/phase3_policy_starter_packet_manifest.json`.",
    "keep the returned notifier-binding and focused export/UAPI layout replay pair explicit here instead of leaving `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/phase3_export_uapi_layout_build.zig` framed as broader repo-reality gaps",
    "Keep the current same-lane helper follow-through explicit too: `Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `zigux/helpers/bitmap_view.zig`, `zigux/helpers/cpumask_view.zig`, `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`, `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`, `Documentation/zigux/phase3-list-hlist-slice.md`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/tests/phase3_list_hlist_starter_packet.zig`, and `zigux/tests/phase3_list_hlist_starter_packet_build.zig`.",
    "Keep the direct rerun surface explicit through `zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`, `zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig`, `make -C zigux phase3-export-uapi-layout-test`, and `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`.",
    "Keep the broader validator, manifest, and replay-family boundary truthful: keep `scripts/zigux/validate-phase3.py`, `zigux/tests/fixtures/phase3_abi_manifest.json`, `zigux/tests/phase3_export_uapi_c_header_smoke.c`, and `python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py` reviewable as same-lane companions instead of presenting the broader validator, export/UAPI layout, low-level-wrapper, catalog, IDR, or IDA packet as shipped tests-root evidence.",
    "Tests-root reviewer prompt:",
    "- Does the bounded Phase 3 reminder keep the direct helper, starter, policy, low-level-wrapper, bitmap/cpumask, list/hlist, and export/UAPI layout packet aligned without widening into the broader shared validator, catalog, or replay family?",
)

GAP_MARKERS = (
    "PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the dedicated ABI header-family survey follow-through, the focused abi.h next-step note, the shared ABI catalog helper plus manifest-backed inventory companion, the bounded bitmap/cpumask and list/hlist helper slices, the shared tests-root export/UAPI layout route, the named Linux-side boundary-header helper family plus validation relay, and the direct C smoke proof; the docs-root reminder, shared review checklist, tests-root reminder, and scripts-root reminder are now aligned on those already-returned helper-local slices, and no same-lane shared-summary drift remains on current master",
    "PHASE3_SHARED_REMINDER_NEXT_STEP=keep this note parked unless a fresh current-master reread shows a smaller one-file shared-summary drift around the returned export/UAPI, bitmap/cpumask, list/hlist, shared tests-root layout, named boundary-header helper, or direct C smoke packet",
    "- `zigux/tests/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the packet-local export/UAPI survey note, validator, focused export/UAPI layout replay, and direct C smoke companion family, so the tests-root reminder no longer carries a same-lane summary gap.",
    "The earlier shared-reminder drift is now closed for the packet-local export/UAPI survey, the dedicated header-family and abi.h follow-through, the manifest-backed catalog packet, the landed helper-local interop slices themselves, and the shared docs-root, review-checklist, tests-root, and scripts-root reminder surfaces. No smaller same-lane shared-summary drift is visible on current `master` right now.",
    "Current `master` already keeps the returned bitmap/cpumask packet explicit through `Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `zigux/helpers/bitmap_view.zig`, `zigux/helpers/cpumask_view.zig`, `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`, and `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`, and it already keeps the returned list/hlist packet explicit through `Documentation/zigux/phase3-list-hlist-slice.md`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/tests/phase3_list_hlist_starter_packet.zig`, and `zigux/tests/phase3_list_hlist_starter_packet_build.zig`. `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` now all reflect those returned helper-local slices directly, so the next same-lane follow-through should stay parked until future boundary evidence actually lands.",
)

REQUIRED_MARKERS = {
    README_PATH: README_MARKERS,
    GAP_PATH: GAP_MARKERS,
}

SELF_TEST_CASES = tuple(
    (relative_path, marker)
    for relative_path, markers in REQUIRED_MARKERS.items()
    for marker in markers
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        target = repo_root / relative_path
        try:
            text = read_text(target)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        write_text(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_tests_readme_alignment_") as temp_dir:
        root = Path(temp_dir)
        populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_TESTS_README_ALIGNMENT_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            populate_repo(root)
            target = root / relative_path
            target.write_text(read_text(target).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_TESTS_README_ALIGNMENT_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE3_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={1 + len(SELF_TEST_CASES)}")
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
        print("PHASE3_TESTS_README_ALIGNMENT=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / README_PATH}")
    print("PHASE3_TESTS_README_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())