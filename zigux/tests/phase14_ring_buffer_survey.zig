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
    try std.testing.expectEqualStrings("f9a7a6e93c8e6a1b6550fd7b2aa5571729aab05b", manifest.surveyed_commit);
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
    try std.testing.expectEqual(@as(usize, 21), manifest.gaps.len);

    var landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_boundary_checklist = false;
    var saw_remote_reader_metadata_followup = false;
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
    var saw_cpu_hotplug_lifetime_followup = false;
    var saw_reset_governance_followup = false;
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
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-remote-reader-metadata-followup")) {
            saw_remote_reader_metadata_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rb_read_remote_meta_page()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__rb_get_reader_page_from_remote()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "meta_page_update") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-overwrite-audit")) {
            saw_overwrite_audit = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "overwrite") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "lost-event") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-wakeup-mmap-followup")) {
            saw_wakeup_mmap_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rb_wake_up_waiters()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_wait()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-splice-resize-followup")) {
            saw_splice_resize_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "resize") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "splice") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-mapped-reader-ioctl-followup")) {
            saw_mapped_reader_ioctl_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "TRACE_MMAP_IOCTL_GET_READER") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_map_get_reader()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-reader-page-consume-followup")) {
            saw_reader_page_consume_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rb_get_reader_page()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_consume()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-read-page-extraction-followup")) {
            saw_read_page_extraction_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_read_page()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "page-swap") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "resize_disabled") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-read-page-allocation-contract-followup")) {
            saw_read_page_allocation_contract_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_alloc_read_page()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_free_read_page()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "order") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-subbuf-order-reconfig-followup")) {
            saw_subbuf_order_reconfig_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_subbuf_order_set()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "buffer_subbuf_size_write()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tracing_buffers_read()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-snapshot-rollback-failure-followup")) {
            saw_snapshot_rollback_failure_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "buffer_subbuf_size_write()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tracing_resize_ring_buffer()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tracing_disabled") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-tracing-disabled-recovery-followup")) {
            saw_tracing_disabled_recovery_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tracing_on") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "current_tracer") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tracing_check_open_get_tr()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tracer_alloc_buffers()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "-ENODEV") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-map-dup-unmap-lifetime-followup")) {
            saw_map_dup_unmap_lifetime_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_map_dup()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__rb_inc_dec_mapped()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_unmap()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "resize_disabled") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-cpu-hotplug-lifetime-followup")) {
            saw_cpu_hotplug_lifetime_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "trace_rb_cpu_prepare()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tracer_alloc_buffers()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "CPUHP_TRACE_RB_PREPARE") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "buffer->cpumask") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-reset-governance-followup")) {
            saw_reset_governance_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase14-ring-buffer-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_reset_cpu()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_reset_online_cpus()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ring_buffer_reset()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "trace_access_lock()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "current_tracer") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "trace") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase14-ring-buffer-zig-port-blocker")) {
            saw_port_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expectEqualStrings("kernel/trace/ring_buffer.zig", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 20), landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_boundary_checklist);
    try std.testing.expect(saw_remote_reader_metadata_followup);
    try std.testing.expect(saw_overwrite_audit);
    try std.testing.expect(saw_wakeup_mmap_followup);
    try std.testing.expect(saw_splice_resize_followup);
    try std.testing.expect(saw_mapped_reader_ioctl_followup);
    try std.testing.expect(saw_reader_page_consume_followup);
    try std.testing.expect(saw_read_page_extraction_followup);
    try std.testing.expect(saw_read_page_allocation_contract_followup);
    try std.testing.expect(saw_subbuf_order_reconfig_followup);
    try std.testing.expect(saw_snapshot_rollback_failure_followup);
    try std.testing.expect(saw_tracing_disabled_recovery_followup);
    try std.testing.expect(saw_map_dup_unmap_lifetime_followup);
    try std.testing.expect(saw_cpu_hotplug_lifetime_followup);
    try std.testing.expect(saw_reset_governance_followup);
    try std.testing.expect(saw_port_blocker);
}

