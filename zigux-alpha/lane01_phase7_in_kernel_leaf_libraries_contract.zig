const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const phase6_heading = "## Phase 6: Greenfield Leaf Helpers";
const phase7_heading = "## Phase 7: In-Kernel Leaf Libraries";
const phase8_heading = "## Phase 8: Userspace-Adjacent Tooling Expansion";

const phase7_markers = [_][]const u8{
    "Primary product goal:\n- bring the first reusable runtime helper families into the product path",
    "Primary Linux anchors:\n- `lib/string_helpers.c`\n- `lib/cmdline.c`\n- `lib/argv_split.c`\n- `lib/rbtree.c`",
    "Required Zigux features:\n- runtime-safe leaf helpers\n- stronger ownership and pointer discipline\n- integration with validation substrate",
    "Recommended Zigux destinations:\n- `lib/string_helpers.zig`\n- `lib/cmdline.zig`\n- `lib/argv_split.zig`\n- `lib/rbtree.zig`",
};

fn markerIndex(haystack: []const u8, marker: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, marker) orelse error.MissingRoadmapMarker;
}

fn expectContains(marker: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, roadmap, marker) != null);
}

test "Phase 7 roadmap packet preserves runtime leaf-library purpose" {
    try expectContains("## Phase 7: In-Kernel Leaf Libraries");
    try expectContains("bring the first reusable runtime helper families into the product path");
    try expectContains("runtime-safe leaf helpers");
    try expectContains("stronger ownership and pointer discipline");
    try expectContains("integration with validation substrate");
}

test "Phase 7 roadmap packet preserves anchors and destinations" {
    try expectContains("`lib/string_helpers.c`");
    try expectContains("`lib/cmdline.c`");
    try expectContains("`lib/argv_split.c`");
    try expectContains("`lib/rbtree.c`");

    try expectContains("`lib/string_helpers.zig`");
    try expectContains("`lib/cmdline.zig`");
    try expectContains("`lib/argv_split.zig`");
    try expectContains("`lib/rbtree.zig`");
}

test "Phase 7 roadmap packet keeps grouped contract blocks intact" {
    for (phase7_markers) |marker| {
        try expectContains(marker);
    }
}

test "Phase 7 roadmap packet stays between Phase 6 and Phase 8" {
    const phase6 = try markerIndex(roadmap, phase6_heading);
    const phase7 = try markerIndex(roadmap, phase7_heading);
    const phase8 = try markerIndex(roadmap, phase8_heading);

    try testing.expect(phase6 < phase7);
    try testing.expect(phase7 < phase8);
}
