#!/usr/bin/env python3
"""Fail-close the current Phase 3 dev_t starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ABI_SLICE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
LINUX_HEADER_PATH = Path("include/linux/zigux.h")
DEV_T_HEADER_PATH = Path("include/zigux/dev_t.h")
UAPI_DEV_T_PATH = Path("zigux/uapi/dev_t.zig")
UAPI_VERSION_PATH = Path("zigux/uapi/version.zig")
ABI_BINDING_PATH = Path("zigux/bindings/abi.zig")
BINDING_PATH = Path("zigux/bindings/dev_t.zig")
VERSION_BINDING_PATH = Path("zigux/bindings/version.zig")
EXPORT_SHIM_PATH = Path("zigux/kernel/export_shim.zig")
TEST_PATH = Path("zigux/tests/phase3_dev_t_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_dev_t_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_dev_t_starter_packet_manifest.json")

COMPILE_ROUTE = (
    "zig build phase3-dev-t-starter-packet-test --build-file "
    "zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all"
)

REQUIRED_MARKERS = {
    ABI_SLICE_PATH: (
        "zigux/bindings/abi.zig",
        "zigux/bindings/version.zig",
        "zigux/kernel/export_shim.zig",
    ),
    VALIDATOR_NOTE_PATH: (
        "zigux/bindings/abi.zig",
        "zigux/bindings/version.zig",
        "zigux/kernel/export_shim.zig",
        "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
        "scripts/zigux/check-phase3-dev-t-starter-packet.py",
        "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py",
        COMPILE_ROUTE,
        "the broader export/UAPI survey, catalog, or shared Phase 3 replay packet",
    ),
    LINUX_HEADER_PATH: (
        "#define ZIGUX_UAPI_ABI_MAJOR 0u",
        "#define ZIGUX_UAPI_ABI_MINOR 1u",
        "#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u",
        "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u",
        "struct zigux_uapi_version {",
        "static inline struct zigux_uapi_version zigux_uapi_version_current(void) {",
    ),
    DEV_T_HEADER_PATH: (
        "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
        "#define ZIGUX_DEV_T_FIELDS_SIZE 8u",
        "#define ZIGUX_DEV_T_FIELDS_ALIGN 4u",
        "#define ZIGUX_DEV_T_MAJOR_OFFSET 0u",
        "#define ZIGUX_DEV_T_MINOR_OFFSET 4u",
        "struct zigux_dev_t_fields {",
        "static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(",
    ),
    UAPI_DEV_T_PATH: (
        "pub const abi_version: u32 = 1;",
        "pub const Fields = extern struct {",
        "pub const fields_size: usize = @sizeOf(Fields);",
        "pub const fields_align: usize = @alignOf(Fields);",
        'pub const major_offset: usize = @offsetOf(Fields, "major");',
        'pub const minor_offset: usize = @offsetOf(Fields, "minor");',
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn validate(fields: Fields) bool {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
        "std.debug.assert(fields_size == 8);",
        "std.debug.assert(fields_align == 4);",
        "std.debug.assert(major_offset == 0);",
        "std.debug.assert(minor_offset == 4);",
        "std.debug.assert(major_bits + minor_bits == 32);",
    ),
    UAPI_VERSION_PATH: (
        "pub const abi_major: u32 = 0;",
        "pub const abi_minor: u32 = 1;",
        "pub const header_family_revision: u32 = 1;",
        "pub const Version = extern struct {",
        "pub fn current() Version {",
        "std.debug.assert(version_size == 12);",
        "std.debug.assert(version_align == 4);",
    ),
    ABI_BINDING_PATH: (
        "pub const ABI_VERSION: u16 = 1;",
        "pub const STATUS_FLAG_ERROR: u16 = 1;",
        "pub const BoundaryHeader = extern struct {",
        "pub const ExportStatus = extern struct {",
        "pub const Facility = enum(u16) {",
        "pub fn defaultHeader(flags: u16) BoundaryHeader {",
    ),
    BINDING_PATH: (
        "pub const abi_version = uapi.abi_version;",
        "pub const fields_size = uapi.fields_size;",
        "pub const fields_align = uapi.fields_align;",
        "pub const major_offset = uapi.major_offset;",
        "pub const minor_offset = uapi.minor_offset;",
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn eql(left: Fields, right: Fields) bool {",
        "pub fn validate(fields: Fields) bool {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
        "std.debug.assert(major_offset == 0);",
        "std.debug.assert(minor_offset == 4);",
    ),
    VERSION_BINDING_PATH: (
        "pub const abi_major = uapi.abi_major;",
        "pub const abi_minor = uapi.abi_minor;",
        "pub const header_family_revision = uapi.header_family_revision;",
        "pub const version_size: usize = uapi.version_size;",
        "pub const version_align: usize = uapi.version_align;",
        "pub const abi_major_offset: usize = uapi.abi_major_offset;",
        "pub const abi_minor_offset: usize = uapi.abi_minor_offset;",
        "pub const header_family_revision_offset: usize = uapi.header_family_revision_offset;",
        "pub fn current() Version {",
        "pub fn eql(left: Version, right: Version) bool {",
        "std.debug.assert(header_family_revision_offset == 8);",
    ),
    EXPORT_SHIM_PATH: (
        'const abi = @import("abi_bindings");',
        'const dev_t = @import("dev_t_binding");',
        'const version = @import("version_binding");',
        "pub const BoundaryHeader = abi.BoundaryHeader;",
        "pub const ExportStatus = abi.ExportStatus;",
        "pub const Facility = abi.Facility;",
        "pub fn canonicalHeader(flags: u16) BoundaryHeader {",
        "pub fn currentVersion() Version {",
        "pub fn makeDevTFields(major: u32, minor: u32) DevTFields {",
        "pub fn okStatus(facility: Facility) ExportStatus {",
        "pub fn errorStatus(code: i32, facility: Facility) ExportStatus {",
        "pub fn validateDeviceFields(fields: DevTFields) ExportStatus {",
        "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
        "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
    ),
    TEST_PATH: (
        'const uapi_dev_t = @import("uapi_dev_t");',
        'const export_shim = @import("export_shim");',
        'test "dev_t starter binding preserves the current ABI layout" {',
        'test "dev_t starter binding stays aligned with the UAPI field offsets" {',
        'test "starter packet version binding preserves the Linux-facing header family layout" {',
        'test "dev_t binding equality stays field based" {',
        'test "starter dev_t validation keeps the boundary range explicit" {',
        'test "version binding equality stays field based" {',
        'test "starter export shim reuses the canonical boundary header and version snapshot" {',
        'test "starter export shim keeps facility-tagged status helpers explicit" {',
        'test "starter export shim forwards dev_t fields without changing starter layout semantics" {',
        'test "starter export shim relays dev_t validation status" {',
        "try testing.expectEqual(@as(u32, 1), dev_t.abi_version);",
        "try testing.expectEqual(uapi_dev_t.major_offset, dev_t.major_offset);",
        "try testing.expect(dev_t.eql(left, same));",
        "try testing.expect(dev_t.validate(valid));",
        "try testing.expect(version.eql(current, same));",
        "const header = export_shim.canonicalHeader(0x41);",
        "const ok = export_shim.okStatus(.helpers);",
        "const fields = export_shim.makeDevTFields(11, 29);",
        "const valid = export_shim.validateDeviceNumber(dev_t.max_major, dev_t.max_minor);",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../uapi/dev_t.zig"),',
        '.root_source_file = b.path("../uapi/version.zig"),',
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../bindings/dev_t.zig"),',
        '.root_source_file = b.path("../bindings/version.zig"),',
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        '.root_source_file = b.path("phase3_dev_t_starter_packet.zig"),',
        'dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);',
        'version_binding.addImport("uapi_version", uapi_version);',
        'export_shim.addImport("abi_bindings", abi_bindings);',
        'export_shim.addImport("dev_t_binding", dev_t_binding);',
        'export_shim.addImport("version_binding", version_binding);',
        'root_module.addImport("uapi_dev_t", uapi_dev_t);',
        'root_module.addImport("dev_t_binding", dev_t_binding);',
        'root_module.addImport("version_binding", version_binding);',
        'root_module.addImport("export_shim", export_shim);',
        '"phase3-dev-t-starter-packet-test"',
        '"Run the Phase 3 dev_t starter-packet ABI self-check"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-dev-t-starter-packet"',
        '"status": "starter_packet_present"',
        '"scope": "starter Linux-facing header family plus dev_t, version, and export shim replay"',
        '"Documentation/zigux/phase3-abi-slice.md"',
        '"Documentation/zigux/phase3-validator-support-surface.md"',
        '"zigux/bindings/abi.zig"',
        '"zigux/bindings/version.zig"',
        '"zigux/kernel/export_shim.zig"',
        '"zigux/tests/phase3_dev_t_starter_packet_manifest.json"',
        '"python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase3-dev-t-starter-packet.py"',
        f'"{COMPILE_ROUTE}"',
        '"next_safe_step": "keep the live starter packet honest with bounded manifest-backed checker and compile replay work before widening the broader Phase 3 ABI substrate"',
    ),
}

SAMPLE_FILES = {
    ABI_SLICE_PATH: """# Phase 3 ABI Slice

