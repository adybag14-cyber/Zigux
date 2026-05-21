#!/usr/bin/env python3
"""Fail-close the current Phase 3 catalog selftest guard."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

CATALOG_PATH = Path("scripts/zigux/phase3_catalog.py")
RUNNER_PATH = Path("scripts/zigux/run-phase3-checks.py")
SELFTEST_RUNNER_PATH = Path("scripts/zigux/validate_phase3_selftest.py")
SURVEY_PATH = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")
EXPORT_UAPI_VALIDATOR_PATH = Path("scripts/zigux/validate-phase3-export-uapi-survey.py")
LOW_LEVEL_WRAPPER_SURVEY_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
LOW_LEVEL_WRAPPER_VALIDATOR_PATH = Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")
HEADER_FAMILY_SURVEY_PATH = Path("Documentation/zigux/phase3-abi-header-family-survey.md")
HEADER_FAMILY_VALIDATOR_PATH = Path("scripts/zigux/validate-phase3-abi-header-family-survey.py")
POLICY_UNSAFE_SURVEY_PATH = Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")
POLICY_UNSAFE_VALIDATOR_PATH = Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py")
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
        'Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")',
        'Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")',
        'Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")',
        'Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")',
        'Path("Documentation/zigux/phase3-abi-header-family-survey.md")',
        'Path("Documentation/zigux/phase3-xarray-slot-slice.md")',
        'Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py")',
        'Path("scripts/zigux/check-phase3-xarray-slot.py")',
        'Path("scripts/zigux/check-phase3-policy-dump.py")',
        'Path("scripts/zigux/check-phase3-wrapper-templates.py")',
        'Path("scripts/zigux/generate-phase3-check-wrappers.py")',
        'Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py")',
        'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py")',
        'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
        'Path("zigux/helpers/layout_assert.zig")',
        'Path("zigux/tests/phase3_abi.zig")',
        'Path("zigux/tests/phase3_policy_dump.zig")',
        'Path("zigux/tests/fixtures/phase3_policy_dump_expected.txt")',
        'Path("zigux/tests/phase3_export_uapi_c_header_smoke.c")',
        'Path("zigux/Makefile")',
        'Path("zigux/tests/fixtures/phase3_abi_manifest.json")',
        '"python3 scripts/zigux/check-phase3-abi.py --self-test"',
        '"python3 scripts/zigux/check-phase3-abi.py"',
        '"python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase3-policy-starter-packet.py"',
        '"python3 scripts/zigux/check-phase3-policy-dump.py --self-test"',
        '"python3 scripts/zigux/check-phase3-policy-dump.py"',
        '"python3 scripts/zigux/check-phase3-wrapper-templates.py --self-test"',
        '"python3 scripts/zigux/check-phase3-wrapper-templates.py"',
        '"python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test"',
        '"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"',
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py"',
        '"python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py"',
        '"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py"',
        '"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py"',
        '"python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase3-xarray-slot.py --self-test"',
        '"zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig"',
        '"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"',
        '"zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"',
        '"zig build phase3-abi-core-packet --build-file zigux/tests/build.zig"',
        '"zig build phase3-dump --build-file zigux/tests/build.zig"',
        '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
        '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
        '"make -C zigux phase3-export-uapi-layout"',
        '"make -C zigux phase3-export-uapi-layout-test"',
        '"zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig"',
        '"zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"',
        '"make -C zigux phase3-low-level-wrappers"',
        '"make -C zigux phase3-low-level-wrappers-test"',
        '"make -C zigux phase3-test"',
        '"make -C zigux phase3-dump"',
        '"make -C zigux phase3-validate"',
        '"make -C zigux phase3"',
        'print("PHASE3_CATALOG_SELF_TEST=pass")',
    ),
    RUNNER_PATH: (
        'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"),',
        '("validated Documentation/zigux/phase3-linux-zigux-header-governance.md",),',
        'Path("scripts/zigux/check-phase3-policy-dump.py"),',
        '("validated zigux/tests/phase3_policy_dump.zig",',
        'Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),',
        '("validated Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",',
        'Path("scripts/zigux/check-phase3-wrapper-templates.py"),',
        '("validated scripts/zigux/generate-phase3-check-wrappers.py",',
        '"expected missing linux-zigux header-governance output marker to fail the runner"',
    ),
    SELFTEST_RUNNER_PATH: (
        'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"),',
        '("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass",),',
        'Path("scripts/zigux/check-phase3-policy-dump.py"),',
        '("PHASE3_POLICY_DUMP_SELF_TEST=pass",',
        'Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),',
        '("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass",',
        'Path("scripts/zigux/check-phase3-wrapper-templates.py"),',
        '("PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=pass",',
        'Path("scripts/zigux/generate-phase3-check-wrappers.py"),',
        '("PHASE3_WRAPPER_SELF_TEST=pass",',
        '"expected linux-zigux header governance validator omission was not reported"',
        '"expected missing governance pass marker to fail the packet"',
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
    POLICY_UNSAFE_SURVEY_PATH: (
        "PHASE3_POLICY_UNSAFE_SURVEY_GATE=python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py",
        "PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py",
    ),
    POLICY_UNSAFE_VALIDATOR_PATH: (
        'NOTE_PATH = Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")',
        'print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")',
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
            '"python3 scripts/zigux/check-phase3-abi.py --self-test"',
            "expected missing catalog abi self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-abi.py"',
            "expected missing catalog abi checker route marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")',
            "expected missing catalog policy-unsafe survey note marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("scripts/zigux/check-phase3-policy-dump.py")',
            "expected missing catalog policy-dump validator marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("scripts/zigux/check-phase3-wrapper-templates.py")',
            "expected missing catalog wrapper-template checker marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("scripts/zigux/generate-phase3-check-wrappers.py")',
            "expected missing catalog wrapper-generator marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py")',
            "expected missing catalog policy-unsafe validator marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")',
            "expected missing catalog low-level-wrapper survey note marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
            "expected missing catalog export-uapi c-header smoke checker marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("zigux/helpers/layout_assert.zig")',
            "expected missing catalog layout-assert helper marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("zigux/tests/phase3_policy_dump.zig")',
            "expected missing catalog phase3 policy dump replay marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("zigux/tests/fixtures/phase3_policy_dump_expected.txt")',
            "expected missing catalog phase3 policy dump fixture marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("zigux/tests/phase3_export_uapi_c_header_smoke.c")',
            "expected missing catalog export-uapi c-header smoke fixture marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("zigux/Makefile")',
            "expected missing catalog phase3 Makefile marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("zigux/tests/fixtures/phase3_abi_manifest.json")',
            "expected missing catalog phase3 abi manifest marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test"',
            "expected missing catalog policy starter self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-policy-starter-packet.py"',
            "expected missing catalog policy starter route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-policy-dump.py --self-test"',
            "expected missing catalog policy-dump self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-policy-dump.py"',
            "expected missing catalog policy-dump route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-wrapper-templates.py --self-test"',
            "expected missing catalog wrapper-template self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-wrapper-templates.py"',
            "expected missing catalog wrapper-template route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test"',
            "expected missing catalog wrapper-generator self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"',
            "expected missing catalog export-uapi c-header smoke route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test"',
            "expected missing catalog policy-unsafe survey self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py"',
            "expected missing catalog policy-unsafe survey route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"',
            "expected missing catalog low-level-wrapper survey self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py"',
            "expected missing catalog low-level-wrapper survey route marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")',
            "expected missing catalog linux-zigux header-governance note marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py")',
            "expected missing catalog linux-zigux header-governance validator marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("zigux/tests/phase3_abi.zig")',
            "expected missing catalog shared abi core replay marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"',
            "expected missing catalog export-uapi self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test"',
            "expected missing catalog header-family self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test"',
            "expected missing catalog linux-zigux header-governance self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            'Path("Documentation/zigux/phase3-xarray-slot-slice.md")',
            "expected missing catalog xarray-slot slice marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test"',
            "expected missing catalog xarray-slot starter self-test route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig"',
            "expected missing catalog xarray-slot dump route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"',
            "expected missing catalog policy starter build route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"',
            "expected missing catalog policy dump build route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-abi-core-packet --build-file zigux/tests/build.zig"',
            "expected missing catalog abi core build route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-dump --build-file zigux/tests/build.zig"',
            "expected missing catalog abi dump build route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
            "expected missing catalog shared export-uapi build route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
            "expected missing catalog dedicated export-uapi build route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"make -C zigux phase3-export-uapi-layout"',
            "expected missing catalog export-uapi Makefile route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"make -C zigux phase3-export-uapi-layout-test"',
            "expected missing catalog export-uapi test Makefile route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig"',
            "expected missing catalog shared low-level-wrapper build route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"',
            "expected missing catalog dedicated low-level-wrapper build route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"make -C zigux phase3-low-level-wrappers"',
            "expected missing catalog low-level-wrapper Makefile route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"make -C zigux phase3-low-level-wrappers-test"',
            "expected missing catalog low-level-wrapper test Makefile route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"make -C zigux phase3-test"',
            "expected missing catalog phase3 test Makefile route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"make -C zigux phase3-dump"',
            "expected missing catalog phase3 dump Makefile route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"make -C zigux phase3-validate"',
            "expected missing catalog phase3 validate Makefile route marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"make -C zigux phase3"',
            "expected missing catalog aggregate phase3 Makefile route marker was not reported",
        ),
        (
            RUNNER_PATH,
            'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"),',
            "expected missing runner governance validator route marker was not reported",
        ),
        (
            RUNNER_PATH,
            '("validated Documentation/zigux/phase3-linux-zigux-header-governance.md",),',
            "expected missing runner governance output marker was not reported",
        ),
        (
            RUNNER_PATH,
            'Path("scripts/zigux/check-phase3-wrapper-templates.py"),',
            "expected missing runner wrapper-template checker route marker was not reported",
        ),
        (
            RUNNER_PATH,
            '("validated scripts/zigux/generate-phase3-check-wrappers.py",',
            "expected missing runner wrapper-template output marker was not reported",
        ),
        (
            SELFTEST_RUNNER_PATH,
            'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"),',
            "expected missing selftest-packet governance validator route marker was not reported",
        ),
        (
            SELFTEST_RUNNER_PATH,
            '("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass",),',
            "expected missing selftest-packet governance pass marker was not reported",
        ),
        (
            SELFTEST_RUNNER_PATH,
            'Path("scripts/zigux/check-phase3-wrapper-templates.py"),',
            "expected missing selftest-packet wrapper-template checker route marker was not reported",
        ),
        (
            SELFTEST_RUNNER_PATH,
            '("PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=pass",',
            "expected missing selftest-packet wrapper-template checker pass marker was not reported",
        ),
        (
            SELFTEST_RUNNER_PATH,
            'Path("scripts/zigux/generate-phase3-check-wrappers.py"),',
            "expected missing selftest-packet wrapper-generator route marker was not reported",
        ),
        (
            SELFTEST_RUNNER_PATH,
            '("PHASE3_WRAPPER_SELF_TEST=pass",',
            "expected missing selftest-packet wrapper-generator pass marker was not reported",
        ),
        (
            LOW_LEVEL_WRAPPER_SURVEY_PATH,
            "scripts/zigux/check-phase3-catalog-selftest.py",
            "expected missing low-level-wrapper survey catalog-selftest guard marker was not reported",
        ),
        (
            LOW_LEVEL_WRAPPER_VALIDATOR_PATH,
            'print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")',
            "expected missing low-level-wrapper validator self-test marker was not reported",
        ),
        (
            HEADER_FAMILY_SURVEY_PATH,
            "PHASE3_ABI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
            "expected missing header-family survey catalog-selftest guard marker was not reported",
        ),
        (
            HEADER_FAMILY_VALIDATOR_PATH,
            'CATALOG_SELFTEST_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")',
            "expected missing header-family validator catalog-selftest marker was not reported",
        ),
        (
            POLICY_UNSAFE_SURVEY_PATH,
            "PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py",
            "expected missing policy-unsafe survey policy-dump gate marker was not reported",
        ),
        (
            POLICY_UNSAFE_VALIDATOR_PATH,
            'NOTE_PATH = Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")',
            "expected missing policy-unsafe validator note path marker was not reported",
        ),
        (
            POLICY_UNSAFE_VALIDATOR_PATH,
            'print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")',
            "expected missing policy-unsafe validator self-test marker was not reported",
        ),
        (
            LINUX_ZIGUX_HEADER_GOVERNANCE_VALIDATOR_PATH,
            'NOTE_PATH = Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")',
            "expected missing linux-zigux header-governance note path marker was not reported",
        ),
        (
            LINUX_ZIGUX_HEADER_GOVERNANCE_VALIDATOR_PATH,
            'print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass")',
            "expected missing linux-zigux header-governance self-test pass marker was not reported",
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
    print(f"PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST_CASE_COUNT={1 + len(marker_cases)}")
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
