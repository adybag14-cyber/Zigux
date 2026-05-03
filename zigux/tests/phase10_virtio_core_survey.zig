const std = @import("std");

const SurveySummary = struct {
    virtio_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_phase10_build_present: bool,
    preexisting_phase10_closure_validator_present: bool,
    preexisting_phase10_closure_note_present: bool,
    preexisting_virtio_core_zig_present: bool,
    preexisting_virtio_core_test_present: bool,
    preexisting_virtio_core_slice_note_present: bool,
    preexisting_virtio_ring_survey_present: bool,
    preexisting_virtio_input_survey_present: bool,
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
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_risky_transport");
}

test "phase10 virtio core survey manifest records the live core validation bundle" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_virtio_core_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase10-virtio-core-survey.md",
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

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const closure_parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, closure_manifest_json, .{});
    defer closure_parsed.deinit();

    const manifest = parsed.value;
    const closure_manifest = closure_parsed.value;
    try std.testing.expectEqualStrings("P10-Y01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 10", manifest.phase);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", manifest.anchor);
    try std.testing.expectEqualStrings("d30cbe483a2f019ae797b309a29556bd58fe00d0", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.virtio_c_lines >= 700);
    try std.testing.expectEqual(@as(usize, 9), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_closure_validator_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_closure_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_survey_present);
    try std.testing.expect(manifest.gaps.len >= 13);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, manifest.surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-config-change-bookkeeping-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-driver-binding-bookkeeping-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-driver-remove-bookkeeping-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-config-generation-summary-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-config-delivery-disposition-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-core-probe-remove-lifecycle") != null);
    try std.testing.expect(closure_manifest == .object);

    const survey_provenance = closure_manifest.object.get("survey_provenance") orelse return error.TestUnexpectedResult;
    try std.testing.expect(survey_provenance == .object);
    const lane_keys = survey_provenance.object.get("lane_keys") orelse return error.TestUnexpectedResult;
    try std.testing.expect(lane_keys == .object);
    const core_lane_key = lane_keys.object.get("core") orelse return error.TestUnexpectedResult;
    try std.testing.expect(core_lane_key == .string);
    try std.testing.expectEqualStrings(manifest.lane_key, core_lane_key.string);
    const surveyed_commits = survey_provenance.object.get("surveyed_commits") orelse return error.TestUnexpectedResult;
    try std.testing.expect(surveyed_commits == .object);
    const core_surveyed_commit = surveyed_commits.object.get("core") orelse return error.TestUnexpectedResult;
    try std.testing.expect(core_surveyed_commit == .string);
    try std.testing.expectEqualStrings(manifest.surveyed_commit, core_surveyed_commit.string);

    const landed_core_helper_evidence = closure_manifest.object.get("landed_core_helper_evidence") orelse return error.TestUnexpectedResult;
    try std.testing.expect(landed_core_helper_evidence == .object);
    const core_helper_evidence = landed_core_helper_evidence.object.get("zigux/tests/phase10_virtio_core_manifest.json") orelse return error.TestUnexpectedResult;
    try std.testing.expect(core_helper_evidence == .array);
    const expected_landed_core_helpers = [_][]const u8{
        "phase10-config-generation-summary-helper",
        "phase10-config-delivery-disposition-helper",
    };
    try std.testing.expectEqual(expected_landed_core_helpers.len, core_helper_evidence.array.items.len);
    for (expected_landed_core_helpers, 0..) |helper_id, index| {
        try std.testing.expect(core_helper_evidence.array.items[index] == .string);
        try std.testing.expectEqualStrings(helper_id, core_helper_evidence.array.items[index].string);
    }

    const roadmap_parity_scoreboard = closure_manifest.object.get("roadmap_parity_scoreboard") orelse return error.TestUnexpectedResult;
    try std.testing.expect(roadmap_parity_scoreboard == .object);
    const lab_only_driver_validation = roadmap_parity_scoreboard.object.get("lab_only_driver_validation") orelse return error.TestUnexpectedResult;
    try std.testing.expect(lab_only_driver_validation == .object);
    const lab_only_driver_validation_status = lab_only_driver_validation.object.get("status") orelse return error.TestUnexpectedResult;
    try std.testing.expect(lab_only_driver_validation_status == .string);
    try std.testing.expectEqualStrings("starter_landed", lab_only_driver_validation_status.string);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_core_helper = false;
    var saw_core_gate = false;
    var saw_survey_gate = false;
    var saw_config_change_helper = false;
    var saw_driver_binding_helper = false;
    var saw_driver_remove_helper = false;
    var saw_config_generation_helper = false;
    var saw_delivery_disposition_helper = false;
    var saw_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_risky_transport")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-core-lab-starter")) {
            saw_core_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "status sequencing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "feature negotiation") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue callback bookkeeping") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-core-lab-gate")) {
            saw_core_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase10_virtio_core.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-core-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase10_virtio_core_survey.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-config-change-bookkeeping-helper")) {
            saw_config_change_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtio_config_enable()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtio_config_disable()") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-driver-binding-bookkeeping-helper")) {
            saw_driver_binding_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "drv && drv->config_changed") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-driver-remove-bookkeeping-helper")) {
            saw_driver_remove_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtio_dev_remove()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ACKNOWLEDGE") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-config-generation-summary-helper")) {
            saw_config_generation_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "config-generation increments") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "last observed generation") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-config-delivery-disposition-helper")) {
            saw_delivery_disposition_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__virtio_config_changed()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "no handler was bound") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-core-probe-remove-lifecycle")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe, full remove, reset") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landed remove-side bookkeeping helper") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expect(starter_landed_count >= 12);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_core_helper);
    try std.testing.expect(saw_core_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_config_change_helper);
    try std.testing.expect(saw_driver_binding_helper);
    try std.testing.expect(saw_driver_remove_helper);
    try std.testing.expect(saw_config_generation_helper);
    try std.testing.expect(saw_delivery_disposition_helper);
    try std.testing.expect(saw_blocker);
}
