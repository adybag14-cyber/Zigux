const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const linux_anchor_markers = [_][]const u8{
    "- `lib/base64.c`",
    "- `lib/bsearch.c`",
    "- `lib/checksum.c`",
    "- `lib/hexdump.c`",
};

const required_feature_markers = [_][]const u8{
    "- leaf helper portability",
    "- clear API parity",
    "- perf gates for math-sensitive helpers",
};

const destination_markers = [_][]const u8{
    "- `lib/base64.zig`",
    "- `lib/bsearch.zig`",
    "- `lib/checksum.zig`",
    "- `lib/hexdump.zig`",
};

test "phase 6 roadmap packet keeps low-risk helper goal" {
    try expectContains("## Phase 6: Greenfield Leaf Helpers");
    try expectContains("Primary product goal:");
    try expectContains("- allow low-risk new helper code in Zigux without taking runtime-core risk");
}

test "phase 6 roadmap packet keeps greenfield helper anchors and required features" {
    try expectContains("Primary Linux anchors:");
    for (linux_anchor_markers) |marker| {
        try expectContains(marker);
    }

    try expectContains("Required Zigux features:");
    for (required_feature_markers) |marker| {
        try expectContains(marker);
    }
}

test "phase 6 roadmap packet keeps lib helper destinations" {
    try expectContains("Recommended Zigux destinations:");
    for (destination_markers) |marker| {
        try expectContains(marker);
    }
}

test "phase 6 roadmap packet stays after samples and before in-kernel leaf libraries" {
    try expectOrder("## Phase 5: Samples and Reference Patterns", "## Phase 6: Greenfield Leaf Helpers");
    try expectOrder("## Phase 6: Greenfield Leaf Helpers", "## Phase 7: In-Kernel Leaf Libraries");
    try expectOrder("- `Documentation/zigux/`", "- allow low-risk new helper code in Zigux without taking runtime-core risk");
    try expectOrder("- `lib/hexdump.zig`", "## Phase 7: In-Kernel Leaf Libraries");
}

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, roadmap, 1, needle));
}

fn expectOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}
