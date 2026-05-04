const std = @import("std");

const SurveySummary = struct {
    virtio_mmio_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_virtio_core_zig_present: bool,
    preexisting_virtio_core_survey_present: bool,
    preexisting_phase10_build_present: bool,
    preexisting_phase10_core_doc_present: bool,
    preexisting_virtio_core_survey_doc_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_ring_doc_present: bool,
    preexisting_virtio_ring_survey_present: bool,
    preexisting_virtio_ring_reset_reuse_present: bool,
    preexisting_virtio_input_zig_present: bool,
    preexisting_virtio_input_test_present: bool,
    preexisting_virtio_input_survey_present: bool,
    preexisting_virtio_mmio_zig_present: bool,
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

test "phase10 virtio mmio survey manifest records the landed probe-preflight rung and remaining transport gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_virtio_mmio_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-mmio-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-mmio-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

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
    const expected_forbidden_transport_claims = [_][]const u8{
        "queue_setup_reset_paths",
        "irq_parity",
        "dma_paths",
        "input_registration_lifecycle",
        "probe_remove_lifecycle",
    };
    try std.testing.expectEqualStrings("P10-L18", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 10", manifest.phase);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);
    for (manifest.surveyed_commit) |ch| {
        try std.testing.expect(std.ascii.isHex(ch));
    }
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("drivers/virtio/*.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("zigux/kernel/", manifest.roadmap_destinations[1]);
    try std.testing.expectEqualStrings("zigux/helpers/", manifest.roadmap_destinations[2]);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.freeze_map);
    try std.testing.expectEqualStrings("aligned", manifest.freeze_boundary_status);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", manifest.risky_transport_posture);
    try std.testing.expect(manifest.architecture_council_reopen_required);
    try std.testing.expect(!manifest.architecture_council_reopen_attached);
    try std.testing.expectEqual(expected_forbidden_transport_claims.len, manifest.forbidden_transport_claims.len);
    for (expected_forbidden_transport_claims, 0..) |claim, index| {
        try std.testing.expectEqualStrings(claim, manifest.forbidden_transport_claims[index]);
    }
    try std.testing.expect(manifest.survey_summary.virtio_mmio_c_lines >= 800);
    try std.testing.expectEqual(@as(usize, 11), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_core_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_survey_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_reset_reuse_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_zig_present);
    try std.testing.expectEqual(@as(usize, 20), manifest.gaps.len);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, manifest.surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10_virtio_ring_reset_reuse.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/phase10-virtio-ring-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/phase10-virtio-input-module-slice.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-virtio-ring-slice-note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-config-write-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-interrupt-ack-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-probe-preflight-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-virtio-mmio-slice-note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-lifecycle-and-irq-paths") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase10_virtio_mmio_queue_isolation.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "bounded transport-identity and register-window helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "transport-identity snapshots for the magic value, transport version, device-id presence, and vendor-id bookkeeping") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FREEZE_BOUNDARY_STATUS=aligned") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/workqueue.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/trace/ring_buffer.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "boundary maps") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "concurrency audits") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "explicit stay-in-C decisions where warranted") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "wrapper-first or study-only posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/*.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/kernel/") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/helpers/") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "transport-identity snapshots") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "probe-preflight summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "bounded interrupt-state summaries") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "interrupt acknowledge") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "PHASE10_SLICE=virtio-mmio-probe-preflight-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "transport-identity snapshot plus a bounded probe-preflight summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "phase10-mmio-lifecycle-and-irq-paths") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "add one small config-window write-planning helper next") == null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "next honest follow-on after the config-write helper") == null);
    try std.testing.expect(closure_manifest == .object);

    const landed_mmio_helper_evidence = closure_manifest.object.get("landed_mmio_helper_evidence") orelse return error.TestUnexpectedResult;
    try std.testing.expect(landed_mmio_helper_evidence == .object);
    const mmio_helper_evidence = landed_mmio_helper_evidence.object.get("zigux/tests/phase10_virtio_mmio_manifest.json") orelse return error.TestUnexpectedResult;
    try std.testing.expect(mmio_helper_evidence == .array);
    const expected_landed_mmio_helpers = [_][]const u8{
        "phase10-mmio-register-window-helper",
        "phase10-mmio-queue-register-helper",
        "phase10-mmio-queue-notify-helper",
        "phase10-mmio-queue-address-helper",
        "phase10-mmio-config-window-helper",
        "phase10-mmio-config-write-helper",
        "phase10-mmio-interrupt-ack-helper",
        "phase10-mmio-probe-preflight-helper",
    };
    try std.testing.expectEqual(expected_landed_mmio_helpers.len, mmio_helper_evidence.array.items.len);
    for (expected_landed_mmio_helpers, 0..) |helper_id, index| {
        try std.testing.expect(mmio_helper_evidence.array.items[index] == .string);
        try std.testing.expectEqualStrings(helper_id, mmio_helper_evidence.array.items[index].string);
    }

    const blocked_transport_gaps = closure_manifest.object.get("blocked_transport_gaps") orelse return error.TestUnexpectedResult;
    try std.testing.expect(blocked_transport_gaps == .object);
    const mmio_blocked_gap = blocked_transport_gaps.object.get("zigux/tests/phase10_virtio_mmio_manifest.json") orelse return error.TestUnexpectedResult;
    try std.testing.expect(mmio_blocked_gap == .string);
    try std.testing.expectEqualStrings("phase10-mmio-lifecycle-and-irq-paths", mmio_blocked_gap.string);

    const roadmap_parity_scoreboard = closure_manifest.object.get("roadmap_parity_scoreboard") orelse return error.TestUnexpectedResult;
    try std.testing.expect(roadmap_parity_scoreboard == .object);
    const mmio_wrappers_scoreboard = roadmap_parity_scoreboard.object.get("mmio_wrappers") orelse return error.TestUnexpectedResult;
    try std.testing.expect(mmio_wrappers_scoreboard == .object);
    const mmio_wrappers_status = mmio_wrappers_scoreboard.object.get("status") orelse return error.TestUnexpectedResult;
    try std.testing.expect(mmio_wrappers_status == .string);
    try std.testing.expectEqualStrings("starter_landed", mmio_wrappers_status.string);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_mmio_survey_gate = false;
    var saw_mmio_survey_note = false;
    var saw_mmio_blocker = false;
    var saw_ring_helper = false;
    var saw_ring_slice_note = false;
    var saw_ring_callback_delay = false;
    var saw_mmio_slice_note = false;
    var saw_mmio_landed_helper = false;
    var saw_mmio_queue_helper = false;
    var saw_mmio_queue_notify_helper = false;
    var saw_mmio_queue_address_helper = false;
    var saw_mmio_config_window_helper = false;
    var saw_mmio_config_write_landed = false;
    var saw_mmio_interrupt_ack_landed = false;
    var saw_mmio_probe_preflight_landed = false;

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

        if (std.mem.eql(u8, gap.id, "phase10-virtio-ring-lab-helper")) {
            saw_ring_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-core-lab-starter")) {
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-change disposition summaries") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-callback-delay-helper")) {
            saw_ring_callback_delay = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "delayed-callback pacing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue reset discipline") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-mmio-survey-gate")) {
            saw_mmio_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase10_virtio_mmio_survey.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-ring-survey-gate")) {
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landed queue-discipline surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remaining MMIO ladder") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue-wrapper roadmap gap explicit") == null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-ring-slice-note")) {
            saw_ring_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase10-virtio-ring-slice.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bounded queue-helper surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "transport readiness") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-mmio-survey-note")) {
            saw_mmio_survey_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase10-virtio-mmio-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe-preflight helpers landed") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-mmio-slice-note")) {
            saw_mmio_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase10-virtio-mmio-slice.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe-preflight surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-window surface rather than the full transport driver") == null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-register-window-helper")) {
            saw_mmio_landed_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "transport-identity and register-window helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "magic-value, transport-version, device-id, and vendor-id bookkeeping") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "delayed-callback pacing") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-queue-register-helper")) {
            saw_mmio_queue_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue-register planning helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue size bounds") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-queue-notify-helper")) {
            saw_mmio_queue_notify_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue-notify snapshot helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notify bookkeeping") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-queue-address-helper")) {
            saw_mmio_queue_address_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "version-scoped queue-address planning helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "DESC, AVAIL, and USED") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-config-window-helper")) {
            saw_mmio_config_window_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-window snapshot helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-generation") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "now-landed config-write planning helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "without claiming config writes") == null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-config-write-helper")) {
            saw_mmio_config_write_landed = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-write planning helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "previous and planned values") != null or std.mem.indexOf(u8, gap.why_now, "byte, halfword, and word") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-interrupt-ack-helper")) {
            saw_mmio_interrupt_ack_landed = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "interrupt-status acknowledge bookkeeping") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue and config interrupt bits") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-probe-preflight-helper")) {
            saw_mmio_probe_preflight_landed = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtio_mmio_probe()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "magic, version, device, vendor") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "interrupt-ack readiness") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-lifecycle-and-irq-paths")) {
            saw_mmio_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "interrupt acknowledgement") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue notify side effects") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "interrupt-ack") != null or std.mem.indexOf(u8, gap.why_now, "config-space writes") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 19), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_ring_helper);
    try std.testing.expect(saw_ring_slice_note);
    try std.testing.expect(saw_ring_callback_delay);
    try std.testing.expect(saw_mmio_slice_note);
    try std.testing.expect(saw_mmio_landed_helper);
    try std.testing.expect(saw_mmio_queue_helper);
    try std.testing.expect(saw_mmio_queue_notify_helper);
    try std.testing.expect(saw_mmio_queue_address_helper);
    try std.testing.expect(saw_mmio_config_window_helper);
    try std.testing.expect(saw_mmio_config_write_landed);
    try std.testing.expect(saw_mmio_interrupt_ack_landed);
    try std.testing.expect(saw_mmio_probe_preflight_landed);
    try std.testing.expect(saw_mmio_survey_gate);
    try std.testing.expect(saw_mmio_survey_note);
    try std.testing.expect(saw_mmio_blocker);
}
