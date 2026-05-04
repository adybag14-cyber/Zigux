const std = @import("std");

const GovernanceRequirement = struct {
    id: []const u8,
    summary: []const u8,
    required_terms: []const []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const BlockerOwnershipRecord = struct {
    anchor: []const u8,
    lane_owner: []const u8,
    validation_gate: []const u8,
    rollback_owner: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_freeze_in_c_targets: []const []const u8,
    roadmap_study_only_targets: []const []const u8,
    freeze_in_c_targets: []const []const u8,
    study_only_targets: []const []const u8,
    repo_reality_evidence_paths: []const []const u8,
    current_blockers: []const []const u8,
    blocker_ownership_records: []const BlockerOwnershipRecord,
    governance_requirements: []const GovernanceRequirement,
    gaps: []const Gap,
};

fn hasSubstring(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase 15 freeze-map governance manifest records the active lane and blocker survey" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_freeze_map_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("5bf6598fadf90e6ab59b1d402fa5decc1c1c6b05", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_freeze_in_c_targets.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_study_only_targets.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.freeze_in_c_targets.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.study_only_targets.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.repo_reality_evidence_paths.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.current_blockers.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.blocker_ownership_records.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.governance_requirements.len);
    try std.testing.expectEqual(@as(usize, 11), manifest.gaps.len);

    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.roadmap_freeze_in_c_targets[0]);
    try std.testing.expectEqualStrings("mm/page_alloc.c", manifest.roadmap_freeze_in_c_targets[1]);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", manifest.roadmap_freeze_in_c_targets[2]);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.roadmap_freeze_in_c_targets[3]);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.roadmap_study_only_targets[0]);
    try std.testing.expectEqualStrings("kernel/trace/ring_buffer.c", manifest.roadmap_study_only_targets[1]);
    try std.testing.expectEqualStrings("kernel/sched/core.c: blocked_no_bounded_scheduler_seam", manifest.current_blockers[0]);
    try std.testing.expectEqualStrings("mm/page_alloc.c: blocked_no_bounded_allocator_seam", manifest.current_blockers[1]);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c: blocked_phase14_followup_still_wider_than_allowed_rcu_seam", manifest.current_blockers[2]);
    try std.testing.expectEqualStrings("net/core/skbuff.c: blocked_packet_lifetime_boundary_still_too_wide", manifest.current_blockers[3]);

    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.blocker_ownership_records[0].anchor);
    try std.testing.expectEqualStrings("Architecture Council", manifest.blocker_ownership_records[0].lane_owner);
    try std.testing.expectEqualStrings("Architecture Council + PMO / Release Management", manifest.blocker_ownership_records[0].rollback_owner);
    try std.testing.expect(hasSubstring(manifest.blocker_ownership_records[0].validation_gate, "future lane-local parity harness"));

    try std.testing.expectEqualStrings("mm/page_alloc.c", manifest.blocker_ownership_records[1].anchor);
    try std.testing.expectEqualStrings("Architecture Council", manifest.blocker_ownership_records[1].lane_owner);
    try std.testing.expectEqualStrings("Architecture Council + Validation and Perf Team", manifest.blocker_ownership_records[1].rollback_owner);

    try std.testing.expectEqualStrings("kernel/rcu/tree.c", manifest.blocker_ownership_records[2].anchor);
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.blocker_ownership_records[2].lane_owner);
    try std.testing.expectEqualStrings("Architecture Council + ABI and Runtime Team", manifest.blocker_ownership_records[2].rollback_owner);
    try std.testing.expect(hasSubstring(manifest.blocker_ownership_records[2].validation_gate, "existing Phase 14 survey evidence must stay green"));

    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.blocker_ownership_records[3].anchor);
    try std.testing.expectEqualStrings("Shared Subsystems Pod", manifest.blocker_ownership_records[3].lane_owner);
    try std.testing.expectEqualStrings("Architecture Council + Shared Subsystems Pod", manifest.blocker_ownership_records[3].rollback_owner);
    try std.testing.expect(hasSubstring(manifest.blocker_ownership_records[3].validation_gate, "existing Phase 14 survey evidence must stay green"));

    var landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_note = false;
    var saw_roadmap_vs_repo_reality = false;
    var saw_rollback_threshold_sync = false;
    var saw_blocker_ownership_sync = false;
    var saw_rollback_threshold_requirement = false;

    for (manifest.governance_requirements) |requirement| {
        if (std.mem.eql(u8, requirement.id, "freeze-map-rollback-threshold")) {
            saw_rollback_threshold_requirement = true;
            try std.testing.expectEqualStrings(
                "Any reopened freeze-in-C review packet must state the rollback threshold that forces the anchor back to its blocked freeze posture if review evidence stops being explicit.",
                requirement.summary,
            );
        }
    }

    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) landed_count += 1;
        if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) blocked_count += 1;

        if (std.mem.eql(u8, gap.id, "phase15-freeze-map-governance-note")) {
            saw_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-freeze-map-governance.md", gap.zigux_destination);
            try std.testing.expect(hasSubstring(gap.why_now, "reviewed-head provenance boundary"));
            try std.testing.expect(hasSubstring(gap.why_now, "current-`master` enforcement claim"));
            try std.testing.expect(!hasSubstring(gap.why_now, "latest visible current-head survey"));
        }
        if (std.mem.eql(u8, gap.id, "phase15-roadmap-vs-repo-reality-survey")) {
            saw_roadmap_vs_repo_reality = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-freeze-map-governance.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-rollback-threshold-sync")) {
            saw_rollback_threshold_sync = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-freeze-map-governance.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-blocker-ownership-sync")) {
            saw_blocker_ownership_sync = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-freeze-map-governance.md", gap.zigux_destination);
        }
    }

    try std.testing.expectEqual(@as(usize, 10), landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_roadmap_vs_repo_reality);
    try std.testing.expect(saw_rollback_threshold_sync);
    try std.testing.expect(saw_blocker_ownership_sync);
    try std.testing.expect(saw_rollback_threshold_requirement);
}

