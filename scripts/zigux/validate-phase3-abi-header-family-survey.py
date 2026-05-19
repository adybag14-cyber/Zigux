#!/usr/bin/env python3
"""Fail-close the current Phase 3 ABI header-family survey packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SURVEY_PATH = Path("Documentation/zigux/phase3-abi-header-family-survey.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase3-abi-header-family-survey.py")
ABI_SLICE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
CATALOG_PATH = Path("scripts/zigux/phase3_catalog.py")
CATALOG_SELFTEST_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")
LINUX_HEADER_PATH = Path("include/linux/zigux.h")
ABI_HEADER_PATH = Path("include/zigux/abi.h")
DEV_T_HEADER_PATH = Path("include/zigux/dev_t.h")
UAPI_VERSION_PATH = Path("zigux/uapi/version.zig")
UAPI_DEV_T_PATH = Path("zigux/uapi/dev_t.zig")
VERSION_BINDING_PATH = Path("zigux/bindings/version.zig")
DEV_T_BINDING_PATH = Path("zigux/bindings/dev_t.zig")
LAYOUT_TEST_PATH = Path("zigux/tests/phase3_export_uapi_layout.zig")
LAYOUT_BUILD_PATH = Path("zigux/tests/phase3_export_uapi_layout_build.zig")

REQUIRED_MARKERS = {
    SURVEY_PATH: (
        "PHASE3_ABI_HEADER_FAMILY_VALIDATOR_PATH=scripts/zigux/validate-phase3-abi-header-family-survey.py",
        "PHASE3_ABI_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md",
        "PHASE3_ABI_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json",
        "PHASE3_ABI_CATALOG_HELPER=scripts/zigux/phase3_catalog.py",
        "PHASE3_ABI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
        "PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h",
        "PHASE3_ABI_HEADER_PATH=include/zigux/abi.h",
        "PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h",
        "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
        "PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig",
        "PHASE3_VERSION_BINDING_PATH=zigux/bindings/version.zig",
        "PHASE3_DEV_T_BINDING_PATH=zigux/bindings/dev_t.zig",
        "PHASE3_EXPORT_UAPI_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
        "- `include/linux/zigux.h` keeps the Linux-facing header-family relay bounded to `zigux_uapi_version_current()`, the `zigux_uapi_version_has_current_*()` helpers, `zigux_uapi_version_matches_current()`, and `zigux_uapi_validate_version()` rather than introducing a second semantic owner.",
        "- `include/zigux/abi.h` remains the canonical owner for `zigux_boundary_header`, `zigux_export_status`, `zigux_default_header()`, `zigux_compatible_header()`, `zigux_abi_version_is_current()`, `zigux_header_is_canonical()`, `zigux_header_is_compatible()`, `zigux_header_extends_boundary()`, `zigux_header_requested_extra_bytes()`, and `zigux_header_canonicalize()`.",
        "- `include/zigux/dev_t.h` remains the canonical owner for the starter `dev_t` limits, `zigux_dev_t_fields_make()`, `zigux_mkdev()`, `zigux_major()`, `zigux_minor()`, `zigux_dev_t_fields_is_valid()`, and `zigux_dev_t_fields_range_is_valid()`.",
        "- `zigux/uapi/version.zig` and `zigux/bindings/version.zig` keep the current version packet aligned through `current()`, `matchesCurrent()`, the `hasCurrent*` helper family, and the shared size, alignment, and field-offset constants.",
        "- `zigux/uapi/dev_t.zig` and `zigux/bindings/dev_t.zig` keep the starter `dev_t` packet aligned through `init()`, `makeDeviceNumber()`, `majorFromDeviceNumber()`, `minorFromDeviceNumber()`, `fieldsFromDeviceNumber()`, `validate()`, and `validateRange()`.",
        "Current `master` no longer has a packet-local repo-reality gap for the bounded header-family survey follow-through itself.",
    ),
    VALIDATOR_PATH: (
        '"""Fail-close the current Phase 3 ABI header-family survey packet."""',
        'SURVEY_PATH = Path("Documentation/zigux/phase3-abi-header-family-survey.md")',
        'CATALOG_SELFTEST_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")',
        'print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass")',
        'print("PHASE3_ABI_HEADER_FAMILY_SURVEY=pass")',
    ),
    ABI_SLICE_PATH: (
        "scripts/zigux/validate-phase3-abi-header-family-survey.py",
        "Documentation/zigux/phase3-abi-header-family-survey.md",
        "the separate broader header-family binding follow-through remains the wider gap",
    ),
    MANIFEST_PATH: (
        '"Documentation/zigux/phase3-abi-header-family-survey.md"',
        '"scripts/zigux/validate-phase3-abi-header-family-survey.py"',
    ),
    CATALOG_PATH: (
        'Path("Documentation/zigux/phase3-abi-header-family-survey.md")',
        'Path("scripts/zigux/validate-phase3-abi-header-family-survey.py")',
        '"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py"',
    ),
    CATALOG_SELFTEST_PATH: (
        'Path("Documentation/zigux/phase3-abi-header-family-survey.md")',
        'Path("scripts/zigux/validate-phase3-abi-header-family-survey.py")',
    ),
    LINUX_HEADER_PATH: (
        "static inline struct zigux_uapi_version zigux_uapi_version_current(void) {",
        "static inline int zigux_uapi_version_matches_current(struct zigux_uapi_version version) {",
        "static inline struct zigux_export_status zigux_uapi_validate_version(",
        "static inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)",
        "static inline uint32_t zigux_uapi_boundary_header_requested_extra_bytes(",
        "static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
    ),
    ABI_HEADER_PATH: (
        "typedef struct zigux_boundary_header {",
        "struct zigux_export_status {",
        "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
        "static inline int zigux_header_is_canonical(zigux_boundary_header header)",
        "static inline uint32_t zigux_header_requested_extra_bytes(",
    ),
    DEV_T_HEADER_PATH: (
        "struct zigux_dev_t_fields {",
        "static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(",
        "static inline uint32_t zigux_mkdev(uint32_t major, uint32_t minor)",
        "static inline int zigux_dev_t_fields_range_is_valid(",
    ),
    UAPI_VERSION_PATH: (
        "pub const abi_major: u32 = 0;",
        "pub const abi_minor: u32 = 1;",
        "pub const header_family_revision: u32 = 1;",
        "pub fn current() Version {",
        "pub fn matchesCurrent(version: Version) bool {",
    ),
    UAPI_DEV_T_PATH: (
        "pub const abi_version: u32 = 1;",
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
        "pub fn validate(fields: Fields) bool {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    VERSION_BINDING_PATH: (
        "pub const abi_major = uapi.abi_major;",
        "pub const header_family_revision = uapi.header_family_revision;",
        "pub fn current() Version {",
        "pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {",
        "pub fn matchesCurrent(version: Version) bool {",
    ),
    DEV_T_BINDING_PATH: (
        "pub const abi_version = uapi.abi_version;",
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
        "pub fn validate(fields: Fields) bool {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    LAYOUT_TEST_PATH: (
        'test "export and uapi version layouts stay aligned" {',
        'test "export shim relays version compatibility without widening the boundary" {',
        'test "export shim reuses the canonical boundary header contract" {',
        'test "export shim mirrors boundary header predicate helpers" {',
        'test "export shim relays starter dev_t validation and range checks through the focused replay" {',
    ),
    LAYOUT_BUILD_PATH: (
        '.root_source_file = b.path("../uapi/dev_t.zig"),',
        '.root_source_file = b.path("../uapi/version.zig"),',
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        '"phase3-export-uapi-layout-test"',
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
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    marker_cases = (
        (
            SURVEY_PATH,
            "PHASE3_ABI_CATALOG_HELPER=scripts/zigux/phase3_catalog.py",
            "expected missing survey catalog helper marker was not reported",
        ),
        (
            SURVEY_PATH,
            "- `include/linux/zigux.h` keeps the Linux-facing header-family relay bounded to `zigux_uapi_version_current()`, the `zigux_uapi_version_has_current_*()` helpers, `zigux_uapi_version_matches_current()`, and `zigux_uapi_validate_version()` rather than introducing a second semantic owner.",
            "expected missing survey linux-header marker was not reported",
        ),
        (
            VALIDATOR_PATH,
            'print("PHASE3_ABI_HEADER_FAMILY_SURVEY=pass")',
            "expected missing validator pass marker was not reported",
        ),
        (
            CATALOG_PATH,
            '"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test"',
            "expected missing catalog header-family self-test route marker was not reported",
        ),
        (
            MANIFEST_PATH,
            '"Documentation/zigux/phase3-abi-header-family-survey.md"',
            "expected missing manifest header-family survey marker was not reported",
        ),
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_header_family_") as tmp_dir:
        root = Path(tmp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker, message in marker_cases:
            _populate_repo(root)
            if _expect_missing_marker(root, relative_path, marker, message) != 0:
                return 1

    print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST_CASE_COUNT={1 + len(marker_cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 ABI header-family survey packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the current Phase 3 ABI header-family packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / SURVEY_PATH}")
    print("PHASE3_ABI_HEADER_FAMILY_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
