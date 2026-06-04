const std = @import("std");

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

const blocker_ids = [_][]const u8{
    "blocked_no_bounded_scheduler_seam",
    "blocked_no_bounded_allocator_seam",
    "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
    "blocked_packet_lifetime_boundary_still_too_wide",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectLacks(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase 15 deep-core blocker survey preserves freeze-in-C anchor blockers" {
    const survey = try readRepoFile("Documentation/zigux/phase15-deep-core-blocker-survey.md", 48 * 1024);
    defer std.testing.allocator.free(survey);

    try expectContains(survey, "PHASE15_STATUS=deep_core_blocker_survey_landed");
    try expectContains(survey, "PHASE15_SLICE=roadmap_vs_repo_reality_deep_core_blocker_crosswalk");
    try expectContains(survey, "current-master-readback-2026-05-27");

    for (freeze_in_c_anchors) |anchor| {
        try expectContains(survey, anchor);
    }
    for (study_only_anchors) |anchor| {
        try expectContains(survey, anchor);
    }
    for (blocker_ids) |blocker_id| {
        try expectContains(survey, blocker_id);
    }

    try expectContains(survey, "zigux/tests/phase15_build.zig");
    try expectContains(survey, "directly materialized");
    try expectContains(survey, "broader wrapper and shared-CI surfaces remain current gaps");
    try expectContains(survey, "no Architecture Council approval is currently recorded");
    try expectContains(survey, "blocker accounting and reminder-surface maintenance, not deep-core delivery");
    try expectContains(survey, "does not claim");
    try expectContains(survey, "a direct Zig bridge or dual implementation for any deep-core freeze-in-C anchor");
}

test "freeze map and shared summaries keep the blocker survey below status-change evidence" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 64 * 1024);
    defer std.testing.allocator.free(freeze_map);
    const handoff = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 96 * 1024);
    defer std.testing.allocator.free(handoff);
    const shared_gap = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 96 * 1024);
    defer std.testing.allocator.free(shared_gap);

    try expectContains(freeze_map, "## Freeze In C Initially");
    for (freeze_in_c_anchors) |anchor| {
        try expectContains(freeze_map, anchor);
    }
    try expectContains(freeze_map, "## Study / Boundary Only");
    for (study_only_anchors) |anchor| {
        try expectContains(freeze_map, anchor);
    }
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "no silent exception path");

    try expectContains(handoff, "Documentation/zigux/phase15-deep-core-blocker-survey.md");
    try expectContains(handoff, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(handoff, "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body");
    try expectContains(handoff, "no dedicated shared-CI Phase 15 validate, test, or aggregate route");

    try expectContains(shared_gap, "Documentation/zigux/phase15-deep-core-blocker-survey.md");
    try expectContains(shared_gap, "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body");
    try expectContains(shared_gap, ".github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route name");
    try expectContains(shared_gap, "a freeze-map status change for any deep-core anchor");
    try expectContains(shared_gap, "a direct deep-core Zig bridge or port-readiness decision");
}

test "blocked-route recovery checker keeps wrapper and shared-CI gaps fail-closed" {
    const checker = try readRepoFile("scripts/zigux/check-phase15-blocked-route-recovery.py", 32 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "BLOCKED_MAKE_TARGETS");
    try expectContains(checker, "\"phase15-validate\", \"phase15-test\", \"phase15\"");
    try expectContains(checker, "\"missing_make_routes\"");
    try expectContains(checker, "\"missing_workflow_route\"");
    try expectContains(checker, "\"no_architecture_council_status_change_approval\"");
    try expectContains(checker, "unexpected_make_target");
    try expectContains(checker, "unexpected_workflow_phase15_route");
    try expectContains(checker, "gap_matrix_gap_not_blocked");

    const false_recovery_claim =
        \\phase15-deep-core-status-change-blocker
        \\make -C zigux phase15-validate
        \\Architecture Council approval recorded
        \\direct deep-core Zig bridge is ready
    ;
    try expectContains(false_recovery_claim, "make -C zigux phase15-validate");
    try expectContains(false_recovery_claim, "Architecture Council approval recorded");
    try expectLacks(false_recovery_claim, "missing_workflow_route");
}