test "phase 15 freeze-map governance note keeps the active lane, reviewed head boundary, ownership inventory, rollback threshold, and unchanged blocker posture explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-freeze-map-governance.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expect(hasSubstring(note, "PHASE15_LANE_KEY=P15-L04"));
    try std.testing.expect(hasSubstring(note, "5bf6598fadf90e6ab59b1d402fa5decc1c1c6b05"));
    try std.testing.expect(hasSubstring(note, "survey provenance last refreshed against reviewed `master` head"));
    try std.testing.expect(hasSubstring(note, "before this note should make a new current-`master` claim"));
    try std.testing.expect(!hasSubstring(note, "survey provenance refreshed against latest visible `master` head"));
    try std.testing.expect(!hasSubstring(note, "The roadmap and the live repo still agree on the Phase 15 deep-core freeze set."));
    try std.testing.expect(!hasSubstring(note, "Current repo reality also still supports the same blocker posture rather than a status-change-ready one:"));
    try std.testing.expect(hasSubstring(note, "## Current blocker ownership"));
    try std.testing.expect(hasSubstring(note, "Architecture Council + PMO / Release Management"));
    try std.testing.expect(hasSubstring(note, "Architecture Council + Validation and Perf Team"));
    try std.testing.expect(hasSubstring(note, "Architecture Council + ABI and Runtime Team"));
    try std.testing.expect(hasSubstring(note, "Architecture Council + Shared Subsystems Pod"));
    try std.testing.expect(hasSubstring(note, "existing Phase 14 survey evidence must stay green"));
    try std.testing.expect(hasSubstring(note, "rollback threshold"));
    try std.testing.expect(hasSubstring(note, "forces the anchor back to its blocked freeze posture"));
    try std.testing.expect(hasSubstring(note, "phase15-rollback-threshold-rule-present"));
    try std.testing.expect(hasSubstring(note, "phase15-blocker-ownership-present"));
    try std.testing.expect(hasSubstring(note, "closed_docs_root_summary_alignment_landed_in_readiness_and_handoff_packets"));
    try std.testing.expect(hasSubstring(note, "docs-root summary drift is already closed in the dedicated readiness and handoff packets"));
    try std.testing.expect(hasSubstring(note, "blocked_no_bounded_scheduler_seam"));
    try std.testing.expect(hasSubstring(note, "blocked_no_bounded_allocator_seam"));
    try std.testing.expect(hasSubstring(note, "blocked_phase14_followup_still_wider_than_allowed_rcu_seam"));
    try std.testing.expect(hasSubstring(note, "blocked_packet_lifetime_boundary_still_too_wide"));
    try std.testing.expect(hasSubstring(note, "Run Phase 15 governance tests"));
    try std.testing.expect(hasSubstring(note, "phase15-shared-ci-enforcement-present"));
}