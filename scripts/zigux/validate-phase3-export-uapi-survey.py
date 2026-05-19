#!/usr/bin/env python3
"""Fail-close the current Phase 3 export/UAPI boundary survey packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SURVEY_PATH = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase3-export-uapi-survey.py")
EXPORT_SHIM_PATH = Path("zigux/kernel/export_shim.zig")
UAPI_VERSION_PATH = Path("zigux/uapi/version.zig")
UAPI_DEV_T_PATH = Path("zigux/uapi/dev_t.zig")
LINUX_HEADER_PATH = Path("include/linux/zigux.h")
LINUX_HEADER_GOVERNANCE_GAP_PATH = (
    "Documentation/zigux/phase3-linux-zigux-header-governance.md"
)
DEV_T_HEADER_PATH = Path("include/zigux/dev_t.h")
ABI_HEADER_PATH = Path("include/zigux/abi.h")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
LAYOUT_TEST_PATH = Path("zigux/tests/phase3_export_uapi_layout.zig")
LAYOUT_BUILD_PATH = Path("zigux/tests/phase3_export_uapi_layout_build.zig")
CATALOG_HELPER_PATH = Path("scripts/zigux/phase3_catalog.py")
CATALOG_SELFTEST_GAP_PATH = "scripts/zigux/check-phase3-catalog-selftest.py"

MISSING_GAP_PATHS = (
    LINUX_HEADER_GOVERNANCE_GAP_PATH,
    CATALOG_SELFTEST_GAP_PATH,
)

REQUIRED_MARKERS = {
    SURVEY_PATH: (
        "PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py",
        "PHASE3_EXPORT_UAPI_VALIDATOR_SELF_TEST=python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
        "PHASE3_EXPORT_UAPI_VALIDATOR_RUN=python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
        "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
        "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
        "PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig",
        "PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h",
        "PHASE3_LINUX_ZIGUX_H_GOVERNANCE_GAP=Documentation/zigux/phase3-linux-zigux-header-governance.md",
        "PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h",
        "PHASE3_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json",
        "PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig",
        "PHASE3_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig",
        "PHASE3_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
        "PHASE3_EXPORT_UAPI_CATALOG_HELPER=scripts/zigux/phase3_catalog.py",
        "PHASE3_EXPORT_UAPI_ACTIVE_GAP=scripts/zigux/check-phase3-catalog-selftest.py",
        "The packet-local validator is now present and should stay aligned with this survey rather than being tracked as a missing companion.",
        "- `zigux/kernel/export_shim.zig` keeps the export boundary reviewable through `canonicalHeader`, `headerIsCanonical`, `headerIsCompatible`, `requestedExtraBytes`, `versionMatchesCurrent`, `validateVersion`, and the status-tagged `validateDeviceNumber` relay.",
        "- That same starter export surface also now carries the status-tagged `validateDeviceRange` relay plus the bounded `encodeDeviceNumber` and `decodeDeviceNumber` bridge without widening into broader UAPI growth.",
        "- `zigux/tests/phase3_export_uapi_layout.zig` together with `zigux/tests/phase3_export_uapi_layout_build.zig` keeps the `BoundaryHeader`, `ExportStatus`, starter version-compatibility relay, and device-number bridge contract visible on the direct replay route `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`.",
        "Current `master` does directly serve `scripts/zigux/phase3_catalog.py` as the bounded Phase 3 catalog helper and `zigux/tests/fixtures/phase3_abi_manifest.json` as the same-family manifest-backed inventory companion, but repeated current-head reads still return missing for `Documentation/zigux/phase3-linux-zigux-header-governance.md`.",
        "The remaining repo-reality gap for this packet is now the absent linux-header governance companion plus the separate catalog-selftest guard:",
        "This survey should keep the manifest-backed ABI inventory explicit as a shipped same-family companion while continuing to treat the absent linux-header governance note and absent catalog-selftest guard as the active packet-local gaps.",
    ),
    VALIDATOR_PATH: (
        '"""Fail-close the current Phase 3 export/UAPI boundary survey packet."""',
        'SURVEY_PATH = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")',
        'LINUX_HEADER_GOVERNANCE_GAP_PATH = (',
        'MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")',
        'CATALOG_SELFTEST_GAP_PATH = "scripts/zigux/check-phase3-catalog-selftest.py"',
        'print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
        'print("PHASE3_EXPORT_UAPI_SURVEY=pass")',
    ),
    EXPORT_SHIM_PATH: (
        "pub fn canonicalHeader(flags: u16) BoundaryHeader {",
        "pub fn headerIsCanonical(header: BoundaryHeader) bool {",
        "pub fn headerIsCompatible(header: BoundaryHeader) bool {",
        "pub fn requestedExtraBytes(header: BoundaryHeader) u32 {",
        "pub fn versionMatchesCurrent(candidate: Version) bool {",
        "pub fn validateVersion(candidate: Version) ExportStatus {",
        "pub fn encodeDeviceNumber(fields: DevTFields) ?u32 {",
        "pub fn decodeDeviceNumber(device_number: u32) DevTFields {",
        "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
        "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
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
        "pub const Fields = extern struct {",
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn validate(fields: Fields) bool {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    LINUX_HEADER_PATH: (
        "#define ZIGUX_UAPI_ABI_MAJOR 0u",
        "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u",
        "static inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)",
        "static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
    ),
    DEV_T_HEADER_PATH: (
        "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
        "#define ZIGUX_DEV_MINOR_BITS 20u",
        "struct zigux_dev_t_fields {",
        "static inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
    ),
    ABI_HEADER_PATH: (
        "#define ZIGUX_ABI_VERSION 1U",
        "typedef struct zigux_boundary_header {",
        "struct zigux_export_status {",
        "struct zigux_interop_policy {",
    ),
    MANIFEST_PATH: (
        '"phase": "Phase 3"',
        '"Documentation/zigux/phase3-export-uapi-boundary-survey.md"',
        '"scripts/zigux/validate-phase3-export-uapi-survey.py"',
    ),
    LAYOUT_TEST_PATH: (
        'test "export and uapi dev_t layouts stay aligned" {',
        'test "export and uapi version layouts stay aligned" {',
        'test "export shim relays version compatibility without widening the boundary" {',
        'test "export shim encodes starter dev_t numbers without widening the boundary" {',
        'test "export shim reuses the canonical boundary header contract" {',
        'test "export shim mirrors boundary header predicate helpers" {',
        'test "export shim keeps facility tagged statuses explicit" {',
    ),
    LAYOUT_BUILD_PATH: (
        '.root_source_file = b.path("../uapi/dev_t.zig"),',
        '.root_source_file = b.path("../uapi/version.zig"),',
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        '"phase3-export-uapi-layout-test"',
    ),
    CATALOG_HELPER_PATH: (
        'PHASE3_CATALOG_SCOPE = "abi-runtime"',
        'Path("scripts/zigux/phase3_catalog.py")',
        'print("PHASE3_CATALOG_SELF_TEST=pass")',
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

    for gap in MISSING_GAP_PATHS:
        if (repo_root / gap).exists():
            issues.append(f"expected gap is present on disk: {gap}")

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
        print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def _expect_returned_gap(root: Path, gap_path: str, message: str) -> int:
    _populate_repo(root)
    (root / gap_path).parent.mkdir(parents=True, exist_ok=True)
    _write(root / gap_path, "# drift\n")
    issues = validate_repo(root)
    expected = f"expected gap is present on disk: {gap_path}"
    if expected not in issues:
        print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    marker_cases = (
        (
            SURVEY_PATH,
            "PHASE3_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json",
            "expected missing survey manifest marker was not reported",
        ),
        (
            SURVEY_PATH,
            "- `zigux/kernel/export_shim.zig` keeps the export boundary reviewable through `canonicalHeader`, `headerIsCanonical`, `headerIsCompatible`, `requestedExtraBytes`, `versionMatchesCurrent`, `validateVersion`, and the status-tagged `validateDeviceNumber` relay.",
            "expected missing survey export-shim relay marker was not reported",
        ),
        (
            SURVEY_PATH,
            "- That same starter export surface also now carries the status-tagged `validateDeviceRange` relay plus the bounded `encodeDeviceNumber` and `decodeDeviceNumber` bridge without widening into broader UAPI growth.",
            "expected missing survey dev_t relay marker was not reported",
        ),
        (
            SURVEY_PATH,
            "PHASE3_LINUX_ZIGUX_H_GOVERNANCE_GAP=Documentation/zigux/phase3-linux-zigux-header-governance.md",
            "expected missing survey linux-header governance gap marker was not reported",
        ),
        (
            SURVEY_PATH,
            "PHASE3_EXPORT_UAPI_ACTIVE_GAP=scripts/zigux/check-phase3-catalog-selftest.py",
            "expected missing catalog-selftest gap marker was not reported",
        ),
        (
            VALIDATOR_PATH,
            'print("PHASE3_EXPORT_UAPI_SURVEY=pass")',
            "expected missing validator pass marker was not reported",
        ),
        (
            EXPORT_SHIM_PATH,
            "pub fn versionMatchesCurrent(candidate: Version) bool {",
            "expected missing export-shim version relay marker was not reported",
        ),
        (
            EXPORT_SHIM_PATH,
            "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
            "expected missing export-shim range relay marker was not reported",
        ),
        (
            UAPI_VERSION_PATH,
            "pub fn matchesCurrent(version: Version) bool {",
            "expected missing version compatibility marker was not reported",
        ),
        (
            UAPI_DEV_T_PATH,
            "pub fn validateRange(start: Fields, end: Fields) bool {",
            "expected missing dev_t range marker was not reported",
        ),
        (
            LINUX_HEADER_PATH,
            "static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
            "expected missing linux header validator marker was not reported",
        ),
        (
            DEV_T_HEADER_PATH,
            "static inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
            "expected missing dev_t header validator marker was not reported",
        ),
        (
            ABI_HEADER_PATH,
            "struct zigux_interop_policy {",
            "expected missing abi header interop policy marker was not reported",
        ),
        (
            MANIFEST_PATH,
            '"scripts/zigux/validate-phase3-export-uapi-survey.py"',
            "expected missing manifest survey validator marker was not reported",
        ),
        (
            LAYOUT_TEST_PATH,
            'test "export shim relays version compatibility without widening the boundary" {',
            "expected missing layout version relay marker was not reported",
        ),
        (
            LAYOUT_TEST_PATH,
            'test "export shim encodes starter dev_t numbers without widening the boundary" {',
            "expected missing layout dev_t bridge marker was not reported",
        ),
        (
            LAYOUT_BUILD_PATH,
            '"phase3-export-uapi-layout-test"',
            "expected missing layout build target marker was not reported",
        ),
        (
            CATALOG_HELPER_PATH,
            'print("PHASE3_CATALOG_SELF_TEST=pass")',
            "expected missing catalog helper marker was not reported",
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

        for gap_path in MISSING_GAP_PATHS:
            if (
                _expect_returned_gap(
                    root,
                    gap_path,
                    f"expected returned-gap guard was not reported for {gap_path}",
                )
                != 0
            ):
                return 1

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print(
        "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES="
        f"{1 + len(marker_cases) + len(MISSING_GAP_PATHS)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 export/UAPI packet."
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
