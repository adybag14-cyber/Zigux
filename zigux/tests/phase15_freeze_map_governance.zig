const std = @import("std");

const GovernanceRequirement = struct {
    id: []const u8,
    summary: []const u8,
    required_terms: []const []const u8,
};

const BlockerOwnership = struct {
    anchor: []const u8,
    owner: []const u8,
    phase: []const u8,
    status_bucket: []const u8,
    required_approver_set: []const u8,
    validation_gate: []const u8,
    rollback_owner: []const u8,
    evidence_archive_path: []const u8,
    benchmark_notes: []const u8,
    replay_command: []const u8,
    latest_blocker_disposition: []const u8,
};

const DeepCoreBlockerSurvey = struct {
    anchor: []const u8,
    roadmap_basis: []const u8,
    repo_reality: []const u8,
    current_blocker: []const u8,
};

const MaintenanceHandoff = struct {
    current_lane_posture: []const u8,
    replay_before_trusting: []const []const u8,
    reopen_conditions: []const []const u8,
    next_future_target: []const u8,
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
    surveyed_commit_mode: []const u8,
    surveyed_commit_mode_reason: []const u8,
    anchor: []const u8,
    freeze_in_c_targets: []const []const u8,
    study_only_targets: []const []const u8,
    governance_requirements: []const GovernanceRequirement,
    blocker_ownership: []const BlockerOwnership,
    deep_core_blocker_survey: []const DeepCoreBlockerSurvey,
    maintenance_handoff: MaintenanceHandoff,
    gaps: []const Gap,
};

fn loadFile(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsWithoutBackticks(haystack: []const u8, needle: []const u8) !void {
    var normalized: std.ArrayList(u8) = .empty;
    defer normalized.deinit(std.testing.allocator);

    for (haystack) |byte| {
        if (byte != '`') try normalized.append(std.testing.allocator, byte);
    }

    try expectContains(normalized.items, needle);
}

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

test "phase 15 freeze-map governance manifest records the current dated-readback blocker survey" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try loadFile(io_instance.io(), "zigux/tests/phase15_freeze_map_manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P15-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-18", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("dated_master_readback", manifest.surveyed_commit_mode);
    try expectContains(manifest.surveyed_commit_mode_reason, "dated master-readback marker");
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 4), manifest.freeze_in_c_targets.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.study_only_targets.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.governance_requirements.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.blocker_ownership.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.deep_core_blocker_survey.len);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.maintenance_handoff.current_lane_posture);
    try std.testing.expectEqual(@as(usize, 5), manifest.maintenance_handoff.replay_before_trusting.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.maintenance_handoff.reopen_conditions.len);
    try std.testing.expectEqual(@as(usize, 18), manifest.gaps.len);

    const sched = manifest.blocker_ownership[0];
    try std.testing.expectEqualStrings("kernel/sched/core.c", sched.anchor);
    try std.testing.expectEqualStrings("zig test zigux/tests/phase15_freeze_map_governance.zig", sched.replay_command);
    try std.testing.expectEqualStrings("Architecture Council + PMO / Release Management", sched.required_approver_set);

    const rcu = manifest.deep_core_blocker_survey[2];
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", rcu.anchor);
    try expectContains(rcu.repo_reality, "Documentation/zigux/phase14-rcu-tree-survey.md");
    try expectContains(rcu.repo_reality, "P14-L16");
    try expectContains(rcu.repo_reality, "phase14-rcu-tree-bridge-blocker");
    try expectContains(rcu.repo_reality, "missing Phase 15 validator");
    try expectContains(rcu.repo_reality, "repo-reality gaps");
    try std.testing.expectEqualStrings("blocked_phase14_followup_still_wider_than_allowed_rcu_seam", rcu.current_blocker);

    const skbuff = manifest.deep_core_blocker_survey[3];
    try std.testing.expectEqualStrings("net/core/skbuff.c", skbuff.anchor);
    try expectContains(skbuff.repo_reality, "Documentation/zigux/phase14-skbuff-bridge-survey.md");
    try expectContains(skbuff.repo_reality, "P14-L11");
    try expectContains(skbuff.repo_reality, "phase14-skbuff-live-ownership-blocker");
    try expectContains(skbuff.repo_reality, "review-first");
    try expectContains(skbuff.repo_reality, "boundary_map_only");
    try expectContains(skbuff.repo_reality, "Documentation/zigux/phase14-core-boundary-traceability.md");
    try expectContains(skbuff.repo_reality, "retained-in-C posture");
    try expectContains(skbuff.repo_reality, "missing Phase 15 validator");
    try expectContains(skbuff.repo_reality, "repo-reality gaps");
    try std.testing.expectEqualStrings("blocked_packet_lifetime_boundary_still_too_wide", skbuff.current_blocker);

    try expectContains(manifest.maintenance_handoff.replay_before_trusting[0], "check-phase15-docs-readme-alignment.py");
    try expectContains(manifest.maintenance_handoff.replay_before_trusting[1], "check-phase15-scripts-readme-alignment.py");
    try expectContains(manifest.maintenance_handoff.replay_before_trusting[2], "check-phase15-review-process-handoff.py");
    try expectContains(manifest.maintenance_handoff.replay_before_trusting[3], "check-phase15-shared-summary-gap.py");
    try expectContains(manifest.maintenance_handoff.replay_before_trusting[4], "phase15_freeze_map_governance.zig");
    try expectContains(manifest.maintenance_handoff.reopen_conditions[2], "no-silent-exception posture");
    try expectContains(manifest.maintenance_handoff.next_future_target, "phase15-shared-summary-gap.md");
    try expectContains(manifest.maintenance_handoff.next_future_target, "validate-phase15.py");
    try expectContains(manifest.maintenance_handoff.next_future_target, "phase15_build.zig");
    try expectContains(manifest.maintenance_handoff.next_future_target, "zigux/Makefile");
    try expectContains(manifest.maintenance_handoff.next_future_target, "phase15 routes");

    const validator_gap = findGap(manifest.gaps, "phase15-shared-validator-route-readback") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("repo_reality_gap_confirmed", validator_gap.status);
    try std.testing.expectEqualStrings("shared_route_gap", validator_gap.kind);
    try expectContains(validator_gap.why_now, "not-found for scripts/zigux/validate-phase15.py");

    const build_gap = findGap(manifest.gaps, "phase15-shared-build-route-readback") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("repo_reality_gap_confirmed", build_gap.status);
    try std.testing.expectEqualStrings("shared_route_gap", build_gap.kind);
    try expectContains(build_gap.why_now, "not-found for zigux/tests/phase15_build.zig");

    const wrapper_gap = findGap(manifest.gaps, "phase15-shared-wrapper-route-readback") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("repo_reality_gap_confirmed", wrapper_gap.status);
    try std.testing.expectEqualStrings("shared_route_gap", wrapper_gap.kind);
    try expectContains(wrapper_gap.why_now, "resolve zigux/Makefile");
    try expectContains(wrapper_gap.why_now, "phase15-validate");
    try expectContains(wrapper_gap.why_now, "phase15-test");
    try expectContains(wrapper_gap.why_now, "phase15");
}

