const std = @import("std");
const testing = std.testing;

const docs_readme = @embedFile("README.md");
const review_checklist = @embedFile("review-checklist.md");
const freeze_map = @embedFile("freeze-map.md");

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
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "phase14 docs root keeps validate route and bounded study packet visible" {
    try expectContains(docs_readme, "Phase 14 notes");
    try expectContains(docs_readme, "Documentation/zigux/freeze-map.md");
    try expectContains(docs_readme, "Documentation/zigux/phase14-end-to-end-smoke-survey.md");
    try expectContains(docs_readme, "Documentation/zigux/phase14-release-boundary-survey.md");
    try expectContains(docs_readme, "scripts/zigux/validate-phase14.py");
    try expectContains(docs_readme, "make -C zigux phase14-validate");
    try expectContains(docs_readme, "zigux/tests/phase14_workqueue_reviewability.zig");
    try expectContains(docs_readme, "zigux/tests/phase14_workqueue_bridge.zig");
    try expectContains(docs_readme, "zigux/tests/phase14_ring_buffer_survey.zig");
    try expectContains(docs_readme, "zigux/tests/phase14_end_to_end_smoke_manifest.json");
}

test "review checklist preserves phase14 freeze review prompts" {
    try expectContains(review_checklist, "if the change touches the shared Phase 14 smoke packet");
    try expectContains(review_checklist, "Documentation/zigux/freeze-map.md");
    try expectContains(review_checklist, "scripts/zigux/validate-phase14.py");
    try expectContains(review_checklist, "make -C zigux phase14-validate");
    try expectContains(review_checklist, "zigux/tests/phase14_workqueue_bridge.zig");
    try expectContains(review_checklist, "zigux/tests/phase14_ring_buffer_survey.zig");
    try expectContains(review_checklist, "kernel/workqueue.c");
    try expectContains(review_checklist, "kernel/trace/ring_buffer.c");
    try expectContains(review_checklist, "kernel/rcu/tree.c");
    try expectContains(review_checklist, "net/core/skbuff.c");
}

test "freeze map keeps deep-core status split and governance non-goals explicit" {
    try expectBefore(freeze_map, "## Freeze In C Initially", "## Study / Boundary Only");
    try expectBefore(freeze_map, "## Study / Boundary Only", "## Governance For Freeze-Map Changes");
    try expectBefore(freeze_map, "## Governance For Freeze-Map Changes", "## Stay-In-C Policy");

    for (freeze_in_c_anchors) |anchor| {
        try expectContains(freeze_map, anchor);
    }

    for (study_only_anchors) |anchor| {
        try expectContains(freeze_map, anchor);
    }

    try expectContains(freeze_map, "explicit Architecture Council decision");
    try expectContains(freeze_map, "without implying");
    try expectContains(freeze_map, "allowed near-term Zigux work on those anchors is limited to survey notes, boundary manifests, validation gates");
    try expectContains(freeze_map, "explicit non-goal records");
}
