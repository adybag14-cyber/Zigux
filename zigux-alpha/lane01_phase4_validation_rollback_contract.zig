const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn section(title: []const u8, next_title: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, roadmap, title) orelse return error.MissingSection;
    const tail = roadmap[start..];
    const end = std.mem.indexOf(u8, tail, next_title) orelse return error.MissingNextSection;
    return tail[0..end];
}

test "Phase 4 keeps measurable reversible validation goal" {
    const phase4 = try section(
        "## Phase 4: Differential Validation and Rollback",
        "## Phase 5: Samples and Reference Patterns",
    );

    try requireContains(phase4, "Primary product goal:\n- make every future Zigux port measurable and reversible");
    try requireContains(phase4, "Required Zigux features:");
    try requireContains(phase4, "- `zigux/tests/` parity harnesses");
    try requireContains(phase4, "- perf baselines and thresholds");
    try requireContains(phase4, "- rollback ownership");
    try requireContains(phase4, "- lab and CI matrices");
    try requireContains(phase4, "- artifact-diff checks for host-side tools");

    try requireOrder(phase4, "Primary product goal:", "Primary Linux anchors:");
    try requireOrder(phase4, "Primary Linux anchors:", "Required Zigux features:");
    try requireOrder(phase4, "Required Zigux features:", "Recommended Zigux destinations:");
}

test "Phase 4 keeps Linux validation anchors and Zigux destinations paired" {
    const phase4 = try section(
        "## Phase 4: Differential Validation and Rollback",
        "## Phase 5: Samples and Reference Patterns",
    );

    try requireContains(phase4, "- `lib/atomic64_test.c`");
    try requireContains(phase4, "- `lib/test_bitmap.c`");
    try requireContains(phase4, "- `samples/kprobes/kprobe_example.c`");
    try requireContains(phase4, "- `samples/vfs/test-fsmount.c`");

    try requireContains(phase4, "- `zigux/tests/atomic64_diff.zig`");
    try requireContains(phase4, "- `zigux/tests/bitmap_diff.zig`");
    try requireContains(phase4, "- `samples/zigux/kprobe_example.zig`");
    try requireContains(phase4, "- `samples/zigux/test_fsmount.zig`");
    try requireContains(phase4, "- `scripts/zigux/` diff and layout tools");

    try requireOrder(phase4, "`lib/atomic64_test.c`", "`zigux/tests/atomic64_diff.zig`");
    try requireOrder(phase4, "`lib/test_bitmap.c`", "`zigux/tests/bitmap_diff.zig`");
}

test "Phase 4 stays between ABI substrate and sample patterns" {
    try requireOrder(
        roadmap,
        "## Phase 3: ABI and Interop Substrate",
        "## Phase 4: Differential Validation and Rollback",
    );
    try requireOrder(
        roadmap,
        "## Phase 4: Differential Validation and Rollback",
        "## Phase 5: Samples and Reference Patterns",
    );
}

test "Phase 4 preserves validation-first ZAR transfer boundary" {
    const phase4 = try section(
        "## Phase 4: Differential Validation and Rollback",
        "## Phase 5: Samples and Reference Patterns",
    );

    try requireContains(phase4, "Why ZAR matters here:");
    try requireContains(phase4, "This is the strongest area to port from ZAR");
    try requireContains(phase4, "current practice.");
    try requireContains(phase4, "ZAR already behaves like a validation-first system");
    try requireContains(phase4, "Zigux should inherit that immediately.");
    try std.testing.expect(std.mem.indexOf(u8, phase4, "Zigux should inherit ZAR code directly") == null);
}