test "phase 15 freeze-map governance doc records the current blocker posture honestly" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const governance_note = try loadFile(io_instance.io(), "Documentation/zigux/phase15-freeze-map-governance.md", 32 * 1024);
    defer std.testing.allocator.free(governance_note);

    try expectContains(governance_note, "PHASE15_STATUS=governance_slice_landed");
    try expectContains(governance_note, "PHASE15_LANE_KEY=P15-L04");
    try expectContains(governance_note, "PHASE15_SLICE=freeze-map-deep-core-blocker-dated-readback-alignment");
    try expectContains(governance_note, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(governance_note, "current-master-readback-2026-05-18");
    try expectContains(governance_note, "shared reminder surfaces still carry as repo-reality gaps on current `master`");
    try expectContains(governance_note, "direct current-master contents reads still return not-found for the broader Phase 15 validator-first and dedicated-build companion paths");
    try expectContains(governance_note, "the current `zigux/Makefile` readback still carries no `phase15-validate`, `phase15-test`, or `phase15` targets");
    try expectContains(governance_note, "exact branch-head parity is not recorded");
    try expectContains(governance_note, "blocked_no_bounded_scheduler_seam");
    try expectContains(governance_note, "blocked_no_bounded_allocator_seam");
    try expectContains(governance_note, "blocked_phase14_followup_still_wider_than_allowed_rcu_seam");
    try expectContains(governance_note, "blocked_packet_lifetime_boundary_still_too_wide");
    try expectContains(governance_note, "lane P14-L16 still records blocked `phase14-rcu-tree-bridge-blocker`");
    try expectContains(governance_note, "`Documentation/zigux/phase14-skbuff-bridge-survey.md` on lane P14-L11 still records blocked `phase14-skbuff-live-ownership-blocker`");
    try expectContains(governance_note, "surviving skbuff packet review-first and `boundary_map_only`");
    try expectContains(governance_note, "`Documentation/zigux/phase14-core-boundary-traceability.md` still keeps skbuff in retained-in-C posture");
    try expectContains(governance_note, "## Maintenance-Mode Handoff");
    try expectContains(governance_note, "current lane posture: `maintenance_mode`");
    try expectContains(governance_note, "check-phase15-docs-readme-alignment.py");
    try expectContains(governance_note, "check-phase15-review-process-handoff.py");
    try expectContains(governance_note, "check-phase15-shared-summary-gap.py");
    try expectContains(governance_note, "scripts/zigux/validate-phase15.py");
    try expectContains(governance_note, "zigux/tests/phase15_build.zig");
    try expectContains(governance_note, "current-master contents reads now resolve `zigux/Makefile`");
    try expectContains(governance_note, "those wrapper route names remain gap vocabulary rather than direct landed evidence");
    try expectContains(governance_note, "phase15-freeze-map-manifest");
    try expectContains(governance_note, "phase15-freeze-map-governance-gate");
    try expectContains(governance_note, "phase15-shared-validator-route-readback");
    try expectContains(governance_note, "phase15-shared-build-route-readback");
    try expectContains(governance_note, "phase15-shared-wrapper-route-readback");
}

