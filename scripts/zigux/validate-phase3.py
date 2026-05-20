#!/usr/bin/env python3
"""Validate the current bounded Phase 3 shared ABI binding surface."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDINGS_PATH = Path("zigux/bindings/abi.zig")
NOTIFIER_BINDINGS_PATH = Path("zigux/bindings/notifier_abi.zig")
ABI_CHECKER_PATH = Path("scripts/zigux/check-phase3-abi.py")
PHASE3_CATALOG_PATH = Path("scripts/zigux/phase3_catalog.py")
TESTS_BUILD_PATH = Path("zigux/tests/build.zig")
ABI_TEST_PATH = Path("zigux/tests/phase3_abi.zig")
ABI_MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
EXPORT_UAPI_LAYOUT_PATH = Path("zigux/tests/phase3_export_uapi_layout.zig")
EXPORT_UAPI_LAYOUT_BUILD_PATH = Path("zigux/tests/phase3_export_uapi_layout_build.zig")

REQUIRED_SOURCE_MARKERS = {
    ABI_HEADER_PATH: (
        "#define ZIGUX_ABI_VERSION 1U",
        "#define ZIGUX_FACILITY_KERNEL 1U",
        "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
        "struct zigux_boundary_header {",
        "struct zigux_interop_policy {",
        "struct zigux_export_status {",
        "struct zigux_notifier_block {",
        "struct zigux_list_head {",
        "struct zigux_hlist_head {",
        "struct zigux_hlist_node {",
        "static inline int zigux_notifier_chain_has_nonincreasing_priority(",
        "static inline int zigux_notifier_first_chain_priority_increase(",
        "static inline int zigux_list_has_consistent_backlinks(",
        "static inline int zigux_hlist_has_consistent_prev_links(",
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
    ),
    ABI_BINDINGS_PATH: (
        "pub const ABI_VERSION: u16 = 1;",
        "pub const FACILITY_KERNEL: u16 = 1;",
        "pub const UNSAFE_RAW_POINTER_BRIDGE: u8 = 2;",
        "pub const BoundaryHeader = extern struct {",
        "pub const InteropPolicy = extern struct {",
        "pub const ExportStatus = extern struct {",
        "pub const NotifierBlock = notifier_abi.NotifierBlock;",
        "pub const ListHead = notifier_abi.ListHead;",
        "pub const HListHead = notifier_abi.HListHead;",
        "pub const HListNode = notifier_abi.HListNode;",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
        "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease {",
        "pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {",
        "pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {",
        "pub fn defaultHeader(flags: u16) BoundaryHeader {",
        "pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader {",
        "pub fn headerHasCurrentAbiVersion(abi_version: u16) bool {",
        "pub fn headerIsCanonical(header: BoundaryHeader) bool {",
        "pub fn headerIsCompatible(header: BoundaryHeader) bool {",
        "pub fn extendsBoundary(header: BoundaryHeader) bool {",
        "pub fn requestedExtraBytes(header: BoundaryHeader) u32 {",
        "pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {",
        "pub fn defaultInteropPolicy() InteropPolicy {",
        "pub fn makeStatus(code: i32, facility: Facility) ExportStatus {",
        "pub fn okStatus(facility: Facility) ExportStatus {",
        "pub fn statusIsOk(status: ExportStatus) bool {",
    ),
    NOTIFIER_BINDINGS_PATH: (
        "pub const NotifierBlock = extern struct {",
        "pub const NotifierChainPriorityIncrease = extern struct {",
        "pub const ListHead = extern struct {",
        "pub const HListHead = extern struct {",
        "pub const HListNode = extern struct {",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
        "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?NotifierChainPriorityIncrease {",
        "pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {",
        "pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {",
    ),
    ABI_CHECKER_PATH: (
        'ABI_SLICE_NOTE = Path("Documentation/zigux/phase3-abi-slice.md")',
        'ABI_HEADER = Path("include/zigux/abi.h")',
        'BINDING_ABI = Path("zigux/bindings/abi.zig")',
        'EXPORT_SHIM = Path("zigux/kernel/export_shim.zig")',
        'MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")',
        "def validate_repo(repo_root: Path) -> list[str]:",
        'print("PHASE3_ABI_CHECK_SELF_TEST=pass")',
    ),
    PHASE3_CATALOG_PATH: (
        'PHASE3_CATALOG_PHASE = "Phase 3"',
        'PHASE3_CATALOG_SCOPE = "abi-runtime"',
        "def build_catalog(repo_root: Path) -> dict[str, object]:",
        'print("PHASE3_CATALOG_SELF_TEST=pass")',
    ),
    TESTS_BUILD_PATH: (
        'const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);',
        'const phase3_abi_dump = addPhase3AbiDump(b, target, optimize);',
        'root_source_file = b.path("phase3_abi.zig"),',
        'root_source_file = b.path("phase3_abi_dump_current.zig"),',
        '"phase3-abi-core-packet"',
        '"phase3-dump"',
        'phase3_abi_core_step.dependOn(&phase3_abi_core_packet.step);',
        'phase3_dump_step.dependOn(&phase3_abi_dump.step);',
    ),
    ABI_TEST_PATH: (
        'test "phase3 abi keeps shared layout assertions wired into the replay" {',
        'try layout_assert.assertPublishedAbiLayouts();',
        'test "phase3 abi keeps export shim compatibility and status helpers reviewable" {',
        'test "phase3 abi keeps version and dev_t relays explicit" {',
        'test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {',
        'test "phase3 abi keeps byte-level policy relays aligned with published ABI constants" {',
    ),
    EXPORT_UAPI_LAYOUT_PATH: (
        'test "export and uapi dev_t layouts stay aligned" {',
        'test "export and uapi version layouts stay aligned" {',
        'test "export shim relays version compatibility without widening the boundary" {',
        'test "export shim reuses the canonical boundary header contract" {',
        'test "export shim mirrors boundary header predicate helpers" {',
    ),
    EXPORT_UAPI_LAYOUT_BUILD_PATH: (
        '.root_source_file = b.path("../uapi/dev_t.zig"),',
        '.root_source_file = b.path("../uapi/version.zig"),',
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        '"phase3-export-uapi-layout-test"',
    ),
    ABI_MANIFEST_PATH: (
        '"phase": "Phase 3"',
        '"lane": "abi-runtime"',
        '"slug": "phase3-abi-packet"',
        '"zigux/tests/phase3_abi.zig"',
        '"zig build phase3-abi-core-packet --build-file zigux/tests/build.zig"',
    ),
}

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_and_header_family_binding_surface_present",
    "scope": "shared ABI bindings, header-family follow-through, notifier layouts, export-status layout, and header-compatibility replay",
}

REQUIRED_MANIFEST_PACKET_FILES = (
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/check-phase3-abi.py",
    "zigux/tests/build.zig",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump_current.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
)

REQUIRED_MANIFEST_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-abi.py --self-test",
    "python3 scripts/zigux/check-phase3-abi.py",
    "zig build phase3-abi-core-packet --build-file zigux/tests/build.zig",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
)

ABI_LAYOUT_STRUCTS = (
    ("zigux_boundary_header", "BoundaryHeader", ABI_BINDINGS_PATH),
    ("zigux_export_status", "ExportStatus", ABI_BINDINGS_PATH),
    ("zigux_notifier_chain_priority_increase", "ChainPriorityIncrease", ABI_BINDINGS_PATH),
    ("zigux_interop_policy", "InteropPolicy", ABI_BINDINGS_PATH),
    ("zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view", "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView", ABI_BINDINGS_PATH),
    ("zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary", "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary", ABI_BINDINGS_PATH),
    ("zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view", "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView", ABI_BINDINGS_PATH),
    ("zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary", "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary", ABI_BINDINGS_PATH),
    ("zigux_notifier_block", "NotifierBlock", NOTIFIER_BINDINGS_PATH),
    ("zigux_list_head", "ListHead", NOTIFIER_BINDINGS_PATH),
    ("zigux_hlist_head", "HListHead", NOTIFIER_BINDINGS_PATH),
    ("zigux_hlist_node", "HListNode", NOTIFIER_BINDINGS_PATH),
)

C_TO_ZIG_TYPE_MAP = {
    "uint8_t": "u8",
    "uint16_t": "u16",
    "uint32_t": "u32",
    "int32_t": "i32",
    "size_t": "usize",
    "uintptr_t": "usize",
}

SELF_TEST_HEADER = """\
#define ZIGUX_ABI_VERSION 1U
#define ZIGUX_FACILITY_KERNEL 1U
#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U
typedef struct zigux_boundary_header {
    uint32_t size;
    uint16_t abi_version;
    uint16_t flags;
} zigux_boundary_header;
struct zigux_interop_policy {
    uint8_t panic_mode;
    uint8_t allocator_mode;
    uint8_t unsafe_scope;
    uint8_t reserved;
};
struct zigux_export_status {
    int32_t code;
    uint16_t facility;
    uint16_t flags;
};
typedef struct zigux_notifier_chain_priority_increase {
    size_t previous_index;
    size_t current_index;
    int32_t previous_priority;
    int32_t current_priority;
} zigux_notifier_chain_priority_increase;
struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {
    uint32_t ack_window;
    uint32_t delivery_window;
    uint32_t status;
};
struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {
    uint32_t applied;
    uint32_t skipped;
    uint32_t delivered;
};
struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view {
    uint32_t budget;
    uint32_t window;
    uint32_t flags;
};
struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary {
    uint32_t attempted;
    uint32_t applied;
    uint32_t skipped;
};
struct zigux_notifier_block {
    uintptr_t notifier_call;
    uintptr_t next;
    int32_t priority;
};
struct zigux_list_head {
    uintptr_t next;
    uintptr_t prev;
};
struct zigux_hlist_head {
    uintptr_t first;
};
struct zigux_hlist_node {
    uintptr_t next;
    uintptr_t pprev;
};
static inline int zigux_notifier_chain_has_nonincreasing_priority(
    const struct zigux_notifier_block *head)
{
    return head != 0;
}
static inline int zigux_notifier_first_chain_priority_increase(
    const struct zigux_notifier_block *head,
    zigux_notifier_chain_priority_increase *out)
{
    return head != 0 && out != 0;
}
static inline int zigux_list_has_consistent_backlinks(
    const struct zigux_list_head *head)
{
    return head != 0;
}
static inline int zigux_hlist_has_consistent_prev_links(
    const struct zigux_hlist_head *head)
{
    return head != 0;
}
static inline zigux_boundary_header zigux_default_header(uint16_t flags)
{
    zigux_boundary_header header = { .size = 8u, .abi_version = 1u, .flags = flags };
    return header;
}
static inline zigux_boundary_header zigux_compatible_header(
    uint32_t size,
    uint16_t flags)
{
    zigux_boundary_header header = zigux_default_header(flags);
    header.size = size;
    return header;
}
static inline int zigux_abi_version_is_current(uint16_t abi_version)
{
    return abi_version == (uint16_t)ZIGUX_ABI_VERSION;
}
static inline int zigux_header_is_canonical(zigux_boundary_header header)
{
    return header.size == 8u &&
        zigux_abi_version_is_current(header.abi_version);
}
static inline int zigux_header_is_compatible(zigux_boundary_header header)
{
    return header.size >= 8u &&
        zigux_abi_version_is_current(header.abi_version);
}
static inline int zigux_header_extends_boundary(zigux_boundary_header header)
{
    return zigux_header_is_compatible(header) &&
        !zigux_header_is_canonical(header);
}
static inline uint32_t zigux_header_requested_extra_bytes(
    zigux_boundary_header header)
{
    if (!zigux_header_extends_boundary(header))
        return 0u;
    return header.size - 8u;
}
static inline zigux_boundary_header zigux_header_canonicalize(
    zigux_boundary_header header)
{
    header.size = 8u;
    header.abi_version = (uint16_t)ZIGUX_ABI_VERSION;
    return header;
}
static inline struct zigux_interop_policy zigux_default_interop_policy(void)
{
    struct zigux_interop_policy policy = {
        .panic_mode = 0u,
        .allocator_mode = 0u,
        .unsafe_scope = 0u,
        .reserved = 0u,
    };
    return policy;
}
static inline struct zigux_export_status zigux_make_status(
    int32_t code,
    uint16_t facility)
{
    struct zigux_export_status status = {
        .code = code,
        .facility = facility,
        .flags = (uint16_t)(code < 0 ? 1u : 0u),
    };
    return status;
}
static inline struct zigux_export_status zigux_ok_status(uint16_t facility)
{
    return zigux_make_status(0, facility);
}
static inline int zigux_export_status_ok(struct zigux_export_status status)
{
    return status.flags == 0;
}
"""

SELF_TEST_BINDINGS = """\
pub const ABI_VERSION: u16 = 1;
pub const FACILITY_KERNEL: u16 = 1;
pub const UNSAFE_RAW_POINTER_BRIDGE: u8 = 2;
pub const BoundaryHeader = extern struct {
    size: u32,
    abi_version: u16,
    flags: u16,
};
pub const ExportStatus = extern struct {
    code: i32,
    facility: u16,
    flags: u16,
};
pub const InteropPolicy = extern struct {
    panic_mode: u8,
    allocator_mode: u8,
    unsafe_scope: u8,
    reserved: u8,
};
pub const Facility = enum(u16) {
    kernel = FACILITY_KERNEL,
};
pub const PanicMode = enum(u8) {
    abort = 0,
};
pub const AllocatorMode = enum(u8) {
    caller_provided = 0,
};
pub const UnsafeScope = enum(u8) {
    none = 0,
};
pub const ChainPriorityIncrease = extern struct {
    previous_index: usize,
    current_index: usize,
    previous_priority: i32,
    current_priority: i32,
};
pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView = extern struct {
    ack_window: u32,
    delivery_window: u32,
    status: u32,
};
pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary = extern struct {
    applied: u32,
    skipped: u32,
    delivered: u32,
};
pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView = extern struct {
    budget: u32,
    window: u32,
    flags: u32,
};
pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary = extern struct {
    attempted: u32,
    applied: u32,
    skipped: u32,
};
pub const NotifierBlock = notifier_abi.NotifierBlock;
pub const ListHead = notifier_abi.ListHead;
pub const HListHead = notifier_abi.HListHead;
pub const HListNode = notifier_abi.HListNode;
pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {
    _ = head;
    return true;
}
pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease {
    _ = head;
    return null;
}
pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {
    _ = head;
    return true;
}
pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {
    _ = head;
    return true;
}
pub fn defaultHeader(flags: u16) BoundaryHeader {
    return .{ .size = @sizeOf(BoundaryHeader), .abi_version = ABI_VERSION, .flags = flags };
}
pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader {
    var header = defaultHeader(flags);
    header.size = size;
    return header;
}
pub fn headerHasCurrentAbiVersion(abi_version: u16) bool {
    return abi_version == ABI_VERSION;
}
pub fn headerIsCanonical(header: BoundaryHeader) bool {
    return header.size == @sizeOf(BoundaryHeader) and headerHasCurrentAbiVersion(header.abi_version);
}
pub fn headerIsCompatible(header: BoundaryHeader) bool {
    return header.size >= @sizeOf(BoundaryHeader) and headerHasCurrentAbiVersion(header.abi_version);
}
pub fn extendsBoundary(header: BoundaryHeader) bool {
    return headerIsCompatible(header) and !headerIsCanonical(header);
}
pub fn requestedExtraBytes(header: BoundaryHeader) u32 {
    if (!extendsBoundary(header)) return 0;
    return header.size - @as(u32, @sizeOf(BoundaryHeader));
}
pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {
    var canonical = header;
    canonical.size = @sizeOf(BoundaryHeader);
    canonical.abi_version = ABI_VERSION;
    return canonical;
}
pub fn defaultInteropPolicy() InteropPolicy {
    return .{ .panic_mode = @intFromEnum(PanicMode.abort), .allocator_mode = @intFromEnum(AllocatorMode.caller_provided), .unsafe_scope = @intFromEnum(UnsafeScope.none), .reserved = 0 };
}
pub fn makeStatus(code: i32, facility: Facility) ExportStatus {
    return .{ .code = code, .facility = @intFromEnum(facility), .flags = if (code < 0) 1 else 0 };
}
pub fn okStatus(facility: Facility) ExportStatus {
    return makeStatus(0, facility);
}
pub fn statusIsOk(status: ExportStatus) bool {
    return status.flags == 0;
}
"""

SELF_TEST_NOTIFIER_BINDINGS = """\
pub const NotifierBlock = extern struct {
    notifier_call: usize,
    next: usize,
    priority: i32,
};
pub const NotifierChainPriorityIncrease = extern struct {
    previous_index: usize,
    current_index: usize,
    previous_priority: i32,
    current_priority: i32,
};
pub const ListHead = extern struct {
    next: usize,
    prev: usize,
};
pub const HListHead = extern struct {
    first: usize,
};
pub const HListNode = extern struct {
    next: usize,
    pprev: usize,
};
pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {
    _ = head;
    return true;
}
pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?NotifierChainPriorityIncrease {
    _ = head;
    return null;
}
pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {
    _ = head;
    return true;
}
pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {
    _ = head;
    return true;
}
"""

SELF_TEST_CHECKER = """\
ABI_SLICE_NOTE = Path("Documentation/zigux/phase3-abi-slice.md")
ABI_HEADER = Path("include/zigux/abi.h")
BINDING_ABI = Path("zigux/bindings/abi.zig")
EXPORT_SHIM = Path("zigux/kernel/export_shim.zig")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

