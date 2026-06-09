const std = @import("std");

const study_only_anchors = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const freeze_in_c_anchors = [_][]const u8{
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
};

const RootSurface = struct {
    path: []const u8,
    terms: []const []const u8,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectContainsAll(haystack: []const u8, terms: []const []const u8) !void {
    for (terms) |term| {
        try expectContains(haystack, term);
    }
}

fn expectSurface(surface: RootSurface) !void {
    const text = try readRepoFile(surface.path, 256 * 1024);
    defer std.testing.allocator.free(text);
    try expectContainsAll(text, surface.terms);
}

test "study-only anchor accounting keeps the two-anchor inventory explicit" {
    const accounting = try readRepoFile("Documentation/zigux/phase15-study-only-anchor-accounting.md", 96 * 1024);
    defer std.testing.allocator.free(accounting);

    try expectContains(accounting, "PHASE15_STATUS=study_only_accounting_slice_landed");
    try expectContains(accounting, "PHASE15_LANE_KEY=P15-L05");
    try expectContains(accounting, "PHASE15_SLICE=study-only-anchor-accounting");
    try expectContains(accounting, "boundary-study target first, not a rewrite target");
    try expectContains(accounting, "no Architecture Council approval is currently recorded for a deep-core status change");
    try expectContains(accounting, "this note is an inventory and handoff surface, not an approval record");
    try expectContains(accounting, "tracked outside the freeze-in-C scorecard and outside blocked status-change rows");

    for (study_only_anchors) |anchor| {
        try expectContains(accounting, anchor);
    }
    for (freeze_in_c_anchors) |anchor| {
        var heading_buf: [128]u8 = undefined;
        const heading = try std.fmt.bufPrint(&heading_buf, "### `{s}`", .{anchor});
        try expectNotContains(accounting, heading);
    }
}

test "freeze map and shared surfaces route study-only summaries back to accounting" {
    const surfaces = [_]RootSurface{
        .{
            .path = "Documentation/zigux/freeze-map.md",
            .terms = &.{
                "## Study / Boundary Only",
                "kernel/workqueue.c",
                "kernel/trace/ring_buffer.c",
                "Documentation/zigux/phase15-study-only-anchor-accounting.md",
                "must not present `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as active delivery targets",
                "study-only anchor maintenance must stay aligned",
            },
        },
        .{
            .path = "Documentation/zigux/README.md",
            .terms = &.{
                "Phase 15 notes",
                "Documentation/zigux/freeze-map.md",
                "Documentation/zigux/phase15-study-only-anchor-accounting.md",
                "kernel/workqueue.c",
                "kernel/trace/ring_buffer.c",
                "remain study-only anchors",
                "no Architecture Council approval is currently recorded for a freeze-map status change",
            },
        },
        .{
            .path = "Documentation/zigux/review-checklist.md",
            .terms = &.{
                "Documentation/zigux/freeze-map.md",
                "Documentation/zigux/phase15-study-only-anchor-accounting.md",
                "kernel/workqueue.c",
                "kernel/trace/ring_buffer.c",
                "stay explicit as study-only boundary context",
                "rather than runtime-substrate or bridge-readiness evidence",
            },
        },
    };

    for (surfaces) |surface| {
        try expectSurface(surface);
    }
}

test "governance and validator keep study-only accounting adjacent to Phase 15 maintenance" {
    const governance = try readRepoFile("Documentation/zigux/phase15-freeze-map-governance.md", 128 * 1024);
    defer std.testing.allocator.free(governance);
    const validator = try readRepoFile("scripts/zigux/validate-phase15.py", 128 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(governance, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(governance, "the freeze-map anchor set and study-only scope therefore stay unchanged on current `master`");
    try expectContains(governance, "the checklist-specific study-only routing guard stays adjacent direct-readback evidence");
    try expectContains(governance, "direct Zig bridge or port claims for a freeze-in-C anchor stay blocked");
    try expectContains(governance, "phase15-shared-wrapper-route-readback");

    try expectContains(validator, "\"Documentation/zigux/phase15-study-only-anchor-accounting.md\"");
    try expectContains(validator, "\"scripts/zigux/check-phase15-review-checklist-study-only-alignment.py\"");
    try expectContains(validator, "\"phase15_review_checklist_study_only_alignment_checker_present\": True");
    try expectContains(validator, "\"phase15_validate_target_present\": False");
    try expectContains(validator, "\"phase15_test_target_present\": False");
    try expectContains(validator, "\"phase15_aggregate_target_present\": False");
}
