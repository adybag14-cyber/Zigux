#!/usr/bin/env python3
"""Fail-close the current bounded Phase 3 shared ABI packet."""

from __future__ import annotations

import argparse
import json
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
BINDING_HEADER_FAMILY = Path("zigux/bindings/header_family.zig")
BINDING_NOTIFIER = Path("zigux/bindings/notifier_abi.zig")
EXPORT_SHIM = Path("zigux/kernel/export_shim.zig")
PHASE3_CATALOG = Path("scripts/zigux/phase3_catalog.py")
ABI_TEST = Path("zigux/tests/phase3_abi.zig")
TESTS_BUILD = Path("zigux/tests/build.zig")
ABI_DUMP = Path("zigux/tests/phase3_abi_dump_current.zig")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_MARKERS = {
    ABI_SLICE_NOTE: (
        "PHASE3_CURRENT_INTEROP_GAP=",
        "PHASE3_CURRENT_INTEROP_GAP_DETAIL=",
        "Documentation/zigux/phase3-policy-slice.md",
        "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
        "Documentation/zigux/phase3-linux-zigux-header-governance.md",
        "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
        "include/linux/zigux.h",
        "include/zigux/dev_t.h",
        "include/zigux/abi.h",
        "zigux/uapi/dev_t.zig",
        "zigux/uapi/version.zig",
        "zigux/bindings/dev_t.zig",
        "zigux/bindings/version.zig",
        "zigux/bindings/header_family.zig",
        "zigux/bindings/abi.zig",
        "zigux/bindings/notifier_abi.zig",
        "zigux/kernel/export_shim.zig",
        "zigux/helpers/layout_assert.zig",
        "scripts/zigux/check-phase3-abi.py",
        "scripts/zigux/check-phase3-abi-support-packet.py",
        "scripts/zigux/validate-phase3.py",
        "scripts/zigux/phase3_catalog.py",
        "scripts/zigux/check-phase3-catalog-selftest.py",
        "scripts/zigux/validate-phase3-export-uapi-survey.py",
        "scripts/zigux/validate-phase3-abi-header-family-survey.py",
        "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "zigux/tests/phase3_abi.zig",
        "zigux/tests/build.zig",
        "zigux/tests/phase3_abi_dump_current.zig",
        "zigux/tests/fixtures/phase3_abi_manifest.json",
        "zigux/tests/phase3_export_uapi_layout.zig",
        "zigux/tests/phase3_export_uapi_layout_build.zig",
        "zigux/tests/phase3_low_level_wrappers.zig",
        "zigux/tests/phase3_low_level_wrappers_build.zig",
        "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-abi-support-packet.py",
        "make -C zigux phase3-low-level-wrappers-test",
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
        "typedef struct zigux_list_backlink_break {",
        "typedef struct zigux_hlist_prev_link_break {",
        "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
        "static inline zigux_boundary_header zigux_compatible_header(",
        "static inline int zigux_abi_version_is_current(uint16_t abi_version)",
        "static inline int zigux_header_is_canonical(zigux_boundary_header header)",
        "static inline int zigux_header_is_compatible(zigux_boundary_header header)",
        "static inline int zigux_header_extends_boundary(zigux_boundary_header header)",
        "static inline uint32_t zigux_header_requested_extra_bytes(",
        "static inline zigux_boundary_header zigux_header_canonicalize(",
        "static inline struct zigux_interop_policy zigux_default_interop_policy(void)",
        "static inline struct zigux_export_status zigux_make_status(",
        "static inline struct zigux_export_status zigux_ok_status(uint16_t facility)",
        "static inline int zigux_export_status_ok(struct zigux_export_status status)",
        "static inline int zigux_notifier_chain_has_nonincreasing_priority(",
        "previous_priority = head->priority;",
        "if (node->priority > previous_priority)",
        "static inline int zigux_notifier_first_chain_priority_increase(",
        "out->previous_index = previous_index;",
        "out->current_index = current_index;",
        "out->previous_priority = previous_priority;",
        "out->current_priority = node->priority;",
        "static inline int zigux_list_first_broken_backlink(",
        "static inline int zigux_list_has_consistent_backlinks(",
        "static inline int zigux_hlist_first_broken_prev_link(",
        "static inline int zigux_hlist_has_consistent_prev_links(",
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
    BINDING_HEADER_FAMILY: (
        'const abi = @import("abi_bindings");',
        'const dev_t_binding = @import("dev_t_binding");',
        'const version_binding = @import("version_binding");',
        'const uapi_version = @import("uapi_version");',
        "pub const abi_major: u32 = uapi_version.abi_major;",
        "pub const header_family_revision: u32 = uapi_version.header_family_revision;",
        "pub const BoundaryHeader = abi.BoundaryHeader;",
        "pub fn currentVersion() Version {",
        "pub fn currentBoundaryHeader(flags: u16) BoundaryHeader {",
        "pub fn boundaryHeaderRequestedExtraBytes(header: BoundaryHeader) u32 {",
        "pub fn initDevTFields(major: u32, minor: u32) DevTFields {",
        "pub fn validateDevTRange(start: DevTFields, end: DevTFields) bool {",
    ),
    BINDING_NOTIFIER: (
        "pub const NotifierResult = enum(u32) {",
        "done = 0,",
        "ok = 1,",
        "stop = 2,",
        "pub const NotifierBlock = extern struct {",
        "pub const ListBackLinkBreak = extern struct {",
        "pub const HListPrevLinkBreak = extern struct {",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
        "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?NotifierChainPriorityIncrease {",
        "pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {",
        "pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {",
        "pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {",
        "pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {",
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
        "pub const ListBackLinkBreak = notifier_abi.ListBackLinkBreak;",
        "pub const HListPrevLinkBreak = notifier_abi.HListPrevLinkBreak;",
        "pub fn defaultHeader(flags: u16) BoundaryHeader {",
        "pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader {",
        "pub fn headerHasCurrentAbiVersion(abi_version: u16) bool {",
        "pub fn defaultInteropPolicy() InteropPolicy {",
        "pub fn headerIsCanonical(header: BoundaryHeader) bool {",
        "pub fn headerIsCompatible(header: BoundaryHeader) bool {",
        "pub fn extendsBoundary(header: BoundaryHeader) bool {",
        "pub fn requestedExtraBytes(header: BoundaryHeader) u32 {",
        "pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {",
        "pub fn makeStatus(code: i32, facility: Facility) ExportStatus {",
        "pub fn okStatus(facility: Facility) ExportStatus {",
        "pub fn statusIsOk(status: ExportStatus) bool {",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
        "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease {",
        "pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {",
        "pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {",
        "pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {",
        "pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {",
    ),
    EXPORT_SHIM: (
        'const abi = @import("abi_bindings");',
        'const dev_t = @import("dev_t_binding");',
        'const version = @import("version_binding");',
        "pub const BoundaryHeader = abi.BoundaryHeader;",
        "pub const ExportStatus = abi.ExportStatus;",
        "pub const Facility = abi.Facility;",
        "pub fn canonicalHeader(flags: u16) BoundaryHeader {",
        "pub fn headerIsCanonical(header: BoundaryHeader) bool {",
        "pub fn headerIsCompatible(header: BoundaryHeader) bool {",
        "pub fn extendsBoundary(header: BoundaryHeader) bool {",
        "pub fn requestedExtraBytes(header: BoundaryHeader) u32 {",
        "pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {",
        "pub fn okStatus(facility: Facility) ExportStatus {",
        "pub fn errorStatus(code: i32, facility: Facility) ExportStatus {",
        "pub fn statusIsOk(status: ExportStatus) bool {",
        "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
    ),
    PHASE3_CATALOG: (
        'PHASE3_CATALOG_SCOPE = "abi-runtime"',
        'Path("zigux/bindings/header_family.zig")',
        'print("PHASE3_CATALOG_SELF_TEST=pass")',
    ),
    ABI_TEST: (
        'test "phase3 abi keeps shared layout assertions wired into the replay" {',
        "try layout_assert.assertPublishedAbiLayouts();",
        "layout_assert.assertInteropPolicyModeValues();",
        "layout_assert.assertNotifierResultValues();",
        'test "phase3 abi keeps export shim compatibility and status helpers reviewable" {',
        'test "phase3 abi keeps version and dev_t relays explicit" {',
        'test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {',
        'test "phase3 abi keeps byte-level policy relays aligned with published ABI constants" {',
        'test "phase3 abi keeps malformed notifier list relays visible through the shared ABI surface" {',
    ),
    TESTS_BUILD: (
        "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);",
        "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);",
        "const phase3_abi_dump = addPhase3AbiDump(b, target, optimize);",
        '"phase3-abi-core-packet"',
        '"phase3-export-uapi-layout"',
        '"phase3-dump"',
        "phase3_test_step.dependOn(&phase3_abi_core_packet.step);",
        "phase3_test_step.dependOn(&phase3_export_uapi_layout.step);",
    ),
    ABI_DUMP: (
        'const abi = @import("abi_bindings");',
        "pub fn main(init: std.process.Init) !void {",
        "const default_header = abi.defaultHeader(0);",
        "const policy = abi.defaultInteropPolicy();",
        "const header_is_canonical = abi.headerIsCanonical(default_header);",
        "abi.STATUS_FLAG_ERROR,",
        "abi.NOTIFIER_DONE,",
        '@offsetOf(abi.NotifierBlock, "priority"),',
        '"  \\\"abi_version\\\": {},\\n"',
        '"  \\\"notifier\\\": {{\\n"',
    ),
    MANIFEST_PATH: (
        '"phase": "Phase 3"',
        '"lane": "abi-runtime"',
        '"slug": "phase3-abi-packet"',
        '"status": "shared_abi_and_header_family_binding_surface_present"',
        '"scope": "shared ABI bindings, directly coupled helper decoding, header-family follow-through, notifier layouts, export-status layout, and header-compatibility replay"',
        '"Documentation/zigux/phase3-abi-slice.md"',
        '"Documentation/zigux/phase3-abi-header-family-survey.md"',
        '"scripts/zigux/check-phase3-abi-support-packet.py"',
        '"zigux/bindings/abi.zig"',
        '"zigux/bindings/header_family.zig"',
        '"zigux/bindings/notifier_abi.zig"',
        '"zigux/helpers/atomic.zig"',
        '"zigux/helpers/barrier.zig"',
        '"zigux/helpers/mmio.zig"',
        '"zigux/unsafe/narrow.zig"',
        '"scripts/zigux/validate-phase3.py"',
        '"scripts/zigux/validate-phase3-abi-header-family-survey.py"',
        '"scripts/zigux/validate-phase3-linux-zigux-header-governance.py"',
        '"zigux/tests/README.md"',
        '"scripts/zigux/phase3_catalog.py"',
        '"scripts/zigux/check-phase3-policy-starter-packet.py"',
        '"scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"',
        '"zigux/tests/phase3_abi.zig"',
        '"zigux/tests/phase3_abi_dump_current.zig"',
        '"zigux/tests/phase3_policy_starter_packet.zig"',
        '"zigux/tests/phase3_policy_starter_packet_build.zig"',
        '"zigux/tests/phase3_policy_starter_packet_manifest.json"',
        '"zigux/tests/phase3_export_uapi_c_header_smoke.c"',
        '"python3 scripts/zigux/check-phase3-abi.py --self-test"',
        '"python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase3-abi-support-packet.py"',
        '"python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase3-policy-starter-packet.py"',
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py"',
        '"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"',
        '"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"',
        '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
        '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
        '"zig build phase3-abi-core-packet --build-file zigux/tests/build.zig"',
        '"zig build phase3-dump --build-file zigux/tests/build.zig"',
        '"zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig"',
        '"zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"',
        '"make -C zigux phase3-low-level-wrappers-test"',
        '"repo_reality_gaps": []',
        '"next_safe_step": "keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again"',
    ),
}

SELF_TEST_CASES = (
    (ABI_SLICE_NOTE, "zigux/bindings/header_family.zig"),
    (ABI_SLICE_NOTE, "Documentation/zigux/phase3-linux-zigux-header-governance.md"),
    (ABI_SLICE_NOTE, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    (ABI_SLICE_NOTE, "zigux/helpers/layout_assert.zig"),
    (ABI_SLICE_NOTE, "scripts/zigux/check-phase3-abi-support-packet.py"),
    (ABI_SLICE_NOTE, "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test"),
    (ABI_HEADER, "previous_priority = head->priority;"),
    (ABI_HEADER, "out->current_priority = node->priority;"),
    (BINDING_HEADER_FAMILY, "pub fn currentBoundaryHeader(flags: u16) BoundaryHeader {"),
    (BINDING_ABI, "pub const NotifierResult = notifier_abi.NotifierResult;"),
    (BINDING_ABI, "pub const ListBackLinkBreak = notifier_abi.ListBackLinkBreak;"),
    (BINDING_NOTIFIER, "pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {"),
    (EXPORT_SHIM, "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {"),
    (ABI_TEST, "try layout_assert.assertPublishedAbiLayouts();"),
    (ABI_TEST, "layout_assert.assertInteropPolicyModeValues();"),
    (ABI_TEST, "layout_assert.assertNotifierResultValues();"),
    (ABI_TEST, 'test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {'),
    (ABI_TEST, 'test "phase3 abi keeps byte-level policy relays aligned with published ABI constants" {'),
    (ABI_TEST, 'test "phase3 abi keeps malformed notifier list relays visible through the shared ABI surface" {'),
    (ABI_DUMP, "abi.NOTIFIER_DONE,"),
    (PHASE3_CATALOG, 'Path("zigux/bindings/header_family.zig")'),
    (MANIFEST_PATH, '"status": "shared_abi_and_header_family_binding_surface_present"'),
    (MANIFEST_PATH, '"scripts/zigux/check-phase3-abi-support-packet.py"'),
    (MANIFEST_PATH, '"zigux/tests/README.md"'),
    (MANIFEST_PATH, '"python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test"'),
    (MANIFEST_PATH, '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"'),
)

SEMANTIC_SELF_TEST_CASES = (
    (
        BINDING_ABI,
        "pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader {",
        "missing ABI binding helper for ABI header inline helper: zigux_compatible_header -> compatibleHeader",
    ),
    (
        BINDING_ABI,
        "pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {",
        "missing ABI binding helper for ABI header inline helper: zigux_list_first_broken_backlink -> firstBrokenBacklink",
    ),
    (
        EXPORT_SHIM,
        "pub fn extendsBoundary(header: BoundaryHeader) bool {",
        "missing export shim helper for ABI header inline helper: zigux_header_extends_boundary -> extendsBoundary",
    ),
    (
        ABI_HEADER,
        "static inline uint32_t zigux_header_requested_extra_bytes(",
        "missing ABI header inline helper: zigux_header_requested_extra_bytes",
    ),
)

HEADER_DEFINE_RE = re.compile(r"^\s*#define\s+ZIGUX_([A-Z0-9_]+)\b", re.MULTILINE)
BINDING_CONST_RE = re.compile(r"^\s*pub const\s+([A-Z0-9_]+)\s*:", re.MULTILINE)
C_INLINE_HELPER_RE = re.compile(
    r"^\s*static\s+inline\b[^\n(]*\b(zigux_[A-Za-z0-9_]+)\s*\(",
    re.MULTILINE,
)
ZIG_FUNCTION_RE = re.compile(r"^\s*pub fn\s+([A-Za-z][A-Za-z0-9_]*)\s*\(", re.MULTILINE)

REQUIRED_HEADER_BINDING_HELPERS = {
    "zigux_default_header": "defaultHeader",
    "zigux_compatible_header": "compatibleHeader",
    "zigux_abi_version_is_current": "headerHasCurrentAbiVersion",
    "zigux_header_is_canonical": "headerIsCanonical",
    "zigux_header_is_compatible": "headerIsCompatible",
    "zigux_header_extends_boundary": "extendsBoundary",
    "zigux_header_requested_extra_bytes": "requestedExtraBytes",
    "zigux_header_canonicalize": "canonicalizeHeader",
    "zigux_default_interop_policy": "defaultInteropPolicy",
    "zigux_make_status": "makeStatus",
    "zigux_ok_status": "okStatus",
    "zigux_export_status_ok": "statusIsOk",
    "zigux_notifier_chain_has_nonincreasing_priority": "chainHasNonincreasingPriority",
    "zigux_notifier_first_chain_priority_increase": "firstChainPriorityIncrease",
    "zigux_list_first_broken_backlink": "firstBrokenBacklink",
    "zigux_list_has_consistent_backlinks": "listHasConsistentBacklinks",
    "zigux_hlist_first_broken_prev_link": "firstBrokenPrevLink",
    "zigux_hlist_has_consistent_prev_links": "hlistHasConsistentPrevLinks",
}

REQUIRED_HEADER_EXPORT_SHIM_HELPERS = {
    "zigux_header_is_canonical": "headerIsCanonical",
    "zigux_header_is_compatible": "headerIsCompatible",
    "zigux_header_extends_boundary": "extendsBoundary",
    "zigux_header_requested_extra_bytes": "requestedExtraBytes",
    "zigux_header_canonicalize": "canonicalizeHeader",
    "zigux_ok_status": "okStatus",
    "zigux_export_status_ok": "statusIsOk",
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
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "include/zigux/abi.h",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
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
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
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
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/Makefile",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-abi.py --self-test",
    "python3 scripts/zigux/check-phase3-abi.py",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
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
    "zig build phase3-abi-core-packet --build-file zigux/tests/build.zig",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
)

REQUIRED_REPO_REALITY_GAPS: tuple[str, ...] = ()

SAMPLE_MANIFEST = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_and_header_family_binding_surface_present",
    "scope": "shared ABI bindings, directly coupled helper decoding, header-family follow-through, notifier layouts, export-status layout, and header-compatibility replay",
    "packet_files": list(REQUIRED_PACKET_FILES),
    "replay_routes": list(REQUIRED_REPLAY_ROUTES),
    "repo_reality_gaps": list(REQUIRED_REPO_REALITY_GAPS),
    "next_safe_step": "keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _header_names(text: str) -> set[str]:
    return set(HEADER_DEFINE_RE.findall(text))


def _binding_names(text: str) -> set[str]:
    return set(BINDING_CONST_RE.findall(text))


def _header_inline_helpers(text: str) -> set[str]:
    return set(C_INLINE_HELPER_RE.findall(text))


def _zig_function_names(text: str) -> set[str]:
    return set(ZIG_FUNCTION_RE.findall(text))


def _append_duplicate_list_entry_issues(
    manifest_name: str,
    field_name: str,
    values: list[object],
    issues: list[str],
) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{manifest_name} duplicate {field_name} entry: "
            f"{value!r} (first index {first_index}, duplicate index {index})"
        )


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

        _append_helper_mapping_issues(
            "ABI header inline helper",
            _header_inline_helpers(header_text),
            "ABI binding helper",
            _zig_function_names(binding_text),
            REQUIRED_HEADER_BINDING_HELPERS,
            issues,
        )

    export_shim_text = texts.get(EXPORT_SHIM)
    if header_text is not None and export_shim_text is not None:
        _append_helper_mapping_issues(
            "ABI header inline helper",
            _header_inline_helpers(header_text),
            "export shim helper",
            _zig_function_names(export_shim_text),
            REQUIRED_HEADER_EXPORT_SHIM_HELPERS,
            issues,
        )

    notifier_text = texts.get(BINDING_NOTIFIER)
    if binding_text is not None and notifier_text is not None:
        for marker in (
            "pub const NotifierResult = notifier_abi.NotifierResult;",
            "pub const NotifierBlock = notifier_abi.NotifierBlock;",
            "pub const ListBackLinkBreak = notifier_abi.ListBackLinkBreak;",
            "pub const HListPrevLinkBreak = notifier_abi.HListPrevLinkBreak;",
        ):
            if marker not in binding_text:
                issues.append(f"missing {BINDING_ABI.as_posix()} marker: {marker}")
        for marker in (
            "done = 0,",
            "ok = 1,",
            "stop = 2,",
            "pub const ListBackLinkBreak = extern struct {",
            "pub const HListPrevLinkBreak = extern struct {",
            "pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {",
            "pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {",
        ):
            if marker not in notifier_text:
                issues.append(f"missing {BINDING_NOTIFIER.as_posix()} marker: {marker}")

    manifest_text = texts.get(MANIFEST_PATH)
    if manifest_text is not None:
        try:
            manifest = json.loads(manifest_text)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            for field, expected in REQUIRED_MANIFEST_FIELDS.items():
                actual = manifest.get(field)
                if actual != expected:
                    issues.append(
                        "phase3_abi_manifest.json wrong "
                        f"{field}: {actual!r} != {expected!r}"
                    )

            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            repo_reality_gaps = manifest.get("repo_reality_gaps")
            if not isinstance(packet_files, list):
                issues.append("phase3_abi_manifest.json packet_files is not a list")
            if not isinstance(replay_routes, list):
                issues.append("phase3_abi_manifest.json replay_routes is not a list")
            if not isinstance(repo_reality_gaps, list):
                issues.append("phase3_abi_manifest.json repo_reality_gaps is not a list")
            if isinstance(packet_files, list):
                _append_duplicate_list_entry_issues(
                    "phase3_abi_manifest.json",
                    "packet_files",
                    packet_files,
                    issues,
                )
                for required_path in REQUIRED_PACKET_FILES:
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_abi_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                _append_duplicate_list_entry_issues(
                    "phase3_abi_manifest.json",
                    "replay_routes",
                    replay_routes,
                    issues,
                )
                for route in REQUIRED_REPLAY_ROUTES:
                    if route not in replay_routes:
                        issues.append(
                            "phase3_abi_manifest.json missing replay route: "
                            f"{route}"
                        )
            if isinstance(repo_reality_gaps, list):
                _append_duplicate_list_entry_issues(
                    "phase3_abi_manifest.json",
                    "repo_reality_gaps",
                    repo_reality_gaps,
                    issues,
                )
                for gap in repo_reality_gaps:
                    if (repo_root / gap).exists():
                        issues.append(
                            "phase3_abi_manifest.json repo_reality_gaps entry is present on disk: "
                            f"{gap}"
                        )
                for gap in REQUIRED_REPO_REALITY_GAPS:
                    if gap not in repo_reality_gaps:
                        issues.append(
                            "phase3_abi_manifest.json missing repo_reality_gaps entry: "
                            f"{gap}"
                        )

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_check_") as temp_dir:
        root = Path(temp_dir)

        for rel_path, markers in REQUIRED_MARKERS.items():
            _write(root / rel_path, "\n".join(markers) + "\n")
        _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for rel_path, marker in SELF_TEST_CASES:
            for populate_path, markers in REQUIRED_MARKERS.items():
                _write(root / populate_path, "\n".join(markers) + "\n")
            _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")
            _write(root / rel_path, _read(root / rel_path).replace(marker, "", 1))
            issues = validate_repo(root)
            expected = f"missing {rel_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_ABI_CHECK_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        for rel_path, marker, expected in SEMANTIC_SELF_TEST_CASES:
            for populate_path, markers in REQUIRED_MARKERS.items():
                _write(root / populate_path, "\n".join(markers) + "\n")
            _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")
            _write(root / rel_path, _read(root / rel_path).replace(marker, "", 1))
            issues = validate_repo(root)
            if expected not in issues:
                print("PHASE3_ABI_CHECK_SELF_TEST=fail")
                print(f"expected semantic issue was not reported: {expected}")
                return 1

        for populate_path, markers in REQUIRED_MARKERS.items():
            _write(root / populate_path, "\n".join(markers) + "\n")
        _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].append(REQUIRED_REPLAY_ROUTES[0])
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_duplicate = (
            "phase3_abi_manifest.json duplicate replay_routes entry: "
            "'python3 scripts/zigux/check-phase3-abi.py --self-test' "
        )
        if not any(issue.startswith(expected_duplicate) for issue in issues):
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected duplicate replay route was not reported")
            return 1

        for populate_path, markers in REQUIRED_MARKERS.items():
            _write(root / populate_path, "\n".join(markers) + "\n")
        _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].remove("python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_missing_route = (
            "phase3_abi_manifest.json missing replay route: "
            "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test"
        )
        if expected_missing_route not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected missing replay route was not reported")
            return 1

        for populate_path, markers in REQUIRED_MARKERS.items():
            _write(root / populate_path, "\n".join(markers) + "\n")
        _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["packet_files"].remove("zigux/tests/README.md")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_missing_packet_file = (
            "phase3_abi_manifest.json missing packet_files entry: "
            "zigux/tests/README.md"
        )
        if expected_missing_packet_file not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected missing packet_files entry was not reported")
            return 1

        for populate_path, markers in REQUIRED_MARKERS.items():
            _write(root / populate_path, "\n".join(markers) + "\n")
        _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["repo_reality_gaps"].append(BINDING_ABI.as_posix())
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_present_gap = (
            "phase3_abi_manifest.json repo_reality_gaps entry is present on disk: "
            f"{BINDING_ABI.as_posix()}"
        )
        if expected_present_gap not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected present-on-disk repo-reality gap was not reported")
            return 1

    print("PHASE3_ABI_CHECK_SELF_TEST=pass")
    print(f"PHASE3_ABI_CHECK_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + len(SEMANTIC_SELF_TEST_CASES) + 4}")
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
    print("PHASE3_ABI_SCOPE=shared-abi-and-header-family-packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
