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

const ScorecardEvidenceArchive = struct {
    decision_record_path: []const u8,
    linked_evidence: []const []const u8,
    benchmark_notes_status: []const u8,
    replay_command: []const u8,
    latest_blocker_disposition: []const u8,
};

const ScorecardAnchor = struct {
    path: []const u8,
    lane_owner: []const u8,
    phase: []const u8,
    current_status_bucket: []const u8,
    required_approver_set: []const u8,
    validation_gate_summary: []const u8,
    rollback_owner: []const u8,
    evidence_archive: ScorecardEvidenceArchive,
};

const ScorecardMetrics = struct {
    active_freeze_in_c_anchor_count: usize,
    blocked_status_change_anchor_count: usize,
};

const ScorecardManifest = struct {
    surveyed_commit: []const u8,
    metrics: ScorecardMetrics,
    anchors: []const ScorecardAnchor,
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

test "phase 15 freeze-map governance manifest records the dated-readback blocker survey" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try loadFile(io_instance.io(), "zigux/tests/phase15_freeze_map_manifest.json", 48 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P15-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-11", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("dated_master_readback", manifest.surveyed_commit_mode);
    try expectContains(manifest.surveyed_commit_mode_reason, "dated master-readback marker");
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 4), manifest.freeze_in_c_targets.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.study_only_targets.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.governance_requirements.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.blocker_ownership.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.deep_core_blocker_survey.len);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.maintenance_handoff.current_lane_posture);
    try std.testing.expectEqual(@as(usize, 4), manifest.maintenance_handoff.replay_before_trusting.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.maintenance_handoff.reopen_conditions.len);
    try std.testing.expectEqual(@as(usize, 15), manifest.gaps.len);

    const sched = manifest.blocker_ownership[0];
    try std.testing.expectEqualStrings("kernel/sched/core.c", sched.anchor);
    try std.testing.expectEqualStrings("Architecture Council + PMO / Release Management", sched.required_approver_set);

    const skbuff = manifest.deep_core_blocker_survey[3];
    try std.testing.expectEqualStrings("net/core/skbuff.c", skbuff.anchor);
    try expectContains(skbuff.repo_reality, "P14-Y03");
    try expectContains(skbuff.repo_reality, "phase14-skbuff-live-ownership-blocker");
    try std.testing.expectEqualStrings("blocked_packet_lifetime_boundary_still_too_wide", skbuff.current_blocker);

    try expectContains(manifest.maintenance_handoff.replay_before_trusting[0], "validate-phase15.py");
    try expectContains(manifest.maintenance_handoff.replay_before_trusting[3], "phase15_freeze_map_governance.zig");
    try expectContains(manifest.maintenance_handoff.reopen_conditions[2], "no-silent-exception posture");
    try expectContains(manifest.maintenance_handoff.next_future_target, "freeze-map-local");

    const required_field_sync = findGap(manifest.gaps, "phase15-review-process-required-field-sync") orelse return error.MissingGap;
    try expectContains(required_field_sync.why_now, "required approver set");

    const approver_sync = findGap(manifest.gaps, "phase15-freeze-map-required-approver-sync") orelse return error.MissingGap;
    try expectContains(approver_sync.why_now, "required-approver-set inventory");

    const dated_refresh = findGap(manifest.gaps, "phase15-dated-readback-provenance-refresh") orelse return error.MissingGap;
    try expectContains(dated_refresh.why_now, "drifted behind current master");

    const maintenance_handoff = findGap(manifest.gaps, "phase15-freeze-map-maintenance-handoff") orelse return error.MissingGap;
    try expectContains(maintenance_handoff.why_now, "when to reopen");
}

test "phase 15 freeze-map governance doc records the current blocker posture honestly" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const governance_note = try loadFile(io_instance.io(), "Documentation/zigux/phase15-freeze-map-governance.md", 28 * 1024);
    defer std.testing.allocator.free(governance_note);

    try expectContains(governance_note, "PHASE15_STATUS=governance_slice_landed");
    try expectContains(governance_note, "PHASE15_LANE_KEY=P15-L04");
    try expectContains(governance_note, "PHASE15_SLICE=freeze-map-deep-core-blocker-dated-readback-alignment");
    try expectContains(governance_note, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(governance_note, "current-master-readback-2026-05-11");
    try expectContains(governance_note, "previously recorded verified head `4fc891b380cdd2991dff7676ade7f844df1b55fd` no longer matched current `master`");
    try expectContains(governance_note, "exact branch-head parity is not recorded");
    try expectContains(governance_note, "blocked_no_bounded_scheduler_seam");
    try expectContains(governance_note, "blocked_no_bounded_allocator_seam");
    try expectContains(governance_note, "blocked_phase14_followup_still_wider_than_allowed_rcu_seam");
    try expectContains(governance_note, "blocked_packet_lifetime_boundary_still_too_wide");
    try expectContains(governance_note, "lane P14-L16 still records blocked phase14-rcu-tree-bridge-blocker");
    try expectContains(governance_note, "lane P14-Y03 still records blocked phase14-skbuff-live-ownership-blocker");
    try expectContains(governance_note, "## Maintenance-Mode Handoff");
    try expectContains(governance_note, "current lane posture: `maintenance_mode`");
    try expectContains(governance_note, "check-phase15-review-process-handoff.py");
    try expectContains(governance_note, "shared-summary, parity-scorecard, or readiness packets");
    try expectContains(governance_note, "phase15-review-process-required-field-sync");
    try expectContains(governance_note, "phase15-freeze-map-required-approver-sync");
    try expectContains(governance_note, "phase15-dated-readback-provenance-refresh");
    try expectContains(governance_note, "phase15-freeze-map-maintenance-handoff");
}

