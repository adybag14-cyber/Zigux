#!/usr/bin/env python3
"""Fail-close the current Phase 3 export/UAPI boundary survey packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase3-export-uapi-survey.py")
EXPORT_SHIM_PATH = Path("zigux/kernel/export_shim.zig")
BINDING_VERSION_PATH = Path("zigux/bindings/version.zig")
BINDING_DEV_T_PATH = Path("zigux/bindings/dev_t.zig")
UAPI_VERSION_PATH = Path("zigux/uapi/version.zig")
UAPI_DEV_T_PATH = Path("zigux/uapi/dev_t.zig")
LINUX_HEADER_PATH = Path("include/linux/zigux.h")
GOVERNANCE_NOTE_PATH = Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
TESTS_BUILD_PATH = Path("zigux/tests/build.zig")
LAYOUT_TEST_PATH = Path("zigux/tests/phase3_export_uapi_layout.zig")
LAYOUT_BUILD_PATH = Path("zigux/tests/phase3_export_uapi_layout_build.zig")
CATALOG_HELPER_PATH = Path("scripts/zigux/phase3_catalog.py")
CATALOG_SELFTEST_CHECK_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")
SHARED_CHECK_RUNNER_PATH = Path("scripts/zigux/run-phase3-checks.py")

REQUIRED_MARKERS = {
    SURVEY_PATH: (
        "PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py",
        "PHASE3_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json",
        "PHASE3_SHARED_TESTS_BUILD_PATH=zigux/tests/build.zig",
        "PHASE3_SHARED_CHECK_RUNNER_PATH=scripts/zigux/run-phase3-checks.py",
        "PHASE3_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
        "Current `master` no longer shows the older packet-local compile-wiring gap",
        "the shared tests-root replay route in `zigux/tests/build.zig` now imports `header_family_binding` inside `addPhase3ExportUapiLayout(...)`",
        "the shared `phase3-export-uapi-layout` route and the dedicated `phase3-export-uapi-layout-test` route agree on the live starter packet wiring",
        "the shared tests-root replay wiring explicit as shipped same-family evidence",
    ),
    VALIDATOR_PATH: (
        '"""Fail-close the current Phase 3 export/UAPI boundary survey packet."""',
        'TESTS_BUILD_PATH = Path("zigux/tests/build.zig")',
        'print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
        'print("PHASE3_EXPORT_UAPI_SURVEY=pass")',
    ),
    EXPORT_SHIM_PATH: (
        "pub fn versionMatchesCurrent(candidate: Version) bool {",
        "pub fn validateVersion(candidate: Version) ExportStatus {",
        "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
        "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
    ),
    BINDING_VERSION_PATH: (
        "pub fn current() Version {",
        "pub fn matchesCurrent(version: Version) bool {",
        'test "version binding keeps current compatibility explicit" {',
    ),
    BINDING_DEV_T_PATH: (
        "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
        'test "dev_t binding keeps validation and range edges aligned with the UAPI packet" {',
    ),
    UAPI_VERSION_PATH: (
        "pub fn matchesCurrent(version: Version) bool {",
        'test "version helpers keep current compatibility explicit" {',
    ),
    UAPI_DEV_T_PATH: (
        "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
        'test "dev_t validation keeps the starter boundary explicit" {',
    ),
    LINUX_HEADER_PATH: (
        "static inline zigux_uapi_version zigux_uapi_version_current(void)",
        "static inline int zigux_uapi_dev_t_fields_range_is_valid(",
        "static inline struct zigux_export_status zigux_uapi_validate_dev_t_range(",
    ),
    GOVERNANCE_NOTE_PATH: (
        "PHASE3_ZIGUX_H_PATH=include/linux/zigux.h",
        "PHASE3_ZIGUX_H_EXPORT_UAPI_SURVEY=Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    ),
    MANIFEST_PATH: (
        '"Documentation/zigux/phase3-export-uapi-boundary-survey.md"',
        '"scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
        '"keep the shared Phase 3 export/UAPI layout route aligned with the dedicated replay and only reopen this packet if the shared tests-root build wiring, export shim bindings, or focused layout tests drift again"',
    ),
    TESTS_BUILD_PATH: (
        "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);",
        '"phase3-export-uapi-layout"',
        'root_module.addImport("header_family_binding", header_family_binding);',
        'root_module.addImport("export_shim", export_shim);',
    ),
    LAYOUT_TEST_PATH: (
        'test "header-family binding keeps the bounded relay surface explicit" {',
        'test "export shim relays version compatibility without widening the boundary" {',
        'test "export shim encodes starter dev_t numbers without widening the boundary" {',
    ),
    LAYOUT_BUILD_PATH: (
        'const header_family_binding = b.createModule(.{',
        'header_family_binding.addImport("abi_bindings", abi_bindings);',
        'root_module.addImport("header_family_binding", header_family_binding);',
        '"phase3-export-uapi-layout-test"',
    ),
    CATALOG_HELPER_PATH: (
        'Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")',
        'print("PHASE3_CATALOG_SELF_TEST=pass")',
    ),
    CATALOG_SELFTEST_CHECK_PATH: (
        'Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")',
        'print("PHASE3_CATALOG_SELFTEST_CHECK=pass")',
    ),
    SHARED_CHECK_RUNNER_PATH: (
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
        '"phase3-validate"',
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


def _expect_missing_marker(root: Path, relative_path: Path, marker: str, message: str) -> int:
    target = root / relative_path
    target.write_text(_read(target).replace(marker, "", 1), encoding="utf-8")
    issues = validate_repo(root)
    expected = f"missing {relative_path.as_posix()} marker: {marker}"
    if expected not in issues:
        print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    marker_cases = (
        (
            SURVEY_PATH,
            "PHASE3_SHARED_TESTS_BUILD_PATH=zigux/tests/build.zig",
            "expected missing shared tests build path marker was not reported",
        ),
        (
            SURVEY_PATH,
            "Current `master` no longer shows the older packet-local compile-wiring gap",
            "expected missing shared-route-aligned survey marker was not reported",
        ),
        (
            MANIFEST_PATH,
            '"keep the shared Phase 3 export/UAPI layout route aligned with the dedicated replay and only reopen this packet if the shared tests-root build wiring, export shim bindings, or focused layout tests drift again"',
            "expected missing manifest next-safe-step marker was not reported",
        ),
        (
            TESTS_BUILD_PATH,
            'root_module.addImport("header_family_binding", header_family_binding);',
            "expected missing shared tests-root header-family import marker was not reported",
        ),
        (
            LAYOUT_BUILD_PATH,
            'root_module.addImport("header_family_binding", header_family_binding);',
            "expected missing dedicated layout build header-family import marker was not reported",
        ),
        (
            EXPORT_SHIM_PATH,
            "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
            "expected missing export shim range relay marker was not reported",
        ),
        (
            BINDING_VERSION_PATH,
            "pub fn matchesCurrent(version: Version) bool {",
            "expected missing binding version compatibility marker was not reported",
        ),
        (
            BINDING_DEV_T_PATH,
            "pub fn validateRange(start: Fields, end: Fields) bool {",
            "expected missing binding dev_t range marker was not reported",
        ),
        (
            UAPI_VERSION_PATH,
            "pub fn matchesCurrent(version: Version) bool {",
            "expected missing uapi version compatibility marker was not reported",
        ),
        (
            UAPI_DEV_T_PATH,
            "pub fn validateRange(start: Fields, end: Fields) bool {",
            "expected missing uapi dev_t range marker was not reported",
        ),
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker, message in marker_cases:
            _populate_repo(root)
            if _expect_missing_marker(root, relative_path, marker, message) != 0:
                return 1

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES={1 + len(marker_cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 3 export/UAPI packet.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 export/UAPI packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_EXPORT_UAPI_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / SURVEY_PATH}")
    print("PHASE3_EXPORT_UAPI_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