zigux/bindings/abi.zig
zigux/bindings/version.zig
zigux/kernel/export_shim.zig
""",
    VALIDATOR_NOTE_PATH: f"""# Phase 3 Validator Support Surface

zigux/bindings/abi.zig
zigux/bindings/version.zig
zigux/kernel/export_shim.zig
zigux/tests/phase3_dev_t_starter_packet_manifest.json
scripts/zigux/check-phase3-dev-t-starter-packet.py
python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test
python3 scripts/zigux/check-phase3-dev-t-starter-packet.py
{COMPILE_ROUTE}
the broader export/UAPI survey, catalog, or shared Phase 3 replay packet
""",
    LINUX_HEADER_PATH: "\n".join(REQUIRED_MARKERS[LINUX_HEADER_PATH]) + "\n",
    DEV_T_HEADER_PATH: "\n".join(REQUIRED_MARKERS[DEV_T_HEADER_PATH]) + "\n",
    UAPI_DEV_T_PATH: "\n".join(REQUIRED_MARKERS[UAPI_DEV_T_PATH]) + "\n",
    UAPI_VERSION_PATH: "\n".join(REQUIRED_MARKERS[UAPI_VERSION_PATH]) + "\n",
    ABI_BINDING_PATH: "\n".join(REQUIRED_MARKERS[ABI_BINDING_PATH]) + "\n",
    BINDING_PATH: "\n".join(REQUIRED_MARKERS[BINDING_PATH]) + "\n",
    VERSION_BINDING_PATH: "\n".join(REQUIRED_MARKERS[VERSION_BINDING_PATH]) + "\n",
    EXPORT_SHIM_PATH: "\n".join(REQUIRED_MARKERS[EXPORT_SHIM_PATH]) + "\n",
    TEST_PATH: "\n".join(REQUIRED_MARKERS[TEST_PATH]) + "\n",
    BUILD_PATH: "\n".join(REQUIRED_MARKERS[BUILD_PATH]) + "\n",
    MANIFEST_PATH: f"""{{
  \"slug\": \"phase3-dev-t-starter-packet\",
  \"status\": \"starter_packet_present\",
  \"scope\": \"starter Linux-facing header family plus dev_t, version, and export shim replay\",
  \"packet_files\": [
    \"Documentation/zigux/phase3-abi-slice.md\",
    \"Documentation/zigux/phase3-validator-support-surface.md\",
    \"include/linux/zigux.h\",
    \"include/zigux/dev_t.h\",
    \"zigux/uapi/version.zig\",
    \"zigux/uapi/dev_t.zig\",
    \"zigux/bindings/abi.zig\",
    \"zigux/bindings/dev_t.zig\",
    \"zigux/bindings/version.zig\",
    \"zigux/kernel/export_shim.zig\",
    \"zigux/tests/phase3_dev_t_starter_packet.zig\",
    \"zigux/tests/phase3_dev_t_starter_packet_build.zig\",
    \"zigux/tests/phase3_dev_t_starter_packet_manifest.json\",
    \"scripts/zigux/check-phase3-dev-t-starter-packet.py\"
  ],
  \"replay_routes\": [
    \"python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test\",
    \"python3 scripts/zigux/check-phase3-dev-t-starter-packet.py\",
    \"{COMPILE_ROUTE}\"
  ],
  \"repo_reality_gaps\": [
    \"scripts/zigux/validate-phase3-export-uapi-survey.py\",
    \"zigux/tests/phase3_export_uapi_layout.zig\"
  ],
  \"next_safe_step\": \"keep the live starter packet honest with bounded manifest-backed checker and compile replay work before widening the broader Phase 3 ABI substrate\"
}}
""",
}

SELF_TEST_CASES = (
    (ABI_SLICE_PATH, "zigux/kernel/export_shim.zig"),
    (VALIDATOR_NOTE_PATH, "zigux/kernel/export_shim.zig"),
    (LINUX_HEADER_PATH, "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u"),
    (DEV_T_HEADER_PATH, "#define ZIGUX_DEV_T_MAJOR_OFFSET 0u"),
    (UAPI_DEV_T_PATH, 'pub const major_offset: usize = @offsetOf(Fields, \"major\");'),
    (UAPI_DEV_T_PATH, "pub fn validateRange(start: Fields, end: Fields) bool {"),
    (UAPI_VERSION_PATH, "pub const header_family_revision: u32 = 1;"),
    (ABI_BINDING_PATH, "pub fn defaultHeader(flags: u16) BoundaryHeader {"),
    (BINDING_PATH, "pub const major_offset = uapi.major_offset;"),
    (BINDING_PATH, "pub fn validateRange(start: Fields, end: Fields) bool {"),
    (VERSION_BINDING_PATH, "pub const version_size: usize = uapi.version_size;"),
    (EXPORT_SHIM_PATH, "pub fn errorStatus(code: i32, facility: Facility) ExportStatus {"),
    (EXPORT_SHIM_PATH, "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {"),
    (TEST_PATH, 'test \"starter export shim reuses the canonical boundary header and version snapshot\" {'),
    (TEST_PATH, "const valid = export_shim.validateDeviceNumber(dev_t.max_major, dev_t.max_minor);"),
    (BUILD_PATH, 'root_module.addImport(\"export_shim\", export_shim);'),
    (MANIFEST_PATH, '\"zigux/kernel/export_shim.zig\"'),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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

    manifest_path = repo_root / MANIFEST_PATH
    if manifest_path.exists():
        try:
            manifest = json.loads(_read(manifest_path))
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            if not isinstance(packet_files, list):
                issues.append("phase3_dev_t_starter_packet_manifest.json packet_files is not a list")
            if not isinstance(replay_routes, list):
                issues.append("phase3_dev_t_starter_packet_manifest.json replay_routes is not a list")
            if isinstance(packet_files, list):
                for required_path in (
                    "Documentation/zigux/phase3-abi-slice.md",
                    "Documentation/zigux/phase3-validator-support-surface.md",
                    "include/linux/zigux.h",
                    "include/zigux/dev_t.h",
                    "zigux/uapi/version.zig",
                    "zigux/uapi/dev_t.zig",
                    "zigux/bindings/abi.zig",
                    "zigux/bindings/dev_t.zig",
                    "zigux/bindings/version.zig",
                    "zigux/kernel/export_shim.zig",
                    "zigux/tests/phase3_dev_t_starter_packet.zig",
                    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
                    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
                    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
                ):
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_dev_t_starter_packet_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                for route in (
                    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test",
                    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py",
                    COMPILE_ROUTE,
                ):
                    if route not in replay_routes:
                        issues.append(
                            "phase3_dev_t_starter_packet_manifest.json missing replay route: "
                            f"{route}"
                        )
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, text in SAMPLE_FILES.items():
        _write(root / relative_path, text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_dev_t_starter_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_DEV_T_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 dev_t starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 dev_t starter packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_DEV_T_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())