test "phase 15 freeze-map required terms, maintenance handoff, and scorecard ownership stay aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try loadFile(io_instance.io(), "zigux/tests/phase15_freeze_map_manifest.json", 48 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const freeze_map = try loadFile(io_instance.io(), "Documentation/zigux/freeze-map.md", 20 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const governance_note = try loadFile(io_instance.io(), "Documentation/zigux/phase15-freeze-map-governance.md", 28 * 1024);
    defer std.testing.allocator.free(governance_note);

    const scorecard_doc = try loadFile(io_instance.io(), "Documentation/zigux/phase15-parity-scorecard.md", 24 * 1024);
    defer std.testing.allocator.free(scorecard_doc);

    const scorecard_json = try loadFile(io_instance.io(), "zigux/tests/phase15_parity_scorecard.json", 48 * 1024);
    defer std.testing.allocator.free(scorecard_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const scorecard = try std.json.parseFromSlice(ScorecardManifest, std.testing.allocator, scorecard_json, .{});
    defer scorecard.deinit();

    try std.testing.expect(scorecard.value.surveyed_commit.len != 0);
    try std.testing.expectEqual(parsed.value.freeze_in_c_targets.len, scorecard.value.metrics.active_freeze_in_c_anchor_count);
    try std.testing.expectEqual(parsed.value.blocker_ownership.len, scorecard.value.metrics.blocked_status_change_anchor_count);
    try std.testing.expectEqual(parsed.value.deep_core_blocker_survey.len, scorecard.value.metrics.blocked_status_change_anchor_count);

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

    for (scorecard.value.anchors, parsed.value.blocker_ownership) |anchor, ownership| {
        try std.testing.expectEqualStrings(ownership.anchor, anchor.path);
        try std.testing.expectEqualStrings(ownership.owner, anchor.lane_owner);
        try std.testing.expectEqualStrings(ownership.phase, anchor.phase);
        try std.testing.expectEqualStrings(ownership.status_bucket, anchor.current_status_bucket);
        try std.testing.expectEqualStrings(ownership.required_approver_set, anchor.required_approver_set);
        try std.testing.expectEqualStrings(ownership.validation_gate, anchor.validation_gate_summary);
        try std.testing.expectEqualStrings(ownership.rollback_owner, anchor.rollback_owner);
        try std.testing.expectEqualStrings(ownership.evidence_archive_path, anchor.evidence_archive.decision_record_path);
        try std.testing.expectEqualStrings(ownership.benchmark_notes, anchor.evidence_archive.benchmark_notes_status);
        try std.testing.expectEqualStrings(ownership.replay_command, anchor.evidence_archive.replay_command);
        try std.testing.expectEqualStrings(ownership.latest_blocker_disposition, anchor.evidence_archive.latest_blocker_disposition);

        try expectContains(governance_note, anchor.lane_owner);
        try expectContains(governance_note, anchor.phase);
        try expectContains(governance_note, anchor.current_status_bucket);
        try expectContains(governance_note, anchor.required_approver_set);
        try expectContains(governance_note, anchor.validation_gate_summary);
        try expectContains(governance_note, anchor.rollback_owner);
        try expectContains(governance_note, anchor.evidence_archive.decision_record_path);
        try expectContains(governance_note, anchor.evidence_archive.benchmark_notes_status);
        try expectContains(governance_note, anchor.evidence_archive.replay_command);
        try expectContains(governance_note, anchor.evidence_archive.latest_blocker_disposition);

        try expectContains(scorecard_doc, anchor.path);
        try expectContains(scorecard_doc, anchor.phase);
        try expectContains(scorecard_doc, anchor.current_status_bucket);
        try expectContains(scorecard_doc, anchor.required_approver_set);
        try expectContains(scorecard_doc, anchor.validation_gate_summary);
        try expectContains(scorecard_doc, anchor.rollback_owner);
        try expectContains(scorecard_doc, anchor.evidence_archive.decision_record_path);
        try expectContains(scorecard_doc, anchor.evidence_archive.benchmark_notes_status);
        try expectContains(scorecard_doc, anchor.evidence_archive.replay_command);
        try expectContains(scorecard_doc, anchor.evidence_archive.latest_blocker_disposition);
    }
}

test "phase 15 freeze-map linked blocker evidence stays explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const rcu_note = try loadFile(io_instance.io(), "Documentation/zigux/phase14-rcu-tree-survey.md", 32 * 1024);
    defer std.testing.allocator.free(rcu_note);
    try expectContains(rcu_note, "PHASE14_LANE_KEY=P14-L16");
    try expectContains(rcu_note, "blocked `phase14-rcu-tree-bridge-blocker`");
    try expectContains(rcu_note, "Keep this packet blocked until a real Architecture Council reopen record");

    const skbuff_note = try loadFile(io_instance.io(), "Documentation/zigux/phase14-skbuff-bridge-survey.md", 24 * 1024);
    defer std.testing.allocator.free(skbuff_note);
    try expectContains(skbuff_note, "PHASE14_LANE_KEY=P14-Y03");
    try expectContains(skbuff_note, "blocked `phase14-skbuff-live-ownership-blocker`");
    try expectContains(skbuff_note, "no smaller review-only skbuff follow-up remains before the live ownership blocker");
}