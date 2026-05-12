const std = @import("std");

const SurveySummary = struct {
    virtio_net_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_phase10_build_present: bool,
    preexisting_virtio_core_zig_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_input_zig_present: bool,
    preexisting_phase12_build_present: bool,
    preexisting_phase12_virtio_net_survey_present: bool,
    preexisting_phase12_survey_note_present: bool,
    preexisting_virtio_net_zig_present: bool,
    preexisting_phase12_virtio_net_syntax_lab_present: bool,
};

const RoadmapGapStatus = struct {
    required_by_roadmap: bool,
    status: []const u8,
    current_surface: []const u8,
    blocked_by: []const u8,
};

const RoadmapGapCheck = struct {
    dma_safe_abstractions: RoadmapGapStatus,
    queueing_correctness: RoadmapGapStatus,
    throughput_and_recovery_parity: RoadmapGapStatus,
    segmented_rollout: RoadmapGapStatus,
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
    verified_on: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    roadmap_gap_check: RoadmapGapCheck,
    gaps: []const Gap,
};

fn readFileAlloc(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn pathExists(path: []const u8) !bool {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const file = std.Io.Dir.cwd().openFile(io_instance.io(), path, .{}) catch |err| switch (err) {
        error.FileNotFound => return false,
        else => return err,
    };
    file.close(io_instance.io());
    return true;
}

test "phase12 virtio net survey manifest keeps the bounded mergeable-buffer starter truthful" {
    const manifest_json = try readFileAlloc("zigux/tests/phase12_virtio_net_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P12-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("unresolved_on_master", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("2026-05-12", manifest.verified_on);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.virtio_net_c_lines >= 7000);
    try std.testing.expectEqual(@as(usize, 7), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_input_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_syntax_lab_present);

    try std.testing.expectEqualStrings("starter_present_runtime_data_path_blocked", manifest.roadmap_gap_check.dma_safe_abstractions.status);
    try std.testing.expectEqualStrings("starter_present_direct_gate_present_shared_smoke_present", manifest.roadmap_gap_check.queueing_correctness.status);
    try std.testing.expectEqualStrings("starter_present_throughput_gate_missing", manifest.roadmap_gap_check.throughput_and_recovery_parity.status);
    try std.testing.expectEqualStrings("starter_present_direct_lab_present_shared_route_present", manifest.roadmap_gap_check.segmented_rollout.status);

    var saw_starter = false;
    var saw_syntax_lab = false;
    var saw_build_gap = false;
    var saw_runtime_gap = false;

    try std.testing.expectEqual(@as(usize, 8), manifest.gaps.len);
    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-mergeable-receive-buffer-starter")) {
            saw_starter = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "mergeable receive-buffer planner") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-syntax-lab-gate")) {
            saw_syntax_lab = true;
            try std.testing.expectEqualStrings("starter_landed_and_shared_smoke_wired", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_net_syntax_lab.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase12-build-gate")) {
            saw_build_gap = true;
            try std.testing.expectEqualStrings("shared_build_present_with_direct_virtio_net_syntax_lab", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-runtime-data-path")) {
            saw_runtime_gap = true;
            try std.testing.expectEqualStrings("blocked_on_dma_transport_runtime", gap.status);
        }
    }

    try std.testing.expect(saw_starter);
    try std.testing.expect(saw_syntax_lab);
    try std.testing.expect(saw_build_gap);
    try std.testing.expect(saw_runtime_gap);
}

test "phase12 virtio net survey note stays aligned with the bounded starter" {
    const survey_note = try readFileAlloc("Documentation/zigux/phase12-virtio-net-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_note);

    const manifest_json = try readFileAlloc("zigux/tests/phase12_virtio_net_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("2026-05-12", manifest.verified_on);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_STATUS=starter-present-buffer-planner") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "current `master` now carries `drivers/net/virtio_net.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "planMergeableReceiveBuffer()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "current `master` now carries `zigux/tests/phase12_virtio_net_syntax_lab.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared build route now carries the direct `virtio_net` syntax-lab smoke shard") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "still does not claim live DMA-safe receive ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "probe-snapshot or queue-summary follow-up") != null);
}

test "phase12 virtio net survey gate keeps present lane files explicit" {
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_manifest.json"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_survey.zig"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-net-survey.md"));
    try std.testing.expect(try pathExists("drivers/net/virtio_net.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_syntax_lab.zig"));
}
