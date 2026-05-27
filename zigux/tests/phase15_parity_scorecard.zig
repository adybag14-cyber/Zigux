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

const FreezeMapBlockerOwnership = struct {
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

const FreezeMapManifest = struct {
    freeze_in_c_targets: []const []const u8,
    study_only_targets: []const []const u8,
    blocker_ownership: []const FreezeMapBlockerOwnership,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |entry| {
        if (std.mem.eql(u8, entry, needle)) return;
    }
    return error.TestUnexpectedResult;
}

fn expectMetricLine(scorecard_doc: []const u8, label: []const u8, value: usize) !void {
    var line_buffer: [128]u8 = undefined;
    const rendered = try std.fmt.bufPrint(&line_buffer, "{s}: `{d}`", .{ label, value });
    try expectContains(scorecard_doc, rendered);
}

fn expectCurrentReminderRoute(scorecard_doc: []const u8) !void {
    try expectContains(scorecard_doc, "## Current reminder route");
    try expectContains(scorecard_doc, "python3 scripts/zigux/check-phase15-docs-readme-alignment.py");
    try expectContains(scorecard_doc, "python3 scripts/zigux/check-phase15-scripts-readme-alignment.py");
    try expectContains(scorecard_doc, "python3 scripts/zigux/check-phase15-tests-readme-alignment.py");
    try expectContains(scorecard_doc, "python3 scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(scorecard_doc, "python3 scripts/zigux/check-phase15-shared-summary-gap.py");
    try expectContains(scorecard_doc, "zig test zigux/tests/phase15_parity_scorecard.zig");
    try expectContains(scorecard_doc, "anchor-level blocker evidence stays reviewable through `zig test zigux/tests/phase15_freeze_map_governance.zig`");
    try expectContains(scorecard_doc, "validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`");
    try expectContains(scorecard_doc, "shared replay build route is directly readable on current `master` through `zigux/tests/phase15_build.zig` and `zig build test --build-file zigux/tests/phase15_build.zig`");
    try expectContains(scorecard_doc, "current `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15` targets, so the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes remain wrapper-gap vocabulary rather than shipped reminder-route evidence");
}

fn expectCurrentBoundedStepHandoff(scorecard_doc: []const u8) !void {
    try expectContains(scorecard_doc, "## Next bounded step");
    try expectContains(scorecard_doc, "Keep the scorecard parked until one of the named reopen triggers fits the evidence, the blocker posture changes, or the direct reminder-route wording, machine-readable companion inventory, and current-master wrapper-gap or workflow-gap inventory drift enough that the aggregate metrics or anchor records need another truthfulness refresh.");
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

fn expectFreezeMapAnchorAlignment(anchor: Anchor, blocker_ownership: FreezeMapBlockerOwnership) !void {
    try std.testing.expectEqualStrings(anchor.path, blocker_ownership.anchor);
    try std.testing.expectEqualStrings(anchor.lane_owner, blocker_ownership.owner);
    try std.testing.expectEqualStrings(anchor.phase, blocker_ownership.phase);
    try std.testing.expectEqualStrings(anchor.current_status_bucket, blocker_ownership.status_bucket);
    try std.testing.expectEqualStrings(anchor.required_approver_set, blocker_ownership.required_approver_set);
    try std.testing.expectEqualStrings(anchor.validation_gate_summary, blocker_ownership.validation_gate);
    try std.testing.expectEqualStrings(anchor.rollback_owner, blocker_ownership.rollback_owner);
    try std.testing.expectEqualStrings(anchor.evidence_archive.decision_record_path, blocker_ownership.evidence_archive_path);
    try std.testing.expectEqualStrings(anchor.evidence_archive.benchmark_notes_status, blocker_ownership.benchmark_notes);
    try std.testing.expectEqualStrings(anchor.evidence_archive.replay_command, blocker_ownership.replay_command);
    try std.testing.expectEqualStrings(anchor.evidence_archive.latest_blocker_disposition, blocker_ownership.latest_blocker_disposition);
}

fn expectAnchorsOmitPath(anchors: []const Anchor, forbidden_path: []const u8) !void {
    for (anchors) |anchor| {
        try std.testing.expect(!std.mem.eql(u8, anchor.path, forbidden_path));
    }
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

fn expectEvidenceArchiveTruthfulness(manifest: Manifest) !void {
    for (manifest.anchors) |anchor| {
        const archive_doc = try readRepoFile(anchor.evidence_archive.decision_record_path, 12 * 1024);
        defer std.testing.allocator.free(archive_doc);

        try expectContains(archive_doc, "`PHASE=Phase 15`");
        try expectContains(archive_doc, "`LANE_KEY=P15-L03`");
        try expectContains(archive_doc, "`SURVEYED_COMMIT=current-master-readback-2026-05-25`");
        try expectContains(archive_doc, "`REVIEW_STATUS=blocked_review`");
        try expectContains(archive_doc, "current Architecture Council status-change approval: `not_recorded`");
        try expectContains(archive_doc, anchor.path);
        try expectContains(archive_doc, anchor.lane_owner);
        try expectContains(archive_doc, anchor.phase);
        try expectContains(archive_doc, anchor.current_status_bucket);
        try expectContains(archive_doc, anchor.required_approver_set);
        try expectContains(archive_doc, anchor.rollback_owner);
        try expectContains(archive_doc, anchor.validation_gate_summary);
        try expectContains(archive_doc, anchor.evidence_archive.decision_record_path);
        try expectContains(archive_doc, anchor.evidence_archive.latest_blocker_disposition);
        try expectContains(archive_doc, anchor.evidence_archive.benchmark_notes_status);
        try expectContains(archive_doc, anchor.evidence_archive.replay_command);
        try expectContains(archive_doc, "Documentation/zigux/phase15-parity-scorecard.md");
        try expectContains(archive_doc, "Documentation/zigux/phase15-indefinite-c-policy.md");

        for (anchor.evidence_archive.linked_evidence) |linked_evidence| {
            try expectContains(archive_doc, linked_evidence);
        }
    }
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
    try std.testing.expectEqualStrings("P15-L03", manifest.lane_key);
    try std.testing.expectEqualStrings("parity-scorecard-baseline", manifest.slice);
    try std.testing.expectEqualStrings("dated_master_readback", manifest.provenance_mode);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-27", manifest.surveyed_commit);
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
        "zig test zigux/tests/phase15_freeze_map_governance.zig",
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
    try expectSliceContains(
        skbuff.evidence_archive.linked_evidence,
        "Documentation/zigux/phase14-core-boundary-traceability.md",
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

    const freeze_map_manifest_json = try readRepoFile("zigux/tests/phase15_freeze_map_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(freeze_map_manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const freeze_map_manifest = try std.json.parseFromSlice(
        FreezeMapManifest,
        std.testing.allocator,
        freeze_map_manifest_json,
        .{ .ignore_unknown_fields = true },
    );
    defer freeze_map_manifest.deinit();

    try expectContains(scorecard_doc, "P15-L03");
    try expectContains(scorecard_doc, "parity-scorecard-baseline");
    try expectContains(scorecard_doc, "blocked_posture_accounting_not_port_readiness");
    try expectContains(scorecard_doc, "current-master-readback-2026-05-27");
    try expectMetricLine(scorecard_doc, "active freeze-in-C anchor count", parsed.value.metrics.active_freeze_in_c_anchor_count);
    try expectMetricLine(scorecard_doc, "blocked status-change anchor count", parsed.value.metrics.blocked_status_change_anchor_count);
    try expectMetricLine(scorecard_doc, "anchors blocked entirely within Phase 15 governance evidence", parsed.value.metrics.phase15_governance_only_blocker_anchor_count);
    try expectMetricLine(scorecard_doc, "Phase 14 coupled blocker anchor count", parsed.value.metrics.phase14_coupled_blocker_anchor_count);
    try expectMetricLine(scorecard_doc, "anchors still blocked on prior-phase bridge evidence", parsed.value.metrics.anchors_still_blocked_on_prior_phase_bridge_evidence);
    try expectMetricLine(scorecard_doc, "study-only anchors tracked outside this scorecard", parsed.value.metrics.study_only_anchors_tracked_outside_scorecard);
    try expectMetricLine(scorecard_doc, "Architecture Council approvals recorded for status change", parsed.value.metrics.architecture_council_status_change_approval_count);
    try expectCurrentReminderRoute(scorecard_doc);
    try expectCurrentBoundedStepHandoff(scorecard_doc);
    try expectContains(scorecard_doc, "python3 scripts/zigux/check-phase15-tests-readme-alignment.py");

    try std.testing.expectEqual(
        freeze_map_manifest.value.study_only_targets.len,
        parsed.value.metrics.study_only_anchors_tracked_outside_scorecard,
    );
    for (freeze_map_manifest.value.study_only_targets) |study_only_target| {
        try expectContains(freeze_map, study_only_target);
        try expectAnchorsOmitPath(parsed.value.anchors, study_only_target);
    }

    try std.testing.expectEqual(
        freeze_map_manifest.value.freeze_in_c_targets.len,
        parsed.value.metrics.blocked_status_change_anchor_count,
    );
    try std.testing.expectEqual(
        freeze_map_manifest.value.freeze_in_c_targets.len,
        freeze_map_manifest.value.blocker_ownership.len,
    );
    try std.testing.expectEqual(
        parsed.value.anchors.len,
        freeze_map_manifest.value.blocker_ownership.len,
    );
    for (
        parsed.value.anchors,
        freeze_map_manifest.value.blocker_ownership,
        freeze_map_manifest.value.freeze_in_c_targets,
    ) |anchor, blocker_ownership, freeze_target| {
        try std.testing.expectEqualStrings(anchor.path, freeze_target);
        try expectFreezeMapAnchorAlignment(anchor, blocker_ownership);
        try expectAnchorPacketAlignment(scorecard_doc, governance_note, anchor);
        try expectContains(freeze_map, anchor.path);
    }
}

test "phase 15 parity scorecard evidence archives stay aligned with the dated readback packet" {
    const manifest_json = try readRepoFile("zigux/tests/phase15_parity_scorecard.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    try expectEvidenceArchiveTruthfulness(parsed.value);
}
