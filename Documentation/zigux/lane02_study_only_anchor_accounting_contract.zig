const std = @import("std");

const freeze_map = @embedFile("freeze-map.md");
const study_only_accounting = @embedFile("phase15-study-only-anchor-accounting.md");
const handoff_next_steps = @embedFile("phase15-handoff-next-steps-survey.md");
const shared_summary_gap = @embedFile("phase15-shared-summary-gap.md");

const freeze_in_c_anchors = [_][]const u8{
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
};

const study_only_anchors = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var seen: usize = 0;
    var start: usize = 0;

    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        seen += 1;
        start = index + needle.len;
    }

    try std.testing.expectEqual(expected, seen);
}

fn expectBulletOnce(haystack: []const u8, anchor: []const u8) !void {
    var buffer: [128]u8 = undefined;
    const needle = try std.fmt.bufPrint(&buffer, "- `{s}`", .{anchor});
    try expectCount(haystack, needle, 1);
}

test "freeze map keeps four freeze-in-C anchors and two study-only anchors distinct" {
    try expectContains(freeze_map, "## Freeze In C Initially");
    try expectContains(freeze_map, "## Study / Boundary Only");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "study-only anchor maintenance must stay aligned");

    for (freeze_in_c_anchors) |anchor| {
        try expectBulletOnce(freeze_map, anchor);
        try expectContains(freeze_map, anchor);
    }

    for (study_only_anchors) |anchor| {
        try expectBulletOnce(freeze_map, anchor);
        try expectContains(freeze_map, anchor);
    }
}

test "study-only accounting note remains inventory-only and blocks approval drift" {
    try expectContains(study_only_accounting, "PHASE15_STATUS=study_only_accounting_slice_landed");
    try expectContains(study_only_accounting, "study-only anchors tracked outside this scorecard: 2");
    try expectContains(study_only_accounting, "no Architecture Council approval is currently recorded for a deep-core status change");
    try expectContains(study_only_accounting, "this note is an inventory and handoff surface, not an approval record");

    for (study_only_anchors) |anchor| {
        try expectContains(study_only_accounting, anchor);
        try expectContains(study_only_accounting, "posture: `study_only`");
    }

    try expectNotContains(study_only_accounting, "PHASE15_STATUS=approved_for_delivery");
    try expectNotContains(study_only_accounting, "posture: `port_now`");
}

test "handoff and shared-summary notes preserve the same study-only boundary" {
    try expectContains(handoff_next_steps, "keep the two roadmap study-only anchors parked");
    try expectContains(handoff_next_steps, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(handoff_next_steps, "if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only");
    try expectContains(handoff_next_steps, "broader dedicated `phase15*` wrapper routes or shared-CI route are already shipped");

    try expectContains(shared_summary_gap, "freeze-map status change for any deep-core anchor");
    try expectContains(shared_summary_gap, "direct deep-core Zig bridge or port-readiness decision");
    try expectContains(shared_summary_gap, "Architecture Council decision index");
    try expectContains(shared_summary_gap, "dedicated validator maintenance gate");

    for (study_only_anchors) |anchor| {
        try expectContains(handoff_next_steps, anchor);
    }
}
