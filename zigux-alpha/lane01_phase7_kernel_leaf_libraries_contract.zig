const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const phase6_heading = "## Phase 6: Greenfield Leaf Helpers";
const phase7_heading = "## Phase 7: In-Kernel Leaf Libraries";
const phase8_heading = "## Phase 8: Userspace-Adjacent Tooling Expansion";

test "Phase 7 remains ordered between Phase 6 and Phase 8" {
    const phase6 = requireIndex(phase6_heading);
    const phase7 = requireIndex(phase7_heading);
    const phase8 = requireIndex(phase8_heading);

    try std.testing.expect(phase6 < phase7);
    try std.testing.expect(phase7 < phase8);
}

test "Phase 7 product goal stays runtime-helper focused" {
    const phase7 = phaseBody();

    try expectContains(phase7, "Primary product goal:");
    try expectContains(
        phase7,
        "- bring the first reusable runtime helper families into the product path",
    );
}

test "Phase 7 keeps the in-kernel leaf-library anchor roster" {
    const phase7 = phaseBody();

    try expectContains(phase7, "Primary Linux anchors:");
    try expectOrdered(phase7, &.{
        "- `lib/string_helpers.c`",
        "- `lib/cmdline.c`",
        "- `lib/argv_split.c`",
        "- `lib/rbtree.c`",
    });
}

test "Phase 7 keeps runtime-safe features and native destinations" {
    const phase7 = phaseBody();

    try expectContains(phase7, "Required Zigux features:");
    try expectOrdered(phase7, &.{
        "- runtime-safe leaf helpers",
        "- stronger ownership and pointer discipline",
        "- integration with validation substrate",
    });

    try expectContains(phase7, "Recommended Zigux destinations:");
    try expectOrdered(phase7, &.{
        "- `lib/string_helpers.zig`",
        "- `lib/cmdline.zig`",
        "- `lib/argv_split.zig`",
        "- `lib/rbtree.zig`",
    });
}

fn phaseBody() []const u8 {
    const start = requireIndex(phase7_heading);
    const end = requireIndex(phase8_heading);
    std.debug.assert(start < end);
    return roadmap[start..end];
}

fn requireIndex(needle: []const u8) usize {
    return std.mem.indexOf(u8, roadmap, needle) orelse
        @panic("required roadmap marker is missing");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var previous: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, haystack[previous..], needle) orelse {
            std.debug.print("missing ordered marker: {s}\n", .{needle});
            return error.MissingMarker;
        };
        previous += relative + needle.len;
    }
}
