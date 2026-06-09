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
    const phase6 = try phase6Section();

    try expectSliceContains(phase6, "Primary Linux anchors:");
    for (linux_anchor_markers) |marker| {
        try expectSliceContains(phase6, marker);
    }

    try expectSliceContains(phase6, "Required Zigux features:");
    for (required_feature_markers) |marker| {
        try expectSliceContains(phase6, marker);
    }
}

test "phase 6 roadmap packet keeps lib helper destinations" {
    const phase6 = try phase6Section();

    try expectSliceContains(phase6, "Recommended Zigux destinations:");
    for (destination_markers) |marker| {
        try expectSliceContains(phase6, marker);
    }
}

test "phase 6 roadmap packet stays after samples and before in-kernel leaf libraries" {
    try expectOrder("## Phase 5: Samples and Reference Patterns", "## Phase 6: Greenfield Leaf Helpers");
    try expectOrder("## Phase 6: Greenfield Leaf Helpers", "## Phase 7: In-Kernel Leaf Libraries");
    try expectOrder("- `Documentation/zigux/`", "- allow low-risk new helper code in Zigux without taking runtime-core risk");
    try expectOrder("- `lib/hexdump.zig`", "## Phase 7: In-Kernel Leaf Libraries");
}

test "phase 6 section does not borrow phase 7 runtime-library markers" {
    const phase6 = try phase6Section();

    try expectSliceExcludes(phase6, "runtime-safe leaf helpers");
    try expectSliceExcludes(phase6, "- `lib/string_helpers.c`");
    try expectSliceExcludes(phase6, "- `lib/string_helpers.zig`");
}

fn phase6Section() ![]const u8 {
    const start_marker = "## Phase 6: Greenfield Leaf Helpers";
    const end_marker = "## Phase 7: In-Kernel Leaf Libraries";
    const start = std.mem.indexOf(u8, roadmap, start_marker) orelse return error.MissingPhase6Marker;
    const after_start = roadmap[start..];
    const end = std.mem.indexOf(u8, after_start, end_marker) orelse return error.MissingPhase7Marker;
    return after_start[0..end];
}

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, roadmap, 1, needle));
}

fn expectSliceContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, haystack, 1, needle));
}

fn expectSliceExcludes(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(!std.mem.containsAtLeast(u8, haystack, 1, needle));
}

fn expectOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}
