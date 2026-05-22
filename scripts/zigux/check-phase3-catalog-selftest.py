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
        'Path("Documentation/zigux/phase3-policy-slice.md")',
        'Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")',
        'Path("Documentation/zigux/phase3-kernel-export-shim-governance.md")',
        'Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")',
        'Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")',
        'Path("Documentation/zigux/phase3-validator-support-surface.md")',
        'Path("Documentation/zigux/phase3-shared-reminder-gap.md")',
        'Path("scripts/zigux/check-phase3-abi.py")',
        'Path("scripts/zigux/check-phase3-abi-support-packet.py")',
        'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
        'Path("scripts/zigux/check-phase3-selftest-surface.py")',
        'Path("scripts/zigux/validate-phase3-validator-support-surface.py")',
        'Path("scripts/zigux/check-phase3-catalog-selftest.py")',
        'Path("scripts/zigux/check-phase3-policy-starter-packet.py")',
        'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
        'Path("scripts/zigux/validate-phase3-export-uapi-survey.py")',
        'Path("scripts/zigux/validate-phase3-abi-header-family-survey.py")',
        'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
        'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py")',
        'Path("scripts/zigux/validate_phase3_selftest.py")',
        'Path("scripts/zigux/run-phase3-checks.py")',
        'Path("zigux/helpers/layout_assert.zig")',
        'Path("zigux/tests/phase3_abi.zig")',
        'Path("zigux/tests/fixtures/phase3_abi_manifest.json")',
        'Path("zigux/tests/phase3_export_shim_build.zig")',
        'Path("zigux/bindings/header_family.zig")',
        'Path("zigux/Makefile")',
        '"python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test"',
        '"python3 scripts/zigux/check-phase3-catalog-selftest.py"',
        '"python3 scripts/zigux/validate-phase3.py --self-test"',
        '"python3 scripts/zigux/validate-phase3.py"',
        '"python3 scripts/zigux/check-phase3-abi.py --self-test"',
        '"python3 scripts/zigux/check-phase3-abi.py"',
        '"python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase3-abi-support-packet.py"',
        '"python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test"',
        '"python3 scripts/zigux/check-phase3-shared-tests-routes.py"',
        '"python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase3-policy-starter-packet.py"',
        '"python3 scripts/zigux/validate-phase3-validator-support-surface.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-validator-support-surface.py"',
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py"',
        '"python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py"',
        '"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py"',
        '"python3 scripts/zigux/validate_phase3_selftest.py"',
        '"python3 scripts/zigux/run-phase3-checks.py"',
        '"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"',
        '"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"',
        '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
        '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
        '"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"',
        '"make -C zigux phase3-export-uapi-layout"',
        '"make -C zigux phase3-export-uapi-layout-test"',
        '"zig build phase3-abi-core-packet --build-file zigux/tests/build.zig"',
        '"zig build phase3-dump --build-file zigux/tests/build.zig"',
        '"zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig"',
        '"zig build phase3-test --build-file zigux/tests/build.zig"',
        '"zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"',
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


def _expect_missing_marker(
    root: Path, relative_path: Path, marker: str, message: str
) -> int:
    path = root / relative_path
    path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
    issues = validate_repo(root)
    expected = f"missing {relative_path.as_posix()} marker: {marker}"
    if expected not in issues:
        print("PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    marker_cases = (
        (
            CATALOG_PATH,
            'Path("Documentation/zigux/phase3-policy-slice.md")',
            "expected missing catalog policy-slice marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("Documentation/zigux/phase3-validator-support-surface.md")',
            "expected missing catalog validator-support marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("Documentation/zigux/phase3-shared-reminder-gap.md")',
            "expected missing catalog shared-reminder marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("Documentation/zigux/phase3-kernel-export-shim-governance.md")',
            "expected missing catalog kernel-export governance marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("scripts/zigux/check-phase3-abi-support-packet.py")',
            "expected missing catalog abi-support checker marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
            "expected missing catalog shared-tests-routes marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("scripts/zigux/validate-phase3-validator-support-surface.py")',
            "expected missing catalog validator-support script marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("scripts/zigux/validate_phase3_selftest.py")',
            "expected missing catalog selftest-driver marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("scripts/zigux/run-phase3-checks.py")',
            "expected missing catalog runner marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("zigux/tests/fixtures/phase3_abi_manifest.json")',
            "expected missing catalog phase3 abi manifest marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("zigux/tests/phase3_export_shim_build.zig")',
            "expected missing catalog export-shim build marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("zigux/bindings/header_family.zig")',
            "expected missing catalog header-family binding marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test"',
            "expected missing catalog selftest route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate-phase3.py --self-test"',
            "expected missing catalog shared validator selftest route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test"',
            "expected missing catalog abi-support selftest route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test"',
            "expected missing catalog shared-tests selftest route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate-phase3-validator-support-surface.py --self-test"',
            "expected missing catalog validator-support selftest route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate_phase3_selftest.py"',
            "expected missing catalog selftest-driver route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/run-phase3-checks.py"',
            "expected missing catalog runner route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-abi-core-packet --build-file zigux/tests/build.zig"',
            "expected missing catalog abi core build route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"',
            "expected missing catalog export-shim test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"make -C zigux phase3-export-uapi-layout"',
            "expected missing catalog export-uapi shared make route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"make -C zigux phase3-export-uapi-layout-test"',
            "expected missing catalog export-uapi dedicated make route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-test --build-file zigux/tests/build.zig"',
            "expected missing catalog shared tests-root route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"make -C zigux phase3-low-level-wrappers-test"',
            "expected missing catalog low-level-wrapper make route marker was not reported",
        ),
        (
            SURVEY_PATH,
            "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
            "expected missing export-uapi survey guard marker was not reported",
        ),
        (
            HEADER_FAMILY_VALIDATOR_PATH,
            'CATALOG_SELFTEST_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")',
            "expected missing header-family validator guard marker was not reported",
        ),
        (
            LINUX_ZIGUX_HEADER_GOVERNANCE_VALIDATOR_PATH,
            'HEADER_PATH = Path("include/linux/zigux.h")',
            "expected missing linux-zigux governance header-path marker was not reported",
        ),
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_catalog_selftest_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker, message in marker_cases:
            _populate_repo(root)
            if _expect_missing_marker(root, relative_path, marker, message) != 0:
                return 1

    print("PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=pass")
    print(
        "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST_CASE_COUNT="
        f"{1 + len(marker_cases)}"
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