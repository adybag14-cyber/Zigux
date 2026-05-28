#!/usr/bin/env python3
"""Validate the current bounded Phase 3 export/UAPI survey packet."""

from __future__ import annotations

import argparse
import collections
import re
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
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
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

PUB_FN_PATTERN = re.compile(r"^pub fn ([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)

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
        "PHASE3_C_HEADER_SMOKE_WORKFLOW_ROUTE=.github/workflows/zigux-bootstrap.yml",
        "PHASE3_C_HEADER_SMOKE_WORKFLOW_GATE=.github/workflows/zigux-bootstrap.yml -> Run current Phase 3 export/UAPI C header smoke",
        "PHASE3_EXPORT_UAPI_GAP=broader curated UAPI families and wider export-shim coverage remain open after the landed starter packet",
        "Do not use this lane to claim broader Phase 3 completion.",
    ),
    VALIDATOR_PATH: (
        '"""Validate the current bounded Phase 3 export/UAPI survey packet."""',
        'WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")',
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
    WORKFLOW_PATH: (
        "- name: Run current Phase 3 export/UAPI C header smoke",
        "run: python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    ),
    MANIFEST_PATH: (
        '"Documentation/zigux/phase3-export-uapi-boundary-survey.md"',
        '"scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
        '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
        '"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"',
        '"make -C zigux phase3-export-uapi-layout-test"',
        '"make -C zigux phase3-export-shim-test"',
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
        'test "header-family status wrappers stay aligned with export shim validation" {',
        'test "version binding relays centralized boundary header helpers without widening the boundary" {',
        'test "export shim relays version compatibility without widening the boundary" {',
        'test "export shim relays starter boundary-header validation through the focused replay" {',
        'test "export shim relays starter dev_t validation and range checks through the focused replay" {',
        'test "export shim reuses the canonical boundary header contract" {',
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
        'Path("scripts/zigux/validate-phase3-export-uapi-survey.py")',
        '"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass"',
        '"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES="',
        'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
        '"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass"',
        '"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT="',
        'print("PHASE3_VALIDATE_SELFTEST=pass")',
    ),
    SHARED_CHECK_RUNNER_PATH: (
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"validated Documentation/zigux/phase3-export-uapi-boundary-survey.md"',
        '"PHASE3_EXPORT_UAPI_SURVEY=pass"',
        '"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"',
        '"validated zigux/tests/phase3_export_uapi_c_header_smoke.c"',
        '"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass"',
    ),
}

REQUIRED_FUNCTIONS = {
    EXPORT_SHIM_PATH: (
        "canonicalHeader",
        "compatibleHeader",
        "isCurrentAbiVersion",
        "isCanonicalSize",
        "isCompatibleSize",
        "headerIsCanonical",
        "headerIsCompatible",
        "extendsBoundary",
        "requestedExtraBytes",
        "canonicalizeHeader",
        "validateBoundaryHeader",
        "currentVersion",
        "hasCurrentAbiMajor",
        "hasCurrentAbiMinor",
        "hasCurrentHeaderFamilyRevision",
        "versionMatchesCurrent",
        "validateVersion",
        "makeDevTFields",
        "encodeDeviceNumber",
        "decodeDeviceNumber",
        "deviceFieldsAreValid",
        "validateDeviceFields",
        "validateDeviceNumber",
        "deviceRangeIsValid",
        "validateDeviceRange",
    ),
    UAPI_VERSION_PATH: (
        "current",
        "eql",
        "hasCurrentAbiMajor",
        "hasCurrentAbiMinor",
        "hasCurrentHeaderFamilyRevision",
        "matchesCurrent",
        "validate",
        "canonicalHeader",
        "boundaryHeader",
        "compatibleHeader",
        "hasCurrentAbiVersion",
        "isCanonicalSize",
        "isCompatibleSize",
        "isCanonical",
        "isCompatible",
        "extendsBoundary",
        "requestedExtraBytes",
        "canonicalizeHeader",
        "validateBoundaryHeader",
    ),
    UAPI_DEV_T_PATH: (
        "init",
        "makeDeviceNumber",
        "majorFromDeviceNumber",
        "minorFromDeviceNumber",
        "fieldsFromDeviceNumber",
        "validate",
        "validateRange",
    ),
    BINDING_HEADER_FAMILY_PATH: (
        "currentVersion",
        "hasCurrentAbiMajor",
        "hasCurrentAbiMinor",
        "hasCurrentHeaderFamilyRevision",
        "versionMatchesCurrent",
        "validateVersionStatus",
        "currentBoundaryHeader",
        "compatibleBoundaryHeader",
        "boundaryHeaderHasCurrentAbiVersion",
        "boundaryHeaderIsCompatibleSize",
        "boundaryHeaderIsCanonicalSize",
        "boundaryHeaderIsCanonical",
        "boundaryHeaderIsCompatible",
        "boundaryHeaderExtendsBoundary",
        "boundaryHeaderRequestedExtraBytes",
        "canonicalizeBoundaryHeader",
        "validateBoundaryHeaderStatus",
        "initDevTFields",
        "makeDeviceNumber",
        "majorFromDeviceNumber",
        "minorFromDeviceNumber",
        "fieldsFromDeviceNumber",
        "validateDevTFields",
        "validateDevTFieldsStatus",
        "validateDevTComponentsStatus",
        "validateDevTRange",
        "validateDevTRangeStatus",
        "okStatus",
        "errorStatus",
        "statusIsOk",
        "facilityFromInt",
        "facilityIsKnown",
        "statusHasKnownFacility",
    ),
}

UAPI_VERSION_EXPORT_SHIM_ALIGNMENT = {
    "current": "currentVersion",
    "hasCurrentAbiMajor": "hasCurrentAbiMajor",
    "hasCurrentAbiMinor": "hasCurrentAbiMinor",
    "hasCurrentHeaderFamilyRevision": "hasCurrentHeaderFamilyRevision",
    "matchesCurrent": "versionMatchesCurrent",
    "validate": "validateVersion",
    "boundaryHeader": "canonicalHeader",
    "compatibleHeader": "compatibleHeader",
    "hasCurrentAbiVersion": "isCurrentAbiVersion",
    "isCanonicalSize": "isCanonicalSize",
    "isCompatibleSize": "isCompatibleSize",
    "isCanonical": "headerIsCanonical",
    "isCompatible": "headerIsCompatible",
    "extendsBoundary": "extendsBoundary",
    "requestedExtraBytes": "requestedExtraBytes",
    "canonicalizeHeader": "canonicalizeHeader",
    "validateBoundaryHeader": "validateBoundaryHeader",
}

UAPI_VERSION_HEADER_FAMILY_ALIGNMENT = {
    "current": "currentVersion",
    "hasCurrentAbiMajor": "hasCurrentAbiMajor",
    "hasCurrentAbiMinor": "hasCurrentAbiMinor",
    "hasCurrentHeaderFamilyRevision": "hasCurrentHeaderFamilyRevision",
    "matchesCurrent": "versionMatchesCurrent",
    "validate": "validateVersionStatus",
    "boundaryHeader": "currentBoundaryHeader",
    "compatibleHeader": "compatibleBoundaryHeader",
    "hasCurrentAbiVersion": "boundaryHeaderHasCurrentAbiVersion",
    "isCanonicalSize": "boundaryHeaderIsCanonicalSize",
    "isCompatibleSize": "boundaryHeaderIsCompatibleSize",
    "isCanonical": "boundaryHeaderIsCanonical",
    "isCompatible": "boundaryHeaderIsCompatible",
    "extendsBoundary": "boundaryHeaderExtendsBoundary",
    "requestedExtraBytes": "boundaryHeaderRequestedExtraBytes",
    "canonicalizeHeader": "canonicalizeBoundaryHeader",
    "validateBoundaryHeader": "validateBoundaryHeaderStatus",
}

UAPI_DEV_T_EXPORT_SHIM_ALIGNMENT = {
    "init": "makeDevTFields",
    "fieldsFromDeviceNumber": "decodeDeviceNumber",
    "validate": "deviceFieldsAreValid",
    "validateRange": "deviceRangeIsValid",
}

UAPI_DEV_T_HEADER_FAMILY_ALIGNMENT = {
    "init": "initDevTFields",
    "makeDeviceNumber": "makeDeviceNumber",
    "majorFromDeviceNumber": "majorFromDeviceNumber",
    "minorFromDeviceNumber": "minorFromDeviceNumber",
    "fieldsFromDeviceNumber": "fieldsFromDeviceNumber",
    "validate": "validateDevTFields",
    "validateRange": "validateDevTRange",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _exported_pub_function_names(text: str) -> list[str]:
    return PUB_FN_PATTERN.findall(text)


def _validate_required_markers(repo_root: Path) -> list[str]:
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


def _validate_required_functions(repo_root: Path) -> tuple[list[str], dict[Path, set[str]]]:
    issues: list[str] = []
    exported_by_path: dict[Path, set[str]] = {}
    for relative_path, required_functions in REQUIRED_FUNCTIONS.items():
        path = repo_root / relative_path
        if not path.is_file():
            continue
        exported = _exported_pub_function_names(_read(path))
        exported_counts = collections.Counter(exported)
        exported_set = set(exported)
        exported_by_path[relative_path] = exported_set
        for function_name in sorted(
            name for name, count in exported_counts.items() if count > 1
        ):
            issues.append(
                f"duplicate {relative_path.as_posix()} pub fn: {function_name}"
            )
        for function_name in required_functions:
            if function_name not in exported_set:
                issues.append(
                    f"missing {relative_path.as_posix()} exported pub fn: {function_name}"
                )
    return issues, exported_by_path


def _validate_alignment(
    exported_by_path: dict[Path, set[str]],
    source_path: Path,
    target_path: Path,
    mapping: dict[str, str],
) -> list[str]:
    issues: list[str] = []
    source_exported = exported_by_path.get(source_path, set())
    target_exported = exported_by_path.get(target_path, set())
    for source_name, target_name in mapping.items():
        if source_name not in source_exported:
            continue
        if target_name not in target_exported:
            issues.append(
                "missing aligned relay function: "
                f"{target_path.as_posix()}::{target_name} "
                f"for {source_path.as_posix()}::{source_name}"
            )
    return issues


def validate_repo(repo_root: Path) -> list[str]:
    issues = _validate_required_markers(repo_root)
    function_issues, exported_by_path = _validate_required_functions(repo_root)
    issues.extend(function_issues)
    issues.extend(
        _validate_alignment(
            exported_by_path,
            UAPI_VERSION_PATH,
            EXPORT_SHIM_PATH,
            UAPI_VERSION_EXPORT_SHIM_ALIGNMENT,
        )
    )
    issues.extend(
        _validate_alignment(
            exported_by_path,
            UAPI_VERSION_PATH,
            BINDING_HEADER_FAMILY_PATH,
            UAPI_VERSION_HEADER_FAMILY_ALIGNMENT,
        )
    )
    issues.extend(
        _validate_alignment(
            exported_by_path,
            UAPI_DEV_T_PATH,
            EXPORT_SHIM_PATH,
            UAPI_DEV_T_EXPORT_SHIM_ALIGNMENT,
        )
    )
    issues.extend(
        _validate_alignment(
            exported_by_path,
            UAPI_DEV_T_PATH,
            BINDING_HEADER_FAMILY_PATH,
            UAPI_DEV_T_HEADER_FAMILY_ALIGNMENT,
        )
    )
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        lines = list(markers)
        existing = "\n".join(lines) + "\n"
        if relative_path in REQUIRED_FUNCTIONS:
            for function_name in REQUIRED_FUNCTIONS[relative_path]:
                signature = f"pub fn {function_name}("
                if signature not in existing:
                    lines.append(f"pub fn {function_name}() void {{}}")
        _write(root / relative_path, "\n".join(lines) + "\n")


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


def _expect_missing_pub_fn(
    root: Path, relative_path: Path, function_name: str, message: str
) -> int:
    path = root / relative_path
    text = _read(path)
    stub = f"pub fn {function_name}() void {{}}\n"
    if stub not in text:
        print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=fail")
        print(f"self-test stub missing for {relative_path.as_posix()}::{function_name}")
        return 1
    _write(path, text.replace(stub, "", 1))
    issues = validate_repo(root)
    expected = f"missing {relative_path.as_posix()} exported pub fn: {function_name}"
    if expected not in issues:
        print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def _expect_duplicate_pub_fn(
    root: Path, relative_path: Path, function_name: str, message: str
) -> int:
    path = root / relative_path
    text = _read(path)
    stub = f"pub fn {function_name}() void {{}}\n"
    _write(path, text + stub)
    issues = validate_repo(root)
    expected = f"duplicate {relative_path.as_posix()} pub fn: {function_name}"
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
                SURVEY_PATH,
                "PHASE3_C_HEADER_SMOKE_WORKFLOW_GATE=.github/workflows/zigux-bootstrap.yml -> Run current Phase 3 export/UAPI C header smoke",
                "expected export/UAPI workflow gate marker removal to fail validation",
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
                WORKFLOW_PATH,
                "- name: Run current Phase 3 export/UAPI C header smoke",
                "expected workflow phase3 export/UAPI C smoke step removal to fail validation",
            ),
            (
                BINDING_HEADER_FAMILY_PATH,
                "pub fn validateDevTRangeStatus(start: DevTFields, end: DevTFields) ExportStatus {",
                "expected header-family range-status marker removal to fail validation",
            ),
            (
                LAYOUT_TEST_PATH,
                'test "header-family status wrappers stay aligned with export shim validation" {',
                "expected export/UAPI layout status-wrapper replay removal to fail validation",
            ),
            (
                LAYOUT_TEST_PATH,
                'test "export shim reuses the canonical boundary header contract" {',
                "expected export/UAPI layout canonical-boundary replay removal to fail validation",
            ),
            (
                MANIFEST_PATH,
                '"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"',
                "expected manifest replay-route marker removal to fail validation",
            ),
            (
                MANIFEST_PATH,
                '"make -C zigux phase3-export-shim-test"',
                "expected manifest make-route marker removal to fail validation",
            ),
            (
                SHARED_SELFTEST_PATH,
                'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
                "expected shared self-test export/UAPI c-header smoke marker removal to fail validation",
            ),
            (
                SHARED_CHECK_RUNNER_PATH,
                '"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"',
                "expected shared check runner export/UAPI c-header smoke route removal to fail validation",
            ),
        )

        for relative_path, marker, message in cases:
            _populate_repo(root)
            if _expect_missing_marker(root, relative_path, marker, message) != 0:
                return 1

        function_cases = (
            (
                UAPI_VERSION_PATH,
                "current",
                "expected missing UAPI version current helper to fail validation",
            ),
            (
                UAPI_DEV_T_PATH,
                "fieldsFromDeviceNumber",
                "expected missing UAPI dev_t decode helper to fail validation",
            ),
            (
                EXPORT_SHIM_PATH,
                "deviceFieldsAreValid",
                "expected missing export shim dev_t validity relay to fail validation",
            ),
            (
                BINDING_HEADER_FAMILY_PATH,
                "currentVersion",
                "expected missing header-family currentVersion relay to fail validation",
            ),
        )

        for relative_path, function_name, message in function_cases:
            _populate_repo(root)
            if _expect_missing_pub_fn(root, relative_path, function_name, message) != 0:
                return 1

        duplicate_cases = (
            (
                EXPORT_SHIM_PATH,
                "validateDeviceRange",
                "expected duplicate export shim dev_t range relay to fail validation",
            ),
            (
                BINDING_HEADER_FAMILY_PATH,
                "currentVersion",
                "expected duplicate header-family currentVersion relay to fail validation",
            ),
        )

        for relative_path, function_name, message in duplicate_cases:
            _populate_repo(root)
            if _expect_duplicate_pub_fn(root, relative_path, function_name, message) != 0:
                return 1

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES={1 + len(cases) + len(function_cases) + len(duplicate_cases)}")
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
