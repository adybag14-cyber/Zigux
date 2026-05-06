const std = @import("std");

const SurveySummary = struct {
    virtio_ring_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_virtio_core_zig_present: bool,
    preexisting_phase10_build_present: bool,
    preexisting_phase10_core_doc_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_ring_doc_present: bool,
    preexisting_virtio_input_zig_present: bool,
    preexisting_virtio_input_test_present: bool,
    preexisting_virtio_input_survey_present: bool,
    preexisting_virtio_mmio_zig_present: bool,
    preexisting_virtio_mmio_test_present: bool,
    preexisting_virtio_mmio_survey_present: bool,
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
    freeze_map: []const u8,
    freeze_boundary_status: []const u8,
    freeze_status_change_claimed: bool,
    risky_transport_posture: []const u8,
    allowed_evidence_kinds: []const []const u8,
    forbidden_transport_claims: []const []const u8,
    architecture_council_reopen_required: bool,
    architecture_council_reopen_attached: bool,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_risky_transport");
}

fn containsString(list: []const []const u8, needle: []const u8) bool {
    for (list) |item| {
        if (std.mem.eql(u8, item, needle)) return true;
    }
    return false;
}

test "phase10 virtio ring survey manifest records the live queue-wrapper gap and freeze boundary" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_virtio_ring_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P10-L07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 10", manifest.phase);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", manifest.anchor);
    try std.testing.expectEqualStrings("e42103fc02f544e1bd23a5ec2e5b584734f5af7d", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(containsString(manifest.roadmap_destinations, "drivers/virtio/*.zig"));
    try std.testing.expect(containsString(manifest.roadmap_destinations, "zigux/kernel/"));
    try std.testing.expect(containsString(manifest.roadmap_destinations, "zigux/helpers/"));
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.freeze_map);
    try std.testing.expectEqualStrings("aligned", manifest.freeze_boundary_status);
    try std.testing.expect(!manifest.freeze_status_change_claimed);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", manifest.risky_transport_posture);
    try std.testing.expectEqual(@as(usize, 3), manifest.allowed_evidence_kinds.len);
    try std.testing.expect(containsString(manifest.allowed_evidence_kinds, "driver_local_lab_slices"));
    try std.testing.expect(containsString(manifest.allowed_evidence_kinds, "survey_manifests"));
    try std.testing.expect(containsString(manifest.allowed_evidence_kinds, "shared_validation_gates"));
    try std.testing.expectEqual(@as(usize, 5), manifest.forbidden_transport_claims.len);
    try std.testing.expect(containsString(manifest.forbidden_transport_claims, "queue_setup_reset_paths"));
    try std.testing.expect(containsString(manifest.forbidden_transport_claims, "irq_parity"));
    try std.testing.expect(containsString(manifest.forbidden_transport_claims, "dma_paths"));
    try std.testing.expect(containsString(manifest.forbidden_transport_claims, "input_registration_lifecycle"));
    try std.testing.expect(containsString(manifest.forbidden_transport_claims, "probe_remove_lifecycle"));
    try std.testing.expect(manifest.architecture_council_reopen_required);
    try std.testing.expect(!manifest.architecture_council_reopen_attached);
    try std.testing.expect(manifest.survey_summary.virtio_ring_c_lines >= 3000);
    try std.testing.expectEqual(@as(usize, 7), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_core_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_survey_present);
    try std.testing.expect(manifest.gaps.len >= 16);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-ring-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`Documentation/zigux/freeze-map.md`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "freeze-boundary owner: `P10-L10`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback owner") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`drivers/virtio/*.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`kernel/workqueue.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`kernel/trace/ring_buffer.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "freeze-map status change") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Architecture Council reopen request") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "feature-word") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "config-word window") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "config-write-disposition") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "probe-preflight") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shorter restaged config window clears stale second-word data") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-queue-reset-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "notify-prepare bookkeeping") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "reset-readiness preflight") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`resetQueue()` helper") != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_ring_helper = false;
    var saw_used_buffer_polling = false;
    var saw_callback_enable_helper = false;
    var saw_callback_delay_helper = false;
    var saw_notify_prepare_helper = false;
    var saw_broken_queue_poll_guard = false;
    var saw_queue_reset_helper = false;
    var saw_queue_reset_readiness_helper = false;
    var saw_mmio_register_landed = false;
    var saw_mmio_queue_size_helper = false;
    var saw_mmio_feature_word_helper = false;
    var saw_mmio_config_window_helper = false;
    var saw_mmio_config_write_disposition_helper = false;
    var saw_mmio_probe_preflight_helper = false;
    var saw_mmio_lifecycle_blocker = false;
    var saw_ring_slice_note = false;
    var saw_core_progress_note = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_risky_transport")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtqueue-shape-helper")) {
            saw_ring_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-used-buffer-polling-helper")) {
            saw_used_buffer_polling = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "newly consumed chains") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-callback-enable-helper")) {
            saw_callback_enable_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "follow-up poll") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-callback-delay-helper")) {
            saw_callback_delay_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtqueue_enable_cb_delayed()") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-notify-prepare-helper")) {
            saw_notify_prepare_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtqueue_kick_prepare()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "num_added") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-broken-queue-poll-guard")) {
            saw_broken_queue_poll_guard = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "marked broken") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "callback re-enable") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-queue-reset-helper")) {
            saw_queue_reset_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`resetQueue()` helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "descriptor-count and layout metadata") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notify bookkeeping") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-queue-reset-readiness-helper")) {
            saw_queue_reset_readiness_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reset-readiness preflight") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "unpublished chains") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "unpolled used chains") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-core-lab-starter")) {
            saw_core_progress_note = true;
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "descriptor-shape metadata") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notification accounting") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-register-window-helper")) {
            saw_mmio_register_landed = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "already landed") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-queue-size-helper")) {
            saw_mmio_queue_size_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue_num_max") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue discovery") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-feature-word-selector-helper")) {
            saw_mmio_feature_word_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "device-feature selector") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-config-window-helper")) {
            saw_mmio_config_window_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-word window") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-config-write-disposition-helper")) {
            saw_mmio_config_write_disposition_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "changed-byte mask") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "absolute window end offset") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-probe-preflight-helper")) {
            saw_mmio_probe_preflight_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtio_mmio_probe()-style preflight checks") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "interrupt-ack readiness") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-lifecycle-and-irq-paths")) {
            saw_mmio_lifecycle_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Interrupt acknowledgement") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue discovery") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe or remove lifecycle") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-ring-slice-note")) {
            saw_ring_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase10-virtio-ring-slice.md", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expect(starter_landed_count >= 15);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_core_progress_note);
    try std.testing.expect(saw_ring_helper);
    try std.testing.expect(saw_used_buffer_polling);
    try std.testing.expect(saw_callback_enable_helper);
    try std.testing.expect(saw_callback_delay_helper);
    try std.testing.expect(saw_notify_prepare_helper);
    try std.testing.expect(saw_broken_queue_poll_guard);
    try std.testing.expect(saw_queue_reset_helper);
    try std.testing.expect(saw_queue_reset_readiness_helper);
    try std.testing.expect(saw_mmio_register_landed);
    try std.testing.expect(saw_mmio_queue_size_helper);
    try std.testing.expect(saw_mmio_feature_word_helper);
    try std.testing.expect(saw_mmio_config_window_helper);
    try std.testing.expect(saw_mmio_config_write_disposition_helper);
    try std.testing.expect(saw_mmio_probe_preflight_helper);
    try std.testing.expect(saw_mmio_lifecycle_blocker);
    try std.testing.expect(saw_ring_slice_note);
}
