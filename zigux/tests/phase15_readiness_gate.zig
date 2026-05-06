const std = @import("std");

const RepoEvidence = struct {
    freeze_map_present: bool,
    review_checklist_present: bool,
    review_process_present: bool,
    parity_scorecard_present: bool,
    indefinite_c_policy_present: bool,
    handoff_next_steps_present: bool,
    phase15_build_present: bool,
    phase15_make_target_present: bool,
    shared_ci_phase15_present: bool,
    phase15_replay_green_on_current_master: bool,
    deep_core_status_change_ready: bool,
};

const DeepCoreBlocker = struct {
    anchor: []const u8,
    parity_scorecard_owner: []const u8,
    blocker_disposition: []const u8,
    roadmap_constraint: []const u8,
    repo_evidence: []const []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    roadmap_phase_title: []const u8,
    roadmap_requirements: []const []const u8,
    bootstrap_ledger_anchor: []const u8,
    ledger_scope: []const []const u8,
    repo_evidence: RepoEvidence,
    deep_core_blockers: []const DeepCoreBlocker,
    remaining_gaps: []const Gap,
    next_step: []const u8,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase 15 readiness manifest records the roadmap, ledger, and current repo posture" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_readiness_gate_manifest.json",
        std.testing.allocator,
        .limited(28 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expect(manifest.surveyed_commit.len > 0);
    try std.testing.expectEqualStrings("Full-Parity Blockers and Long-Term Governance", manifest.roadmap_phase_title);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_requirements.len);
    try std.testing.expectEqualStrings("freeze map", manifest.roadmap_requirements[0]);
    try std.testing.expectEqualStrings("Architecture Council review process", manifest.roadmap_requirements[1]);
    try std.testing.expectEqualStrings("parity scorecard", manifest.roadmap_requirements[2]);
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirements[3]);
    try std.testing.expect(std.mem.indexOf(u8, manifest.bootstrap_ledger_anchor, "freeze map") != null);
    try std.testing.expectEqual(@as(usize, 3), manifest.ledger_scope.len);
    try std.testing.expectEqualStrings("Documentation/zigux/README.md", manifest.ledger_scope[0]);
    try std.testing.expectEqualStrings("Documentation/zigux/review-checklist.md", manifest.ledger_scope[1]);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.ledger_scope[2]);

    try std.testing.expect(manifest.repo_evidence.freeze_map_present);
    try std.testing.expect(manifest.repo_evidence.review_checklist_present);
    try std.testing.expect(manifest.repo_evidence.review_process_present);
    try std.testing.expect(manifest.repo_evidence.parity_scorecard_present);
    try std.testing.expect(manifest.repo_evidence.indefinite_c_policy_present);
    try std.testing.expect(manifest.repo_evidence.handoff_next_steps_present);
    try std.testing.expect(manifest.repo_evidence.phase15_build_present);
    try std.testing.expect(manifest.repo_evidence.phase15_make_target_present);
    try std.testing.expect(manifest.repo_evidence.shared_ci_phase15_present);
    try std.testing.expect(manifest.repo_evidence.phase15_replay_green_on_current_master);
    try std.testing.expect(!manifest.repo_evidence.deep_core_status_change_ready);

    try std.testing.expectEqual(@as(usize, 4), manifest.deep_core_blockers.len);
    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.deep_core_blockers[0].anchor);
    try std.testing.expectEqualStrings("Architecture Council", manifest.deep_core_blockers[0].parity_scorecard_owner);
    try std.testing.expectEqualStrings("blocked_no_bounded_scheduler_seam", manifest.deep_core_blockers[0].blocker_disposition);
    try std.testing.expectEqualStrings("mm/page_alloc.c", manifest.deep_core_blockers[1].anchor);
    try std.testing.expectEqualStrings("Architecture Council", manifest.deep_core_blockers[1].parity_scorecard_owner);
    try std.testing.expectEqualStrings("blocked_no_bounded_allocator_seam", manifest.deep_core_blockers[1].blocker_disposition);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", manifest.deep_core_blockers[2].anchor);
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.deep_core_blockers[2].parity_scorecard_owner);
    try std.testing.expectEqualStrings("blocked_phase14_followup_still_wider_than_allowed_rcu_seam", manifest.deep_core_blockers[2].blocker_disposition);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.deep_core_blockers[3].anchor);
    try std.testing.expectEqualStrings("Shared Subsystems Pod", manifest.deep_core_blockers[3].parity_scorecard_owner);
    try std.testing.expectEqualStrings("blocked_packet_lifetime_boundary_still_too_wide", manifest.deep_core_blockers[3].blocker_disposition);

    for (manifest.deep_core_blockers) |blocker| {
        try std.testing.expect(blocker.roadmap_constraint.len > 0);
        try std.testing.expectEqual(@as(usize, 2), blocker.repo_evidence.len);
        try std.testing.expect(blocker.repo_evidence[0].len > 0);
        try std.testing.expect(blocker.repo_evidence[1].len > 0);
    }

    try std.testing.expectEqual(@as(usize, 1), manifest.remaining_gaps.len);

    var saw_status_change_blocker = false;
    for (manifest.remaining_gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.zigux_destination.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.id, "phase15-deep-core-status-change-blocker")) {
            saw_status_change_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freeze-in-C posture") != null);
        }

        for (manifest.remaining_gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expect(saw_status_change_blocker);
    try std.testing.expect(std.mem.indexOf(u8, manifest.next_step, "maintenance mode") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.next_step, "four recorded deep-core blocker dispositions") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.next_step, "make -C zigux phase15") != null);
}

