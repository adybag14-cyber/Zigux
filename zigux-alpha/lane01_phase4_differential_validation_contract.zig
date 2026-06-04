const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const linux_anchor_markers = [_][]const u8{
    "- `lib/atomic64_test.c`",
    "- `lib/test_bitmap.c`",
    "- `samples/kprobes/kprobe_example.c`",
    "- `samples/vfs/test-fsmount.c`",
};

const required_feature_markers = [_][]const u8{
    "- `zigux/tests/` parity harnesses",
    "- perf baselines and thresholds",
    "- rollback ownership",
    "- lab and CI matrices",
    "- artifact-diff checks for host-side tools",
};

const destination_markers = [_][]const u8{
    "- `zigux/tests/atomic64_diff.zig`",
    "- `zigux/tests/bitmap_diff.zig`",
    "- `samples/zigux/kprobe_example.zig`",
    "- `samples/zigux/test_fsmount.zig`",
    "- `scripts/zigux/` diff and layout tools",
};

test "phase 4 roadmap packet keeps measurable rollback goal" {
    try expectContains("## Phase 4: Differential Validation and Rollback");
    try expectContains("Primary product goal:");
    try expectContains("- make every future Zigux port measurable and reversible");
}

test "phase 4 roadmap packet keeps validation anchors and required gates" {
    try expectContains("Primary Linux anchors:");
    for (linux_anchor_markers) |marker| {
        try expectContains(marker);
    }

    try expectContains("Required Zigux features:");
    for (required_feature_markers) |marker| {
        try expectContains(marker);
    }
}

test "phase 4 roadmap packet keeps product destinations and ZAR validation handoff" {
    try expectContains("Recommended Zigux destinations:");
    for (destination_markers) |marker| {
        try expectContains(marker);
    }

    try expectContains("ZAR already behaves like a validation-first system");
    try expectContains("Zigux should inherit that immediately");
}

test "phase 4 roadmap packet stays between ABI substrate and samples phases" {
    try expectOrder("## Phase 3: ABI and Interop Substrate", "## Phase 4: Differential Validation and Rollback");
    try expectOrder("## Phase 4: Differential Validation and Rollback", "## Phase 5: Samples and Reference Patterns");
    try expectOrder("- narrow unsafe surface", "- make every future Zigux port measurable and reversible");
    try expectOrder("- `scripts/zigux/` diff and layout tools", "## Phase 5: Samples and Reference Patterns");
}

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, roadmap, 1, needle));
}

fn expectOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}
