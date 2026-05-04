const std = @import("std");

const SurveySummary = struct {
    virtio_input_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_phase10_build_present: bool,
    preexisting_virtio_core_zig_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_mmio_survey_present: bool,
    preexisting_virtio_input_zig_present: bool,
    preexisting_virtio_input_test_present: bool,
    preexisting_virtio_input_slice_note_present: bool,
    preexisting_virtio_input_module_note_present: bool,
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

test "phase10 virtio input survey manifest records the live starter and remaining gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_virtio_input_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);
    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-input-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);
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
    try std.testing.expectEqualStrings("P10-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 10", manifest.phase);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", manifest.anchor);
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
    try std.testing.expect(manifest.survey_summary.virtio_input_c_lines >= 400);
    try std.testing.expectEqual(@as(usize, 9), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_module_note_present);
    try std.testing.expect(manifest.gaps.len >= 15);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, manifest.surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-virtio-input-probe-preflight-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FREEZE_BOUNDARY_STATUS=aligned") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/workqueue.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/trace/ring_buffer.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/*.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/kernel/") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/helpers/") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "boundary maps") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "concurrency audits") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "explicit stay-in-C decisions where warranted") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "wrapper-first or study-only posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/workqueue_bridge.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/trace/ring_buffer.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/check-phase10-harness-coverage.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/validate-phase10.py") != null);
    try std.testing.expect(closure_manifest == .object);

    const survey_provenance = closure_manifest.object.get("survey_provenance") orelse return error.TestUnexpectedResult;
    try std.testing.expect(survey_provenance == .object);
    const survey_lane_keys = survey_provenance.object.get("lane_keys") orelse return error.TestUnexpectedResult;
    try std.testing.expect(survey_lane_keys == .object);
    const input_lane_key = survey_lane_keys.object.get("input") orelse return error.TestUnexpectedResult;
    try std.testing.expect(input_lane_key == .string);
    try std.testing.expectEqualStrings(manifest.lane_key, input_lane_key.string);
    const surveyed_commits = survey_provenance.object.get("surveyed_commits") orelse return error.TestUnexpectedResult;
    try std.testing.expect(surveyed_commits == .object);
    const input_surveyed_commit = surveyed_commits.object.get("input") orelse return error.TestUnexpectedResult;
    try std.testing.expect(input_surveyed_commit == .string);
    try std.testing.expectEqualStrings(manifest.surveyed_commit, input_surveyed_commit.string);

    const exact_checks = closure_manifest.object.get("exact_checks") orelse return error.TestUnexpectedResult;
    try std.testing.expect(exact_checks == .array);
    var saw_harness_coverage_check = false;
    var saw_validate_phase10_check = false;
    for (exact_checks.array.items) |item| {
        try std.testing.expect(item == .string);
        if (std.mem.eql(u8, item.string, "python3 scripts/zigux/check-phase10-harness-coverage.py")) {
            saw_harness_coverage_check = true;
        }
        if (std.mem.eql(u8, item.string, "python3 scripts/zigux/validate-phase10.py")) {
            saw_validate_phase10_check = true;
        }
    }
    try std.testing.expect(saw_harness_coverage_check);
    try std.testing.expect(saw_validate_phase10_check);

    const landed_input_helper_evidence = closure_manifest.object.get("landed_input_helper_evidence") orelse return error.TestUnexpectedResult;
    try std.testing.expect(landed_input_helper_evidence == .object);
    const input_helper_evidence = landed_input_helper_evidence.object.get("zigux/tests/phase10_virtio_input_manifest.json") orelse return error.TestUnexpectedResult;
    try std.testing.expect(input_helper_evidence == .array);
    const expected_landed_input_helpers = [_][]const u8{
        "phase10-virtio-input-capability-setup-helper",
        "phase10-virtio-input-multitouch-slot-helper",
        "phase10-virtio-input-teardown-observation-helper",
        "phase10-virtio-input-registration-preflight-helper",
        "phase10-virtio-input-queue-callback-preflight-helper",
        "phase10-virtio-input-probe-preflight-helper",
    };
    try std.testing.expectEqual(expected_landed_input_helpers.len, input_helper_evidence.array.items.len);
    for (expected_landed_input_helpers, 0..) |helper_id, index| {
        try std.testing.expect(input_helper_evidence.array.items[index] == .string);
        try std.testing.expectEqualStrings(helper_id, input_helper_evidence.array.items[index].string);
    }

    const blocked_transport_gaps = closure_manifest.object.get("blocked_transport_gaps") orelse return error.TestUnexpectedResult;
    try std.testing.expect(blocked_transport_gaps == .object);
    const input_blocked_gap = blocked_transport_gaps.object.get("zigux/tests/phase10_virtio_input_manifest.json") orelse return error.TestUnexpectedResult;
    try std.testing.expect(input_blocked_gap == .string);
    try std.testing.expectEqualStrings("phase10-virtio-input-registration-lifecycle", input_blocked_gap.string);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_helper = false;
    var saw_gate = false;
    var saw_survey_gate = false;
    var saw_teardown_helper = false;
    var saw_preflight_helper = false;
    var saw_queue_callback_helper = false;
    var saw_probe_preflight_helper = false;
    var saw_blocker = false;

    for (manifest.gaps) |gap| {
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

        if (std.mem.eql(u8, gap.id, "phase10-virtio-input-lab-helper")) {
            saw_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_input.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "identity snapshots") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config bitmaps") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ABS metadata") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "timestamp suppression") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-input-lab-gate")) {
            saw_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase10_virtio_input.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-input-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase10_virtio_input_survey.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-input-capability-setup-helper")) {
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_input.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtinput_cfg_bits()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtinput_cfg_abs()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "input_set_capability()") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-input-multitouch-slot-helper")) {
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_input.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ABS_MT_SLOT") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "input_mt_init_slots()") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-input-teardown-observation-helper")) {
            saw_teardown_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_input.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reset-local cleanup") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "identity strings") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-input-registration-preflight-helper")) {
            saw_preflight_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_input.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "identity") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "slot-init intent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "input_register_device()") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-input-queue-callback-preflight-helper")) {
            saw_queue_callback_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_input.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "registration intent is staged") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "event queue is filled") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "status queue is configured") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "device is ready") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-input-probe-preflight-helper")) {
            saw_probe_preflight_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_input.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "registration intent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue provisioning") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ready-state gating") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "transport-backed probe handoff") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-input-registration-lifecycle")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase10_virtio_input.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "input_register_device()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freeze or restore") != null);
        }
    }

    try std.testing.expect(starter_landed_count >= 13);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_helper);
    try std.testing.expect(saw_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_teardown_helper);
    try std.testing.expect(saw_preflight_helper);
    try std.testing.expect(saw_queue_callback_helper);
    try std.testing.expect(saw_probe_preflight_helper);
    try std.testing.expect(saw_blocker);
}
