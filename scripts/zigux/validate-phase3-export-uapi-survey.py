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
KERNEL_EXPORT_SHIM_GOVERNANCE_NOTE_PATH = Path(
    "Documentation/zigux/phase3-kernel-export-shim-governance.md"
)
DEV_T_HEADER_PATH = Path("include/zigux/dev_t.h")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
TESTS_BUILD_PATH = Path("zigux/tests/build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
LAYOUT_TEST_PATH = Path("zigux/tests/phase3_export_uapi_layout.zig")
C_HEADER_SMOKE_PATH = Path("zigux/tests/phase3_export_uapi_c_header_smoke.c")
C_HEADER_SMOKE_CHECK_PATH = Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")
CATALOG_HELPER_PATH = Path("scripts/zigux/phase3_catalog.py")
CATALOG_SELFTEST_CHECK_PATH = Path("scripts/zigux/check-phase3-catalog-selftest.py")
SHARED_CHECK_RUNNER_PATH = Path("scripts/zigux/run-phase3-checks.py")

REQUIRED_MARKERS = {
    SURVEY_PATH: (
        "PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py",
        "PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h",
        "PHASE3_KERNEL_EXPORT_SHIM_GOVERNANCE_NOTE=Documentation/zigux/phase3-kernel-export-shim-governance.md",
        "PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h",
        "PHASE3_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json",
        "PHASE3_SHARED_TESTS_BUILD_PATH=zigux/tests/build.zig",
        "PHASE3_SHARED_CHECK_RUNNER_PATH=scripts/zigux/run-phase3-checks.py",
        "PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig",
        "PHASE3_LAYOUT_SHARED_GATE=zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
        "PHASE3_LAYOUT_MAKE_ROUTE=make -C zigux phase3-export-uapi-layout",
        "PHASE3_C_HEADER_SMOKE_PATH=zigux/tests/phase3_export_uapi_c_header_smoke.c",
        "PHASE3_C_HEADER_SMOKE_CHECK=scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
        "PHASE3_C_HEADER_SMOKE_GATE=python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
        "PHASE3_EXPORT_UAPI_CATALOG_HELPER=scripts/zigux/phase3_catalog.py",
        "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
        "the status-tagged `validateDeviceFields` plus `validateDeviceNumber` relays",
        "the shared tests-root route in `zigux/tests/build.zig`, where `addPhase3ExportUapiLayout(...)` imports `header_family_binding`",
        "Current `master` now directly carries `zigux/tests/phase3_export_uapi_layout_build.zig`, so the dedicated `phase3-export-uapi-layout-test` route is shipped compile wiring rather than a missing same-family handoff.",
        "The existing `phase3-export-uapi-layout-test` target in `zigux/Makefile` therefore now points at live dedicated build wiring on current `master`.",
        "the shared tests-root export/UAPI layout replay, the dedicated `zigux/tests/phase3_export_uapi_layout_build.zig` handoff plus `phase3-export-uapi-layout-test` route, the direct C smoke replay, the kernel-facing governance note, and the starter validation relays explicit as shipped same-family evidence while leaving broader unfinished Phase 3 coverage and adjacent shared-summary truthfulness as the remaining follow-through",
        "the focused `zigux/tests/phase3_export_uapi_layout.zig` replay as wired through `zigux/tests/build.zig`",
    ),
    VALIDATOR_PATH: (
        '"""Fail-close the current Phase 3 export/UAPI boundary survey packet."""',
        'MAKEFILE_PATH = Path("zigux/Makefile")',
        'print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
        'print("PHASE3_EXPORT_UAPI_SURVEY=pass")',
    ),
    EXPORT_SHIM_PATH: (
        "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {",
        "pub fn validateDeviceFields(fields: DevTFields) ExportStatus {",
        "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
        "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
    ),
    BINDING_VERSION_PATH: (
        "pub fn current() Version {",
        "pub fn matchesCurrent(version: Version) bool {",
    ),
    BINDING_DEV_T_PATH: (
        "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    UAPI_VERSION_PATH: (
        "pub fn matchesCurrent(version: Version) bool {",
        "pub fn validate(version: Version) abi.ExportStatus {",
    ),
    UAPI_DEV_T_PATH: (
        "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    LINUX_HEADER_PATH: (
        "static inline struct zigux_export_status zigux_uapi_validate_boundary_header(",
        "static inline struct zigux_export_status zigux_validate_boundary_header(",
        "static inline struct zigux_export_status zigux_uapi_validate_dev_t_fields(",
        "static inline struct zigux_export_status zigux_uapi_validate_dev_t_components(",
        "static inline struct zigux_export_status zigux_uapi_validate_dev_t_range(",
    ),
    GOVERNANCE_NOTE_PATH: (
        "PHASE3_ZIGUX_H_PATH=include/linux/zigux.h",
        "PHASE3_ZIGUX_H_EXPORT_UAPI_SURVEY=Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    ),
    KERNEL_EXPORT_SHIM_GOVERNANCE_NOTE_PATH: (
        "PHASE3_KERNEL_EXPORT_SHIM_SCOPE=",
        "PHASE3_KERNEL_EXPORT_SHIM_NEXT_SAFE_STEP=",
        "It does not claim broader shared ABI validator, manifest, linux-header-governance, or low-level-wrapper completion.",
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
    ),
    TESTS_BUILD_PATH: (
        "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);",
        '"phase3-export-uapi-layout"',
        'root_module.addImport("header_family_binding", header_family_binding);',
        'root_module.addImport("export_shim", export_shim);',
    ),
    MAKEFILE_PATH: (
        "phase3-export-uapi-layout:",
        "phase3-export-uapi-layout-test:",
        "zigux/tests/phase3_export_uapi_layout_build.zig",
    ),
    LAYOUT_TEST_PATH: (
        'test "header-family binding keeps the bounded relay surface explicit" {',
        'test "export shim relays starter boundary-header validation through the focused replay" {',
        'test "export shim relays starter dev_t validation and range checks through the focused replay" {',
    ),
    C_HEADER_SMOKE_PATH: (
        "#include <linux/zigux.h>",
        "static int check_boundary_header_relays(void)",
        "zigux_validate_boundary_header(",
        "static int check_dev_t_relays(void)",
        "zigux_uapi_validate_dev_t_range(",
        "int main(void)",
    ),
    C_HEADER_SMOKE_CHECK_PATH: (
        '"""Compile and run the current Phase 3 export/UAPI C header smoke."""',
        'SMOKE_PATH = Path("zigux/tests/phase3_export_uapi_c_header_smoke.c")',
        'print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass")',
        'print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass")',
    ),
    CATALOG_HELPER_PATH: (
        'Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")',
        '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
        '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
        '"make -C zigux phase3-export-uapi-layout"',
        '"make -C zigux phase3-export-uapi-layout-test"',
    ),
    CATALOG_SELFTEST_CHECK_PATH: (
        'Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")',
        '\'"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"\'',
        '\'"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"\'',
        '\'"make -C zigux phase3-export-uapi-layout"\'',
        '\'"make -C zigux phase3-export-uapi-layout-test"\'',
    ),
    SHARED_CHECK_RUNNER_PATH: (
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
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
            "PHASE3_KERNEL_EXPORT_SHIM_GOVERNANCE_NOTE=Documentation/zigux/phase3-kernel-export-shim-governance.md",
            "expected missing kernel export-shim governance survey marker was not reported",
        ),
        (
            SURVEY_PATH,
            "PHASE3_EXPORT_UAPI_CATALOG_HELPER=scripts/zigux/phase3_catalog.py",
            "expected missing catalog helper survey marker was not reported",
        ),
        (
            SURVEY_PATH,
            "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
            "expected missing catalog selftest guard survey marker was not reported",
        ),
        (
            SURVEY_PATH,
            "PHASE3_LAYOUT_SHARED_GATE=zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
            "expected missing shared export/uapi layout gate marker was not reported",
        ),
        (
            SURVEY_PATH,
            "Current `master` now directly carries `zigux/tests/phase3_export_uapi_layout_build.zig`, so the dedicated `phase3-export-uapi-layout-test` route is shipped compile wiring rather than a missing same-family handoff.",
            "expected missing dedicated build evidence marker was not reported",
        ),
        (
            SURVEY_PATH,
            "The existing `phase3-export-uapi-layout-test` target in `zigux/Makefile` therefore now points at live dedicated build wiring on current `master`.",
            "expected missing makefile-backed dedicated build marker was not reported",
        ),
        (
            TESTS_BUILD_PATH,
            'root_module.addImport("header_family_binding", header_family_binding);',
            "expected missing shared tests-root header-family import marker was not reported",
        ),
        (
            MAKEFILE_PATH,
            "phase3-export-uapi-layout-test:",
            "expected missing phase3 export/uapi dedicated make route marker was not reported",
        ),
        (
            C_HEADER_SMOKE_PATH,
            "zigux_validate_boundary_header(",
            "expected missing c-header smoke boundary-validation marker was not reported",
        ),
        (
            KERNEL_EXPORT_SHIM_GOVERNANCE_NOTE_PATH,
            "PHASE3_KERNEL_EXPORT_SHIM_SCOPE=",
            "expected missing kernel export-shim governance scope marker was not reported",
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