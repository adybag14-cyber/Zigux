const std = @import("std");

const SurveySummary = struct {
    virtio_mmio_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_virtio_core_zig_present: bool,
    preexisting_phase10_build_present: bool,
    preexisting_phase10_core_doc_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_ring_doc_present: bool,
    preexisting_virtio_ring_survey_present: bool,
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
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_risky_transport");
}

test "phase10 virtio mmio survey manifest records the live transport gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_virtio_mmio_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P10-L09", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 10", manifest.phase);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", manifest.anchor);
    try std.testing.expectEqualStrings("05650d80892a38d40ecb19c733816e3b674f6f5f", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.virtio_mmio_c_lines >= 800);
    try std.testing.expectEqual(@as(usize, 6), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_core_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_survey_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_virtio_mmio_zig_present);
    try std.testing.expect(manifest.gaps.len >= 10);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_mmio_survey_gate = false;
    var saw_mmio_survey_note = false;
    var saw_mmio_register_next = false;
    var saw_mmio_lifecycle_blocker = false;
    var saw_ring_helper = false;
    var saw_ring_delay_helper = false;

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

        if (std.mem.eql(u8, gap.id, "phase10-callback-delay-helper")) {
            saw_ring_delay_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "delayed-callback pacing") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-mmio-survey-gate")) {
            saw_mmio_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase10_virtio_mmio_survey.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-mmio-survey-note")) {
            saw_mmio_survey_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase10-virtio-mmio-survey.md", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-register-window-helper")) {
            saw_mmio_register_next = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "register-window helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue setup") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-lifecycle-and-irq-paths")) {
            saw_mmio_lifecycle_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Interrupt acknowledgement") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe or remove lifecycle") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expect(starter_landed_count >= 8);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_ring_helper);
    try std.testing.expect(saw_ring_delay_helper);
    try std.testing.expect(saw_mmio_survey_gate);
    try std.testing.expect(saw_mmio_survey_note);
    try std.testing.expect(saw_mmio_register_next);
    try std.testing.expect(saw_mmio_lifecycle_blocker);
}
