const std = @import("std");

const RootSurface = struct {
    path: []const u8,
    required_terms: []const []const u8,
};

const status_change_fields = [_][]const u8{
    "exact Linux anchor path",
    "roadmap phase",
    "lane owner",
    "current status bucket",
    "requested decision bucket",
    "required approver set",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "rollback threshold",
    "automatic return-to-blocked trigger",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or explicit non-applicability note",
    "governance lane sequencing link or explicit scope note",
    "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
    "explicit non-goals",
    "written rationale",
};

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

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsAll(haystack: []const u8, terms: []const []const u8) !void {
    for (terms) |term| {
        try expectContains(haystack, term);
    }
}

fn expectSurfaceTerms(surface: RootSurface) !void {
    const text = try readRepoFile(surface.path, 192 * 1024);
    defer std.testing.allocator.free(text);
    try expectContainsAll(text, surface.required_terms);
}

test "freeze-map status changes require a full Architecture Council evidence packet" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 64 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(freeze_map, "changes to either list require an explicit Architecture Council decision with written rationale");
    try expectContains(freeze_map, "freeze-map status-change requests must route through");
    try expectContains(freeze_map, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-freeze-map-governance.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "there is no silent exception path around the stay-in-C policy");
    try expectContains(freeze_map, "governance lane sequencing link or explicit scope note");
    try expectContains(freeze_map, "study-only anchor accounting link or explicit freeze-map-anchor confirmation");
    try expectContains(freeze_map, "retired_from_active_discussion");

    for (freeze_in_c_anchors) |anchor| {
        try expectContains(freeze_map, anchor);
    }

    for (study_only_anchors) |anchor| {
        try expectContains(freeze_map, anchor);
    }

    for (status_change_fields) |field| {
        try expectContains(freeze_map, field);
    }
}

test "shared root surfaces route status-change summaries back to the owner notes" {
    const root_surfaces = [_]RootSurface{
        .{
            .path = "Documentation/zigux/README.md",
            .required_terms = &.{
                "Phase 15 notes",
                "Documentation/zigux/freeze-map.md",
                "Documentation/zigux/phase15-freeze-map-governance.md",
                "Documentation/zigux/phase15-architecture-council-review-process.md",
                "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
                "Documentation/zigux/phase15-indefinite-c-policy.md",
                "Documentation/zigux/phase15-parity-scorecard.md",
                "Documentation/zigux/phase15-study-only-anchor-accounting.md",
                "no Architecture Council approval claim",
                "any freeze-map status change",
            },
        },
        .{
            .path = "Documentation/zigux/review-checklist.md",
            .required_terms = &.{
                "Architecture Council status review",
                "stay-in-C closeout",
                "required approver set",
                "rollback owner",
                "evidence archive path",
                "Documentation/zigux/phase15-architecture-council-review-process.md",
                "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
                "Documentation/zigux/phase15-indefinite-c-policy.md",
                "Documentation/zigux/freeze-map.md",
                "Documentation/zigux/phase15-study-only-anchor-accounting.md",
            },
        },
    };

    for (root_surfaces) |surface| {
        try expectSurfaceTerms(surface);
    }
}

test "Architecture Council owner notes default to blocked review, not silent approval" {
    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 64 * 1024);
    defer std.testing.allocator.free(review_process);

    const decision_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 32 * 1024);
    defer std.testing.allocator.free(decision_template);

    try expectContains(review_process, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(review_process, "If one of those fields cannot be stated honestly, the request stays blocked");
    try expectContains(review_process, "This note does not define an exception path outside those reviewable outcomes.");
    try expectContains(review_process, "There is no silent exception path around the indefinite-C policy.");
    try expectContains(review_process, "On current `master`, no freeze-map anchor has an Architecture Council approval for a status change.");
    try expectContains(review_process, "an Architecture Council approval for any freeze-map status change");

    try expectContains(decision_template, "REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>");
    try expectContains(decision_template, "If any required field above cannot be stated honestly, keep the request blocked");
    try expectContains(decision_template, "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review");
    try expectContains(decision_template, "A stay-in-C closeout must keep the retained `freeze_in_c` decision");
    try expectContains(decision_template, "A reopen request must cite the exact reopen trigger being exercised");
}
