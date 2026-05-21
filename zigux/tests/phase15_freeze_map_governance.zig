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

test "phase 15 freeze-map governance manifest records the current route-gap posture" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try loadFile(io_instance.io(), "zigux/tests/phase15_freeze_map_manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P15-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-21", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("dated_master_readback", manifest.surveyed_commit_mode);
    try expectContains(manifest.surveyed_commit_mode_reason, "lane-owner replay");
    try expectContains(manifest.surveyed_commit_mode_reason, "repo-reality gaps");
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 4), manifest.freeze_in_c_targets.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.study_only_targets.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.governance_requirements.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.blocker_ownership.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.deep_core_blocker_survey.len);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.maintenance_handoff.current_lane_posture);
    try std.testing.expectEqual(@as(usize, 5), manifest.maintenance_handoff.replay_before_trusting.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.maintenance_handoff.reopen_conditions.len);
    try std.testing.expectEqual(@as(usize, 16), manifest.gaps.len);
    try expectContains(manifest.maintenance_handoff.next_future_target, "direct contents readback still resolves");
    try expectContains(manifest.maintenance_handoff.next_future_target, "still fail to materialize");
    try expectContains(manifest.maintenance_handoff.next_future_target, "phase15-validate, phase15-test, and phase15");

    const rcu_survey = manifest.deep_core_blocker_survey[2];
    try expectContains(rcu_survey.repo_reality, "Documentation/zigux/phase14-rcu-tree-survey.md");
    try expectContains(rcu_survey.repo_reality, "P14-L16");
    try expectContains(rcu_survey.repo_reality, "phase14-rcu-tree-bridge-blocker");
    try expectContains(rcu_survey.repo_reality, "still do not materialize scripts/zigux/validate-phase15.py or zigux/tests/phase15_build.zig");
    try expectContains(rcu_survey.repo_reality, "direct contents readback now resolves zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig");
    try expectContains(rcu_survey.repo_reality, "zigux/Makefile still carries no phase15-validate, phase15-test, or phase15 routes");

    const lane_owner_gap = findGap(manifest.gaps, "phase15-shared-lane-owner-readback") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("materialized_in_contents_readback", lane_owner_gap.status);
    try std.testing.expectEqualStrings("shared_route_presence", lane_owner_gap.kind);
    try expectContains(lane_owner_gap.why_now, "Direct contents readback resolves zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig");

    const validator_gap = findGap(manifest.gaps, "phase15-shared-validator-route-readback") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("repo_reality_gap_confirmed", validator_gap.status);
    try std.testing.expectEqualStrings("shared_route_gap", validator_gap.kind);
    try expectContains(validator_gap.why_now, "still do not materialize scripts/zigux/validate-phase15.py");

    const build_gap = findGap(manifest.gaps, "phase15-shared-build-route-readback") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("repo_reality_gap_confirmed", build_gap.status);
    try std.testing.expectEqualStrings("shared_route_gap", build_gap.kind);
    try expectContains(build_gap.why_now, "still do not materialize zigux/tests/phase15_build.zig");
}

test "phase 15 freeze-map governance doc records the refreshed route classification honestly" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const governance_note = try loadFile(io_instance.io(), "Documentation/zigux/phase15-freeze-map-governance.md", 48 * 1024);
    defer std.testing.allocator.free(governance_note);

    try expectContains(governance_note, "current-master-readback-2026-05-21");
    try expectContains(governance_note, "returns not-found for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`");
    try expectContains(governance_note, "direct contents readback resolves `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`");
    try expectContains(governance_note, "validator-first, dedicated-build, and wrapper-route names in adjacent repo-reality-gap vocabulary");
    try expectContains(governance_note, "lane `P14-L16`");
    try expectContains(governance_note, "phase14-rcu-tree-bridge-blocker");
    try expectContains(governance_note, "lane `P14-L11`");
    try expectContains(governance_note, "phase14-skbuff-live-ownership-blocker");
    try expectContains(governance_note, "materialized_in_contents_readback `phase15-shared-lane-owner-readback`");
    try expectContains(governance_note, "repo_reality_gap_confirmed `phase15-shared-validator-route-readback`");
    try expectContains(governance_note, "repo_reality_gap_confirmed `phase15-shared-build-route-readback`");
    try expectContains(governance_note, "repo_reality_gap_confirmed `phase15-shared-wrapper-route-readback`");
    try expectContains(governance_note, "blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`");
}

test "phase 15 freeze-map required terms and maintenance handoff stay aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try loadFile(io_instance.io(), "zigux/tests/phase15_freeze_map_manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const freeze_map = try loadFile(io_instance.io(), "Documentation/zigux/freeze-map.md", 24 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const governance_note = try loadFile(io_instance.io(), "Documentation/zigux/phase15-freeze-map-governance.md", 48 * 1024);
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
    try expectContains(governance_note, "returns not-found for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`");
    try expectContains(governance_note, "direct contents readback resolves `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`");
    try expectContains(governance_note, "still carries no `phase15-validate`, `phase15-test`, or `phase15`");
}

test "phase 15 freeze-map linked blocker evidence stays explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const rcu_note = try loadFile(io_instance.io(), "Documentation/zigux/phase14-rcu-tree-survey.md", 8 * 1024);
    defer std.testing.allocator.free(rcu_note);
    try expectContains(rcu_note, "PHASE14_LANE_KEY=P14-L16");
    try expectContains(rcu_note, "blocked by `phase14-rcu-tree-bridge-blocker`");
    try expectContains(rcu_note, "That is still a freeze-in-C posture, not a review-ready bridge seam.");

    const skbuff_note = try loadFile(io_instance.io(), "Documentation/zigux/phase14-skbuff-bridge-survey.md", 8 * 1024);
    defer std.testing.allocator.free(skbuff_note);
    try expectContains(skbuff_note, "PHASE14_LANE_KEY=P14-L11");
    try expectContains(skbuff_note, "PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker");
    try expectContains(skbuff_note, "review-only skbuff bridge packet again");
    try expectContains(skbuff_note, "explicit stay-in-C ownership for qdisc-facing publication");

    const skbuff_traceability = try loadFile(io_instance.io(), "Documentation/zigux/phase14-core-boundary-traceability.md", 8 * 1024);
    defer std.testing.allocator.free(skbuff_traceability);
    try expectContains(skbuff_traceability, "`net/core/skbuff.c`: `Freeze In C Initially`");
    try expectContains(skbuff_traceability, "retained-in-C posture");
    try expectContains(skbuff_traceability, "must not imply a live `net/core/skbuff_bridge.zig` helper or any skbuff-local compile route");
}
