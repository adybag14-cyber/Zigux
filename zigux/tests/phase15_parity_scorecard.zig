const std = @import("std");

const ScorecardPosture = struct {
    architecture_council_status_change_approval_recorded: bool,
    scorecard_role: []const u8,
};

const ScorecardMetrics = struct {
    active_freeze_in_c_anchor_count: usize,
    blocked_status_change_anchor_count: usize,
    phase15_governance_only_blocker_anchor_count: usize,
    phase14_coupled_blocker_anchor_count: usize,
    anchors_still_blocked_on_prior_phase_bridge_evidence: usize,
    study_only_anchors_tracked_outside_scorecard: usize,
    architecture_council_status_change_approval_count: usize,
};

const EvidenceArchive = struct {
    decision_record_path: []const u8,
    linked_evidence: []const []const u8,
    benchmark_notes_status: []const u8,
    replay_command: []const u8,
    latest_blocker_disposition: []const u8,
};

const Anchor = struct {
    path: []const u8,
    lane_owner: []const u8,
    phase: []const u8,
    current_status_bucket: []const u8,
    required_approver_set: []const u8,
    validation_gate_summary: []const u8,
    rollback_owner: []const u8,
    current_blocker: []const u8,
    evidence_archive: EvidenceArchive,
    next_honest_posture: []const u8,
};

