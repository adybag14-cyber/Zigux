#!/usr/bin/env python3
"""Fail-close the current dedicated Phase 3 build-harness inventory."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELFTEST_DRIVER_PATH = Path("scripts/zigux/validate_phase3_selftest.py")

REQUIRED_BUILD_HARNESSES: dict[Path, tuple[str, ...]] = {
    Path("zigux/tests/phase3_dev_t_starter_packet_build.zig"): (
        '.root_source_file = b.path("phase3_dev_t_starter_packet.zig"),',
        '"phase3-dev-t-starter-packet-test"',
    ),
    Path("zigux/tests/phase3_errptr_xarray_starter_packet_build.zig"): (
        '.root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),',
        '"phase3-errptr-xarray-starter-packet-test"',
    ),
    Path("zigux/tests/phase3_errptr_xarray_dump_build.zig"): (
        '.root_source_file = b.path("phase3_errptr_xarray_dump.zig"),',
        '"phase3-errptr-xarray-dump"',
    ),
    Path("zigux/tests/phase3_xarray_slot_starter_packet_build.zig"): (
        '.root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),',
        '"phase3-xarray-slot-starter-packet-test"',
    ),
    Path("zigux/tests/phase3_policy_starter_packet_build.zig"): (
        '.root_source_file = b.path("phase3_policy_starter_packet.zig"),',
        '"phase3-policy-starter-packet-test"',
    ),
    Path("zigux/tests/phase3_policy_dump_build.zig"): (
        '.root_source_file = b.path("phase3_policy_dump.zig"),',
        '"phase3-policy-dump"',
    ),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"): (
        '.root_source_file = b.path("phase3_low_level_wrappers.zig"),',
        '"phase3-low-level-wrappers-test"',
    ),
    Path("zigux/tests/phase3_export_uapi_layout_build.zig"): (
        '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        '"phase3-export-uapi-layout-test"',
    ),
}

REQUIRED_DRIVER_MARKERS = (
    'Path("scripts/zigux/check-phase3-build-harness-inventory.py")',
    "PHASE3_BUILD_HARNESS_INVENTORY_SELF_TEST=pass",
    "PHASE3_BUILD_HARNESS_INVENTORY_SELF_TEST_CASE_COUNT=",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path, markers in REQUIRED_BUILD_HARNESSES.items():
        path = repo_root / rel_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue

        for marker in markers:
            if marker not in text:
                issues.append(
                    f"missing {rel_path.as_posix()} marker: {marker}"
                )

    driver_path = repo_root / SELFTEST_DRIVER_PATH
    try:
        driver_text = _read(driver_path)
    except FileNotFoundError:
        issues.append(f"missing repo file: {SELFTEST_DRIVER_PATH.as_posix()}")
    else:
        for marker in REQUIRED_DRIVER_MARKERS:
            if marker not in driver_text:
                issues.append(
                    "missing "
                    f"{SELFTEST_DRIVER_PATH.as_posix()} marker: {marker}"
                )

    return issues


def _populate_repo(root: Path) -> None:
    for rel_path, markers in REQUIRED_BUILD_HARNESSES.items():
        _write(root / rel_path, "\n".join(markers) + "\n")
    _write(
        root / SELFTEST_DRIVER_PATH,
        "\n".join(REQUIRED_DRIVER_MARKERS) + "\n",
    )


def run_self_test() -> int:
    cases: list[tuple[Path, str]] = [
        (rel_path, marker)
        for rel_path, markers in REQUIRED_BUILD_HARNESSES.items()
        for marker in markers
    ] + [
        (SELFTEST_DRIVER_PATH, marker) for marker in REQUIRED_DRIVER_MARKERS
    ]

    with tempfile.TemporaryDirectory(
        prefix="zigux_phase3_build_harness_inventory_"
    ) as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_BUILD_HARNESS_INVENTORY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for rel_path, marker in cases:
            _populate_repo(root)
            file_path = root / rel_path
            file_path.write_text(
                _read(file_path).replace(marker, "", 1), encoding="utf-8"
            )
            issues = validate_repo(root)
            expected = f"missing {rel_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_BUILD_HARNESS_INVENTORY_SELF_TEST=fail")
                print(
                    "expected missing marker was not reported: " + expected
                )
                return 1

    print("PHASE3_BUILD_HARNESS_INVENTORY_SELF_TEST=pass")
    print(
        "PHASE3_BUILD_HARNESS_INVENTORY_SELF_TEST_CASE_COUNT="
        f"{len(cases)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current dedicated Phase 3 build-harness inventory."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains zigux/tests/ and scripts/zigux/",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_BUILD_HARNESS_INVENTORY=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / SELFTEST_DRIVER_PATH}")
    print(
        "validated dedicated build harness count="
        f"{len(REQUIRED_BUILD_HARNESSES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
