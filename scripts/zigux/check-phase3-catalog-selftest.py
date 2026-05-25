#!/usr/bin/env python3
"""Fail-close the current bounded Phase 3 catalog selftest guard."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

CATALOG_PATH = Path("scripts/zigux/phase3_catalog.py")
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
        'Path("Documentation/zigux/phase3-abi-slice.md")',
        'Path("Documentation/zigux/phase3-abi-header-family-survey.md")',
        'Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md")',
        'Path("Documentation/zigux/phase3-policy-slice.md")',
        'Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")',
        'Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")',
        'Path("Documentation/zigux/phase3-kernel-export-shim-governance.md")',
        'Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")',
        'Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")',
        'Path("Documentation/zigux/phase3-validator-support-surface.md")',
        'Path("Documentation/zigux/phase3-shared-reminder-gap.md")',
        'Path("zigux/kernel/export_shim.zig")',
        'Path("zigux/helpers/layout_assert.zig")',
        'Path("zigux/helpers/mmio.zig")',
        'Path("zigux/unsafe/narrow.zig")',
        'Path("scripts/zigux/check-phase3-abi.py")',
        'Path("scripts/zigux/check-phase3-abi-manifest-replay-routes.py")',
        'Path("scripts/zigux/check-phase3-abi-support-packet.py")',
        'Path("scripts/zigux/check-phase3-selftest-surface.py")',
        'Path("scripts/zigux/check-phase3-dev-t-starter-packet.py")',
        'Path("scripts/zigux/check-phase3-catalog-selftest.py")',
        'Path("scripts/zigux/check-phase3-policy-starter-packet.py")',
        'Path("scripts/zigux/check-phase3-policy-dump.py")',
        'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
        'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
        'Path("scripts/zigux/validate-phase3-validator-support-surface.py")',
        'Path("scripts/zigux/validate-phase3-export-uapi-survey.py")',
        'Path("scripts/zigux/validate-phase3-abi-header-family-survey.py")',
        'Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py")',
        'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
        'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py")',
        'Path("scripts/zigux/validate_phase3_selftest.py")',
        'Path("scripts/zigux/run-phase3-checks.py")',
        'Path("zigux/tests/phase3_abi.zig")',
        'Path("zigux/tests/phase3_abi_dump_current.zig")',
        'Path("zigux/tests/phase3_export_uapi_layout.zig")',
        'Path("zigux/tests/phase3_export_shim_build.zig")',
        'Path("zigux/tests/phase3_policy_dump.zig")',
        'Path("zigux/tests/phase3_low_level_wrappers.zig")',
        'Path("zigux/tests/fixtures/phase3_abi_manifest.json")',
        'Path("zigux/Makefile")',
        '"python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test"',
        '"python3 scripts/zigux/check-phase3-selftest-surface.py --self-test"',
        '"python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"',
        '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
        '"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"',
        '"make -C zigux phase3-export-shim-test"',
        '"make -C zigux phase3"',
        '"make -C zigux phase3-low-level-wrappers-test"',
        'print("PHASE3_CATALOG_SELF_TEST=pass")',
    ),
    SURVEY_PATH: (
        "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
    ),
    EXPORT_UAPI_VALIDATOR_PATH: (
        'CATALOG_SELFTEST_CHECK_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")',
        'print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
    ),
    LOW_LEVEL_WRAPPER_SURVEY_PATH: (
        "scripts/zigux/check-phase3-catalog-selftest.py",
    ),
    LOW_LEVEL_WRAPPER_VALIDATOR_PATH: (
        'print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")',
    ),
    HEADER_FAMILY_SURVEY_PATH: (
        "PHASE3_ABI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
    ),
    HEADER_FAMILY_VALIDATOR_PATH: (
        'CATALOG_SELFTEST_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")',
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
    "phase3-errptr-xarray-slice.md",
    "phase3-xarray-slot-slice.md",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "check-phase3-errptr-xarray-starter-packet.py",
    "check-phase3-xarray-slot-starter-packet.py",
    "check-phase3-xarray-slot.py",
    "phase3_errptr_xarray_starter_packet.zig",
    "phase3_errptr_xarray_starter_packet_build.zig",
    "phase3_errptr_xarray_starter_packet_manifest.json",
    "phase3_errptr_xarray_dump.zig",
    "phase3_errptr_xarray_dump_build.zig",
    "phase3_xarray_slot_starter_packet.zig",
    "phase3_xarray_slot_starter_packet_build.zig",
    "phase3_xarray_slot_dump.zig",
    "phase3_xarray_slot_dump_build.zig",
    "phase3_xarray_slot_manifest.json",
    "check-phase3-xarray-slot.py --repo-root . --zig zig --cc gcc",
    "zig build phase3-errptr-xarray-starter-packet-test --build-file zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
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
                'PHASE3_CATALOG_SCOPE = "abi-runtime"',
                'missing scripts/zigux/phase3_catalog.py marker: PHASE3_CATALOG_SCOPE = "abi-runtime"',
                "expected missing catalog scope marker was not reported",
            ),
            (
                CATALOG_PATH,
                'Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md")',
                'missing scripts/zigux/phase3_catalog.py marker: Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md")',
                "expected missing abi.h next-step catalog marker was not reported",
            ),
            (
                SURVEY_PATH,
                "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
                "missing Documentation/zigux/phase3-export-uapi-boundary-survey.md marker: PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
                "expected missing export-uapi survey guard marker was not reported",
            ),
            (
                HEADER_FAMILY_VALIDATOR_PATH,
                'CATALOG_SELFTEST_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")',
                'missing scripts/zigux/validate-phase3-abi-header-family-survey.py marker: CATALOG_SELFTEST_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")',
                "expected missing header-family validator guard marker was not reported",
            ),
            (
                LINUX_ZIGUX_HEADER_GOVERNANCE_VALIDATOR_PATH,
                'HEADER_PATH = Path("include/linux/zigux.h")',
                'missing scripts/zigux/validate-phase3-linux-zigux-header-governance.py marker: HEADER_PATH = Path("include/linux/zigux.h")',
                "expected missing linux-zigux governance header-path marker was not reported",
            ),
        )

        forbidden_cases = (
            (
                "phase3-errptr-xarray-slice.md",
                "expected forbidden xarray survey marker was not reported",
            ),
            (
                "zigux/helpers/xarray_slot_view.zig",
                "expected forbidden xarray helper marker was not reported",
            ),
            (
                "check-phase3-xarray-slot.py --repo-root . --zig zig --cc gcc",
                "expected forbidden xarray replay route marker was not reported",
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
        description="Validate the current Phase 3 catalog selftest guard."
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