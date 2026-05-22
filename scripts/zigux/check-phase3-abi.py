#!/usr/bin/env python3
"""Fail-close the current bounded Phase 3 ABI, export/UAPI, and dump packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ABI_SLICE_NOTE = Path("Documentation/zigux/phase3-abi-slice.md")
ABI_HEADER = Path("include/zigux/abi.h")
LINUX_ZIGUX_HEADER = Path("include/linux/zigux.h")
DEV_T_HEADER = Path("include/zigux/dev_t.h")
UAPI_DEV_T = Path("zigux/uapi/dev_t.zig")
UAPI_VERSION = Path("zigux/uapi/version.zig")
BINDING_ABI = Path("zigux/bindings/abi.zig")
BINDING_DEV_T = Path("zigux/bindings/dev_t.zig")
BINDING_VERSION = Path("zigux/bindings/version.zig")
BINDING_HEADER_FAMILY = Path("zigux/bindings/header_family.zig")
BINDING_NOTIFIER = Path("zigux/bindings/notifier_abi.zig")
EXPORT_SHIM = Path("zigux/kernel/export_shim.zig")
PHASE3_CATALOG = Path("scripts/zigux/phase3_catalog.py")
ABI_TEST = Path("zigux/tests/phase3_abi.zig")
TESTS_BUILD = Path("zigux/tests/build.zig")
ABI_DUMP = Path("zigux/tests/phase3_abi_dump_current.zig")
EXPORT_UAPI_LAYOUT = Path("zigux/tests/phase3_export_uapi_layout.zig")
EXPORT_UAPI_LAYOUT_BUILD = Path("zigux/tests/phase3_export_uapi_layout_build.zig")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_MARKERS = {
    ABI_SLICE_NOTE: (
        "PHASE3_CURRENT_INTEROP_GAP=",
        "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
        "Documentation/zigux/phase3-linux-zigux-header-governance.md",
        "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
        "zigux/kernel/export_shim.zig",
        "zigux/tests/phase3_export_uapi_layout.zig",
        "zigux/tests/phase3_abi_dump_current.zig",
        "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
        "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
        "zig build phase3-dump --build-file zigux/tests/build.zig",
        ".github/workflows/zigux-bootstrap.yml",
    ),
    ABI_HEADER: (
        "#define ZIGUX_ABI_VERSION 1U",
        "struct zigux_boundary_header {",
        "struct zigux_export_status {",
        "struct zigux_interop_policy {",
        "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
        "static inline zigux_boundary_header zigux_compatible_header(",
        "static inline uint32_t zigux_header_requested_extra_bytes(",
        "static inline struct zigux_export_status zigux_ok_status(uint16_t facility)",
    ),
    LINUX_ZIGUX_HEADER: (
        "#define ZIGUX_UAPI_ABI_MAJOR 0u",
        "#define ZIGUX_UAPI_ABI_MINOR 1u",
        "struct zigux_uapi_version {",
        "static inline struct zigux_uapi_version zigux_uapi_version_current(void)",
        "static inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)",
    ),
    DEV_T_HEADER: (
        "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
        "#define ZIGUX_DEV_T_FIELDS_SIZE 8u",
        "struct zigux_dev_t_fields {",
        "static inline uint32_t zigux_mkdev(uint32_t major, uint32_t minor)",
    ),
    UAPI_DEV_T: (
        "pub const abi_version: u32 = 1;",
        "pub const Fields = extern struct {",
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn validate(fields: Fields) bool {",
    ),
    UAPI_VERSION: (
        "pub const abi_major: u32 = 0;",
        "pub const abi_minor: u32 = 1;",
        "pub const Version = extern struct {",
        "pub fn current() Version {",
    ),
    BINDING_ABI: (
        'const notifier_abi = @import("notifier_abi.zig");',
        "pub const ABI_VERSION: u16 = 1;",
        "pub const BoundaryHeader = extern struct {",
        "pub const ExportStatus = extern struct {",
        "pub const InteropPolicy = extern struct {",
        "pub fn defaultHeader(flags: u16) BoundaryHeader {",
        "pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader {",
        "pub fn requestedExtraBytes(header: BoundaryHeader) u32 {",
        "pub fn okStatus(facility: Facility) ExportStatus {",
    ),
    BINDING_DEV_T: (
        "pub const abi_version = uapi.abi_version;",
        "pub const Fields = uapi.Fields;",
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    BINDING_VERSION: (
        "pub const abi_major = uapi.abi_major;",
        "pub const Version = uapi.Version;",
        "pub fn current() Version {",
        "pub fn matchesCurrent(version: Version) bool {",
    ),
    BINDING_HEADER_FAMILY: (
        'const abi = @import("abi_bindings");',
        'const dev_t_binding = @import("dev_t_binding");',
        'const version_binding = @import("version_binding");',
        "pub fn currentBoundaryHeader(flags: u16) BoundaryHeader {",
        "pub fn boundaryHeaderRequestedExtraBytes(header: BoundaryHeader) u32 {",
        "pub fn validateVersionStatus(version: Version) ExportStatus {",
        "pub fn validateDevTRangeStatus(start: DevTFields, end: DevTFields) ExportStatus {",
    ),
    BINDING_NOTIFIER: (
        "pub const NotifierResult = enum(u32) {",
        "pub const NotifierBlock = extern struct {",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
    ),
    EXPORT_SHIM: (
        'const abi = @import("abi_bindings");',
        'const dev_t = @import("dev_t_binding");',
        'const version = @import("version_binding");',
        "pub const BoundaryHeader = abi.BoundaryHeader;",
        "pub const ExportStatus = abi.ExportStatus;",
        "pub fn canonicalHeader(flags: u16) BoundaryHeader {",
        "pub fn requestedExtraBytes(header: BoundaryHeader) u32 {",
        "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {",
        "pub fn validateVersion(candidate: Version) ExportStatus {",
        "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
    ),
    PHASE3_CATALOG: (
        'PHASE3_CATALOG_SCOPE = "abi-runtime"',
        'Path("zigux/kernel/export_shim.zig")',
        'Path("zigux/tests/phase3_export_uapi_layout.zig")',
        'Path("zigux/tests/phase3_abi_dump_current.zig")',
        'print("PHASE3_CATALOG_SELF_TEST=pass")',
    ),
    ABI_TEST: (
        'test "phase3 abi keeps export shim compatibility and status helpers reviewable" {',
        'test "phase3 abi keeps version and dev_t relays explicit" {',
        "try layout_assert.assertPublishedAbiLayouts();",
    ),
    TESTS_BUILD: (
        "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);",
        "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);",
        "const phase3_abi_dump = addPhase3AbiDump(b, target, optimize);",
        '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        '.root_source_file = b.path("phase3_abi_dump_current.zig"),',
        '"phase3-export-uapi-layout"',
        '"phase3-dump"',
        "phase3_test_step.dependOn(&phase3_export_uapi_layout.step);",
        "phase3_dump_step.dependOn(&phase3_abi_dump.step);",
    ),
    ABI_DUMP: (
        'const abi = @import("abi_bindings");',
        "pub fn main(init: std.process.Init) !void {",
        "const default_header = abi.defaultHeader(0);",
        "const policy = abi.defaultInteropPolicy();",
        'try stdout.print("  \\\"abi_version\\\": {},\\n", .{abi.ABI_VERSION});',
        'try stdout.print(',
        '"  \\\"notifier\\\": {\\n',
    ),
    EXPORT_UAPI_LAYOUT: (
        'const header_family = @import("header_family_binding");',
        'test "export and uapi dev_t layouts stay aligned" {',
        'test "header-family binding keeps the bounded relay surface explicit" {',
        'test "export shim relays version compatibility without widening the boundary" {',
        'test "export shim reuses the canonical boundary header contract" {',
        'test "export shim relays starter dev_t validation and range checks through the focused replay" {',
    ),
    EXPORT_UAPI_LAYOUT_BUILD: (
        '.root_source_file = b.path("../uapi/dev_t.zig"),',
        '.root_source_file = b.path("../uapi/version.zig"),',
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        '.root_source_file = b.path("../bindings/header_family.zig"),',
        '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        'root_module.addImport("header_family_binding", header_family_binding);',
        '"phase3-export-uapi-layout-test"',
    ),
}

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_and_header_family_binding_surface_present",
    "scope": "shared ABI bindings, directly coupled helper decoding, header-family follow-through, notifier layouts, export-status layout, and header-compatibility replay",
    "next_safe_step": "keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again",
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "include/linux/zigux.h",
    "zigux/uapi/dev_t.zig",
    "zigux/uapi/version.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/header_family.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/unsafe/narrow.zig",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/check-phase3-abi-support-packet.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "scripts/zigux/check-phase3-shared-tests-routes.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "zigux/tests/build.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump_current.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "zigux/tests/phase3_export_uapi_c_header_smoke.c",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_export_shim_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-abi.py --self-test",
    "python3 scripts/zigux/check-phase3-abi.py",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    "python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test",
    "python3 scripts/zigux/check-phase3-shared-tests-routes.py",
    "python3 scripts/zigux/validate-phase3-validator-support-surface.py --self-test",
    "python3 scripts/zigux/validate-phase3-validator-support-surface.py",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "make -C zigux phase3-export-uapi-layout",
    "make -C zigux phase3-export-uapi-layout-test",
    "zig build phase3-abi-core-packet --build-file zigux/tests/build.zig",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "zig build phase3-test --build-file zigux/tests/build.zig",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
)

SAMPLE_MANIFEST = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_and_header_family_binding_surface_present",
    "scope": "shared ABI bindings, directly coupled helper decoding, header-family follow-through, notifier layouts, export-status layout, and header-compatibility replay",
    "packet_files": list(REQUIRED_PACKET_FILES),
    "replay_routes": list(REQUIRED_REPLAY_ROUTES),
    "repo_reality_gaps": [],
    "next_safe_step": "keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _append_duplicate_list_entry_issues(label: str, values: list[object], issues: list[str]) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{label} duplicate entry: {value!r} (first index {first_index}, duplicate index {index})"
        )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / rel_path
        if not path.is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        text = _read(path)
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")

    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        issues.append(f"missing repo file: {MANIFEST_PATH.as_posix()}")
        return issues

    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(f"phase3_abi_manifest.json wrong {field}: {actual!r} != {expected!r}")

    packet_files = manifest.get("packet_files")
    replay_routes = manifest.get("replay_routes")
    repo_reality_gaps = manifest.get("repo_reality_gaps")

    if not isinstance(packet_files, list):
        issues.append("phase3_abi_manifest.json packet_files is not a list")
    else:
        _append_duplicate_list_entry_issues("phase3_abi_manifest.json packet_files", packet_files, issues)
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(f"phase3_abi_manifest.json missing packet_files entry: {entry}")

    if not isinstance(replay_routes, list):
        issues.append("phase3_abi_manifest.json replay_routes is not a list")
    else:
        _append_duplicate_list_entry_issues("phase3_abi_manifest.json replay_routes", replay_routes, issues)
        for entry in REQUIRED_REPLAY_ROUTES:
            if entry not in replay_routes:
                issues.append(f"phase3_abi_manifest.json missing replay route: {entry}")

    if not isinstance(repo_reality_gaps, list):
        issues.append("phase3_abi_manifest.json repo_reality_gaps is not a list")
    elif repo_reality_gaps:
        issues.append(
            "phase3_abi_manifest.json repo_reality_gaps drifted from the current bounded Phase 3 ABI packet"
        )

    return issues


def _populate_repo(root: Path) -> None:
    for rel_path, markers in REQUIRED_MARKERS.items():
        _write(root / rel_path, "\n".join(markers) + "\n")

    for rel_path in REQUIRED_PACKET_FILES:
        path = root / rel_path
        if path.exists():
            continue
        _write(path, "// packet placeholder\n")

    _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_check_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        cases = (
            (
                TESTS_BUILD,
                "phase3_test_step.dependOn(&phase3_export_uapi_layout.step);\n",
                "missing zigux/tests/build.zig marker: phase3_test_step.dependOn(&phase3_export_uapi_layout.step);",
            ),
            (
                TESTS_BUILD,
                "phase3_dump_step.dependOn(&phase3_abi_dump.step);\n",
                "missing zigux/tests/build.zig marker: phase3_dump_step.dependOn(&phase3_abi_dump.step);",
            ),
            (
                EXPORT_UAPI_LAYOUT,
                'test "export shim reuses the canonical boundary header contract" {\n',
                'missing zigux/tests/phase3_export_uapi_layout.zig marker: test "export shim reuses the canonical boundary header contract" {',
            ),
            (
                ABI_DUMP,
                "const default_header = abi.defaultHeader(0);\n",
                "missing zigux/tests/phase3_abi_dump_current.zig marker: const default_header = abi.defaultHeader(0);",
            ),
            (
                EXPORT_SHIM,
                "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {\n",
                "missing zigux/kernel/export_shim.zig marker: pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {",
            ),
            (
                ABI_SLICE_NOTE,
                ".github/workflows/zigux-bootstrap.yml\n",
                "missing Documentation/zigux/phase3-abi-slice.md marker: .github/workflows/zigux-bootstrap.yml",
            ),
        )

        for rel_path, marker, expected in cases:
            path = root / rel_path
            _write(path, _read(path).replace(marker, "", 1))
            issues = validate_repo(root)
            if expected not in issues:
                print("PHASE3_ABI_CHECK_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1
            _populate_repo(root)

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].remove("zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"
        )
        if expected not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected export/UAPI layout replay drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].remove("zig build phase3-dump --build-file zigux/tests/build.zig")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "zig build phase3-dump --build-file zigux/tests/build.zig"
        )
        if expected not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected dump replay drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].remove("zig build phase3-test --build-file zigux/tests/build.zig")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "zig build phase3-test --build-file zigux/tests/build.zig"
        )
        if expected not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected aggregate phase3-test replay drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].remove(
            "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"
        )
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"
        )
        if expected not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected export-shim replay drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].remove("make -C zigux phase3-export-uapi-layout")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "make -C zigux phase3-export-uapi-layout"
        )
        if expected not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected export/UAPI Makefile replay drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].remove("make -C zigux phase3-export-uapi-layout-test")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "make -C zigux phase3-export-uapi-layout-test"
        )
        if expected not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected export/UAPI Makefile test replay drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["packet_files"].remove(".github/workflows/zigux-bootstrap.yml")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json missing packet_files entry: "
            ".github/workflows/zigux-bootstrap.yml"
        )
        if expected not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected workflow packet-file drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["packet_files"].remove("scripts/zigux/check-phase3-selftest-surface.py")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json missing packet_files entry: "
            "scripts/zigux/check-phase3-selftest-surface.py"
        )
        if expected not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected selftest-surface packet-file drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["packet_files"].remove("zigux/tests/phase3_export_shim_build.zig")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json missing packet_files entry: "
            "zigux/tests/phase3_export_shim_build.zig"
        )
        if expected not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected export-shim build packet-file drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["packet_files"].append(REQUIRED_PACKET_FILES[0])
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        if not any(issue.startswith("phase3_abi_manifest.json packet_files duplicate entry:") for issue in issues):
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected duplicate packet-file issue was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["repo_reality_gaps"] = ["stale-gap"]
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = "phase3_abi_manifest.json repo_reality_gaps drifted from the current bounded Phase 3 ABI packet"
        if expected not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected repo-reality-gap drift was not reported")
            return 1

    print("PHASE3_ABI_CHECK_SELF_TEST=pass")
    print("PHASE3_ABI_CHECK_SELF_TEST_CASE_COUNT=17")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 3 ABI, export/UAPI, and dump packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the bounded Phase 3 ABI packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_CHECK=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_ABI_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
