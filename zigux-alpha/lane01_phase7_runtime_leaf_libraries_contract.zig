const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn sliceBetween(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse return error.MissingStartMarker;
    const after_start = start + start_marker.len;
    const end_rel = std.mem.indexOf(u8, haystack[after_start..], end_marker) orelse return error.MissingEndMarker;
    return haystack[start .. after_start + end_rel];
}

const phase7 = blk: {
    @setEvalBranchQuota(10_000);
    break :blk sliceBetween(
        roadmap,
        "## Phase 7: In-Kernel Leaf Libraries",
        "## Phase 8: Userspace-Adjacent Tooling Expansion",
    ) catch @compileError("roadmap Phase 7 packet is missing or unsliceable");
};

test "Phase 7 packet keeps the runtime leaf-library goal" {
    try expectContains(phase7, "## Phase 7: In-Kernel Leaf Libraries");
    try expectContains(phase7, "Primary product goal:");
    try expectContains(phase7, "bring the first reusable runtime helper families into the product path");
    try expectContains(phase7, "runtime-safe leaf helpers");
    try expectContains(phase7, "stronger ownership and pointer discipline");
    try expectContains(phase7, "integration with validation substrate");
}

test "Phase 7 packet keeps the in-kernel helper anchor roster" {
    try expectContains(phase7, "Primary Linux anchors:");
    try expectContains(phase7, "`lib/string_helpers.c`");
    try expectContains(phase7, "`lib/cmdline.c`");
    try expectContains(phase7, "`lib/argv_split.c`");
    try expectContains(phase7, "`lib/rbtree.c`");
}

test "Phase 7 packet keeps approved destinations in native lib paths" {
    try expectContains(phase7, "Recommended Zigux destinations:");
    try expectContains(phase7, "`lib/string_helpers.zig`");
    try expectContains(phase7, "`lib/cmdline.zig`");
    try expectContains(phase7, "`lib/argv_split.zig`");
    try expectContains(phase7, "`lib/rbtree.zig`");
    try expectNotContains(phase7, "`zigux-alpha/ports/");
}

test "Phase 7 packet remains between Phase 6 and Phase 8" {
    const phase6_pos = std.mem.indexOf(u8, roadmap, "## Phase 6: Greenfield Leaf Helpers") orelse return error.MissingPhase6;
    const phase7_pos = std.mem.indexOf(u8, roadmap, "## Phase 7: In-Kernel Leaf Libraries") orelse return error.MissingPhase7;
    const phase8_pos = std.mem.indexOf(u8, roadmap, "## Phase 8: Userspace-Adjacent Tooling Expansion") orelse return error.MissingPhase8;

    try testing.expect(phase6_pos < phase7_pos);
    try testing.expect(phase7_pos < phase8_pos);
    try expectNotContains(phase7, "`tools/lib/subcmd/exec-cmd.c`");
    try expectNotContains(phase7, "`samples/zigux/runtime_*`");
}
