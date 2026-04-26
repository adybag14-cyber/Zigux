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
    try std.testing.expectEqualStrings("P14-L06", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("kernel/trace/ring_buffer.c", manifest.anchor);
    try std.testing.expectEqualStrings("56435bdf7b3407a128686725f1ad25000bf49144", manifest.surveyed_commit);
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
    try std.testing.expectEqual(@as(usize, 4), manifest.decision_checklist.len);
    try std.testing.expectEqual(@as(usize, 10), manifest.gaps.len);

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_boundary_checklist = false;
    var saw_overwrite_audit = false;
    var saw_wakeup_mmap_followup = false;
    var saw_splice_resize_followup = false;
    var saw_port_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-boundary-decision-checklist")) {
            saw_boundary_checklist = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase14_ring_buffer_manifest.json", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reader-page rotation") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-overwrite-audit")) {
            saw_overwrite_audit = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rb_move_tail()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "lost-event") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-wakeup-mmap-followup")) {
            saw_wakeup_mmap_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_wait()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "meta-page") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-splice-resize-followup")) {
            saw_splice_resize_followup = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "splice") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "resize") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-zig-port-blocker")) {
            saw_port_blocker = true;
            try std.testing.expectEqualStrings("kernel/trace/ring_buffer.zig", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 8), landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_boundary_checklist);
    try std.testing.expect(saw_overwrite_audit);
    try std.testing.expect(saw_wakeup_mmap_followup);
    try std.testing.expect(saw_splice_resize_followup);
    try std.testing.expect(saw_port_blocker);
}

test "phase 14 ring-buffer survey exposes the landed decision checklist" {
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

    const checklist = parsed.value.decision_checklist;
    try std.testing.expectEqualStrings("reserve-commit-publication", checklist[0].id);
    try std.testing.expectEqualStrings("stay_in_c", checklist[0].ownership);
    try std.testing.expectEqualStrings("ring_buffer_lock_reserve", checklist[0].anchor_symbols[0]);
    try std.testing.expectEqualStrings("ring_buffer_unlock_commit", checklist[0].anchor_symbols[1]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[0].rationale, "nested writer") != null);

    try std.testing.expectEqualStrings("head-page-reader-handoff", checklist[1].id);
    try std.testing.expectEqualStrings("rb_handle_head_page", checklist[1].anchor_symbols[0]);
    try std.testing.expectEqualStrings("ring_buffer_read_page", checklist[1].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[1].rationale, "reader-page swap") != null);

    try std.testing.expectEqualStrings("remote-reader-metadata", checklist[2].id);
    try std.testing.expectEqualStrings("rb_read_remote_meta_page", checklist[2].anchor_symbols[0]);
    try std.testing.expectEqualStrings("__rb_get_reader_page_from_remote", checklist[2].anchor_symbols[1]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[2].rationale, "callback-driven") != null);

    try std.testing.expectEqualStrings("wakeup-watermark-mmap-boundary", checklist[3].id);
    try std.testing.expectEqualStrings("rb_wake_up_waiters", checklist[3].anchor_symbols[0]);
    try std.testing.expectEqualStrings("ring_buffer_poll_wait", checklist[3].anchor_symbols[3]);
    try std.testing.expectEqualStrings("rb_update_meta_page", checklist[3].anchor_symbols[4]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[3].rationale, "irq_work") != null);
}
