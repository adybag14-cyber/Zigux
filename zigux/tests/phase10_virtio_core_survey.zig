const std = @import("std");

const SurveySummary = struct {
    virtio_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_phase10_build_present: bool,
    preexisting_virtio_core_zig_present: bool,
    preexisting_virtio_core_test_present: bool,
    preexisting_virtio_core_reset_queue_test_present: bool,
    preexisting_virtio_driver_id_zig_present: bool,
    preexisting_virtio_driver_id_test_present: bool,
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
        std.mem.eql(u8, status, "blocked_on_risky_transport") or
        std.mem.eql(u8, status, "repo_reality_gap");
}

fn isLowerHexCommit(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |char| {
        if (!std.ascii.isDigit(char) and (char < 'a' or char > 'f')) return false;
    }
    return true;
}

test "phase10 virtio core survey manifest records the roadmap-facing core packet honestly" {
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

    const build_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_file);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P10-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 10", manifest.phase);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", manifest.anchor);
    try std.testing.expect(isLowerHexCommit(manifest.surveyed_commit));

    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("drivers/virtio/*.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("zigux/kernel/", manifest.roadmap_destinations[1]);
    try std.testing.expectEqualStrings("zigux/helpers/", manifest.roadmap_destinations[2]);

    try std.testing.expect(manifest.survey_summary.virtio_c_lines >= 700);
    try std.testing.expectEqual(@as(usize, 11), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_reset_queue_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_driver_id_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_driver_id_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_survey_present);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "lane: `P10-L01`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, manifest.surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-driver-id-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-driver-id-coverage-disposition-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-core-lab-validation-evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-virtio-core-slice.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-core-slice-note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-core-dual-implementation-bridge") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-core-probe-remove-lifecycle") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "lab-only driver validation") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "true lab driver") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/*.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/kernel/") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/helpers/") != null);

    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase10_virtio_core_survey_module") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "\"phase10-virtio-core-survey-tests\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "run_phase10_virtio_core_survey_tests") != null);

    var starter_landed_count: usize = 0;
    var repo_reality_gap_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_driver_id_helper = false;
    var saw_driver_id_coverage_helper = false;
    var saw_slice_note_gap = false;
    var saw_survey_gate = false;
    var saw_survey_note = false;
    var saw_lab_validation_evidence = false;
    var saw_dual_bridge = false;
    var saw_probe_remove_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "repo_reality_gap")) {
            repo_reality_gap_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_risky_transport")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase10-driver-id-helper")) {
            saw_driver_id_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_driver_id.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase10-driver-id-coverage-disposition-helper")) {
            saw_driver_id_coverage_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_driver_id.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase10-virtio-core-slice-note")) {
            saw_slice_note_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase10-virtio-core-slice.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shipped Phase 10 core evidence") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase10-virtio-core-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase10_virtio_core_survey.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase10-virtio-core-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase10-virtio-core-survey.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase10-core-lab-validation-evidence")) {
            saw_lab_validation_evidence = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase10-virtio-core-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "lab-only driver validation evidence") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase10-core-dual-implementation-bridge")) {
            saw_dual_bridge = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dual implementations") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "lab-driver step") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase10-core-probe-remove-lifecycle")) {
            saw_probe_remove_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "true lab driver") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe, full remove, and reset") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expect(starter_landed_count >= 18);
    try std.testing.expectEqual(@as(usize, 0), repo_reality_gap_count);
    try std.testing.expectEqual(@as(usize, 2), blocked_count);
    try std.testing.expect(saw_driver_id_helper);
    try std.testing.expect(saw_driver_id_coverage_helper);
    try std.testing.expect(saw_slice_note_gap);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_lab_validation_evidence);
    try std.testing.expect(saw_dual_bridge);
    try std.testing.expect(saw_probe_remove_blocker);
}
