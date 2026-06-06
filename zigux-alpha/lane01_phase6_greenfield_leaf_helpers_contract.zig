const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
const phase6_heading = "## Phase 6: Greenfield Leaf Helpers";
const phase7_heading = "## Phase 7: In-Kernel Leaf Libraries";

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
    const phase6 = try phase6Section();

    try expectContains(phase6, phase6_heading);
    try expectContains(phase6, "Primary product goal:");
    try expectContains(phase6, "- allow low-risk new helper code in Zigux without taking runtime-core risk");
}

test "phase 6 roadmap packet keeps greenfield helper anchors and required features" {
    const phase6 = try phase6Section();

    try expectContains(phase6, "Primary Linux anchors:");
    for (linux_anchor_markers) |marker| {
        try expectContains(phase6, marker);
    }

    try expectContains(phase6, "Required Zigux features:");
    for (required_feature_markers) |marker| {
        try expectContains(phase6, marker);
    }
}

test "phase 6 roadmap packet keeps lib helper destinations" {
    const phase6 = try phase6Section();

    try expectContains(phase6, "Recommended Zigux destinations:");
    for (destination_markers) |marker| {
        try expectContains(phase6, marker);
    }
}

test "phase 6 roadmap packet stays after samples and before in-kernel leaf libraries" {
    try expectOrder("## Phase 5: Samples and Reference Patterns", phase6_heading);
    try expectOrder(phase6_heading, phase7_heading);
    try expectOrder("- `Documentation/zigux/`", "- allow low-risk new helper code in Zigux without taking runtime-core risk");
    try expectOrder("- `lib/hexdump.zig`", phase7_heading);
}

test "phase 6 section stays separate from adjacent runtime leaf library packet" {
    const phase6 = try phase6Section();

    try expectNotContains(phase6, "## Phase 5: Samples and Reference Patterns");
    try expectNotContains(phase6, phase7_heading);
    try expectNotContains(phase6, "- runtime-safe leaf helpers");
    try expectNotContains(phase6, "- stronger ownership and pointer discipline");
    try expectNotContains(phase6, "- `lib/string_helpers.zig`");
}

fn phase6Section() ![]const u8 {
    const start = std.mem.indexOf(u8, roadmap, phase6_heading) orelse return error.MissingPhase6Heading;
    const end = std.mem.indexOfPos(u8, roadmap, start + phase6_heading.len, phase7_heading) orelse return error.MissingPhase7Heading;
    try std.testing.expect(start < end);
    return roadmap[start..end];
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, haystack, 1, needle));
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(!std.mem.containsAtLeast(u8, haystack, 1, needle));
}

fn expectOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}
