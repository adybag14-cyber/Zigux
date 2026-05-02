const std = @import("std");

const SurveySummary = struct {
    virtio_ring_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_virtio_core_zig_present: bool,
    preexisting_phase10_build_present: bool,
    preexisting_phase10_core_doc_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_ring_reset_reuse_test_present: bool,
    preexisting_virtio_ring_doc_present: bool,
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
    risky_transport_posture: []const u8,
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

test "phase10 virtio ring survey manifest records the live queue-discipline packet and parked MMIO blocker after landed interrupt-ack" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_virtio_ring_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-ring-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-ring-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const phase10_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase10_build);

    const closure_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_closure_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(closure_manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const closure_parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, closure_manifest_json, .{});
    defer closure_parsed.deinit();

    const manifest = parsed.value;
    const closure_manifest = closure_parsed.value;
    try std.testing.expectEqualStrings("P10-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 10", manifest.phase);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", manifest.anchor);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.freeze_map);
    try std.testing.expectEqualStrings("aligned", manifest.freeze_boundary_status);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", manifest.risky_transport_posture);
    try std.testing.expect(manifest.architecture_council_reopen_required);
    try std.testing.expect(!manifest.architecture_council_reopen_attached);
    const expected_forbidden_transport_claims = [_][]const u8{
        "queue_setup_reset_paths",
        "irq_parity",
        "dma_paths",
        "input_registration_lifecycle",
        "probe_remove_lifecycle",
    };
    try std.testing.expectEqual(expected_forbidden_transport_claims.len, manifest.forbidden_transport_claims.len);
    for (expected_forbidden_transport_claims, 0..) |claim, index| {
        try std.testing.expectEqualStrings(claim, manifest.forbidden_transport_claims[index]);
    }
    try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);
    for (manifest.surveyed_commit) |ch| {
        try std.testing.expect(std.ascii.isHex(ch));
    }
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.virtio_ring_c_lines >= 3000);
    try std.testing.expectEqual(@as(usize, 4), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_core_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_reset_reuse_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_doc_present);
    try std.testing.expect(manifest.gaps.len >= 7);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10_virtio_core_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-virtio-core-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "older core slice note alone") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_build.zig`, and `Documentation/zigux/phase10-virtio-core-slice.md`") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase10_build, "phase10_virtio_ring_reset_reuse.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase10_build, "phase10-virtio-ring-reset-reuse-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase10_build, "run_phase10_virtio_ring_reset_reuse_tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-queue-register-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-queue-notify-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-queue-address-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-config-window-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-config-write-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-interrupt-ack-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no smaller ready transport follow-up remains ahead of the still-blocked lifecycle and IRQ packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "remaining MMIO follow-up ladder against the roadmap") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig build test --build-file zigux/tests/phase10_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FREEZE_BOUNDARY_STATUS=aligned") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/sched/core.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "mm/page_alloc.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/rcu/tree.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "net/core/skbuff.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/workqueue.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/trace/ring_buffer.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/*.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/helpers/") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "it does not reopen `queue_setup_reset_paths`, `irq_parity`, `dma_paths`, `input_registration_lifecycle`, or `probe_remove_lifecycle`") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "config-window, config-write, and interrupt-ack helpers are already landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "leave this packet parked unless a future Phase 10 review can split `phase10-mmio-lifecycle-and-irq-paths` into a smaller transport-safe observation helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "next bounded follow-up should come from the survey-backed `virtio_mmio` config-window helper") == null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "zig build test --build-file zigux/tests/phase10_build.zig --summary all") != null);
    try std.testing.expect(closure_manifest == .object);

    const landed_ring_helper_evidence = closure_manifest.object.get("landed_ring_helper_evidence") orelse return error.TestUnexpectedResult;
    try std.testing.expect(landed_ring_helper_evidence == .object);
    const ring_helper_evidence = landed_ring_helper_evidence.object.get("zigux/tests/phase10_virtio_ring_manifest.json") orelse return error.TestUnexpectedResult;
    try std.testing.expect(ring_helper_evidence == .array);
    const expected_landed_ring_helpers = [_][]const u8{
        "phase10-virtqueue-shape-helper",
        "phase10-used-buffer-polling-helper",
        "phase10-callback-disable-helper",
        "phase10-callback-enable-helper",
        "phase10-callback-enable-prepare-helper",
        "phase10-callback-delay-helper",
        "phase10-notify-prepare-helper",
        "phase10-queue-reset-guard-helper",
        "phase10-queue-reset-helper",
    };
    try std.testing.expectEqual(expected_landed_ring_helpers.len, ring_helper_evidence.array.items.len);
    for (expected_landed_ring_helpers, 0..) |helper_id, index| {
        try std.testing.expect(ring_helper_evidence.array.items[index] == .string);
        try std.testing.expectEqualStrings(helper_id, ring_helper_evidence.array.items[index].string);
    }

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_ring_helper = false;
    var saw_used_buffer_polling = false;
    var saw_callback_disable_helper = false;
    var saw_callback_enable_helper = false;
    var saw_callback_enable_prepare_helper = false;
    var saw_callback_delay_helper = false;
    var saw_notify_prepare_helper = false;
    var saw_queue_reset_guard_helper = false;
    var saw_queue_reset_helper = false;
    var saw_mmio_register_window = false;
    var saw_mmio_queue_register = false;
    var saw_mmio_queue_notify = false;
    var saw_mmio_queue_address = false;
    var saw_mmio_config_window = false;
    var saw_mmio_config_write = false;
    var saw_mmio_interrupt_ack = false;
    var saw_mmio_blocker = false;
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

        if (std.mem.eql(u8, gap.id, "phase10-callback-disable-helper")) {
            saw_callback_disable_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "callback disable helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "follow-up poll") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-callback-enable-helper")) {
            saw_callback_enable_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "follow-up poll") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-callback-enable-prepare-helper")) {
            saw_callback_enable_prepare_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtqueue_enable_cb_prepare()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtqueue_poll()") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-callback-delay-helper")) {
            saw_callback_delay_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "delayed-callback pacing") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-notify-prepare-helper")) {
            saw_notify_prepare_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notify-prepare helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtqueue_kick_prepare()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "num_added") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "wrap silently") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-queue-reset-guard-helper")) {
            saw_queue_reset_guard_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue-reset guard helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "follow-up poll debt") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-queue-reset-helper")) {
            saw_queue_reset_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "drained-queue reset helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "preserving queue shape metadata") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-core-lab-starter")) {
            saw_core_progress_note = true;
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "descriptor-shape metadata") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notification accounting") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-register-window-helper")) {
            saw_mmio_register_window = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "register-window helper") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-queue-register-helper")) {
            saw_mmio_queue_register = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue select") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ready-state bookkeeping") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-queue-notify-helper")) {
            saw_mmio_queue_notify = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue-notify snapshot helper") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-queue-address-helper")) {
            saw_mmio_queue_address = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue-address planning step") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-config-window-helper")) {
            saw_mmio_config_window = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-window snapshot helper") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-config-write-helper")) {
            saw_mmio_config_write = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-write planning helper") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-interrupt-ack-helper")) {
            saw_mmio_interrupt_ack = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "interrupt-status acknowledge bookkeeping") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue and config interrupt bits") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-lifecycle-and-irq-paths")) {
            saw_mmio_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "interrupt acknowledgement") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue notify side effects") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-space writes") != null);
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

    try std.testing.expect(starter_landed_count >= 5);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(blocked_count >= 1);
    try std.testing.expect(saw_core_progress_note);
    try std.testing.expect(saw_ring_helper);
    try std.testing.expect(saw_used_buffer_polling);
    try std.testing.expect(saw_callback_disable_helper);
    try std.testing.expect(saw_callback_enable_helper);
    try std.testing.expect(saw_callback_enable_prepare_helper);
    try std.testing.expect(saw_callback_delay_helper);
    try std.testing.expect(saw_notify_prepare_helper);
    try std.testing.expect(saw_queue_reset_guard_helper);
    try std.testing.expect(saw_queue_reset_helper);
    try std.testing.expect(saw_mmio_register_window);
    try std.testing.expect(saw_mmio_queue_register);
    try std.testing.expect(saw_mmio_queue_notify);
    try std.testing.expect(saw_mmio_queue_address);
    try std.testing.expect(saw_mmio_config_window);
    try std.testing.expect(saw_mmio_config_write);
    try std.testing.expect(saw_mmio_interrupt_ack);
    try std.testing.expect(saw_ring_slice_note);
    try std.testing.expect(saw_mmio_blocker);
}
