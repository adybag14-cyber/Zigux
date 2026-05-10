const std = @import("std");

const SurveySummary = struct {
    virtio_ring_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_virtio_core_zig_present: bool,
    preexisting_phase10_build_present: bool,
    preexisting_phase10_core_doc_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_ring_doc_present: bool,
    preexisting_ring_verify_present: bool,
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
    freeze_boundary_owner_lane: []const u8,
    study_only_anchors: []const []const u8,
    freeze_in_c_anchors: []const []const u8,
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

test "phase10 virtio ring survey manifest records the queue-local foothold and remaining lab-driver bridge" {
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
    try std.testing.expectEqualStrings("bdfe88e865b94387b3c3bd41ca98054c452f78b9", manifest.surveyed_commit);
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
    try std.testing.expectEqualStrings("P10-L10", manifest.freeze_boundary_owner_lane);
    try std.testing.expectEqual(@as(usize, 2), manifest.study_only_anchors.len);
    try std.testing.expect(containsString(manifest.study_only_anchors, "kernel/workqueue.c"));
    try std.testing.expect(containsString(manifest.study_only_anchors, "kernel/trace/ring_buffer.c"));
    try std.testing.expectEqual(@as(usize, 4), manifest.freeze_in_c_anchors.len);
    try std.testing.expect(containsString(manifest.freeze_in_c_anchors, "kernel/sched/core.c"));
    try std.testing.expect(containsString(manifest.freeze_in_c_anchors, "mm/page_alloc.c"));
    try std.testing.expect(containsString(manifest.freeze_in_c_anchors, "kernel/rcu/tree.c"));
    try std.testing.expect(containsString(manifest.freeze_in_c_anchors, "net/core/skbuff.c"));
    try std.testing.expect(manifest.survey_summary.virtio_ring_c_lines >= 3000);
    try std.testing.expectEqual(@as(usize, 7), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_core_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_ring_verify_present);
    try std.testing.expect(manifest.gaps.len >= 16);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-ring-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "lab-driver threshold") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "queue-local ring foothold") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "notification-data summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`drivers/virtio/virtio_ring_verify.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-ring-lab-driver-bridge") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "owned by the adjacent `P10-L10` MMIO packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "transport-backed queue discovery, IRQ acknowledgement, queue reset execution, and probe/remove lifecycle behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Do not reopen MMIO helper growth, DMA, interrupt delivery, queue discovery, reset execution, or probe/remove lifecycle work from this note.") != null);

    const sequencing_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(sequencing_note);

    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "notification-data wrap-transition review") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "shipped ring helper plus verifier packet") != null);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "drivers/virtio/virtio_ring_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "zigux/tests/phase10_virtio_ring.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "zigux/tests/phase10_virtio_ring_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "zigux/tests/phase10_virtio_ring_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "lane-sequenced virtio ring plus the focused ring-verify replay") != null);

    const closure_manifest = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_closure_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(closure_manifest);

    try std.testing.expect(std.mem.indexOf(u8, closure_manifest, "\"ring\": \"P10-L07\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, closure_manifest, "\"ring\": \"bdfe88e865b94387b3c3bd41ca98054c452f78b9\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, closure_manifest, "\"drivers/virtio/virtio_ring.zig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, closure_manifest, "\"drivers/virtio/virtio_ring_verify.zig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, closure_manifest, "\"scripts/zigux/check-phase10-ring-packet.py\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, closure_manifest, "\"phase10-notification-data-summary-helper\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, closure_manifest, "\"phase10-ring-verify-replay\"") != null);

    const verify_replay = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/virtio/virtio_ring_verify.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(verify_replay);

    try std.testing.expect(std.mem.indexOf(u8, verify_replay, "test \"virtio ring clearBroken exposes the next reset blocker instead of hiding queue debt\" {") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_replay, "_ = try lab.clearBroken(4);") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_replay, "try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpublished_chains, readiness.blocker.?);") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_replay, "_ = try lab.clearBroken(5);") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_replay, "try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.outstanding_chains, readiness.blocker.?);") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_replay, "_ = try lab.clearBroken(6);") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_replay, "try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpolled_used_chains, readiness.blocker.?);") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_replay, "test \"virtio ring notification-data summary tracks packed wrap and split reset transitions\" {") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_replay, "try testing.expectEqual(@as(u32, 0x8001_0001), summary.notification_data);") != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_ring_helper = false;
    var saw_used_buffer_polling = false;
    var saw_callback_enable_helper = false;
    var saw_callback_delay_helper = false;
    var saw_notify_prepare_helper = false;
    var saw_notification_data_helper = false;
    var saw_broken_queue_poll_guard = false;
    var saw_queue_reset_helper = false;
    var saw_queue_reset_readiness_helper = false;
    var saw_ring_verify_replay = false;
    var saw_ring_lab_driver_bridge = false;
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
        }

        if (std.mem.eql(u8, gap.id, "phase10-notification-data-summary-helper")) {
            saw_notification_data_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "packed wrap-bit transitions") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-broken-queue-poll-guard")) {
            saw_broken_queue_poll_guard = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "marked broken") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-queue-reset-helper")) {
            saw_queue_reset_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "resetQueue()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "layout metadata") != null);
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

        if (std.mem.eql(u8, gap.id, "phase10-ring-verify-replay")) {
            saw_ring_verify_replay = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring_verify.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reset-readiness blockers") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "delayed-callback pacing") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-ring-lab-driver-bridge")) {
            saw_ring_lab_driver_bridge = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue discovery") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "IRQ acknowledgement") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe/remove lifecycle") != null);
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

    try std.testing.expectEqual(@as(usize, 15), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_core_progress_note);
    try std.testing.expect(saw_ring_helper);
    try std.testing.expect(saw_used_buffer_polling);
    try std.testing.expect(saw_callback_enable_helper);
    try std.testing.expect(saw_callback_delay_helper);
    try std.testing.expect(saw_notify_prepare_helper);
    try std.testing.expect(saw_notification_data_helper);
    try std.testing.expect(saw_broken_queue_poll_guard);
    try std.testing.expect(saw_queue_reset_helper);
    try std.testing.expect(saw_queue_reset_readiness_helper);
    try std.testing.expect(saw_ring_verify_replay);
    try std.testing.expect(saw_ring_lab_driver_bridge);
    try std.testing.expect(saw_ring_slice_note);
}
