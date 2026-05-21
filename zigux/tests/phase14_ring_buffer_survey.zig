const std = @import("std");

const SurveySummary = struct {
    preexisting_phase14_build_present: bool,
    preexisting_phase14_make_target_present: bool,
    preexisting_phase14_ring_buffer_manifest_present: bool,
    preexisting_phase14_ring_buffer_survey_test_present: bool,
    preexisting_phase14_ring_buffer_survey_note_present: bool,
};

const Governance = struct {
    status_bucket: []const u8,
    ready_next_gap: []const u8,
    last_closed_followup: []const u8,
    blocked_gap: []const u8,
    lane_reopen_scope: []const u8,
    why_now: []const u8,
};

const MaintenanceHandoff = struct {
    current_lane_posture: []const u8,
    replay_before_trusting: []const []const u8,
    replay_vocabulary_only_until_paths_return: bool,
    reopen_conditions: []const []const u8,
    next_future_target: []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
};

const DecisionChecklist = struct {
    id: []const u8,
    ownership: []const u8,
    summary: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor: []const u8,
    survey_summary: SurveySummary,
    study_only_governance: Governance,
    maintenance_handoff: MaintenanceHandoff,
    decision_checklist: []const DecisionChecklist,
    gaps: []const Gap,
};

fn hasGap(manifest: Manifest, id: []const u8, status: []const u8) bool {
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id) and std.mem.eql(u8, gap.status, status)) return true;
    }
    return false;
}

fn hasDecisionChecklist(manifest: Manifest, id: []const u8, ownership: []const u8, summary_fragment: []const u8) bool {
    for (manifest.decision_checklist) |entry| {
        if (!std.mem.eql(u8, entry.id, id)) continue;
        if (!std.mem.eql(u8, entry.ownership, ownership)) continue;
        if (std.mem.indexOf(u8, entry.summary, summary_fragment) == null) continue;
        return true;
    }
    return false;
}

test "phase14 ring-buffer manifest tracks the returned two-route study packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_ring_buffer_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P14-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("kernel/trace/ring_buffer.c", manifest.anchor);
    try std.testing.expectEqual(true, manifest.survey_summary.preexisting_phase14_build_present);
    try std.testing.expectEqual(false, manifest.survey_summary.preexisting_phase14_make_target_present);
    try std.testing.expectEqual(true, manifest.survey_summary.preexisting_phase14_ring_buffer_manifest_present);
    try std.testing.expectEqual(true, manifest.survey_summary.preexisting_phase14_ring_buffer_survey_test_present);
    try std.testing.expectEqual(true, manifest.survey_summary.preexisting_phase14_ring_buffer_survey_note_present);
    try std.testing.expectEqualStrings("study_only", manifest.study_only_governance.status_bucket);
    try std.testing.expectEqualStrings("", manifest.study_only_governance.ready_next_gap);
    try std.testing.expectEqualStrings("phase14-ring-buffer-maintenance-handoff", manifest.study_only_governance.last_closed_followup);
    try std.testing.expectEqualStrings("phase14-ring-buffer-zig-port-blocker", manifest.study_only_governance.blocked_gap);
    try std.testing.expectEqualStrings("same_packet_truthfulness_repairs_only", manifest.study_only_governance.lane_reopen_scope);
    try std.testing.expect(std.mem.indexOf(u8, manifest.study_only_governance.why_now, "shared Phase 14 build shard") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.study_only_governance.why_now, "ring-buffer-local replay evidence") != null);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.maintenance_handoff.current_lane_posture);
    try std.testing.expectEqual(false, manifest.maintenance_handoff.replay_vocabulary_only_until_paths_return);
    try std.testing.expectEqual(@as(usize, 2), manifest.maintenance_handoff.replay_before_trusting.len);
    try std.testing.expectEqualStrings("zig test zigux/tests/phase14_ring_buffer_survey.zig", manifest.maintenance_handoff.replay_before_trusting[0]);
    try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase14_build.zig --summary all", manifest.maintenance_handoff.replay_before_trusting[1]);
    try std.testing.expectEqual(@as(usize, 3), manifest.maintenance_handoff.reopen_conditions.len);
    try std.testing.expect(std.mem.indexOf(u8, manifest.maintenance_handoff.reopen_conditions[0], "replay-route wording") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.maintenance_handoff.next_future_target, "public-raw-backed ring-buffer-local evidence") != null);
    try std.testing.expect(hasDecisionChecklist(manifest, "read-page-extraction-boundary", "stay_in_c", "partial-copy fallback"));
    try std.testing.expect(hasDecisionChecklist(manifest, "tracefs-reader-serialization-boundary", "stay_in_c", "consumed-page lifetime"));
    try std.testing.expect(hasGap(manifest, "phase14-build-gate-current-master-gap", "restored_via_public_raw_readback"));
    try std.testing.expect(hasGap(manifest, "phase14-make-target", "resolved_as_drift_retired"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-survey-gate-current-master-gap", "restored_via_public_raw_readback"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-maintenance-handoff", "starter_landed"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-zig-port-blocker", "blocked_on_stay_in_c_evidence"));
}

test "phase14 ring-buffer survey note keeps the exact compile-route posture explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-ring-buffer-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expect(std.mem.indexOf(u8, note, "PHASE14_STATUS=study_only") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "current ring-buffer packet replay vocabulary") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`zigux/tests/phase14_ring_buffer_manifest.json`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`Documentation/zigux/phase14-core-boundary-traceability.md`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "public raw-file readback now recovers both `zigux/tests/phase14_ring_buffer_survey.zig` and `zigux/tests/phase14_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`zig test zigux/tests/phase14_ring_buffer_survey.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`zig build test --build-file zigux/tests/phase14_build.zig --summary all`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "dedicated ring-buffer survey replay, backed by current public raw-file readback") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "shared Phase 14 build bundle replay, backed by current public raw-file readback") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "current contents-path readback used by some shared notes is still partial") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "keep those two routes as ring-buffer-local replay vocabulary only") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "missing dedicated `make -C zigux phase14` route") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "returned survey companion and shared build shard framed as public-raw-backed ring-buffer-local evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-maintenance-handoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-zig-port-blocker") != null);
}
