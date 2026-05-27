#!/usr/bin/env python3
"""Validate the current bounded Phase 3 export/UAPI survey packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase3-export-uapi-survey.py")
CATALOG_SELFTEST_CHECK_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")
EXPORT_SHIM_PATH = Path("zigux/kernel/export_shim.zig")
ABI_H_PATH = Path("include/zigux/abi.h")
LINUX_HEADER_PATH = Path("include/linux/zigux.h")
BINDING_VERSION_PATH = Path("zigux/bindings/version.zig")
BINDING_DEV_T_PATH = Path("zigux/bindings/dev_t.zig")
BINDING_HEADER_FAMILY_PATH = Path("zigux/bindings/header_family.zig")
UAPI_VERSION_PATH = Path("zigux/uapi/version.zig")
UAPI_DEV_T_PATH = Path("zigux/uapi/dev_t.zig")
DEV_T_HEADER_PATH = Path("include/zigux/dev_t.h")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
TESTS_BUILD_PATH = Path("zigux/tests/build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
EXPORT_SHIM_BUILD_PATH = Path("zigux/tests/phase3_export_shim_build.zig")
LAYOUT_TEST_PATH = Path("zigux/tests/phase3_export_uapi_layout.zig")
LAYOUT_BUILD_PATH = Path("zigux/tests/phase3_export_uapi_layout_build.zig")
C_HEADER_SMOKE_PATH = Path("zigux/tests/phase3_export_uapi_c_header_smoke.c")
C_HEADER_SMOKE_CHECK_PATH = Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")
DEV_T_STARTER_PACKET_CHECK_PATH = Path("scripts/zigux/check-phase3-dev-t-starter-packet.py")
SHARED_SELFTEST_PATH = Path("scripts/zigux/validate_phase3_selftest.py")
SHARED_CHECK_RUNNER_PATH = Path("scripts/zigux/run-phase3-checks.py")

REQUIRED_MARKERS = {
    SURVEY_PATH: (
        "PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py",
        "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
        "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
        "PHASE3_ABI_H_PATH=include/zigux/abi.h",
        "PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h",
        "PHASE3_BINDING_HEADER_FAMILY_PATH=zigux/bindings/header_family.zig",
        "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
        "PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig",
        "PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig",
        "PHASE3_EXPORT_SHIM_BUILD_PATH=zigux/tests/phase3_export_shim_build.zig",
        "PHASE3_C_HEADER_SMOKE_PATH=zigux/tests/phase3_export_uapi_c_header_smoke.c",
        "PHASE3_EXPORT_UAPI_GAP=broader curated UAPI families and wider export-shim coverage remain open after the landed starter packet",
        "Do not use this lane to claim broader Phase 3 completion.",
    ),
    VALIDATOR_PATH: (
        '"""Validate the current bounded Phase 3 export/UAPI survey packet."""',
        'CATALOG_SELFTEST_CHECK_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")',
        'print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
        'print("PHASE3_EXPORT_UAPI_SURVEY=pass")',
    ),
    EXPORT_SHIM_PATH: (
        "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {",
        "pub fn validateVersion(candidate: Version) ExportStatus {",
        "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
        "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
    ),
    ABI_H_PATH: (
        "#define ZIGUX_ABI_VERSION 1U",
        "typedef struct zigux_boundary_header {",
        "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
        "static inline struct zigux_export_status zigux_ok_status(uint16_t facility)",
    ),
    LINUX_HEADER_PATH: (
        "static inline struct zigux_export_status zigux_uapi_validate_boundary_header(",
        "static inline struct zigux_export_status zigux_validate_boundary_header(",
        "static inline struct zigux_export_status zigux_uapi_validate_dev_t_range(",
    ),
    BINDING_VERSION_PATH: (
        "pub fn current() Version {",
        "pub fn validate(version: Version) abi.ExportStatus {",
    ),
    BINDING_DEV_T_PATH: (
        "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    BINDING_HEADER_FAMILY_PATH: (
        "pub const abi_major: u32 = uapi_version.abi_major;",
        "pub fn validateVersionStatus(version: Version) ExportStatus {",
        "pub fn validateDevTRangeStatus(start: DevTFields, end: DevTFields) ExportStatus {",
    ),
    UAPI_VERSION_PATH: (
        "pub fn matchesCurrent(version: Version) bool {",
        "pub fn validate(version: Version) abi.ExportStatus {",
    ),
    UAPI_DEV_T_PATH: (
        "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    DEV_T_HEADER_PATH: (
        "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
        "struct zigux_dev_t_fields {",
        "static inline int zigux_dev_t_fields_range_is_valid(",
    ),
    MANIFEST_PATH: (
        '"Documentation/zigux/phase3-export-uapi-boundary-survey.md"',
        '"scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
        '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
        '"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"',
        '"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"',
    ),
    TESTS_BUILD_PATH: (
        'const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);',
        'root_module.addImport("header_family_binding", header_family_binding);',
        'root_module.addImport("export_shim", export_shim);',
    ),
    MAKEFILE_PATH: (
        "phase3-export-uapi-layout:",
        "phase3-export-uapi-layout-test:",
        "phase3-export-shim-test:",
    ),
    EXPORT_SHIM_BUILD_PATH: (
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        'export_shim_module.addImport("version_binding", version_binding_module);',
        '"phase3-export-shim-test",',
    ),
    LAYOUT_TEST_PATH: (
        'test "header-family binding keeps the bounded relay surface explicit" {',
        'test "export shim relays starter boundary-header validation through the focused replay" {',
        'test "export shim relays starter dev_t validation and range checks through the focused replay" {',
    ),
    LAYOUT_BUILD_PATH: (
        '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        'root_module.addImport("header_family_binding", header_family_binding);',
        '"phase3-export-uapi-layout-test",',
    ),
    C_HEADER_SMOKE_PATH: (
        "#include <linux/zigux.h>",
        "static int check_boundary_header_relays(void)",
        "zigux_validate_boundary_header(",
        "static int check_dev_t_relays(void)",
        "zigux_uapi_validate_dev_t_range(",
    ),
    C_HEADER_SMOKE_CHECK_PATH: (
        '"""Compile and run the current Phase 3 export/UAPI C header smoke."""',
        'SMOKE_PATH = Path("zigux/tests/phase3_export_uapi_c_header_smoke.c")',
        'print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass")',
    ),
    DEV_T_STARTER_PACKET_CHECK_PATH: (
        'print("PHASE3_DEV_T_STARTER_PACKET=pass")',
    ),
    CATALOG_SELFTEST_CHECK_PATH: (
        "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
    ),
    SHARED_SELFTEST_PATH: (
        'print("PHASE3_VALIDATE_SELFTEST=pass")',
    ),
    SHARED_CHECK_RUNNER_PATH: (
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"PHASE3_EXPORT_UAPI_SURVEY=pass"',
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
    path = root / relative_path
    _write(path, _read(path).replace(marker, "", 1))
    issues = validate_repo(root)
    expected = f"missing {relative_path.as_posix()} marker: {marker}"
    if expected not in issues:
        print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        cases = (
            (
                SURVEY_PATH,
                "PHASE3_EXPORT_UAPI_GAP=broader curated UAPI families and wider export-shim coverage remain open after the landed starter packet",
                "expected export/UAPI gap marker removal to fail validation",
            ),
            (
                SURVEY_PATH,
                "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
                "expected catalog-selftest guard marker removal to fail validation",
            ),
            (
                EXPORT_SHIM_PATH,
                "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {",
                "expected export shim boundary-header marker removal to fail validation",
            ),
            (
                LINUX_HEADER_PATH,
                "static inline struct zigux_export_status zigux_uapi_validate_dev_t_range(",
                "expected linux header dev_t range marker removal to fail validation",
            ),
            (
                BINDING_HEADER_FAMILY_PATH,
                "pub fn validateDevTRangeStatus(start: DevTFields, end: DevTFields) ExportStatus {",
                "expected header-family range-status marker removal to fail validation",
            ),
            (
                MANIFEST_PATH,
                '"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"',
                "expected manifest replay-route marker removal to fail validation",
            ),
        )

        for relative_path, marker, message in cases:
            _populate_repo(root)
            if _expect_missing_marker(root, relative_path, marker, message) != 0:
                return 1

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES={1 + len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 3 export/UAPI survey packet."
    )
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
