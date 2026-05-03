const std = @import("std");

const ArchiveExpectation = struct {
    path: []const u8,
    anchor: []const u8,
    rollback_owner: []const u8,
    benchmark_notes: []const u8,
    blocker: []const u8,
    extra_linked_evidence: ?[]const u8 = null,
};

const archive_expectations = [_]ArchiveExpectation{
    .{
        .path = "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
        .anchor = "kernel/sched/core.c",
        .rollback_owner = "Architecture Council + PMO / Release Management",
        .benchmark_notes = "pending_until_bounded_scheduler_seam_exists",
        .blocker = "blocked_no_bounded_scheduler_seam",
    },
    .{
        .path = "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
        .anchor = "mm/page_alloc.c",
        .rollback_owner = "Architecture Council + Validation and Perf Team",
        .benchmark_notes = "pending_until_bounded_allocator_seam_exists",
        .blocker = "blocked_no_bounded_allocator_seam",
    },
    .{
        .path = "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
        .anchor = "kernel/rcu/tree.c",
        .rollback_owner = "Architecture Council + ABI and Runtime Team",
        .benchmark_notes = "pending_until_rcu_followup_is_narrower_than_freeze_boundary",
        .blocker = "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
        .extra_linked_evidence = "Documentation/zigux/phase14-rcu-tree-survey.md",
    },
    .{
        .path = "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
        .anchor = "net/core/skbuff.c",
        .rollback_owner = "Architecture Council + Shared Subsystems Pod",
        .benchmark_notes = "pending_until_skbuff_followup_is_narrower_than_lifetime_boundary",
        .blocker = "blocked_packet_lifetime_boundary_still_too_wide",
        .extra_linked_evidence = "Documentation/zigux/phase14-skbuff-bridge-survey.md",
    },
};

fn readAlloc(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase15 evidence-archive templates keep no-approval and ownership fields explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    for (archive_expectations) |expectation| {
        const archive_doc = try readAlloc(io_instance.io(), expectation.path, 16 * 1024);
        defer std.testing.allocator.free(archive_doc);

        try expectContains(archive_doc, expectation.anchor);
        try expectContains(archive_doc, "current status bucket: `freeze_in_c`");
        try expectContains(archive_doc, "requested decision bucket: `pending_no_request`");
        try expectContains(archive_doc, "decision record ID: `pending_no_architecture_council_request`");
        try expectContains(archive_doc, "lane owner: `");
        try expectContains(archive_doc, expectation.rollback_owner);
        try expectContains(archive_doc, "validation gate summary:");
        try expectContains(archive_doc, expectation.benchmark_notes);
        try expectContains(archive_doc, "replay command: `zig build test --build-file zigux/tests/phase15_build.zig`");
        try expectContains(archive_doc, "Documentation/zigux/freeze-map.md");
        try expectContains(archive_doc, "Documentation/zigux/phase15-parity-scorecard.md");
        if (expectation.extra_linked_evidence) |extra_linked_evidence| {
            try expectContains(archive_doc, extra_linked_evidence);
        }
        try expectContains(archive_doc, expectation.blocker);
        try expectContains(archive_doc, "automatic return-to-blocked trigger:");
        try expectContains(archive_doc, "Documentation/zigux/phase15-indefinite-c-policy.md");
        try expectContains(archive_doc, "retained discussion state after closeout: `retired_from_active_discussion`");
        try expectContains(archive_doc, "reopen triggers:");
        try expectContains(archive_doc, "no Architecture Council approval claim");
        try expectContains(archive_doc, "written rationale:");
    }
}