test "phase 15 freeze-map required terms and maintenance handoff stay aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try loadFile(io_instance.io(), "zigux/tests/phase15_freeze_map_manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const freeze_map = try loadFile(io_instance.io(), "Documentation/zigux/freeze-map.md", 24 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const governance_note = try loadFile(io_instance.io(), "Documentation/zigux/phase15-freeze-map-governance.md", 32 * 1024);
    defer std.testing.allocator.free(governance_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    for (parsed.value.governance_requirements) |requirement| {
        for (requirement.required_terms) |term| {
            try expectContains(freeze_map, term);
        }
    }

    try expectContains(governance_note, parsed.value.maintenance_handoff.current_lane_posture);
    for (parsed.value.maintenance_handoff.replay_before_trusting) |command| {
        try expectContains(governance_note, command);
    }
    for (parsed.value.maintenance_handoff.reopen_conditions) |condition| {
        try expectContainsWithoutBackticks(governance_note, condition);
    }
    try expectContainsWithoutBackticks(governance_note, parsed.value.maintenance_handoff.next_future_target);

    for (parsed.value.blocker_ownership) |ownership| {
        try expectContains(governance_note, ownership.anchor);
        try expectContains(governance_note, ownership.owner);
        try expectContains(governance_note, ownership.required_approver_set);
        try expectContains(governance_note, ownership.rollback_owner);
        try expectContains(governance_note, ownership.evidence_archive_path);
        try expectContains(governance_note, ownership.benchmark_notes);
        try expectContains(governance_note, ownership.replay_command);
        try expectContains(governance_note, ownership.latest_blocker_disposition);
    }

    for (parsed.value.deep_core_blocker_survey) |survey| {
        try expectContains(governance_note, survey.anchor);
        try expectContains(governance_note, survey.roadmap_basis);
        try expectContains(governance_note, survey.repo_reality);
        try expectContains(governance_note, survey.current_blocker);
    }
}

test "phase 15 freeze-map linked blocker evidence stays explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const rcu_note = try loadFile(io_instance.io(), "Documentation/zigux/phase14-rcu-tree-survey.md", 32 * 1024);
    defer std.testing.allocator.free(rcu_note);
    try expectContains(rcu_note, "PHASE14_LANE_KEY=P14-L16");
    try expectContains(rcu_note, "blocked by `phase14-rcu-tree-bridge-blocker`");
    try expectContains(rcu_note, "That is still a freeze-in-C posture, not a review-ready bridge seam.");

    const skbuff_note = try loadFile(io_instance.io(), "Documentation/zigux/phase14-skbuff-bridge-survey.md", 24 * 1024);
    defer std.testing.allocator.free(skbuff_note);
    try expectContains(skbuff_note, "PHASE14_LANE_KEY=P14-L11");
    try expectContains(skbuff_note, "PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker");
    try expectContains(skbuff_note, "current `master` still ships the bounded skbuff anchor packet files");
    try expectContains(skbuff_note, "review-first and `boundary_map_only`");

    const skbuff_traceability = try loadFile(io_instance.io(), "Documentation/zigux/phase14-core-boundary-traceability.md", 32 * 1024);
    defer std.testing.allocator.free(skbuff_traceability);
    try expectContains(skbuff_traceability, "`net/core/skbuff.c`: `Freeze In C Initially`");
    try expectContains(skbuff_traceability, "retained-in-C posture");
    try expectContains(skbuff_traceability, "must not imply a live `net/core/skbuff_bridge.zig` helper or any skbuff-local compile route");
}