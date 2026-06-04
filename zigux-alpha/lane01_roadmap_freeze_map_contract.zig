const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const freeze_targets = [_][]const u8{
    "`kernel/sched/core.c`",
    "`mm/page_alloc.c`",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
};

const study_only_targets = [_][]const u8{
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
};

fn freezeSection() ![]const u8 {
    const start = std.mem.indexOf(u8, roadmap, "## Freeze Map for Near- and Mid-Term Planning") orelse return error.MissingFreezeMapStart;
    const end = std.mem.indexOfPos(u8, roadmap, start, "## Workstreams and Ownership Model") orelse return error.MissingFreezeMapEnd;
    return roadmap[start..end];
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "roadmap keeps the freeze map section between phase 15 and ownership" {
    try expectOrdered(roadmap, "## Phase 15: Full-Parity Blockers and Long-Term Governance", "## Freeze Map for Near- and Mid-Term Planning");
    try expectOrdered(roadmap, "## Freeze Map for Near- and Mid-Term Planning", "## Workstreams and Ownership Model");

    try expectContains(roadmap, "Active freeze-in-C targets for the current product plan:");
    try expectContains(roadmap, "Boundary-study-only targets before any direct port decision:");
    try expectContains(roadmap, "What this means for ZAR future work:");
}

test "roadmap freeze-in-C targets stay explicit and complete" {
    const section = try freezeSection();

    for (freeze_targets) |target| {
        try expectContains(section, target);
    }

    try expectOrdered(section, "Active freeze-in-C targets for the current product plan:", "`kernel/sched/core.c`");
    try expectOrdered(section, "`kernel/sched/core.c`", "`mm/page_alloc.c`");
    try expectOrdered(section, "`mm/page_alloc.c`", "`kernel/rcu/tree.c`");
    try expectOrdered(section, "`kernel/rcu/tree.c`", "`net/core/skbuff.c`");
}

test "roadmap keeps study-only targets below delivery commitments" {
    const section = try freezeSection();

    for (study_only_targets) |target| {
        try expectContains(section, target);
    }

    try expectOrdered(section, "Boundary-study-only targets before any direct port decision:", "`kernel/workqueue.c`");
    try expectOrdered(section, "`kernel/workqueue.c`", "`kernel/trace/ring_buffer.c`");
    try expectOrdered(section, "What this means for ZAR future work:", "research on these areas can continue in ZAR if it improves understanding");
    try expectOrdered(section, "research on these areas can continue in ZAR if it improves understanding", "those experiments should not be represented as near-term Zigux delivery commitments");
}