def validate_repo(repo_root: Path) -> list[str]:
    return []

print("PHASE3_ABI_CHECK_SELF_TEST=pass")
"""

SELF_TEST_CATALOG = """\
PHASE3_CATALOG_PHASE = "Phase 3"
PHASE3_CATALOG_SCOPE = "abi-runtime"

def build_catalog(repo_root: Path) -> dict[str, object]:
    return {}

print("PHASE3_CATALOG_SELF_TEST=pass")
"""

SELF_TEST_BUILD = """\
const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);
const phase3_abi_dump = addPhase3AbiDump(b, target, optimize);
const phase3_abi_core_step = b.step(
    "phase3-abi-core-packet",
    "Run the shared Phase 3 ABI core packet from zigux/tests",
);
phase3_abi_core_step.dependOn(&phase3_abi_core_packet.step);
const root_module = b.createModule(.{
    .root_source_file = b.path("phase3_abi.zig"),
});
const dump_module = b.createModule(.{
    .root_source_file = b.path("phase3_abi_dump_current.zig"),
});
const phase3_dump_step = b.step(
    "phase3-dump",
    "Dump the current shared Phase 3 ABI snapshot from zigux/tests",
);
phase3_dump_step.dependOn(&phase3_abi_dump.step);
"""

SELF_TEST_ABI_TEST = """\
test "phase3 abi keeps shared layout assertions wired into the replay" {
    try layout_assert.assertPublishedAbiLayouts();
}
test "phase3 abi keeps export shim compatibility and status helpers reviewable" {
}
test "phase3 abi keeps version and dev_t relays explicit" {
}
test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {
}
test "phase3 abi keeps byte-level policy relays aligned with published ABI constants" {
}
"""

SELF_TEST_EXPORT_UAPI_LAYOUT = """\
test "export and uapi dev_t layouts stay aligned" {
}
test "export and uapi version layouts stay aligned" {
}
test "export shim relays version compatibility without widening the boundary" {
}
test "export shim reuses the canonical boundary header contract" {
}
test "export shim mirrors boundary header predicate helpers" {
}
"""

SELF_TEST_EXPORT_UAPI_LAYOUT_BUILD = """\
const uapi_dev_t = b.createModule(.{
    .root_source_file = b.path("../uapi/dev_t.zig"),
});
const uapi_version = b.createModule(.{
    .root_source_file = b.path("../uapi/version.zig"),
});
const export_shim = b.createModule(.{
    .root_source_file = b.path("../kernel/export_shim.zig"),
});
const root_module = b.createModule(.{
    .root_source_file = b.path("phase3_export_uapi_layout.zig"),
});
const test_step = b.step(
    "phase3-export-uapi-layout-test",
    "Run the Phase 3 export/UAPI layout replay",
);
"""

SELF_TEST_MANIFEST = json.dumps(
    {
        "phase": "Phase 3",
        "lane": "abi-runtime",
        "slug": "phase3-abi-packet",
        "status": "shared_abi_and_header_family_binding_surface_present",
        "scope": "shared ABI bindings, header-family follow-through, notifier layouts, export-status layout, and header-compatibility replay",
        "packet_files": list(REQUIRED_MANIFEST_PACKET_FILES),
        "replay_routes": list(REQUIRED_MANIFEST_REPLAY_ROUTES),
        "repo_reality_gaps": [],
        "next_safe_step": "keep the shared ABI packet bounded to manifest-backed header-family parity, dump-route reviewability, and directly coupled header-to-binding checks before widening into later Phase 3 catalog or export/UAPI survey work",
    },
    indent=2,
) + "\n"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _abi_header_constant_names(text: str) -> set[str]:
    return set(re.findall(r"^\s*#define\s+ZIGUX_([A-Z0-9_]+)\b", text, flags=re.MULTILINE))


def _abi_binding_constant_names(text: str) -> set[str]:
    return set(re.findall(r"^\s*pub const\s+([A-Z0-9_]+)\s*:", text, flags=re.MULTILINE))


def _parse_c_struct_fields(text: str) -> dict[str, list[tuple[str, str]]]:
    structs: dict[str, list[tuple[str, str]]] = {}
    for match in re.finditer(r"(?:typedef\s+)?struct\s+([a-z0-9_]+)\s*\{(?P<body>.*?)\}\s*(?:[a-z0-9_]+)?\s*;", text, flags=re.DOTALL):
        fields = [
            (field_name, field_type)
            for field_type, field_name in re.findall(r"^\s*([a-z0-9_]+)\s+([a-z0-9_]+)\s*;$", match.group("body"), flags=re.MULTILINE)
        ]
        structs[match.group(1)] = fields
    return structs


def _parse_zig_extern_struct_fields(text: str) -> dict[str, list[tuple[str, str]]]:
    structs: dict[str, list[tuple[str, str]]] = {}
    for match in re.finditer(r"pub const\s+([A-Za-z0-9_]+)\s*=\s*extern struct\s*\{(?P<body>.*?)\};", text, flags=re.DOTALL):
        structs[match.group(1)] = re.findall(r"^\s*([A-Za-z0-9_]+)\s*:\s*([A-Za-z0-9_]+)\s*,$", match.group("body"), flags=re.MULTILINE)
    return structs


def _validate_layout_structs(header_text: str, zig_texts: dict[Path, str]) -> list[str]:
    issues: list[str] = []
    c_structs = _parse_c_struct_fields(header_text)
    zig_structs_by_path = {path: _parse_zig_extern_struct_fields(text) for path, text in zig_texts.items() if text is not None}
    for c_name, zig_name, zig_path in ABI_LAYOUT_STRUCTS:
        c_fields = c_structs.get(c_name)
        if c_fields is None:
            issues.append(f"missing ABI header struct for layout comparison: {c_name}")
            continue
        zig_fields = zig_structs_by_path.get(zig_path, {}).get(zig_name)
        if zig_fields is None:
            issues.append(f"missing ABI binding extern struct for layout comparison: {zig_name} in {zig_path.as_posix()}")
            continue
        expected_zig_fields = []
        for field_name, c_type in c_fields:
            zig_type = C_TO_ZIG_TYPE_MAP.get(c_type)
            if zig_type is None:
                issues.append(f"unsupported C field type in ABI header layout comparison: {c_name}.{field_name} uses {c_type}")
                expected_zig_fields = []
                break
            expected_zig_fields.append((field_name, zig_type))
        if expected_zig_fields and zig_fields != expected_zig_fields:
            issues.append(f"layout mismatch for {c_name} vs {zig_name}: header fields {expected_zig_fields!r}, binding fields {zig_fields!r}")
    return issues


def _validate_manifest(text: str) -> list[str]:
    issues: list[str] = []
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"invalid JSON in {ABI_MANIFEST_PATH.as_posix()}: {exc}"]

    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(f"phase3_abi_manifest.json wrong {field}: {actual!r} != {expected!r}")

    packet_files = manifest.get("packet_files")
    if not isinstance(packet_files, list):
        issues.append("phase3_abi_manifest.json packet_files is not a list")
    else:
        for required in REQUIRED_MANIFEST_PACKET_FILES:
            if required not in packet_files:
                issues.append(f"phase3_abi_manifest.json missing packet_files entry: {required}")

    replay_routes = manifest.get("replay_routes")
    if not isinstance(replay_routes, list):
        issues.append("phase3_abi_manifest.json replay_routes is not a list")
    else:
        for required in REQUIRED_MANIFEST_REPLAY_ROUTES:
            if required not in replay_routes:
                issues.append(f"phase3_abi_manifest.json missing replay route: {required}")

    repo_reality_gaps = manifest.get("repo_reality_gaps")
    if not isinstance(repo_reality_gaps, list):
        issues.append("phase3_abi_manifest.json repo_reality_gaps is not a list")
    return issues


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    texts: dict[Path, str] = {}

    for rel_path, markers in REQUIRED_SOURCE_MARKERS.items():
        path = repo_root / rel_path
        if not path.is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        text = _read(path)
        texts[rel_path] = text
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")

    header_text = texts.get(ABI_HEADER_PATH)
    bindings_text = texts.get(ABI_BINDINGS_PATH)
    if header_text is not None and bindings_text is not None:
        missing_binding_constants = sorted(_abi_header_constant_names(header_text) - _abi_binding_constant_names(bindings_text))
        for name in missing_binding_constants:
            issues.append(f"missing ABI binding constant for header define: ZIGUX_{name} -> {name}")
        issues.extend(_validate_layout_structs(header_text, {ABI_BINDINGS_PATH: bindings_text, NOTIFIER_BINDINGS_PATH: texts.get(NOTIFIER_BINDINGS_PATH)}))

    manifest_text = texts.get(ABI_MANIFEST_PATH)
    if manifest_text is not None:
        issues.extend(_validate_manifest(manifest_text))

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ABI_HEADER_PATH, SELF_TEST_HEADER)
        _write(root / ABI_BINDINGS_PATH, SELF_TEST_BINDINGS)
        _write(root / NOTIFIER_BINDINGS_PATH, SELF_TEST_NOTIFIER_BINDINGS)
        _write(root / ABI_CHECKER_PATH, SELF_TEST_CHECKER)
        _write(root / PHASE3_CATALOG_PATH, SELF_TEST_CATALOG)
        _write(root / TESTS_BUILD_PATH, SELF_TEST_BUILD)
        _write(root / ABI_TEST_PATH, SELF_TEST_ABI_TEST)
        _write(root / EXPORT_UAPI_LAYOUT_PATH, SELF_TEST_EXPORT_UAPI_LAYOUT)
        _write(root / EXPORT_UAPI_LAYOUT_BUILD_PATH, SELF_TEST_EXPORT_UAPI_LAYOUT_BUILD)
        _write(root / ABI_MANIFEST_PATH, SELF_TEST_MANIFEST)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        cases = [
            (ABI_CHECKER_PATH, 'EXPORT_SHIM = Path("zigux/kernel/export_shim.zig")\n', 'missing scripts/zigux/check-phase3-abi.py marker: EXPORT_SHIM = Path("zigux/kernel/export_shim.zig")'),
            (ABI_BINDINGS_PATH, 'pub const ABI_VERSION: u16 = 1;\n', 'missing ABI binding constant for header define: ZIGUX_ABI_VERSION -> ABI_VERSION'),
            (ABI_BINDINGS_PATH, '    facility: u16,\n    flags: u16,\n', 'layout mismatch for zigux_export_status vs ExportStatus:'),
            (NOTIFIER_BINDINGS_PATH, 'pub const ListHead = extern struct {\n', 'missing zigux/bindings/notifier_abi.zig marker: pub const ListHead = extern struct {'),
            (ABI_TEST_PATH, 'test "phase3 abi keeps byte-level policy relays aligned with published ABI constants" {\n', 'missing zigux/tests/phase3_abi.zig marker: test "phase3 abi keeps byte-level policy relays aligned with published ABI constants" {'),
        ]

        for rel_path, needle, expected in cases:
            replacement = '' if rel_path != ABI_BINDINGS_PATH or 'facility' not in needle else '    flags: u16,\n    facility: u16,\n'
            _write(root / rel_path, _read(root / rel_path).replace(needle, replacement, 1))
            issues = validate_repo(root)
            if not any(expected in issue for issue in issues):
                print("PHASE3_VALIDATION_SELF_TEST=fail")
                print(f"expected issue was not reported: {expected}")
                return 1
            _write(root / ABI_HEADER_PATH, SELF_TEST_HEADER)
            _write(root / ABI_BINDINGS_PATH, SELF_TEST_BINDINGS)
            _write(root / NOTIFIER_BINDINGS_PATH, SELF_TEST_NOTIFIER_BINDINGS)
            _write(root / ABI_CHECKER_PATH, SELF_TEST_CHECKER)
            _write(root / PHASE3_CATALOG_PATH, SELF_TEST_CATALOG)
            _write(root / TESTS_BUILD_PATH, SELF_TEST_BUILD)
            _write(root / ABI_TEST_PATH, SELF_TEST_ABI_TEST)
            _write(root / EXPORT_UAPI_LAYOUT_PATH, SELF_TEST_EXPORT_UAPI_LAYOUT)
            _write(root / EXPORT_UAPI_LAYOUT_BUILD_PATH, SELF_TEST_EXPORT_UAPI_LAYOUT_BUILD)
            _write(root / ABI_MANIFEST_PATH, SELF_TEST_MANIFEST)

        manifest = json.loads(_read(root / ABI_MANIFEST_PATH))
        manifest['replay_routes'].remove('zig build phase3-dump --build-file zigux/tests/build.zig')
        _write(root / ABI_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = 'phase3_abi_manifest.json missing replay route: zig build phase3-dump --build-file zigux/tests/build.zig'
        if expected not in issues:
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print(f"expected issue was not reported: {expected}")
            return 1

    print("PHASE3_VALIDATION_SELF_TEST=pass")
    print("PHASE3_VALIDATION_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current bounded Phase 3 shared ABI binding surface.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="repository root that contains include/zigux/, zigux/bindings/, scripts/zigux/, and zigux/tests/")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_VALIDATION=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_VALIDATION=pass")
    print("PHASE3_SCOPE=shared-abi-binding-layout-catalog-dump-and-export-uapi-layout-route-surface")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
