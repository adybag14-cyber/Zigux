#!/usr/bin/env python3
"""Fail-close the current bounded Phase 3 shared ABI packet."""

from __future__ import annotations

import argparse
import re
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
BINDING_NOTIFIER = Path("zigux/bindings/notifier_abi.zig")
EXPORT_SHIM = Path("zigux/kernel/export_shim.zig")

REQUIRED_MARKERS = {
    ABI_SLICE_NOTE: (
        "PHASE3_CURRENT_INTEROP_GAP=",
        "PHASE3_CURRENT_INTEROP_GAP_DETAIL=",
        "include/linux/zigux.h",
        "include/zigux/dev_t.h",
        "include/zigux/abi.h",
        "zigux/uapi/dev_t.zig",
        "zigux/uapi/version.zig",
        "zigux/bindings/dev_t.zig",
        "zigux/bindings/version.zig",
        "zigux/bindings/abi.zig",
        "zigux/bindings/notifier_abi.zig",
        "zigux/kernel/export_shim.zig",
        "scripts/zigux/check-phase3-abi.py",
        "scripts/zigux/validate-phase3.py",
    ),
    ABI_HEADER: (
        "#define ZIGUX_ABI_VERSION 1U",
        "#define ZIGUX_FACILITY_KERNEL 1U",
        "#define ZIGUX_FACILITY_HELPERS 2U",
        "#define ZIGUX_FACILITY_DRIVERS 3U",
        "#define ZIGUX_STATUS_FLAG_ERROR 1U",
        "#define ZIGUX_PANIC_ABORT 0U",
        "#define ZIGUX_ALLOC_KERNEL_HEAP 1U",
        "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
        "typedef struct zigux_boundary_header {",
        "struct zigux_export_status {",
        "struct zigux_interop_policy {",
        "struct zigux_notifier_block {",
        "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
        "static inline int zigux_export_status_ok(struct zigux_export_status status)",
    ),
    LINUX_ZIGUX_HEADER: (
        "#define ZIGUX_UAPI_ABI_MAJOR 0u",
        "#define ZIGUX_UAPI_ABI_MINOR 1u",
        "#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u",
        "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u",
        "struct zigux_uapi_version {",
        "static inline struct zigux_uapi_version zigux_uapi_version_current(void)",
        "static inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)",
        "static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
        "static inline int zigux_uapi_dev_t_fields_range_is_valid(",
    ),
    DEV_T_HEADER: (
        "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
        "#define ZIGUX_DEV_T_FIELDS_SIZE 8u",
        "#define ZIGUX_DEV_T_FIELDS_ALIGN 4u",
        "#define ZIGUX_DEV_T_MAJOR_OFFSET 0u",
        "#define ZIGUX_DEV_T_MINOR_OFFSET 4u",
        "#define ZIGUX_DEV_MINOR_BITS 20u",
        "struct zigux_dev_t_fields {",
        "static inline uint32_t zigux_mkdev(uint32_t major, uint32_t minor)",
        "static inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
    ),
    UAPI_DEV_T: (
        "pub const abi_version: u32 = 1;",
        "pub const major_bits: u6 = 12;",
        "pub const minor_bits: u6 = 20;",
        "pub const Fields = extern struct {",
        "pub const fields_size: usize = @sizeOf(Fields);",
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn validate(fields: Fields) bool {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    UAPI_VERSION: (
        "pub const abi_major: u32 = 0;",
        "pub const abi_minor: u32 = 1;",
        "pub const header_family_revision: u32 = 1;",
        "pub const Version = extern struct {",
        "pub fn current() Version {",
        "pub fn matchesCurrent(version: Version) bool {",
    ),
    BINDING_DEV_T: (
        "pub const abi_version = uapi.abi_version;",
        "pub const Fields = uapi.Fields;",
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn validate(fields: Fields) bool {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    BINDING_VERSION: (
        "pub const abi_major = uapi.abi_major;",
        "pub const abi_minor = uapi.abi_minor;",
        "pub const header_family_revision = uapi.header_family_revision;",
        "pub const Version = uapi.Version;",
        "pub fn current() Version {",
        "pub fn matchesCurrent(version: Version) bool {",
    ),
    BINDING_NOTIFIER: (
        "pub const NotifierResult = enum(u32) {",
        "done = 0,",
        "ok = 1,",
        "stop = 2,",
        "pub const NotifierBlock = extern struct {",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
    ),
    BINDING_ABI: (
        'const notifier_abi = @import("notifier_abi.zig");',
        "pub const ABI_VERSION: u16 = 1;",
        "pub const FACILITY_KERNEL: u16 = 1;",
        "pub const FACILITY_HELPERS: u16 = 2;",
        "pub const FACILITY_DRIVERS: u16 = 3;",
        "pub const STATUS_FLAG_ERROR: u16 = 1;",
        "pub const PANIC_ABORT: u8 = 0;",
        "pub const PANIC_BUG: u8 = 1;",
        "pub const PANIC_WARN: u8 = 2;",
        "pub const ALLOC_CALLER_PROVIDED: u8 = 0;",
        "pub const ALLOC_KERNEL_HEAP: u8 = 1;",
        "pub const ALLOC_ARENA: u8 = 2;",
        "pub const UNSAFE_NONE: u8 = 0;",
        "pub const UNSAFE_VOLATILE_MMIO: u8 = 1;",
        "pub const UNSAFE_RAW_POINTER_BRIDGE: u8 = 2;",
        "pub const NOTIFIER_DONE: u32 = 0;",
        "pub const NOTIFIER_OK: u32 = 1;",
        "pub const NOTIFIER_STOP: u32 = 2;",
        "pub const PanicMode = enum(u8) {",
        "pub const AllocatorMode = enum(u8) {",
        "pub const UnsafeScope = enum(u8) {",
        "pub const BoundaryHeader = extern struct {",
        "pub const ExportStatus = extern struct {",
        "pub const InteropPolicy = extern struct {",
        "pub const NotifierResult = notifier_abi.NotifierResult;",
        "pub const NotifierBlock = notifier_abi.NotifierBlock;",
        "pub fn defaultHeader(flags: u16) BoundaryHeader {",
        "pub fn defaultInteropPolicy() InteropPolicy {",
        "pub fn headerIsCanonical(header: BoundaryHeader) bool {",
    ),
    EXPORT_SHIM: (
        'const abi = @import("abi_bindings");',
        'const dev_t = @import("dev_t_binding");',
        'const version = @import("version_binding");',
        "pub const BoundaryHeader = abi.BoundaryHeader;",
        "pub const ExportStatus = abi.ExportStatus;",
        "pub const Facility = abi.Facility;",
        "pub fn canonicalHeader(flags: u16) BoundaryHeader {",
        "pub fn okStatus(facility: Facility) ExportStatus {",
        "pub fn errorStatus(code: i32, facility: Facility) ExportStatus {",
        "pub fn statusIsOk(status: ExportStatus) bool {",
        "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
    ),
}

SELF_TEST_CASES = (
    (
        ABI_SLICE_NOTE,
        "scripts/zigux/check-phase3-abi.py",
    ),
    (
        BINDING_ABI,
        "pub const NotifierResult = notifier_abi.NotifierResult;",
    ),
    (
        BINDING_ABI,
        "pub const ABI_VERSION: u16 = 1;",
    ),
    (
        EXPORT_SHIM,
        "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
    ),
)

HEADER_DEFINE_RE = re.compile(r"^\s*#define\s+ZIGUX_([A-Z0-9_]+)\b", re.MULTILINE)
BINDING_CONST_RE = re.compile(r"^\s*pub const\s+([A-Z0-9_]+)\s*:", re.MULTILINE)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _header_names(text: str) -> set[str]:
    return set(HEADER_DEFINE_RE.findall(text))


def _binding_names(text: str) -> set[str]:
    return set(BINDING_CONST_RE.findall(text))


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    texts: dict[Path, str] = {}

    for rel_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / rel_path
        if not path.is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        text = _read(path)
        texts[rel_path] = text
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")

    header_text = texts.get(ABI_HEADER)
    binding_text = texts.get(BINDING_ABI)
    if header_text is not None and binding_text is not None:
        missing_binding_constants = sorted(_header_names(header_text) - _binding_names(binding_text))
        for name in missing_binding_constants:
            issues.append(
                "missing ABI binding constant for header define: "
                f"ZIGUX_{name} -> {name}"
            )

    notifier_text = texts.get(BINDING_NOTIFIER)
    if binding_text is not None and notifier_text is not None:
        for marker in (
            "pub const NotifierResult = notifier_abi.NotifierResult;",
            "pub const NotifierBlock = notifier_abi.NotifierBlock;",
        ):
            if marker not in binding_text:
                issues.append(f"missing {BINDING_ABI.as_posix()} marker: {marker}")
        for marker in ("done = 0,", "ok = 1,", "stop = 2,"):
            if marker not in notifier_text:
                issues.append(f"missing {BINDING_NOTIFIER.as_posix()} marker: {marker}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_check_") as temp_dir:
        root = Path(temp_dir)

        for rel_path, markers in REQUIRED_MARKERS.items():
            _write(root / rel_path, "\n".join(markers) + "\n")

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for rel_path, marker in SELF_TEST_CASES:
            for populate_path, markers in REQUIRED_MARKERS.items():
                _write(root / populate_path, "\n".join(markers) + "\n")
            _write(root / rel_path, _read(root / rel_path).replace(marker, "", 1))
            issues = validate_repo(root)
            expected = f"missing {rel_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_ABI_CHECK_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_ABI_CHECK_SELF_TEST=pass")
    print(f"PHASE3_ABI_CHECK_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 3 shared ABI packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 shared ABI packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_CHECK=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_ABI_CHECK=pass")
    print("PHASE3_ABI_SCOPE=shared-abi-packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
