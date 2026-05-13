const std = @import("std");

const Governance = struct {
    status_bucket: []const u8,
    ready_next_gap: []const u8,
    last_closed_followup: []const u8,
    blocked_gap: []const u8,
    lane_reopen_scope: []const u8,
    why_now: []const u8,
};

const SurveySummary = struct {
    ring_buffer_c_lines: usize,
    ring_buffer_design_doc_lines: usize,
    ring_buffer_map_doc_lines: usize,
    trace_c_lines: usize,
    simple_ring_buffer_c_lines: usize,
    preexisting_phase14_build_present: bool,
    preexisting_phase14_make_target_present: bool,
    preexisting_phase14_workqueue_bridge_present: bool,
    preexisting_ring_buffer_zig_present: bool,
    preexisting_phase14_ring_buffer_manifest_present: bool,
    preexisting_phase14_ring_buffer_survey_test_present: bool,
    preexisting_phase14_ring_buffer_survey_note_present: bool,
};

const MaintenanceHandoff = struct {
    current_lane_posture: []const u8,
    replay_before_trusting: []const []const u8,
    reopen_conditions: []const []const u8,
    next_future_target: []const u8,
};

const ChecklistEntry = struct {
    id: []const u8,
    summary: []const u8,
    ownership: []const u8,
    anchor_symbols: []const []const u8,
    rationale: []const u8,
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
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    study_only_governance: Governance,
    maintenance_handoff: MaintenanceHandoff,
    decision_checklist: []const ChecklistEntry,
    gaps: []const Gap,
};

fn hasChecklistEntry(entries: []const ChecklistEntry, id: []const u8) bool {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.id, id) and std.mem.eql(u8, entry.ownership, "stay_in_c")) {
            return true;
        }
    }
    return false;
}

fn hasGap(manifest: Manifest, id: []const u8, status: []const u8) bool {
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id) and std.mem.eql(u8, gap.status, status)) {
            return true;
        }
    }
    return false;
}

test "phase14 ring-buffer survey manifest records the current study-only packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_ring_buffer_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P14-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("99cd3249c4bab05b74227ed7ca3869284e818588", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("kernel/trace/ring_buffer.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 8103), manifest.survey_summary.ring_buffer_c_lines);
    try std.testing.expectEqual(@as(usize, 983), manifest.survey_summary.ring_buffer_design_doc_lines);
    try std.testing.expectEqual(@as(usize, 106), manifest.survey_summary.ring_buffer_map_doc_lines);
    try std.testing.expectEqual(@as(usize, 10017), manifest.survey_summary.trace_c_lines);
    try std.testing.expectEqual(@as(usize, 517), manifest.survey_summary.simple_ring_buffer_c_lines);
    try std.testing.expectEqual(false, manifest.survey_summary.preexisting_ring_buffer_zig_present);
    try std.testing.expectEqual(true, manifest.survey_summary.preexisting_phase14_ring_buffer_manifest_present);
    try std.testing.expectEqual(true, manifest.survey_summary.preexisting_phase14_ring_buffer_survey_test_present);
    try std.testing.expectEqual(true, manifest.survey_summary.preexisting_phase14_ring_buffer_survey_note_present);
    try std.testing.expectEqualStrings("study_only", manifest.study_only_governance.status_bucket);
    try std.testing.expectEqualStrings("", manifest.study_only_governance.ready_next_gap);
    try std.testing.expectEqualStrings("phase14-ring-buffer-zig-port-blocker", manifest.study_only_governance.blocked_gap);
    try std.testing.expectEqualStrings("phase14-ring-buffer-maintenance-handoff", manifest.study_only_governance.last_closed_followup);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.maintenance_handoff.current_lane_posture);
    try std.testing.expectEqual(@as(usize, 3), manifest.maintenance_handoff.replay_before_trusting.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.maintenance_handoff.reopen_conditions.len);
    try std.testing.expect(std.mem.indexOf(u8, manifest.maintenance_handoff.next_future_target, "ring-buffer-local") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.study_only_governance.why_now, "maintenance-mode handoff") != null);
    try std.testing.expectEqual(@as(usize, 6), manifest.decision_checklist.len);
    try std.testing.expect(hasChecklistEntry(manifest.decision_checklist, "reserve-commit-publication"));
    try std.testing.expect(hasChecklistEntry(manifest.decision_checklist, "wakeup-watermark-mmap-boundary"));
    try std.testing.expect(hasChecklistEntry(manifest.decision_checklist, "tracefs-mapping-limitations"));
    try std.testing.expect(hasChecklistEntry(manifest.decision_checklist, "reader-page-consume-boundary"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-wakeup-mmap-followup", "starter_landed"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-splice-resize-followup", "starter_landed"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-mapped-reader-ioctl-followup", "starter_landed"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-read-page-extraction-followup", "starter_landed"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-tracefs-reader-serialization-followup", "starter_landed"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-maintenance-handoff", "starter_landed"));
    try std.testing.expect(hasGap(manifest, "phase14-ring-buffer-zig-port-blocker", "blocked_on_stay_in_c_evidence"));
}

test "phase14 ring-buffer survey note keeps the parked study-only posture explicit" {
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
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-zig-port-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "## Wakeup and mmap audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "## Tracefs mapping limitations audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "## Mapped-reader ioctl audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-read-page-extraction-followup") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-tracefs-reader-serialization-followup") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "## Maintenance-Mode Handoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "current lane posture: `maintenance_mode`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zig test zigux/tests/phase14_ring_buffer_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14-ring-buffer-maintenance-handoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "ring-buffer-local") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "kernel/trace/ring_buffer.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "run the dedicated ring-buffer survey replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "run the shared Phase 14 build bundle") != null);
}
