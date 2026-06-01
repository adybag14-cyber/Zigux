#!/usr/bin/env python3
"""Fail-close the current Phase 3 ABI header-family survey packet."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path


SURVEY_PATH = Path("Documentation/zigux/phase3-abi-header-family-survey.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase3-abi-header-family-survey.py")
ABI_SLICE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
LINUX_HEADER_PATH = Path("include/linux/zigux.h")
ABI_HEADER_PATH = Path("include/zigux/abi.h")
DEV_T_HEADER_PATH = Path("include/zigux/dev_t.h")
UAPI_VERSION_PATH = Path("zigux/uapi/version.zig")
UAPI_DEV_T_PATH = Path("zigux/uapi/dev_t.zig")
VERSION_BINDING_PATH = Path("zigux/bindings/version.zig")
DEV_T_BINDING_PATH = Path("zigux/bindings/dev_t.zig")
HEADER_FAMILY_BINDING_PATH = Path("zigux/bindings/header_family.zig")
LAYOUT_TEST_PATH = Path("zigux/tests/phase3_export_uapi_layout.zig")
LAYOUT_BUILD_PATH = Path("zigux/tests/phase3_export_uapi_layout_build.zig")

REQUIRED_MARKERS = {
    SURVEY_PATH: (
        "PHASE3_ABI_HEADER_FAMILY_VALIDATOR_PATH=scripts/zigux/validate-phase3-abi-header-family-survey.py",
        "PHASE3_ABI_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md",
        "PHASE3_ABI_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json",
        "PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h",
        "PHASE3_ABI_HEADER_PATH=include/zigux/abi.h",
        "PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h",
        "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
        "PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig",
        "PHASE3_VERSION_BINDING_PATH=zigux/bindings/version.zig",
        "PHASE3_DEV_T_BINDING_PATH=zigux/bindings/dev_t.zig",
        "PHASE3_HEADER_FAMILY_BINDING_PATH=zigux/bindings/header_family.zig",
        "PHASE3_EXPORT_UAPI_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
        "- `include/linux/zigux.h` keeps the Linux-facing header-family relay bounded to `zigux_uapi_version_current()`, the `zigux_uapi_version_has_current_*()` helpers, `zigux_uapi_version_matches_current()`, and `zigux_uapi_validate_version()` rather than introducing a second semantic owner.",
        "- `include/zigux/abi.h` remains the canonical owner for `zigux_boundary_header`, `zigux_export_status`, `zigux_default_header()`, `zigux_compatible_header()`, `zigux_abi_version_is_current()`, `zigux_header_is_canonical()`, `zigux_header_is_compatible()`, `zigux_header_extends_boundary()`, `zigux_header_requested_extra_bytes()`, and `zigux_header_canonicalize()`.",
        "- `include/zigux/dev_t.h` remains the canonical owner for the starter `dev_t` limits, `zigux_dev_t_fields_make()`, `zigux_mkdev()`, `zigux_major()`, `zigux_minor()`, `zigux_dev_t_fields_is_valid()`, and `zigux_dev_t_fields_range_is_valid()`.",
        "- `zigux/uapi/version.zig` and `zigux/bindings/version.zig` keep the current version packet aligned through `current()`, `matchesCurrent()`, the `hasCurrent*` helper family, and the shared size, alignment, and field-offset constants.",
        "- `zigux/uapi/dev_t.zig` and `zigux/bindings/dev_t.zig` keep the starter `dev_t` packet aligned through `init()`, `makeDeviceNumber()`, `majorFromDeviceNumber()`, `minorFromDeviceNumber()`, `fieldsFromDeviceNumber()`, `validate()`, and `validateRange()`.",
        "- `zigux/bindings/header_family.zig` now keeps the shared header-family binding relay explicit through `currentVersion()`, `versionMatchesCurrent()`, `currentBoundaryHeader()`, `compatibleBoundaryHeader()`, `boundaryHeaderHasCurrentAbiVersion()`, `boundaryHeaderIsCanonicalSize()`, `boundaryHeaderIsCompatibleSize()`, `boundaryHeaderRequestedExtraBytes()`, `canonicalizeBoundaryHeader()`, `validateBoundaryHeaderStatus()`, `initDevTFields()`, `makeDeviceNumber()`, `majorFromDeviceNumber()`, `minorFromDeviceNumber()`, `fieldsFromDeviceNumber()`, `validateVersionStatus()`, `validateDevTFieldsStatus()`, `validateDevTComponentsStatus()`, and `validateDevTRangeStatus()` without creating a third semantic owner beside the canonical headers and starter bindings.",
        "Current `master` no longer has a packet-local repo-reality gap for the bounded header-family survey follow-through itself.",
    ),
    VALIDATOR_PATH: (
        '"""Fail-close the current Phase 3 ABI header-family survey packet."""',
        'SURVEY_PATH = Path("Documentation/zigux/phase3-abi-header-family-survey.md")',
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
        '"zigux/bindings/header_family.zig"',
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
    HEADER_FAMILY_BINDING_PATH: (
        "pub const abi_major: u32 = uapi_version.abi_major;",
        "pub const abi_minor: u32 = uapi_version.abi_minor;",
        "pub const header_family_revision: u32 = uapi_version.header_family_revision;",
        "pub const abi_version: u16 = abi.ABI_VERSION;",
        "pub const uapi_dev_t_packet_present: u32 = 1;",
        "pub fn currentVersion() Version {",
        "pub fn versionMatchesCurrent(version: Version) bool {",
        "pub fn currentBoundaryHeader(flags: u16) BoundaryHeader {",
        "pub fn boundaryHeaderRequestedExtraBytes(header: BoundaryHeader) u32 {",
        "pub fn initDevTFields(major: u32, minor: u32) DevTFields {",
        "pub fn fieldsFromDeviceNumber(device_number: u32) DevTFields {",
        "pub fn validateVersionStatus(version: Version) ExportStatus {",
        "pub fn validateDevTFieldsStatus(fields: DevTFields) ExportStatus {",
        "pub fn validateDevTRangeStatus(start: DevTFields, end: DevTFields) ExportStatus {",
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

LINUX_VERSION_DEFINE_TO_ZIG_CONST = {
    "ZIGUX_UAPI_ABI_MAJOR": "abi_major",
    "ZIGUX_UAPI_ABI_MINOR": "abi_minor",
    "ZIGUX_UAPI_HEADER_FAMILY_REVISION": "header_family_revision",
}

DEV_T_DEFINE_TO_ZIG_CONST = {
    "ZIGUX_DEV_T_FIELDS_ABI_VERSION": "abi_version",
    "ZIGUX_DEV_MINOR_BITS": "minor_bits",
}

REQUIRED_VERSION_BINDING_ALIASES = {
    "abi_major": "uapi.abi_major",
    "abi_minor": "uapi.abi_minor",
    "header_family_revision": "uapi.header_family_revision",
    "version_size": "uapi.version_size",
    "version_align": "uapi.version_align",
    "abi_major_offset": "uapi.abi_major_offset",
    "abi_minor_offset": "uapi.abi_minor_offset",
    "header_family_revision_offset": "uapi.header_family_revision_offset",
}

REQUIRED_DEV_T_BINDING_ALIASES = {
    "abi_version": "uapi.abi_version",
    "major_bits": "uapi.major_bits",
    "minor_bits": "uapi.minor_bits",
    "max_major": "uapi.max_major",
    "max_minor": "uapi.max_minor",
    "fields_size": "uapi.fields_size",
    "fields_align": "uapi.fields_align",
    "major_offset": "uapi.major_offset",
    "minor_offset": "uapi.minor_offset",
}

REQUIRED_HEADER_FAMILY_BINDING_ALIASES = {
    "abi_major": "uapi_version.abi_major",
    "abi_minor": "uapi_version.abi_minor",
    "header_family_revision": "uapi_version.header_family_revision",
    "abi_version": "abi.ABI_VERSION",
    "uapi_dev_t_packet_present": "1",
    "version_size": "version_binding.version_size",
    "version_align": "version_binding.version_align",
    "abi_major_offset": "version_binding.abi_major_offset",
    "abi_minor_offset": "version_binding.abi_minor_offset",
    "header_family_revision_offset": "version_binding.header_family_revision_offset",
    "fields_size": "dev_t_binding.fields_size",
    "fields_align": "dev_t_binding.fields_align",
    "major_offset": "dev_t_binding.major_offset",
    "minor_offset": "dev_t_binding.minor_offset",
    "max_major": "dev_t_binding.max_major",
    "max_minor": "dev_t_binding.max_minor",
}

LINUX_VERSION_HELPER_MAP = {
    "zigux_uapi_version_current": "current",
    "zigux_uapi_version_has_current_abi_major": "hasCurrentAbiMajor",
    "zigux_uapi_version_has_current_abi_minor": "hasCurrentAbiMinor",
    "zigux_uapi_version_has_current_header_family_revision": "hasCurrentHeaderFamilyRevision",
    "zigux_uapi_version_matches_current": "matchesCurrent",
}

DEV_T_HEADER_HELPER_MAP = {
    "zigux_dev_t_fields_make": "init",
    "zigux_mkdev": "makeDeviceNumber",
    "zigux_major": "majorFromDeviceNumber",
    "zigux_minor": "minorFromDeviceNumber",
    "zigux_dev_t_fields_is_valid": "validate",
    "zigux_dev_t_fields_range_is_valid": "validateRange",
}

C_DEFINE_RE = re.compile(r"^\s*#define\s+([A-Z0-9_]+)\s+(.+?)\s*$", re.MULTILINE)
ZIG_CONST_RE = re.compile(
    r"^\s*pub const\s+([A-Za-z0-9_]+)(?:\s*:\s*[^=]+)?\s*=\s*([^;]+);",
    re.MULTILINE,
)
C_INLINE_HELPER_RE = re.compile(
    r"^\s*static\s+inline\b[^\n(]*\b(zigux_[A-Za-z0-9_]+)\s*\(",
    re.MULTILINE,
)
ZIG_FUNCTION_RE = re.compile(r"^\s*pub fn\s+([A-Za-z][A-Za-z0-9_]*)\s*\(", re.MULTILINE)

SAMPLE_LINUX_HEADER = """\
#define ZIGUX_UAPI_ABI_MAJOR 0u
#define ZIGUX_UAPI_ABI_MINOR 1u
#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u
static inline struct zigux_uapi_version zigux_uapi_version_current(void) {
    return (struct zigux_uapi_version){0};
}
static inline int zigux_uapi_version_has_current_abi_major(uint32_t abi_major) {
    return abi_major == ZIGUX_UAPI_ABI_MAJOR;
}
static inline int zigux_uapi_version_has_current_abi_minor(uint32_t abi_minor) {
    return abi_minor == ZIGUX_UAPI_ABI_MINOR;
}
static inline int zigux_uapi_version_has_current_header_family_revision(uint32_t header_family_revision) {
    return header_family_revision == ZIGUX_UAPI_HEADER_FAMILY_REVISION;
}
static inline int zigux_uapi_version_matches_current(struct zigux_uapi_version version) {
    return version.abi_major == ZIGUX_UAPI_ABI_MAJOR;
}
static inline struct zigux_export_status zigux_uapi_validate_version(
    struct zigux_uapi_version version)
{
    return (struct zigux_export_status){0};
}
static inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)
{
    return (zigux_boundary_header){ .size = 8u, .abi_version = 1u, .flags = flags };
}
static inline uint32_t zigux_uapi_boundary_header_requested_extra_bytes(
    zigux_boundary_header header)
{
    return header.size;
}
static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)
{
    return fields.major <= 1u;
}
"""

SAMPLE_DEV_T_HEADER = """\
#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u
#define ZIGUX_DEV_T_FIELDS_SIZE 8u
#define ZIGUX_DEV_T_FIELDS_ALIGN 4u
#define ZIGUX_DEV_T_MAJOR_OFFSET 0u
#define ZIGUX_DEV_T_MINOR_OFFSET 4u
#define ZIGUX_DEV_MINOR_BITS 20u
struct zigux_dev_t_fields {
    uint32_t major;
    uint32_t minor;
};
static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(
    uint32_t major,
    uint32_t minor
) {
    return (struct zigux_dev_t_fields){ .major = major, .minor = minor };
}
static inline uint32_t zigux_mkdev(uint32_t major, uint32_t minor)
{
    return major | minor;
}
static inline uint32_t zigux_major(uint32_t dev)
{
    return dev;
}
static inline uint32_t zigux_minor(uint32_t dev)
{
    return dev;
}
static inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)
{
    return fields.major >= fields.minor;
}
static inline int zigux_dev_t_fields_range_is_valid(
    struct zigux_dev_t_fields start,
    struct zigux_dev_t_fields end
)
{
    return start.major <= end.major;
}
"""

SAMPLE_UAPI_VERSION = """\
pub const abi_major: u32 = 0;
pub const abi_minor: u32 = 1;
pub const header_family_revision: u32 = 1;
pub fn current() Version {
    return undefined;
}
pub fn hasCurrentAbiMajor(value: u32) bool {
    return value == abi_major;
}
pub fn hasCurrentAbiMinor(value: u32) bool {
    return value == abi_minor;
}
pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {
    return value == header_family_revision;
}
pub fn matchesCurrent(version: Version) bool {
    return version.abi_major == abi_major;
}
"""

SAMPLE_UAPI_DEV_T = """\
pub const abi_version: u32 = 1;
pub const major_bits: u6 = 12;
pub const minor_bits: u6 = 20;
pub fn init(major: u32, minor: u32) Fields {
    _ = major;
    _ = minor;
    return undefined;
}
pub fn makeDeviceNumber(major: u32, minor: u32) u32 {
    return major + minor;
}
pub fn majorFromDeviceNumber(device_number: u32) u32 {
    return device_number;
}
pub fn minorFromDeviceNumber(device_number: u32) u32 {
    return device_number;
}
pub fn validate(fields: Fields) bool {
    _ = fields;
    return true;
}
pub fn validateRange(start: Fields, end: Fields) bool {
    _ = start;
    _ = end;
    return true;
}
"""

SAMPLE_VERSION_BINDING = """\
pub const abi_major = uapi.abi_major;
pub const abi_minor = uapi.abi_minor;
pub const header_family_revision = uapi.header_family_revision;
pub const version_size = uapi.version_size;
pub const version_align = uapi.version_align;
pub const abi_major_offset = uapi.abi_major_offset;
pub const abi_minor_offset = uapi.abi_minor_offset;
pub const header_family_revision_offset = uapi.header_family_revision_offset;
pub fn current() Version {
    return uapi.current();
}
pub fn hasCurrentAbiMajor(value: u32) bool {
    return uapi.hasCurrentAbiMajor(value);
}
pub fn hasCurrentAbiMinor(value: u32) bool {
    return uapi.hasCurrentAbiMinor(value);
}
pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {
    return uapi.hasCurrentHeaderFamilyRevision(value);
}
pub fn matchesCurrent(version: Version) bool {
    return uapi.matchesCurrent(version);
}
"""

SAMPLE_DEV_T_BINDING = """\
pub const abi_version = uapi.abi_version;
pub const major_bits = uapi.major_bits;
pub const minor_bits = uapi.minor_bits;
pub const max_major = uapi.max_major;
pub const max_minor = uapi.max_minor;
pub const fields_size = uapi.fields_size;
pub const fields_align = uapi.fields_align;
pub const major_offset = uapi.major_offset;
pub const minor_offset = uapi.minor_offset;
pub fn init(major: u32, minor: u32) Fields {
    return uapi.init(major, minor);
}
pub fn makeDeviceNumber(major: u32, minor: u32) u32 {
    return uapi.makeDeviceNumber(major, minor);
}
pub fn majorFromDeviceNumber(device_number: u32) u32 {
    return uapi.majorFromDeviceNumber(device_number);
}
pub fn minorFromDeviceNumber(device_number: u32) u32 {
    return uapi.minorFromDeviceNumber(device_number);
}
pub fn validate(fields: Fields) bool {
    return uapi.validate(fields);
}
pub fn validateRange(start: Fields, end: Fields) bool {
    return uapi.validateRange(start, end);
}
"""

SAMPLE_HEADER_FAMILY_BINDING = """\
pub const abi_major: u32 = uapi_version.abi_major;
pub const abi_minor: u32 = uapi_version.abi_minor;
pub const header_family_revision: u32 = uapi_version.header_family_revision;
pub const abi_version: u16 = abi.ABI_VERSION;
pub const uapi_dev_t_packet_present: u32 = 1;
pub const version_size: usize = version_binding.version_size;
pub const version_align: usize = version_binding.version_align;
pub const abi_major_offset: usize = version_binding.abi_major_offset;
pub const abi_minor_offset: usize = version_binding.abi_minor_offset;
pub const header_family_revision_offset: usize = version_binding.header_family_revision_offset;
pub const fields_size: usize = dev_t_binding.fields_size;
pub const fields_align: usize = dev_t_binding.fields_align;
pub const major_offset: usize = dev_t_binding.major_offset;
pub const minor_offset: usize = dev_t_binding.minor_offset;
pub const max_major: u32 = dev_t_binding.max_major;
pub const max_minor: u32 = dev_t_binding.max_minor;
pub fn currentVersion() Version {
    return version_binding.current();
}
pub fn versionMatchesCurrent(version: Version) bool {
    return version_binding.matchesCurrent(version);
}
pub fn currentBoundaryHeader(flags: u16) BoundaryHeader {
    return abi.defaultHeader(flags);
}
pub fn boundaryHeaderRequestedExtraBytes(header: BoundaryHeader) u32 {
    return header.size;
}
pub fn initDevTFields(major: u32, minor: u32) DevTFields {
    return dev_t_binding.init(major, minor);
}
pub fn fieldsFromDeviceNumber(device_number: u32) DevTFields {
    return dev_t_binding.fieldsFromDeviceNumber(device_number);
}
pub fn validateVersionStatus(version: Version) ExportStatus {
    _ = version;
    return undefined;
}
pub fn validateDevTFieldsStatus(fields: DevTFields) ExportStatus {
    _ = fields;
    return undefined;
}
pub fn validateDevTRangeStatus(start: DevTFields, end: DevTFields) ExportStatus {
    _ = start;
    _ = end;
    return undefined;
}
"""

SAMPLE_FILE_CONTENTS = {
    LINUX_HEADER_PATH: SAMPLE_LINUX_HEADER,
    DEV_T_HEADER_PATH: SAMPLE_DEV_T_HEADER,
    UAPI_VERSION_PATH: SAMPLE_UAPI_VERSION,
    UAPI_DEV_T_PATH: SAMPLE_UAPI_DEV_T,
    VERSION_BINDING_PATH: SAMPLE_VERSION_BINDING,
    DEV_T_BINDING_PATH: SAMPLE_DEV_T_BINDING,
    HEADER_FAMILY_BINDING_PATH: SAMPLE_HEADER_FAMILY_BINDING,
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _parse_c_defines(text: str) -> dict[str, str]:
    return {name: value.strip() for name, value in C_DEFINE_RE.findall(text)}


def _parse_zig_consts(text: str) -> dict[str, str]:
    return {name: value.strip() for name, value in ZIG_CONST_RE.findall(text)}


def _c_inline_helpers(text: str) -> set[str]:
    return set(C_INLINE_HELPER_RE.findall(text))


def _zig_function_names(text: str) -> set[str]:
    return set(ZIG_FUNCTION_RE.findall(text))


def _normalize_c_int(expr: str) -> int | None:
    candidate = expr.strip()
    while candidate.startswith("(") and candidate.endswith(")"):
        candidate = candidate[1:-1].strip()
    candidate = candidate.rstrip("uU")
    if re.fullmatch(r"-?\d+", candidate):
        return int(candidate, 10)
    return None


def _normalize_zig_int(expr: str) -> int | None:
    candidate = expr.strip()
    if re.fullmatch(r"-?\d+", candidate):
        return int(candidate, 10)
    return None


def _append_helper_mapping_issues(
    source_label: str,
    source_helpers: set[str],
    target_label: str,
    target_helpers: set[str],
    required_pairs: dict[str, str],
    issues: list[str],
) -> None:
    for source_name, target_name in required_pairs.items():
        if source_name not in source_helpers:
            issues.append(f"missing {source_label}: {source_name}")
            continue
        if target_name not in target_helpers:
            issues.append(
                f"missing {target_label} for {source_label}: "
                f"{source_name} -> {target_name}"
            )


def _append_define_to_const_issues(
    header_label: str,
    defines: dict[str, str],
    define_to_const: dict[str, str],
    zig_label: str,
    zig_consts: dict[str, str],
    issues: list[str],
) -> None:
    for define_name, const_name in define_to_const.items():
        define_expr = defines.get(define_name)
        if define_expr is None:
            issues.append(f"missing {header_label} define: {define_name}")
            continue

        const_expr = zig_consts.get(const_name)
        if const_expr is None:
            issues.append(f"missing {zig_label} const for {header_label} define: {define_name} -> {const_name}")
            continue

        define_value = _normalize_c_int(define_expr)
        const_value = _normalize_zig_int(const_expr)
        if define_value is None:
            issues.append(f"unsupported {header_label} define expression: {define_name} = {define_expr}")
            continue
        if const_value is None:
            issues.append(f"unsupported {zig_label} const expression: {const_name} = {const_expr}")
            continue
        if define_value != const_value:
            issues.append(
                f"{header_label} define mismatch for {define_name}: "
                f"{define_value} != {zig_label}.{const_name} ({const_value})"
            )


def _append_binding_alias_issues(
    binding_label: str,
    binding_consts: dict[str, str],
    required_aliases: dict[str, str],
    issues: list[str],
) -> None:
    for const_name, expected_expr in required_aliases.items():
        actual_expr = binding_consts.get(const_name)
        if actual_expr is None:
            issues.append(f"missing {binding_label} alias: {const_name}")
            continue
        if actual_expr != expected_expr:
            issues.append(
                f"wrong {binding_label} alias for {const_name}: "
                f"{actual_expr!r} != {expected_expr!r}"
            )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    texts: dict[Path, str] = {}

    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        texts[relative_path] = text
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    linux_header_text = texts.get(LINUX_HEADER_PATH)
    dev_t_header_text = texts.get(DEV_T_HEADER_PATH)
    uapi_version_text = texts.get(UAPI_VERSION_PATH)
    uapi_dev_t_text = texts.get(UAPI_DEV_T_PATH)
    version_binding_text = texts.get(VERSION_BINDING_PATH)
    dev_t_binding_text = texts.get(DEV_T_BINDING_PATH)
    header_family_binding_text = texts.get(HEADER_FAMILY_BINDING_PATH)

    if linux_header_text is not None and uapi_version_text is not None:
        _append_define_to_const_issues(
            "include/linux/zigux.h",
            _parse_c_defines(linux_header_text),
            LINUX_VERSION_DEFINE_TO_ZIG_CONST,
            "zigux/uapi/version.zig",
            _parse_zig_consts(uapi_version_text),
            issues,
        )

    if dev_t_header_text is not None and uapi_dev_t_text is not None:
        _append_define_to_const_issues(
            "include/zigux/dev_t.h",
            _parse_c_defines(dev_t_header_text),
            DEV_T_DEFINE_TO_ZIG_CONST,
            "zigux/uapi/dev_t.zig",
            _parse_zig_consts(uapi_dev_t_text),
            issues,
        )

    if version_binding_text is not None:
        _append_binding_alias_issues(
            "zigux/bindings/version.zig",
            _parse_zig_consts(version_binding_text),
            REQUIRED_VERSION_BINDING_ALIASES,
            issues,
        )

    if dev_t_binding_text is not None:
        _append_binding_alias_issues(
            "zigux/bindings/dev_t.zig",
            _parse_zig_consts(dev_t_binding_text),
            REQUIRED_DEV_T_BINDING_ALIASES,
            issues,
        )

    if header_family_binding_text is not None:
        _append_binding_alias_issues(
            "zigux/bindings/header_family.zig",
            _parse_zig_consts(header_family_binding_text),
            REQUIRED_HEADER_FAMILY_BINDING_ALIASES,
            issues,
        )

    if linux_header_text is not None and uapi_version_text is not None:
        _append_helper_mapping_issues(
            "linux header helper",
            _c_inline_helpers(linux_header_text),
            "uapi version helper",
            _zig_function_names(uapi_version_text),
            LINUX_VERSION_HELPER_MAP,
            issues,
        )

    if linux_header_text is not None and version_binding_text is not None:
        _append_helper_mapping_issues(
            "linux header helper",
            _c_inline_helpers(linux_header_text),
            "version binding helper",
            _zig_function_names(version_binding_text),
            LINUX_VERSION_HELPER_MAP,
            issues,
        )

    if dev_t_header_text is not None and uapi_dev_t_text is not None:
        _append_helper_mapping_issues(
            "dev_t header helper",
            _c_inline_helpers(dev_t_header_text),
            "uapi dev_t helper",
            _zig_function_names(uapi_dev_t_text),
            DEV_T_HEADER_HELPER_MAP,
            issues,
        )

    if dev_t_header_text is not None and dev_t_binding_text is not None:
        _append_helper_mapping_issues(
            "dev_t header helper",
            _c_inline_helpers(dev_t_header_text),
            "dev_t binding helper",
            _zig_function_names(dev_t_binding_text),
            DEV_T_HEADER_HELPER_MAP,
            issues,
        )

    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        content = SAMPLE_FILE_CONTENTS.get(relative_path, "\n".join(markers) + "\n")
        _write(root / relative_path, content)


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


def _expect_issue(root: Path, relative_path: Path, before: str, after: str, expected: str, message: str) -> int:
    path = root / relative_path
    path.write_text(_read(path).replace(before, after, 1), encoding="utf-8")
    issues = validate_repo(root)
    if expected not in issues:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    marker_cases = (
        (
            SURVEY_PATH,
            "PHASE3_ABI_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json",
            "expected missing survey manifest marker was not reported",
        ),
        (
            SURVEY_PATH,
            "PHASE3_VERSION_BINDING_PATH=zigux/bindings/version.zig",
            "expected missing survey version-binding marker was not reported",
        ),
        (
            SURVEY_PATH,
            "PHASE3_HEADER_FAMILY_BINDING_PATH=zigux/bindings/header_family.zig",
            "expected missing survey header-family-binding marker was not reported",
        ),
        (
            SURVEY_PATH,
            "PHASE3_EXPORT_UAPI_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
            "expected missing survey layout-gate marker was not reported",
        ),
        (
            SURVEY_PATH,
            "- `include/linux/zigux.h` keeps the Linux-facing header-family relay bounded to `zigux_uapi_version_current()`, the `zigux_uapi_version_has_current_*()` helpers, `zigux_uapi_version_matches_current()`, and `zigux_uapi_validate_version()` rather than introducing a second semantic owner.",
            "expected missing survey linux-header marker was not reported",
        ),
        (
            SURVEY_PATH,
            "Current `master` no longer has a packet-local repo-reality gap for the bounded header-family survey follow-through itself.",
            "expected missing survey current-gap marker was not reported",
        ),
        (
            VALIDATOR_PATH,
            'print("PHASE3_ABI_HEADER_FAMILY_SURVEY=pass")',
            "expected missing validator pass marker was not reported",
        ),
        (
            ABI_SLICE_PATH,
            "the separate broader header-family binding follow-through remains the wider gap",
            "expected missing shared-slice wider-gap marker was not reported",
        ),
        (
            MANIFEST_PATH,
            '"Documentation/zigux/phase3-abi-header-family-survey.md"',
            "expected missing manifest header-family survey marker was not reported",
        ),
        (
            MANIFEST_PATH,
            '"zigux/bindings/header_family.zig"',
            "expected missing manifest header-family binding marker was not reported",
        ),
        (
            LINUX_HEADER_PATH,
            "static inline struct zigux_export_status zigux_uapi_validate_version(",
            "expected missing linux-header validate-version marker was not reported",
        ),
        (
            UAPI_VERSION_PATH,
            "pub const header_family_revision: u32 = 1;",
            "expected missing uapi version header-family revision marker was not reported",
        ),
        (
            VERSION_BINDING_PATH,
            "pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {",
            "expected missing version-binding header-family revision marker was not reported",
        ),
        (
            HEADER_FAMILY_BINDING_PATH,
            "pub fn validateDevTRangeStatus(start: DevTFields, end: DevTFields) ExportStatus {",
            "expected missing header-family binding range-status marker was not reported",
        ),
        (
            LAYOUT_TEST_PATH,
            'test "export shim mirrors boundary header predicate helpers" {',
            "expected missing layout replay predicate marker was not reported",
        ),
        (
            LAYOUT_BUILD_PATH,
            '"phase3-export-uapi-layout-test"',
            "expected missing layout build route marker was not reported",
        ),
    )

    semantic_cases = (
        (
            LINUX_HEADER_PATH,
            "#define ZIGUX_UAPI_ABI_MINOR 1u",
            "#define ZIGUX_UAPI_ABI_MINOR 2u",
            "include/linux/zigux.h define mismatch for ZIGUX_UAPI_ABI_MINOR: 2 != zigux/uapi/version.zig.abi_minor (1)",
            "expected version define mismatch was not reported",
        ),
        (
            VERSION_BINDING_PATH,
            "pub const abi_minor = uapi.abi_minor;",
            "pub const abi_minor = uapi.abi_major;",
            "wrong zigux/bindings/version.zig alias for abi_minor: 'uapi.abi_major' != 'uapi.abi_minor'",
            "expected version binding alias drift was not reported",
        ),
        (
            DEV_T_BINDING_PATH,
            "pub const minor_bits = uapi.minor_bits;",
            "pub const minor_bits = uapi.major_bits;",
            "wrong zigux/bindings/dev_t.zig alias for minor_bits: 'uapi.major_bits' != 'uapi.minor_bits'",
            "expected dev_t binding alias drift was not reported",
        ),
        (
            HEADER_FAMILY_BINDING_PATH,
            "pub const abi_major: u32 = uapi_version.abi_major;",
            "pub const abi_major: u32 = uapi_version.abi_minor;",
            "wrong zigux/bindings/header_family.zig alias for abi_major: 'uapi_version.abi_minor' != 'uapi_version.abi_major'",
            "expected header-family binding alias drift was not reported",
        ),
        (
            DEV_T_HEADER_PATH,
            "static inline uint32_t zigux_major(uint32_t dev)",
            "static inline uint32_t zigux_device_major(uint32_t dev)",
            "missing dev_t header helper: zigux_major",
            "expected dev_t helper mapping drift was not reported",
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

        for relative_path, before, after, expected, message in semantic_cases:
            _populate_repo(root)
            if _expect_issue(root, relative_path, before, after, expected, message) != 0:
                return 1

    print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass")
    print(
        "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST_CASE_COUNT="
        f"{1 + len(marker_cases) + len(semantic_cases)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 ABI header-family packet."
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
