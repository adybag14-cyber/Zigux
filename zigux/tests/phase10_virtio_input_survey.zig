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

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P10-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 10", manifest.phase);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", manifest.anchor);
    try std.testing.expectEqualStrings("41ee426b91cf612f2d7a5ef5e4754109fc8b6e16", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.virtio_input_c_lines >= 400);
    try std.testing.expectEqual(@as(usize, 5), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_module_note_present);
    try std.testing.expect(manifest.gaps.len >= 10);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_helper = false;
    var saw_gate = false;
    var saw_survey_gate = false;
    var saw_slot_helper = false;
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
            saw_slot_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_input.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ABS_MT_SLOT") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "slot-planning helper") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-input-registration-lifecycle")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase10_virtio_input.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "input_register_device()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freeze or restore") != null);
        }
    }

    try std.testing.expect(starter_landed_count >= 10);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_helper);
    try std.testing.expect(saw_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_slot_helper);
    try std.testing.expect(saw_blocker);
}
