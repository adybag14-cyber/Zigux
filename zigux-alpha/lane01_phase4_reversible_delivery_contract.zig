const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn phase4Section() ![]const u8 {
    @setEvalBranchQuota(20_000);
    const start_marker = "## Phase 4: Differential Validation and Rollback";
    const end_marker = "## Phase 5: Samples and Reference Patterns";
    const start = std.mem.indexOf(u8, roadmap, start_marker) orelse return error.MissingPhase4Heading;
    const end = std.mem.indexOfPos(u8, roadmap, start, end_marker) orelse return error.MissingPhase5Heading;
    return roadmap[start..end];
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "phase4 validation and rollback goal stays explicit" {
    const phase4 = try phase4Section();
    try requireContains(phase4, "## Phase 4: Differential Validation and Rollback");
    try requireContains(phase4, "Primary product goal:");
    try requireContains(phase4, "- make every future Zigux port measurable and reversible");
}

test "phase4 keeps differential validation anchors explicit" {
    const phase4 = try phase4Section();
    try requireContains(phase4, "Primary Linux anchors:");
    try requireContains(phase4, "- `lib/atomic64_test.c`");
    try requireContains(phase4, "- `lib/test_bitmap.c`");
    try requireContains(phase4, "- `samples/kprobes/kprobe_example.c`");
    try requireContains(phase4, "- `samples/vfs/test-fsmount.c`");
}

test "phase4 keeps required reversible delivery features explicit" {
    const phase4 = try phase4Section();
    try requireContains(phase4, "Required Zigux features:");
    try requireContains(phase4, "- `zigux/tests/` parity harnesses");
    try requireContains(phase4, "- perf baselines and thresholds");
    try requireContains(phase4, "- rollback ownership");
    try requireContains(phase4, "- lab and CI matrices");
    try requireContains(phase4, "- artifact-diff checks for host-side tools");
}

test "phase4 destinations and neighboring phase order stay bounded" {
    const phase4 = try phase4Section();
    try requireContains(phase4, "Recommended Zigux destinations:");
    try requireContains(phase4, "- `zigux/tests/atomic64_diff.zig`");
    try requireContains(phase4, "- `zigux/tests/bitmap_diff.zig`");
    try requireContains(phase4, "- `samples/zigux/kprobe_example.zig`");
    try requireContains(phase4, "- `samples/zigux/test_fsmount.zig`");
    try requireContains(phase4, "- `scripts/zigux/` diff and layout tools");

    try requireOrdered(
        roadmap,
        "## Phase 3: ABI and Interop Substrate",
        "## Phase 4: Differential Validation and Rollback",
    );
    try requireOrdered(
        roadmap,
        "## Phase 4: Differential Validation and Rollback",
        "## Phase 5: Samples and Reference Patterns",
    );
}

test "phase4 slice does not borrow adjacent phase evidence" {
    const phase4 = try phase4Section();
    try requireNotContains(phase4, "- explicit export shims");
    try requireNotContains(phase4, "- side-by-side sample ports");
}