test "phase 15 readiness note keeps the roadmap, ledger, and current blocker inventory explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const readiness_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-readiness-gate-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(readiness_note);

    const workflow = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(workflow);

    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "## Roadmap Versus Ledger") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "## Current Repo Readiness") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "## Current Deep-Core Blockers") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "## Remaining Readiness Gaps") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "## Readiness Gate") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "Full-Parity Blockers and Long-Term Governance") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "docs(zigux): add documentation root, review checklist, and freeze map") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "shared replay surface is green on current `master`") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "maintenance-mode ready") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "phase15-handoff-next-steps-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "blocked_no_bounded_scheduler_seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "blocked_no_bounded_allocator_seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "blocked_phase14_followup_still_wider_than_allowed_rcu_seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "blocked_packet_lifetime_boundary_still_too_wide") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "Documentation/zigux/phase14-rcu-tree-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "Documentation/zigux/phase14-skbuff-bridge-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "phase15-deep-core-status-change-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "zig build test --build-file zigux/tests/phase15_build.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, workflow, "Validate Phase 14 shared smoke packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 14 internal bridge tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 15 governance tests") != null);
}

test "phase 15 readiness survey stays aligned with the landed governance bundle" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const freeze_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(freeze_map);

    const review_process = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(review_process);

    const parity_scorecard = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-parity-scorecard.md",
        std.testing.allocator,
        .limited(40 * 1024),
    );
    defer std.testing.allocator.free(parity_scorecard);

    const indefinite_c_policy = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(indefinite_c_policy);

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const readiness_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-readiness-gate-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(readiness_note);

    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "## Governance For Freeze-Map Changes") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Required Review Packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, parity_scorecard, "## Roadmap Handoff Evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, indefinite_c_policy, "## When the indefinite-C policy applies") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase15-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase15: phase15-validate phase15-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, parity_scorecard, "blocked_no_bounded_scheduler_seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, parity_scorecard, "blocked_no_bounded_allocator_seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, parity_scorecard, "blocked_phase14_followup_still_wider_than_allowed_rcu_seam") != null);
    try std.testing.expect(std.mem.indexOf(u8, parity_scorecard, "blocked_packet_lifetime_boundary_still_too_wide") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "Documentation/zigux/phase15-parity-scorecard.md") != null);
}