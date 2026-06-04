const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const linux_anchor_markers = [_][]const u8{
    "- `samples/kfifo/bytestream-example.c`",
    "- `samples/kobject/kobject-example.c`",
    "- `samples/kprobes/kretprobe_example.c`",
    "- `samples/trace_events/trace-events-sample.c`",
};

const required_feature_markers = [_][]const u8{
    "- side-by-side sample ports",
    "- ownership and lifetime examples",
    "- tracing examples",
    "- review checklist and contributor guide",
};

const destination_markers = [_][]const u8{
    "- `samples/zigux/`",
    "- `Documentation/zigux/`",
};

test "phase 5 roadmap packet keeps reviewable sample goal" {
    try expectContains("## Phase 5: Samples and Reference Patterns");
    try expectContains("Primary product goal:");
    try expectContains("- make approved Zigux idioms reviewable and repeatable");
}

test "phase 5 roadmap packet keeps sample anchors and required features" {
    try expectContains("Primary Linux anchors:");
    for (linux_anchor_markers) |marker| {
        try expectContains(marker);
    }

    try expectContains("Required Zigux features:");
    for (required_feature_markers) |marker| {
        try expectContains(marker);
    }
}

test "phase 5 roadmap packet keeps sample and documentation destinations" {
    try expectContains("Recommended Zigux destinations:");
    for (destination_markers) |marker| {
        try expectContains(marker);
    }
}

test "phase 5 roadmap packet stays after validation and before leaf helpers" {
    try expectOrder("## Phase 4: Differential Validation and Rollback", "## Phase 5: Samples and Reference Patterns");
    try expectOrder("## Phase 5: Samples and Reference Patterns", "## Phase 6: Greenfield Leaf Helpers");
    try expectOrder("- `scripts/zigux/` diff and layout tools", "- make approved Zigux idioms reviewable and repeatable");
    try expectOrder("- `Documentation/zigux/`", "## Phase 6: Greenfield Leaf Helpers");
}

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, roadmap, 1, needle));
}

fn expectOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}
