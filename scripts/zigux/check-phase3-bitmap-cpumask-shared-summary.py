#!/usr/bin/env python3
"""Fail-close the current shared-summary posture for the Lane 27 gap."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")
TESTS_ROOT_PATH = Path("zigux/tests/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")

REQUIRED_MARKERS = {
    DOCS_ROOT_PATH: (
        "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md`",
        "`Documentation/zigux/phase3-policy-slice.md`",
        "`Documentation/zigux/phase3-linux-zigux-header-governance.md`",
        "`zigux/helpers/mmio.zig`",
    ),
    TESTS_ROOT_PATH: (
        "## Phase 3 shared substrate packet",
        "`zigux/tests/phase3_xarray_slot_starter_packet.zig`",
        "`zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`zig build phase3-test --build-file zigux/tests/build.zig`",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the shared Phase 3 ABI/runtime packet",
        "`Documentation/zigux/phase3-errptr-xarray-slice.md`",
        "`scripts/zigux/check-phase3-catalog-selftest.py`",
        "`zigux/tests/phase3_export_uapi_layout.zig`",
    ),
}

FORBIDDEN_MARKERS = {
    DOCS_ROOT_PATH: (
        "`include/zigux/bitmap_cpumask.h`",
        "`zigux/uapi/bitmap_cpumask.zig`",
        "`zigux/bindings/bitmap_cpumask.zig`",
        "`zigux/helpers/bitmap_view.zig`",
        "`zigux/helpers/cpumask_view.zig`",
        "`zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`",
        "`zigux/tests/phase3_bitmap_cpumask_dump.zig`",
        "`scripts/zigux/check-phase3-bitmap-cpumask.py`",
    ),
    TESTS_ROOT_PATH: (
        "`zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`",
        "`zigux/tests/phase3_bitmap_cpumask_dump.zig`",
        "`scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py`",
        "`scripts/zigux/check-phase3-bitmap-cpumask.py`",
        "`zig build phase3-bitmap-cpumask`",
    ),
    REVIEW_CHECKLIST_PATH: (
        "`include/zigux/bitmap_cpumask.h`",
        "`zigux/helpers/bitmap_view.zig`",
        "`zigux/helpers/cpumask_view.zig`",
        "`scripts/zigux/check-phase3-bitmap-cpumask.py`",
        "`zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`",
    ),
}

SAMPLE_TEXT = {
    DOCS_ROOT_PATH: """# Zigux Documentation
Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-policy-slice.md` - `Documentation/zigux/phase3-linux-zigux-header-governance.md`
`zigux/helpers/mmio.zig`
""",
    TESTS_ROOT_PATH: """# zigux/tests
## Phase 3 shared substrate packet
`zigux/tests/phase3_xarray_slot_starter_packet.zig`
`zigux/tests/phase3_low_level_wrappers_build.zig`
`zig build phase3-test --build-file zigux/tests/build.zig`
""",
    REVIEW_CHECKLIST_PATH: """# Zigux Review Checklist
  * if the change touches the shared Phase 3 ABI/runtime packet
  * `Documentation/zigux/phase3-errptr-xarray-slice.md`
  * `scripts/zigux/check-phase3-catalog-selftest.py`
  * `zigux/tests/phase3_export_uapi_layout.zig`
""",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
                issues.append(
                    f"missing {relative_path.as_posix()} required marker: {marker}"
                )

        for marker in FORBIDDEN_MARKERS[relative_path]:
            if marker in text:
                issues.append(
                    f"unexpected {relative_path.as_posix()} forbidden marker: {marker}"
                )
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, text in SAMPLE_TEXT.items():
        _write(root / relative_path, text)


SELF_TEST_CASES = (
    (DOCS_ROOT_PATH, "missing", "`zigux/helpers/mmio.zig`"),
    (TESTS_ROOT_PATH, "missing", "`zigux/tests/phase3_low_level_wrappers_build.zig`"),
    (
        REVIEW_CHECKLIST_PATH,
        "missing",
        "`scripts/zigux/check-phase3-catalog-selftest.py`",
    ),
    (DOCS_ROOT_PATH, "forbidden", "`include/zigux/bitmap_cpumask.h`"),
    (TESTS_ROOT_PATH, "forbidden", "`zig build phase3-bitmap-cpumask`"),
    (REVIEW_CHECKLIST_PATH, "forbidden", "`zigux/helpers/bitmap_view.zig`"),
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase3_bitmap_cpumask_shared_summary_"
    ) as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_BITMAP_CPUMASK_SHARED_SUMMARY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, mode, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            text = _read(path)
            if mode == "missing":
                path.write_text(text.replace(marker, "", 1), encoding="utf-8")
                expected = (
                    f"missing {relative_path.as_posix()} required marker: {marker}"
                )
            else:
                path.write_text(text + marker + "\n", encoding="utf-8")
                expected = (
                    f"unexpected {relative_path.as_posix()} forbidden marker: {marker}"
                )

            issues = validate_repo(root)
            if expected not in issues:
                print("PHASE3_BITMAP_CPUMASK_SHARED_SUMMARY_SELF_TEST=fail")
                print(f"expected validation issue was not reported: {expected}")
                return 1

    print("PHASE3_BITMAP_CPUMASK_SHARED_SUMMARY_SELF_TEST=pass")
    print(
        "PHASE3_BITMAP_CPUMASK_SHARED_SUMMARY_SELF_TEST_CASES="
        f"{len(SELF_TEST_CASES)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Lane 27 shared-summary reminder posture."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 reminder surfaces",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_BITMAP_CPUMASK_SHARED_SUMMARY=fail")
        for issue in issues:
            print(issue)
        return 1

    for path in REQUIRED_MARKERS:
        print(f"validated {args.repo_root / path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
