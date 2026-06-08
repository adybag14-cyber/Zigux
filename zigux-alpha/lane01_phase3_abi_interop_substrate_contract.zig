const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn phase3Section() ![]const u8 {
    const start_marker = "## Phase 3: ABI and Interop Substrate";
    const end_marker = "## Phase 4: Differential Validation and Rollback";
    const start = std.mem.indexOf(u8, roadmap, start_marker) orelse return error.MissingPhase3Start;
    const after_start = start + start_marker.len;
    const relative_end = std.mem.indexOf(u8, roadmap[after_start..], end_marker) orelse return error.MissingPhase4Start;
    return roadmap[start .. after_start + relative_end];
}

test "phase3 keeps the permanent boundary goal explicit" {
    const section = try phase3Section();

    try requireContains(section, "## Phase 3: ABI and Interop Substrate");
    try requireContains(section, "Primary product goal:");
    try requireContains(section, "- define the permanent C/Zigux boundary");
}

test "phase3 keeps abi and interop anchors explicit" {
    const section = try phase3Section();

    try requireContains(section, "Primary Linux anchors:");
    try requireContains(section, "- `rust/exports.c`");
    try requireContains(section, "- `lib/bitmap.c`");
    try requireContains(section, "- `lib/rbtree.c`");
    try requireContains(section, "- `lib/cpumask.c`");
}

test "phase3 keeps substrate requirements explicit" {
    const section = try phase3Section();

    try requireContains(section, "Required Zigux features:");
    try requireContains(section, "- explicit export shims");
    try requireContains(section, "- generated or curated bindings");
    try requireContains(section, "- layout assertions");
    try requireContains(section, "- explicit panic policy");
    try requireContains(section, "- explicit allocator policy");
    try requireContains(section, "- approved atomic, barrier, and MMIO wrappers");
    try requireContains(section, "- narrow unsafe surface");
}

test "phase3 keeps support-root destinations explicit" {
    const section = try phase3Section();

    try requireContains(section, "Recommended Zigux destinations:");
    try requireContains(section, "- `zigux/kernel/`");
    try requireContains(section, "- `zigux/helpers/`");
    try requireContains(section, "- `zigux/bindings/`");
    try requireContains(section, "- `zigux/uapi/`");
    try requireContains(section, "- `zigux/unsafe/`");
    try requireContains(section, "- `include/linux/zigux.h`");
    try requireContains(section, "- `include/zigux/abi.h`");
}

test "phase3 stays ordered and distinct from adjacent phase4 validation packet" {
    const section = try phase3Section();

    try requireContains(section, "Why ZAR matters here:");
    try requireContains(section, "ABI gating, and explicit failure-code discipline");
    try requireMissing(section, "zigux/tests/atomic64_diff.zig");

    try requireOrdered("## Phase 2: Toolchain and Kbuild Enablement", "## Phase 3: ABI and Interop Substrate");
    try requireOrdered("## Phase 3: ABI and Interop Substrate", "## Phase 4: Differential Validation and Rollback");
}
