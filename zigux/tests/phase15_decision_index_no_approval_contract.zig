const std = @import("std");

const RootSurface = struct {
    path: []const u8,
    required_terms: []const []const u8,
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

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectNoFormattedPair(haystack: []const u8, anchor: []const u8, suffix: []const u8) !void {
    var buffer: [128]u8 = undefined;
    const marker = try std.fmt.bufPrint(&buffer, "{s}: {s}", .{ anchor, suffix });
    try expectNotContains(haystack, marker);
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

test "Architecture Council decision index keeps the zero-approval inventory explicit" {
    const decision_index = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-index.md", 64 * 1024);
    defer std.testing.allocator.free(decision_index);

    try expectContains(decision_index, "PHASE15_STATUS=architecture_council_decision_index_landed");
    try expectContains(decision_index, "PHASE15_LANE_KEY=P15-L09");
    try expectContains(decision_index, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(decision_index, "PHASE15_PACKET_VALIDATION_GATE=zig run scripts/zigux/check_phase15_architecture_council_decision_index.zig");
    try expectContains(decision_index, "PHASE15_PACKET_ROLLBACK_OWNER=Architecture Council");
    try expectContains(decision_index, "approved status-bucket changes recorded on current `master`: none");
    try expectContains(decision_index, "stay-in-C closeout decision records recorded on current `master`: none");
    try expectContains(decision_index, "no freeze-map anchor has an Architecture Council approval for a status change on current `master`");
    try expectContains(decision_index, "if no reviewable Architecture Council decision record exists yet, keep this note at an explicit zero-decision inventory instead of implying approval by omission");
    try expectContains(decision_index, "This note does not claim:");
    try expectContains(decision_index, "an Architecture Council approval for any freeze-map status change");
    try expectContains(decision_index, "a stay-in-C closeout record that is not linked by path");
    try expectContains(decision_index, "a deep-core Zig bridge or port-readiness decision");

    for (study_only_anchors) |anchor| {
        try expectContains(decision_index, anchor);
    }
}

test "decision-index posture is mirrored by readiness and checker surfaces" {
    const surfaces = [_]RootSurface{
        .{
            .path = "Documentation/zigux/phase15-readiness-gate-survey.md",
            .required_terms = &.{
                "Documentation/zigux/phase15-architecture-council-decision-index.md",
                "the roadmap-required Architecture Council review process is landed and reviewable, but no reopen decision is currently recorded for a deep-core status change",
                "no Architecture Council approval is currently recorded for a freeze-map status change",
                "no direct deep-core Zig bridge or port-readiness decision is implied by the current readiness posture",
                "release_evidence_count=4",
                "make -C zigux phase15-validate",
                ".github/workflows/zigux-bootstrap.yml",
            },
        },
        .{
            .path = "zigux/tests/phase15_readiness_gap_matrix.json",
            .required_terms = &.{
                "\"no_architecture_council_status_change_approval\"",
                "\"status\": \"blocked\"",
                "\"Documentation/zigux/phase15-architecture-council-review-process.md\"",
                "\"the landed governance packet still does not authorize a freeze-map status change or direct deep-core Zig delivery claim\"",
                "\"release_evidence_count\": 4",
            },
        },
        .{
            .path = "scripts\zigux/check_phase15_architecture_council_decision_index.zig",
            .required_terms = &.{
                "approved status-bucket changes recorded on current `master`: none",
                "stay-in-C closeout decision records recorded on current `master`: none",
                "no freeze-map anchor has an Architecture Council approval for a status change on current `master`",
                "missing_review_process_decision_index_marker",
                "missing_validator_direct_packet_marker",
                "manifest_decision_index_note",
            },
        },
        .{
            .path = "scripts\zigux/validate_phase15.zig",
            .required_terms = &.{
                "\"Documentation/zigux/phase15-architecture-council-decision-index.md\"",
                "\"scripts\zigux/check_phase15_architecture_council_packet.zig\"",
                "\"scripts\zigux/validate_phase15.zig\"",
                "\"phase15_validate_target_present\": False",
                "\"phase15_test_target_present\": False",
                "\"phase15_aggregate_target_present\": False",
                "\"shared_ci_phase15_present\": False",
            },
        },
    };

    for (surfaces) |surface| {
        try expectSurfaceTerms(surface);
    }
}

test "zero-decision contract does not promote freeze or study anchors" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 64 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const decision_index = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-index.md", 64 * 1024);
    defer std.testing.allocator.free(decision_index);

    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "study-only follow-up may gather narrower evidence, but it must not present `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as active delivery targets");
    try expectContains(decision_index, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this index until the freeze map changes");

    for (freeze_in_c_anchors) |anchor| {
        try expectContains(freeze_map, anchor);
        try expectNoFormattedPair(decision_index, anchor, "approved");
    }

    for (study_only_anchors) |anchor| {
        try expectContains(freeze_map, anchor);
        try expectContains(decision_index, anchor);
        try expectNoFormattedPair(decision_index, anchor, "status-review");
    }
}
