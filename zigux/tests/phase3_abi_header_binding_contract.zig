const std = @import("std");

const max_source_size = 512 * 1024;

fn readSource(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(max_source_size),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.TestUnexpectedResult;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.TestUnexpectedResult;
    try std.testing.expect(earlier_index < later_index);
}

test "phase3 abi header keeps the exported skeleton families visible" {
    const abi_header = try readSource("include/zigux/abi.h");
    defer std.testing.allocator.free(abi_header);

    try expectContains(abi_header, "#include <stddef.h>");
    try expectContains(abi_header, "#include <stdint.h>");
    try expectBefore(abi_header, "#define ZIGUX_ABI_VERSION 1U", "typedef struct zigux_boundary_header");

    try expectContains(abi_header, "#define ZIGUX_FACILITY_KERNEL 1U");
    try expectContains(abi_header, "#define ZIGUX_FACILITY_HELPERS 2U");
    try expectContains(abi_header, "#define ZIGUX_FACILITY_DRIVERS 3U");
    try expectContains(abi_header, "#define ZIGUX_STATUS_FLAG_ERROR 1U");

    try expectContains(abi_header, "typedef struct zigux_boundary_header");
    try expectContains(abi_header, "struct zigux_export_status");
    try expectContains(abi_header, "struct zigux_interop_policy");
    try expectContains(abi_header, "typedef struct zigux_rbtree_root_view");
    try expectContains(abi_header, "struct zigux_notifier_block");
    try expectContains(abi_header, "struct zigux_list_head");
    try expectContains(abi_header, "struct zigux_hlist_head");
    try expectContains(abi_header, "struct zigux_hlist_node");
    try expectContains(abi_header, "typedef struct zigux_list_backlink_break");
    try expectContains(abi_header, "typedef struct zigux_hlist_prev_link_break");
}

test "phase3 abi header keeps C helper surfaces for boundary, policy, and links" {
    const abi_header = try readSource("include/zigux/abi.h");
    defer std.testing.allocator.free(abi_header);

    try expectContains(abi_header, "zigux_default_header(uint16_t flags)");
    try expectContains(abi_header, "zigux_compatible_header(");
    try expectContains(abi_header, "zigux_header_is_canonical(");
    try expectContains(abi_header, "zigux_header_is_compatible(");
    try expectContains(abi_header, "zigux_header_extends_boundary(");
    try expectContains(abi_header, "zigux_header_requested_extra_bytes(");
    try expectContains(abi_header, "zigux_header_canonicalize(");

    try expectContains(abi_header, "zigux_interop_policy_is_recognized(");
    try expectContains(abi_header, "zigux_rbtree_root_view_is_valid(");
    try expectContains(abi_header, "zigux_rbtree_root_view_canonicalize(");
    try expectContains(abi_header, "zigux_notifier_first_chain_priority_increase(");
    try expectContains(abi_header, "zigux_list_first_broken_backlink(");
    try expectContains(abi_header, "zigux_hlist_first_broken_prev_link(");
    try expectContains(abi_header, "zigux_export_status_has_known_facility(");
}

test "phase3 abi binding keeps Zig constants and layout mirrors explicit" {
    const abi_binding = try readSource("zigux/bindings/abi.zig");
    defer std.testing.allocator.free(abi_binding);

    try expectContains(abi_binding, "pub const ABI_VERSION: u16 = 1;");
    try expectContains(abi_binding, "pub const FACILITY_KERNEL: u16 = 1;");
    try expectContains(abi_binding, "pub const FACILITY_HELPERS: u16 = 2;");
    try expectContains(abi_binding, "pub const FACILITY_DRIVERS: u16 = 3;");
    try expectContains(abi_binding, "pub const STATUS_FLAG_ERROR: u16 = 1;");

    try expectContains(abi_binding, "pub const BoundaryHeader = extern struct");
    try expectContains(abi_binding, "pub const ExportStatus = extern struct");
    try expectContains(abi_binding, "pub const InteropPolicy = extern struct");
    try expectContains(abi_binding, "pub const RbtreeRootView = extern struct");
    try expectContains(abi_binding, "pub const NotifierBlock = notifier_abi.NotifierBlock;");
    try expectContains(abi_binding, "pub const ListHead = notifier_abi.ListHead;");
    try expectContains(abi_binding, "pub const HListHead = notifier_abi.HListHead;");
    try expectContains(abi_binding, "pub const HListNode = notifier_abi.HListNode;");
    try expectContains(abi_binding, "pub const ListBackLinkBreak = notifier_abi.ListBackLinkBreak;");
    try expectContains(abi_binding, "pub const HListPrevLinkBreak = notifier_abi.HListPrevLinkBreak;");

    try expectContains(abi_binding, "pub const boundary_header_size = @sizeOf(BoundaryHeader);");
    try expectContains(abi_binding, "pub const export_status_code_offset = @offsetOf(ExportStatus, \"code\");");
    try expectContains(abi_binding, "pub const interop_policy_reserved_offset = @offsetOf(InteropPolicy, \"reserved\");");
    try expectContains(abi_binding, "pub const rbtree_root_view_flags_offset = @offsetOf(RbtreeRootView, \"flags\");");
}

test "phase3 abi binding keeps relay helpers aligned with the header skeleton" {
    const abi_binding = try readSource("zigux/bindings/abi.zig");
    defer std.testing.allocator.free(abi_binding);

    try expectContains(abi_binding, "pub fn defaultHeader(flags: u16) BoundaryHeader");
    try expectContains(abi_binding, "pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader");
    try expectContains(abi_binding, "pub fn headerIsCanonical(header: BoundaryHeader) bool");
    try expectContains(abi_binding, "pub fn headerIsCompatible(header: BoundaryHeader) bool");
    try expectContains(abi_binding, "pub fn extendsBoundary(header: BoundaryHeader) bool");
    try expectContains(abi_binding, "pub fn requestedExtraBytes(header: BoundaryHeader) u32");
    try expectContains(abi_binding, "pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader");

    try expectContains(abi_binding, "pub fn defaultInteropPolicy() InteropPolicy");
    try expectContains(abi_binding, "pub fn interopPolicyIsRecognized(policy: InteropPolicy) bool");
    try expectContains(abi_binding, "pub fn canonicalizeRbtreeRootView(view: RbtreeRootView) RbtreeRootView");
    try expectContains(abi_binding, "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock)");
    try expectContains(abi_binding, "pub fn firstBrokenBacklink(head: ?*const ListHead)");
    try expectContains(abi_binding, "pub fn firstBrokenPrevLink(head: ?*const HListHead)");
    try expectContains(abi_binding, "pub fn statusHasKnownFacility(status: ExportStatus) bool");
}