const Manifest = struct {
    status: []const u8,
    lane_key: []const u8,
    slice: []const u8,
    provenance_mode: []const u8,
    surveyed_commit: []const u8,
    posture: ScorecardPosture,
    metrics: ScorecardMetrics,
    anchors: []const Anchor,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMetricLine(scorecard_doc: []const u8, label: []const u8, value: usize) !void {
    var line_buffer: [128]u8 = undefined;
    const rendered = try std.fmt.bufPrint(&line_buffer, "{s}: `{d}`", .{ label, value });
    try expectContains(scorecard_doc, rendered);
}

fn expectAnchorPacketAlignment(scorecard_doc: []const u8, governance_note: []const u8, anchor: Anchor) !void {
    try std.testing.expectEqualStrings("Phase 15", anchor.phase);
    try std.testing.expectEqualStrings("freeze_in_c", anchor.current_status_bucket);
    try std.testing.expectEqualStrings(anchor.current_blocker, anchor.evidence_archive.latest_blocker_disposition);

    try expectContains(scorecard_doc, anchor.path);
    try expectContains(scorecard_doc, anchor.phase);
    try expectContains(scorecard_doc, anchor.current_status_bucket);
    try expectContains(scorecard_doc, anchor.lane_owner);
    try expectContains(scorecard_doc, anchor.required_approver_set);
    try expectContains(scorecard_doc, anchor.validation_gate_summary);
    try expectContains(scorecard_doc, anchor.rollback_owner);
    try expectContains(scorecard_doc, anchor.current_blocker);
    try expectContains(scorecard_doc, anchor.evidence_archive.decision_record_path);
    try expectContains(scorecard_doc, anchor.evidence_archive.benchmark_notes_status);
    try expectContains(scorecard_doc, anchor.evidence_archive.replay_command);
    try expectContains(scorecard_doc, anchor.next_honest_posture);
    for (anchor.evidence_archive.linked_evidence) |linked_evidence| {
        try expectContains(scorecard_doc, linked_evidence);
    }

    try expectContains(governance_note, anchor.path);
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
}

fn countStatusBucket(anchors: []const Anchor, expected_status_bucket: []const u8) usize {
    var count: usize = 0;
    for (anchors) |anchor| {
        if (std.mem.eql(u8, anchor.current_status_bucket, expected_status_bucket)) {
            count += 1;
        }
    }
    return count;
}

fn countPhase14CoupledAnchors(anchors: []const Anchor) usize {
    var count: usize = 0;
    for (anchors) |anchor| {
        for (anchor.evidence_archive.linked_evidence) |linked_evidence| {
            if (std.mem.startsWith(u8, linked_evidence, "Documentation/zigux/phase14-")) {
                count += 1;
                break;
            }
        }
    }
    return count;
}

fn countPhase15GovernanceOnlyAnchors(anchors: []const Anchor) usize {
    return anchors.len - countPhase14CoupledAnchors(anchors);
}

test "phase 15 parity scorecard manifest keeps the blocked posture explicit" {
    const manifest_json = try readRepoFile("zigux/tests/phase15_parity_scorecard.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("parity_scorecard_slice_landed", manifest.status);
    try std.testing.expectEqualStrings("P15-Y03", manifest.lane_key);
    try std.testing.expectEqualStrings("parity-scorecard-baseline", manifest.slice);
    try std.testing.expectEqualStrings("dated_master_readback", manifest.provenance_mode);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-13", manifest.surveyed_commit);
    try std.testing.expect(!manifest.posture.architecture_council_status_change_approval_recorded);
    try std.testing.expectEqualStrings("blocked_posture_accounting_not_port_readiness", manifest.posture.scorecard_role);
    try std.testing.expectEqual(@as(usize, 4), manifest.metrics.active_freeze_in_c_anchor_count);
    try std.testing.expectEqual(@as(usize, 4), manifest.metrics.blocked_status_change_anchor_count);
    try std.testing.expectEqual(@as(usize, 2), manifest.metrics.phase15_governance_only_blocker_anchor_count);
    try std.testing.expectEqual(@as(usize, 2), manifest.metrics.phase14_coupled_blocker_anchor_count);
    try std.testing.expectEqual(@as(usize, 2), manifest.metrics.anchors_still_blocked_on_prior_phase_bridge_evidence);
    try std.testing.expectEqual(@as(usize, 2), manifest.metrics.study_only_anchors_tracked_outside_scorecard);
    try std.testing.expectEqual(@as(usize, 0), manifest.metrics.architecture_council_status_change_approval_count);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(
        manifest.metrics.architecture_council_status_change_approval_count > 0,
        manifest.posture.architecture_council_status_change_approval_recorded,
    );
    try std.testing.expectEqual(
        manifest.metrics.active_freeze_in_c_anchor_count,
        countStatusBucket(manifest.anchors, "freeze_in_c"),
    );
    try std.testing.expectEqual(
        manifest.metrics.blocked_status_change_anchor_count,
        manifest.anchors.len,
    );
    try std.testing.expectEqual(
        manifest.metrics.phase15_governance_only_blocker_anchor_count,
        countPhase15GovernanceOnlyAnchors(manifest.anchors),
    );
    try std.testing.expectEqual(
        manifest.metrics.phase14_coupled_blocker_anchor_count,
        countPhase14CoupledAnchors(manifest.anchors),
    );
    try std.testing.expectEqual(
        manifest.metrics.phase14_coupled_blocker_anchor_count,
        manifest.metrics.anchors_still_blocked_on_prior_phase_bridge_evidence,
    );
    try std.testing.expectEqual(
        manifest.metrics.phase15_governance_only_blocker_anchor_count + manifest.metrics.phase14_coupled_blocker_anchor_count,
        manifest.metrics.blocked_status_change_anchor_count,
    );

    const sched = manifest.anchors[0];
    try std.testing.expectEqualStrings("kernel/sched/core.c", sched.path);
    try std.testing.expectEqualStrings("Architecture Council", sched.lane_owner);
    try std.testing.expectEqualStrings("freeze_in_c", sched.current_status_bucket);
    try std.testing.expectEqualStrings("Architecture Council + PMO / Release Management", sched.required_approver_set);
    try std.testing.expectEqualStrings("blocked_no_bounded_scheduler_seam", sched.current_blocker);
    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
        sched.evidence_archive.decision_record_path,
    );
    try std.testing.expectEqualStrings(
        "zig build test --build-file zigux/tests/phase15_build.zig",
        sched.evidence_archive.replay_command,
    );

    const skbuff = manifest.anchors[3];
    try std.testing.expectEqualStrings("net/core/skbuff.c", skbuff.path);
    try std.testing.expectEqualStrings("Shared Subsystems Pod", skbuff.lane_owner);
    try std.testing.expectEqualStrings("blocked_packet_lifetime_boundary_still_too_wide", skbuff.current_blocker);
    try std.testing.expectEqualStrings(
        "pending_until_skbuff_followup_is_narrower_than_lifetime_boundary",
        skbuff.evidence_archive.benchmark_notes_status,
    );
}

test "phase 15 parity scorecard doc stays aligned with the machine readable scorecard" {
    const scorecard_doc = try readRepoFile("Documentation/zigux/phase15-parity-scorecard.md", 24 * 1024);
    defer std.testing.allocator.free(scorecard_doc);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 20 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const governance_note = try readRepoFile("Documentation/zigux/phase15-freeze-map-governance.md", 32 * 1024);
    defer std.testing.allocator.free(governance_note);

    const manifest_json = try readRepoFile("zigux/tests/phase15_parity_scorecard.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    try expectContains(scorecard_doc, "P15-Y03");
    try expectContains(scorecard_doc, "parity-scorecard-baseline");
    try expectContains(scorecard_doc, "blocked_posture_accounting_not_port_readiness");
    try expectContains(scorecard_doc, "current-master-readback-2026-05-13");
    try expectMetricLine(scorecard_doc, "active freeze-in-C anchor count", parsed.value.metrics.active_freeze_in_c_anchor_count);
    try expectMetricLine(scorecard_doc, "blocked status-change anchor count", parsed.value.metrics.blocked_status_change_anchor_count);
    try expectMetricLine(scorecard_doc, "anchors blocked entirely within Phase 15 governance evidence", parsed.value.metrics.phase15_governance_only_blocker_anchor_count);
    try expectMetricLine(scorecard_doc, "Phase 14 coupled blocker anchor count", parsed.value.metrics.phase14_coupled_blocker_anchor_count);
    try expectMetricLine(scorecard_doc, "anchors still blocked on prior-phase bridge evidence", parsed.value.metrics.anchors_still_blocked_on_prior_phase_bridge_evidence);
    try expectMetricLine(scorecard_doc, "study-only anchors tracked outside this scorecard", parsed.value.metrics.study_only_anchors_tracked_outside_scorecard);
    try expectMetricLine(scorecard_doc, "Architecture Council approvals recorded for status change", parsed.value.metrics.architecture_council_status_change_approval_count);

    for (parsed.value.anchors) |anchor| {
        try expectAnchorPacketAlignment(scorecard_doc, governance_note, anchor);
        try expectContains(freeze_map, anchor.path);
    }
}
