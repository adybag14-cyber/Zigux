#!/usr/bin/env python3
"""Fail-close the current bounded Phase 3 catalog selftest guard."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

CATALOG_PATH = Path("scripts/zigux/phase3_catalog.py")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
SURVEY_PATH = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")
EXPORT_UAPI_VALIDATOR_PATH = Path(
    "scripts/zigux/validate-phase3-export-uapi-survey.py"
)
LOW_LEVEL_WRAPPER_SURVEY_PATH = Path(
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"
)
LOW_LEVEL_WRAPPER_VALIDATOR_PATH = Path(
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"
)
HEADER_FAMILY_SURVEY_PATH = Path(
    "Documentation/zigux/phase3-abi-header-family-survey.md"
)
HEADER_FAMILY_VALIDATOR_PATH = Path(
    "scripts/zigux/validate-phase3-abi-header-family-survey.py"
)
LINUX_ZIGUX_HEADER_GOVERNANCE_NOTE_PATH = Path(
    "Documentation/zigux/phase3-linux-zigux-header-governance.md"
)
LINUX_ZIGUX_HEADER_GOVERNANCE_VALIDATOR_PATH = Path(
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py"
)

REQUIRED_MARKERS = {
    CATALOG_PATH: (
        'PHASE3_CATALOG_PHASE = "Phase 3"',
        'PHASE3_CATALOG_SCOPE = "abi-runtime"',
        'MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")',
        '"Documentation/zigux/phase3-abi-slice.md"',
        '"Documentation/zigux/phase3-export-uapi-boundary-survey.md"',
        '"Documentation/zigux/phase3-errptr-xarray-slice.md"',
        '"Documentation/zigux/phase3-xarray-slot-slice.md"',
        '"Documentation/zigux/phase3-idr-slot-slice.md"',
        '"Documentation/zigux/phase3-bitmap-cpumask-slice.md"',
        '"Documentation/zigux/phase3-list-hlist-slice.md"',
        '"scripts/zigux/check-phase3-catalog-selftest.py"',
        '"scripts/zigux/generate-phase3-check-wrappers.py"',
        '"scripts/zigux/check-phase3-wrapper-templates.py"',
        '"scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"',
        '"scripts/zigux/check-phase3-xarray-slot.py"',
        '"scripts/zigux/check-phase3-idr-slot-starter-packet.py"',
        '"scripts/zigux/check-phase3-idr-slot.py"',
        '"scripts/zigux/check-phase3-bitmap-cpumask.py"',
        '"scripts/zigux/check-phase3-list-hlist-starter-packet.py"',
        '"scripts/zigux/check-phase3-list-hlist.py"',
        '"scripts/zigux/check-phase3-low-level-wrappers.py"',
        '"zigux/helpers/idr_slot_view.zig"',
        '"zigux/tests/phase3_idr_slot_starter_packet.zig"',
        '"zigux/tests/phase3_idr_slot_starter_packet_build.zig"',
        '"zigux/tests/fixtures/phase3_idr_slot_manifest.json"',
        '"zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c"',
        '"zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json"',
        '"zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c"',
        '"zigux/tests/fixtures/phase3_list_hlist/expected.json"',
        '"zigux/tests/phase3_list_hlist_dump.zig"',
        '"zigux/tests/phase3_list_hlist_dump_build.zig"',
        '"zigux/tests/phase3_abi_dump_current.zig"',
        '"zigux/Makefile"',
        '".github/workflows/zigux-bootstrap.yml"',
        '"python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test"',
        '"python3 scripts/zigux/check-phase3-wrapper-templates.py --self-test"',
        '"python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --repo-root ."',
        '"python3 scripts/zigux/check-phase3-idr-slot.py --self-test"',
        '"python3 scripts/zigux/check-phase3-idr-slot.py --repo-root . --zig zig --cc gcc"',
        '"python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test"',
        '"python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc"',
        '"zig build phase3-abi-export --build-file zigux/tests/build.zig"',
        '"make -C zigux phase3-abi-export"',
        '"zig build phase3-idr-slot --build-file zigux/tests/build.zig"',
        '"zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig"',
        '"zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig"',
        '"zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig"',
        'print("PHASE3_CATALOG_SELF_TEST=pass")',
    ),
    MANIFEST_PATH: (
        '"Documentation/zigux/phase3-list-hlist-slice.md"',
        '"scripts/zigux/check-phase3-catalog-selftest.py"',
        '"scripts/zigux/check-phase3-list-hlist.py"',
        '"scripts/zigux/check-phase3-low-level-wrappers.py"',
        '"zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c"',
        '"zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c"',
        '"zigux/tests/phase3_list_hlist_dump.zig"',
        '"zigux/tests/phase3_list_hlist_dump_build.zig"',
        '"zigux/tests/phase3_abi_dump_current.zig"',
        '"zigux/Makefile"',
        '".github/workflows/zigux-bootstrap.yml"',
        '"zig build phase3-abi-export --build-file zigux/tests/build.zig"',
        '"make -C zigux phase3-abi-export"',
        '"python3 scripts/zigux/check-phase3-idr-slot.py --repo-root . --zig zig --cc gcc"',
        '"zig build phase3-idr-slot --build-file zigux/tests/build.zig"',
        '"zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig"',
        '"python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc"',
        '"zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig"',
    ),
    SURVEY_PATH: (
        "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
    ),
    EXPORT_UAPI_VALIDATOR_PATH: (
        'CATALOG_SELFTEST_CHECK_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")',
        'print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
    ),
    LOW_LEVEL_WRAPPER_SURVEY_PATH: (
        "`scripts/zigux/check-phase3-catalog-selftest.py`",
    ),
    LOW_LEVEL_WRAPPER_VALIDATOR_PATH: (
        'print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")',
    ),
    HEADER_FAMILY_SURVEY_PATH: (
        "PHASE3_ABI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
    ),
    HEADER_FAMILY_VALIDATOR_PATH: (
        'print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass")',
    ),
    LINUX_ZIGUX_HEADER_GOVERNANCE_NOTE_PATH: (
        "Documentation/zigux/phase3-abi-slice.md",
        "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
        "zigux/tests/fixtures/phase3_abi_manifest.json",
    ),
    LINUX_ZIGUX_HEADER_GOVERNANCE_VALIDATOR_PATH: (
        'NOTE_PATH = Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")',
        'HEADER_PATH = Path("include/linux/zigux.h")',
        'print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass")',
    ),
}

FORBIDDEN_CATALOG_MARKERS = (
    '"zigux/tests/phase3_abi_dump.zig"',
    '"phase3_abi_dump_build.zig"',
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

    catalog_path = repo_root / CATALOG_PATH
    if catalog_path.is_file():
        catalog_text = _read(catalog_path)
        for marker in FORBIDDEN_CATALOG_MARKERS:
            if marker in catalog_text:
                issues.append(
                    f"forbidden {CATALOG_PATH.as_posix()} marker: {marker}"
                )

    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")


def _expect_issue(root: Path, expected: str, message: str) -> int:
    issues = validate_repo(root)
    if expected not in issues:
        print("PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_catalog_selftest_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        required_cases = (
            (
                CATALOG_PATH,
                '"Documentation/zigux/phase3-idr-slot-slice.md"',
                'missing scripts/zigux/phase3_catalog.py marker: "Documentation/zigux/phase3-idr-slot-slice.md"',
                "expected missing idr-slot slice marker was not reported",
            ),
            (
                CATALOG_PATH,
                '"python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --repo-root ."',
                'missing scripts/zigux/phase3_catalog.py marker: "python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --repo-root ."',
                "expected missing idr-slot replay marker was not reported",
            ),
            (
                CATALOG_PATH,
                '"python3 scripts/zigux/check-phase3-idr-slot.py --repo-root . --zig zig --cc gcc"',
                'missing scripts/zigux/phase3_catalog.py marker: "python3 scripts/zigux/check-phase3-idr-slot.py --repo-root . --zig zig --cc gcc"',
                "expected missing idr-slot verification replay marker was not reported",
            ),
            (
                CATALOG_PATH,
                '"zig build phase3-abi-export --build-file zigux/tests/build.zig"',
                'missing scripts/zigux/phase3_catalog.py marker: "zig build phase3-abi-export --build-file zigux/tests/build.zig"',
                "expected missing ABI export build marker was not reported",
            ),
            (
                CATALOG_PATH,
                '"zig build phase3-idr-slot --build-file zigux/tests/build.zig"',
                'missing scripts/zigux/phase3_catalog.py marker: "zig build phase3-idr-slot --build-file zigux/tests/build.zig"',
                "expected missing idr-slot aggregate build marker was not reported",
            ),
            (
                CATALOG_PATH,
                '"zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig"',
                'missing scripts/zigux/phase3_catalog.py marker: "zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig"',
                "expected missing idr-slot build marker was not reported",
            ),
            (
                CATALOG_PATH,
                '"zigux/tests/fixtures/phase3_idr_slot_manifest.json"',
                'missing scripts/zigux/phase3_catalog.py marker: "zigux/tests/fixtures/phase3_idr_slot_manifest.json"',
                "expected missing idr-slot manifest marker was not reported",
            ),
            (
                CATALOG_PATH,
                '"scripts/zigux/check-phase3-low-level-wrappers.py"',
                'missing scripts/zigux/phase3_catalog.py marker: "scripts/zigux/check-phase3-low-level-wrappers.py"',
                "expected missing low-level wrapper checker marker was not reported",
            ),
            (
                CATALOG_PATH,
                '"Documentation/zigux/phase3-list-hlist-slice.md"',
                'missing scripts/zigux/phase3_catalog.py marker: "Documentation/zigux/phase3-list-hlist-slice.md"',
                "expected missing list-hlist slice marker was not reported",
            ),
            (
                CATALOG_PATH,
                '"python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc"',
                'missing scripts/zigux/phase3_catalog.py marker: "python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc"',
                "expected missing list-hlist replay marker was not reported",
            ),
            (
                CATALOG_PATH,
                '"zigux/tests/phase3_abi_dump_current.zig"',
                'missing scripts/zigux/phase3_catalog.py marker: "zigux/tests/phase3_abi_dump_current.zig"',
                "expected missing current ABI dump marker was not reported",
            ),
            (
                CATALOG_PATH,
                '"zigux/Makefile"',
                'missing scripts/zigux/phase3_catalog.py marker: "zigux/Makefile"',
                "expected missing Makefile packet marker was not reported",
            ),
            (
                MANIFEST_PATH,
                '"zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c"',
                'missing zigux/tests/fixtures/phase3_abi_manifest.json marker: "zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c"',
                "expected missing bitmap harness manifest marker was not reported",
            ),
            (
                MANIFEST_PATH,
                '".github/workflows/zigux-bootstrap.yml"',
                'missing zigux/tests/fixtures/phase3_abi_manifest.json marker: ".github/workflows/zigux-bootstrap.yml"',
                "expected missing workflow manifest marker was not reported",
            ),
            (
                SURVEY_PATH,
                "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
                "missing Documentation/zigux/phase3-export-uapi-boundary-survey.md marker: PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
                "expected missing export-uapi survey guard marker was not reported",
            ),
        )

        forbidden_cases = (
            (
                '"zigux/tests/phase3_abi_dump.zig"',
                "expected forbidden legacy abi dump packet marker was not reported",
            ),
            (
                '"phase3_abi_dump_build.zig"',
                "expected forbidden legacy abi dump build marker was not reported",
            ),
        )

        for relative_path, marker, expected, message in required_cases:
            _populate_repo(root)
            path = root / relative_path
            _write(path, _read(path).replace(marker, "", 1))
            if _expect_issue(root, expected, message) != 0:
                return 1

        for marker, message in forbidden_cases:
            _populate_repo(root)
            path = root / CATALOG_PATH
            _write(path, _read(path) + marker + "\n")
            expected = f"forbidden {CATALOG_PATH.as_posix()} marker: {marker}"
            if _expect_issue(root, expected, message) != 0:
                return 1

    print("PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=pass")
    print(
        "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST_CASE_COUNT="
        f"{1 + len(required_cases) + len(forbidden_cases)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 catalog packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 catalog packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_CATALOG_SELFTEST_CHECK=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / CATALOG_PATH}")
    print("PHASE3_CATALOG_SELFTEST_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
