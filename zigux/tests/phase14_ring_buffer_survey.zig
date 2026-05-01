const std = @import("std");

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

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const DecisionChecklistEntry = struct {
    id: []const u8,
    summary: []const u8,
    ownership: []const u8,
    anchor_symbols: []const []const u8,
    rationale: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    decision_checklist: []const DecisionChecklistEntry,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase 14 ring-buffer survey manifest records the study-only gap without inventing a port" {
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
    try std.testing.expectEqualStrings("kernel/trace/ring_buffer.c", manifest.anchor);
    try std.testing.expectEqualStrings("98aa9bb7dd14ed6063f954b0a23c19a537af51a5", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.ring_buffer_c_lines >= 8000);
    try std.testing.expect(manifest.survey_summary.ring_buffer_design_doc_lines >= 900);
    try std.testing.expect(manifest.survey_summary.ring_buffer_map_doc_lines >= 100);
    try std.testing.expect(manifest.survey_summary.trace_c_lines >= 10000);
    try std.testing.expect(manifest.survey_summary.simple_ring_buffer_c_lines >= 500);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_workqueue_bridge_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_ring_buffer_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_ring_buffer_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_ring_buffer_survey_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase14_ring_buffer_survey_note_present);
    try std.testing.expectEqual(@as(usize, 6), manifest.decision_checklist.len);
    try std.testing.expectEqual(@as(usize, 18), manifest.gaps.len);

    var landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_boundary_checklist = false;
    var saw_overwrite_audit = false;
    var saw_wakeup_mmap_followup = false;
    var saw_splice_resize_followup = false;
    var saw_mapped_reader_ioctl_followup = false;
    var saw_reader_page_consume_followup = false;
    var saw_read_page_extraction_followup = false;
    var saw_read_page_allocation_contract_followup = false;
    var saw_subbuf_order_reconfig_followup = false;
    var saw_snapshot_rollback_failure_followup = false;
    var saw_tracing_disabled_recovery_followup = false;
    var saw_map_dup_unmap_lifetime_followup = false;
    var saw_port_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-boundary-decision-checklist")) {
            saw_boundary_checklist = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase14_ring_buffer_manifest.json", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reserve") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remote") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-overwrite-audit")) {
            saw_overwrite_audit = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "overwrite") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "lost-event") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-wakeup-mmap-followup")