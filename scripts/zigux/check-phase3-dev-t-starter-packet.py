#!/usr/bin/env python3
"""Fail-close the current Phase 3 dev_t starter packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ABI_SLICE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
LINUX_HEADER_PATH = Path("include/linux/zigux.h")
DEV_T_HEADER_PATH = Path("include/zigux/dev_t.h")
UAPI_DEV_T_PATH = Path("zigux/uapi/dev_t.zig")
UAPI_VERSION_PATH = Path("zigux/uapi/version.zig")
BINDING_PATH = Path("zigux/bindings/dev_t.zig")
TEST_PATH = Path("zigux/tests/phase3_dev_t_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_dev_t_starter_packet_build.zig")

REQUIRED_MARKERS = {
    ABI_SLICE_PATH: (
        "include/linux/zigux.h",
        "include/zigux/dev_t.h",
        "zigux/uapi/dev_t.zig",
        "zigux/uapi/version.zig",
        "zigux/bindings/dev_t.zig",
        "zigux/tests/phase3_dev_t_starter_packet.zig",
        "zigux/tests/phase3_dev_t_starter_packet_build.zig",
        "scripts/zigux/check-phase3-dev-t-starter-packet.py",
        "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test",
        "`zigux/tests/README.md` still carries a broader Phase 3 packet summary",
        "scripts/zigux/validate-phase3-export-uapi-survey.py",
        "zigux/kernel/export_shim.zig",
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
        "struct zigux_dev_t_fields {",
        "static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(",
    ),
    UAPI_DEV_T_PATH: (
        "pub const abi_version: u32 = 1;",
        "pub const Fields = extern struct {",
        "pub fn init(major: u32, minor: u32) Fields {",
        "std.debug.assert(@sizeOf(Fields) == 8);",
        "std.debug.assert(@alignOf(Fields) == 4);",
    ),
    UAPI_VERSION_PATH: (
        "pub const abi_major: u32 = 0;",
        "pub const abi_minor: u32 = 1;",
        "pub const header_family_revision: u32 = 1;",
        "pub const Version = extern struct {",
        "pub fn current() Version {",
        "std.debug.assert(@sizeOf(Version) == 12);",
        "std.debug.assert(@alignOf(Version) == 4);",
    ),
    BINDING_PATH: (
        "pub const abi_version = uapi.abi_version;",
        "pub const fields_size: usize = @sizeOf(uapi.Fields);",
        "pub const fields_align: usize = @alignOf(uapi.Fields);",
        'pub const major_offset: usize = @offsetOf(uapi.Fields, "major");',
        'pub const minor_offset: usize = @offsetOf(uapi.Fields, "minor");',
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn eql(left: Fields, right: Fields) bool {",
        "std.debug.assert(major_offset == 0);",
        "std.debug.assert(minor_offset == 4);",
    ),
    TEST_PATH: (
        'test "dev_t starter binding preserves the current ABI layout" {',
        'test "starter packet version stays aligned with the Linux-facing header family" {',
        'test "dev_t binding equality stays field based" {',
        "try testing.expectEqual(@as(u32, 1), dev_t.abi_version);",
        "try testing.expectEqual(@as(u32, 1), version.header_family_revision);",
        "try testing.expect(dev_t.eql(left, same));",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../uapi/dev_t.zig"),',
        '.root_source_file = b.path("../uapi/version.zig"),',
        '.root_source_file = b.path("../bindings/dev_t.zig"),',
        '.root_source_file = b.path("phase3_dev_t_starter_packet.zig"),',
        'dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);',
        'root_module.addImport("dev_t_binding", dev_t_binding);',
        '"phase3-dev-t-starter-packet-test"',
        '"Run the Phase 3 dev_t starter-packet ABI self-check"',
    ),
}

SAMPLE_FILES = {path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()}

SELF_TEST_CASES = (
    (
        ABI_SLICE_PATH,
        "`zigux/tests/README.md` still carries a broader Phase 3 packet summary",
    ),
    (LINUX_HEADER_PATH, "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u"),
    (DEV_T_HEADER_PATH, "#define ZIGUX_DEV_T_FIELDS_ALIGN 4u"),
    (UAPI_DEV_T_PATH, "std.debug.assert(@sizeOf(Fields) == 8);"),
    (UAPI_VERSION_PATH, "pub const header_family_revision: u32 = 1;"),
    (BINDING_PATH, 'pub const major_offset: usize = @offsetOf(uapi.Fields, "major");'),
    (TEST_PATH, 'test "starter packet version stays aligned with the Linux-facing header family" {'),
    (BUILD_PATH, '"phase3-dev-t-starter-packet-test"'),
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