test "phase 14 ring-buffer survey exposes the landed stay-in-c checklist" {
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
    try std.testing.expectEqualStrings("rb_move_tail", checklist[0].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[0].rationale, "nested writer") != null);

    try std.testing.expectEqualStrings("head-page-reader-handoff", checklist[1].id);
    try std.testing.expectEqualStrings("rb_handle_head_page", checklist[1].anchor_symbols[0]);
    try std.testing.expectEqualStrings("rb_set_head_page", checklist[1].anchor_symbols[1]);
    try std.testing.expectEqualStrings("ring_buffer_read_page", checklist[1].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[1].rationale, "reader-page") != null);

    try std.testing.expectEqualStrings("remote-reader-metadata", checklist[2].id);
    try std.testing.expectEqualStrings("rb_read_remote_meta_page", checklist[2].anchor_symbols[0]);
    try std.testing.expectEqualStrings("__rb_get_reader_page_from_remote", checklist[2].anchor_symbols[1]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[2].rationale, "Remote readers") != null);

    try std.testing.expectEqualStrings("wakeup-watermark-mmap-boundary", checklist[3].id);
    try std.testing.expectEqualStrings("rb_wake_up_waiters", checklist[3].anchor_symbols[0]);
    try std.testing.expectEqualStrings("rb_watermark_hit", checklist[3].anchor_symbols[1]);
    try std.testing.expectEqualStrings("ring_buffer_wait", checklist[3].anchor_symbols[2]);
    try std.testing.expectEqualStrings("ring_buffer_poll_wait", checklist[3].anchor_symbols[3]);
    try std.testing.expectEqualStrings("rb_update_meta_page", checklist[3].anchor_symbols[4]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[3].rationale, "Wait queues") != null);

    try std.testing.expectEqualStrings("tracefs-mapping-limitations", checklist[4].id);
    try std.testing.expectEqualStrings("ring_buffer_map", checklist[4].anchor_symbols[0]);
    try std.testing.expectEqualStrings("ring_buffer_resize", checklist[4].anchor_symbols[1]);
    try std.testing.expectEqualStrings("ring_buffer_swap_cpu", checklist[4].anchor_symbols[2]);
    try std.testing.expectEqualStrings("ring_buffer_map_get_reader", checklist[4].anchor_symbols[3]);
    try std.testing.expectEqualStrings("tracing_buffers_splice_read", checklist[4].anchor_symbols[4]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[4].rationale, "resize_disabled") != null);

    try std.testing.expectEqualStrings("reader-page-consume-boundary", checklist[5].id);
    try std.testing.expectEqualStrings("rb_get_reader_page", checklist[5].anchor_symbols[0]);
    try std.testing.expectEqualStrings("ring_buffer_read_start", checklist[5].anchor_symbols[1]);
    try std.testing.expectEqualStrings("ring_buffer_consume", checklist[5].anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, checklist[5].rationale, "lost-event") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist[5].rationale, "resize_disabled") != null);
}

test "phase 14 ring-buffer survey note records the landed remote-reader, reset, recovery, and hotplug audits" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-ring-buffer-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-L08") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SURVEYED_COMMIT=f9a7a6e93c8e6a1b6550fd7b2aa5571729aab05b") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Remote-reader metadata audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rb_read_remote_meta_page()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "__rb_get_reader_page_from_remote()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "meta_page_update") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "reader_page()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "lost_events") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Sub-buffer order reconfiguration audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Snapshot rollback failure-path audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "buffer_subbuf_size_write()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "tracing_buffers_read()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "disables tracing outright") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "tracing_disabled = 1") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "tracing_resize_ring_buffer()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Tracing-disabled Recovery Audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "tracing_check_open_get_tr()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "echo 1 > tracing_on") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "tracer_alloc_buffers()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "documented user-visible recovery path") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Mapped-reader duplicate and final-unmap lifetime audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "ring_buffer_map_dup()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "__rb_inc_dec_mapped()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "ring_buffer_unmap()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "resize_disabled") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## CPU hotplug prepare lifetime audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "trace_rb_cpu_prepare()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "on_each_cpu(rb_cpu_sync, NULL, 1)") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "cpuhp_setup_state_multi(CPUHP_TRACE_RB_PREPARE") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "buffer->cpumask") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "never freed when the CPU goes down") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Reset and clear-path governance audit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "ring_buffer_reset_cpu()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "ring_buffer_reset_online_cpus()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "ring_buffer_reset()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "struct ring_buffer_remote") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "trace_access_lock()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "O_TRUNC") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "current_tracer") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "buffer_subbuf_size_kb") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-ring-buffer-reset-governance-followup") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-ring-buffer-remote-reader-metadata-followup") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-ring-buffer-cpu-hotplug-lifetime-followup") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Attached toolchain fallback guidance") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "when `zig` is not on `PATH`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "<attached-zig-path> build test --build-file zigux/tests/phase14_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase14 ZIG=<attached-zig-path>") != null);
}
