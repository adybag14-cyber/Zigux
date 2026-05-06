const std = @import("std");

const AnchorExpectation = struct {
    anchor: []const u8,
    readiness_snippet: []const u8,
    archive_path: []const u8,
    archive_snippets: []const []const u8,
    parity_snippets: []const []const u8,
};

fn expectContains(io: std.Io, path: []const u8, snippets: []const []const u8) !void {
    const contents = try std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(contents);

    for (snippets) |snippet| {
        try std.testing.expect(std.mem.indexOf(u8, contents, snippet) != null);
    }
}

test "phase 15 indefinite-C policy packet keeps exception and blocker evidence aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    try expectContains(io_instance.io(), "Documentation/zigux/phase15-indefinite-c-policy.md", &.{
        "PHASE15_LANE_KEY=P15-L16",
        "There is no silent exception path around the indefinite-C policy.",
        "The only allowed exception is an Architecture Council reopen request",
        "the existing blocker remains recorded",
        "Keep this lane in maintenance mode until new stay-in-C evidence changes one of the named reopen triggers or the deep-core blocker posture changes.",
    });

    try expectContains(io_instance.io(), "Documentation/zigux/phase15-architecture-council-review-process.md", &.{
        "`keep_in_c`",
        "the blocker must remain explicit rather than disappearing into prose",
        "retained discussion state must be `retired_from_active_discussion`",
        "Every retained stay-in-C closeout must cite at least one of these catalog items in its evidence archive",
    });

    try expectContains(io_instance.io(), "Documentation/zigux/phase15-handoff-next-steps-survey.md", &.{
        "the remaining blocked work is only the deep-core status-change evidence",
    });

    try expectContains(io_instance.io(), "Documentation/zigux/phase15-readiness-gate-survey.md", &.{
        "maintenance-mode ready: the parked Phase 15 packet is reviewable and rerunnable, but no freeze-map status-change approval is recorded",
        "phase15-deep-core-status-change-blocker",
    });

    try expectContains(io_instance.io(), "Documentation/zigux/phase15-parity-scorecard.md", &.{
        "blocked status-change anchors: `4`",
        "landed `phase15-stay-in-c-retirement-rule`",
        "landed `phase15-reopen-trigger-catalog-followup`",
        "blocked `phase15-deep-core-status-change-blocker`",
    });

    try expectContains(io_instance.io(), "zigux/tests/phase15_indefinite_c_policy.json", &.{
        "\"lane_key\": \"P15-L16\"",
        "\"id\": \"phase15-deep-core-status-change-blocker\"",
        "\"status\": \"blocked_on_stay_in_c_evidence\"",
        "\"The live repo still lacks evidence strong enough to move any freeze-in-C anchor out of the current long-term C-owned posture.\"",
    });

    const expectations = [_]AnchorExpectation{
        .{
            .anchor = "kernel/sched/core.c",
            .readiness_snippet = "`kernel/sched/core.c`: blocked as `blocked_no_bounded_scheduler_seam`",
            .archive_path = "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
            .archive_snippets = &.{
                "lane owner: `Architecture Council`",
                "latest blocker disposition: `blocked_no_bounded_scheduler_seam`",
                "retained discussion state after closeout: `retired_from_active_discussion`",
                "written rationale: `A narrower scheduler seam has not been isolated yet, so this path remains a reserved template only.`",
            },
            .parity_snippets = &.{
                "### `kernel/sched/core.c`",
                "decision record path: `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`",
                "latest blocker disposition: `blocked_no_bounded_scheduler_seam`",
            },
        },
        .{
            .anchor = "mm/page_alloc.c",
            .readiness_snippet = "`mm/page_alloc.c`: blocked as `blocked_no_bounded_allocator_seam`",
            .archive_path = "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
            .archive_snippets = &.{
                "lane owner: `Architecture Council`",
                "latest blocker disposition: `blocked_no_bounded_allocator_seam`",
                "retained discussion state after closeout: `retired_from_active_discussion`",
                "written rationale: `A narrower allocator-facing seam has not been isolated yet, so this path remains a reserved template only.`",
            },
            .parity_snippets = &.{
                "### `mm/page_alloc.c`",
                "decision record path: `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`",
                "latest blocker disposition: `blocked_no_bounded_allocator_seam`",
            },
        },
        .{
            .anchor = "kernel/rcu/tree.c",
            .readiness_snippet = "`kernel/rcu/tree.c`: blocked as `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`",
            .archive_path = "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
            .archive_snippets = &.{
                "lane owner: `ABI and Runtime Team`",
                "latest blocker disposition: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`",
                "`Documentation/zigux/phase14-rcu-tree-survey.md`",
                "written rationale: `The current RCU follow-up remains wider than the allowed seam, so this path remains a reserved template only.`",
            },
            .parity_snippets = &.{
                "### `kernel/rcu/tree.c`",
                "decision record path: `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`",
                "linked evidence: `Documentation/zigux/phase14-rcu-tree-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-parity-scorecard.md`",
                "latest blocker disposition: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`",
            },
        },
        .{
            .anchor = "net/core/skbuff.c",
            .readiness_snippet = "`net/core/skbuff.c`: blocked as `blocked_packet_lifetime_boundary_still_too_wide`",
            .archive_path = "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
            .archive_snippets = &.{
                "lane owner: `Shared Subsystems Pod`",
                "latest blocker disposition: `blocked_packet_lifetime_boundary_still_too_wide`",
                "`Documentation/zigux/phase14-skbuff-bridge-survey.md`",
                "written rationale: `The current skbuff follow-up remains wider than the allowed lifetime boundary, so this path remains a reserved template only.`",
            },
            .parity_snippets = &.{
                "### `net/core/skbuff.c`",
                "decision record path: `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`",
                "linked evidence: `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-parity-scorecard.md`",
                "latest blocker disposition: `blocked_packet_lifetime_boundary_still_too_wide`",
            },
        },
    };

    for (expectations) |expectation| {
        try expectContains(io_instance.io(), "Documentation/zigux/phase15-readiness-gate-survey.md", &.{expectation.readiness_snippet});
        try expectContains(io_instance.io(), expectation.archive_path, expectation.archive_snippets);
        try expectContains(io_instance.io(), "Documentation/zigux/phase15-parity-scorecard.md", expectation.parity_snippets);
        try std.testing.expect(expectation.anchor.len > 0);
    }
}
