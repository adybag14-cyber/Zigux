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
    preexisting_virtio_net_queue_resume_zig_present: bool,
    preexisting_virtio_net_receive_refill_replay_zig_present: bool,
    preexisting_virtio_net_transmit_recycle_zig_present: bool,
    preexisting_virtio_net_post_reset_replay_zig_present: bool,
    preexisting_virtio_net_throughput_parity_zig_present: bool,
    preexisting_phase12_virtio_net_queue_resume_present: bool,
    preexisting_phase12_virtio_net_receive_refill_replay_present: bool,
    preexisting_phase12_virtio_net_transmit_recycle_present: bool,
    preexisting_phase12_virtio_net_post_reset_replay_present: bool,
    preexisting_phase12_virtio_net_throughput_parity_present: bool,
    preexisting_virtio_net_zig_present: bool,
    preexisting_phase12_virtio_net_zig_present: bool,
    preexisting_phase12_virtio_net_syntax_lab_present: bool,
    preexisting_phase12_virtio_net_syntax_lab_build_present: bool,
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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase12 virtio net survey manifest tracks the shared-build survey-gate coverage truthfully" {
    const manifest_json = try readFileAlloc("zigux/tests/phase12_virtio_net_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P12-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("e0c7303b0874af398d4f02221b97a6c9a1e49d5d", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("2026-05-25", manifest.verified_on);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_syntax_lab_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_syntax_lab_build_present);

    try std.testing.expectEqualStrings(
        "split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present",
        manifest.roadmap_gap_check.queueing_correctness.status,
    );
    try expectContains(
        manifest.roadmap_gap_check.queueing_correctness.current_surface,
        "shared validate, smoke, and test routes",
    );
    try expectContains(
        manifest.roadmap_gap_check.queueing_correctness.current_surface,
        "standalone syntax-lab compile-smoke pair",
    );
    try expectContains(
        manifest.roadmap_gap_check.queueing_correctness.current_surface,
        "phase12-virtio-net-syntax-lab-test",
    );
    try expectContains(
        manifest.roadmap_gap_check.throughput_and_recovery_parity.current_surface,
        "explicit receive-refill and transmit-recycle readiness booleans",
    );
    try std.testing.expectEqualStrings(
        "split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete",
        manifest.roadmap_gap_check.segmented_rollout.status,
    );

    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_runtime_data_path_gap = false;
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, "phase12-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings(
                "shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays",
                gap.status,
            );
            try expectContains(gap.why_now, "`phase12_virtio_net_survey`");
            try expectContains(gap.why_now, "`phase12-validate`");
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("survey_present_shared_route_present", gap.status);
            try expectContains(gap.why_now, "`phase12-validate`");
            try expectContains(gap.why_now, "standalone syntax-lab compile-smoke pair");
            try expectContains(gap.why_now, "phase12-virtio-net-syntax-lab-test");
            try expectContains(gap.why_now, "direct build-file command");
            try expectContains(gap.why_now, "blocked runtime-data-path boundary");
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-runtime-data-path")) {
            saw_runtime_data_path_gap = true;
            try std.testing.expectEqualStrings("blocked_on_dma_transport_runtime", gap.status);
            try expectContains(gap.why_now, "receive-refill and transmit-recycle readiness booleans");
        }
    }
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_runtime_data_path_gap);
}

test "phase12 virtio net survey note reflects the shared survey-gate route" {
    const survey_note = try readFileAlloc("Documentation/zigux/phase12-virtio-net-survey.md", 20 * 1024);
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only");
    try expectContains(survey_note, "lane owner: `P12-L04`");
    try expectContains(survey_note, "drivers/net/virtio_net_receive_refill_replay.zig");
    try expectContains(survey_note, "drivers/net/virtio_net_throughput_parity.zig");
    try expectContains(survey_note, "zigux/tests/phase12_virtio_net_syntax_lab.zig");
    try expectContains(survey_note, "zigux/tests/phase12_virtio_net_syntax_lab_build.zig");
    try expectContains(survey_note, "throughput-parity, and `phase12_virtio_net_survey` gates reachable through the shared Phase 12 validate, smoke, and test routes");
    try expectContains(survey_note, "`phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper proof");
    try expectContains(survey_note, "phase12-virtio-net-syntax-lab-test");
    try expectContains(survey_note, "smoke still runs through the direct build-file command");
    try expectContains(survey_note, "explicit receive-refill and transmit-recycle readiness booleans");
    try expectContains(survey_note, "still does not claim live DMA-safe receive ownership");
    try expectContains(survey_note, "performance-risk wording refresh");
}

test "phase12 virtio net syntax lab note keeps the standalone wrapper and smoke split explicit" {
    const syntax_lab_note = try readFileAlloc("Documentation/zigux/phase12-virtio-net-syntax-lab.md", 12 * 1024);
    defer std.testing.allocator.free(syntax_lab_note);

    try expectContains(syntax_lab_note, "PHASE12_STATUS=standalone-syntax-lab-smoke-present");
    try expectContains(syntax_lab_note, "phase12-virtio-net-syntax-lab-test");
    try expectContains(syntax_lab_note, "smoke remains the direct build-file route");
    try expectContains(syntax_lab_note, "shared Phase 12 sextet stays unchanged");
}

test "phase12 virtio net survey gate keeps the present files and shared routes explicit" {
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_manifest.json"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_survey.zig"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-net-survey.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-net-syntax-lab.md"));
    try std.testing.expect(try pathExists("drivers/net/virtio_net_queue_resume.zig"));
    try std.testing.expect(try pathExists("drivers/net/virtio_net_receive_refill_replay.zig"));
    try std.testing.expect(try pathExists("drivers/net/virtio_net_transmit_recycle.zig"));
    try std.testing.expect(try pathExists("drivers/net/virtio_net_post_reset_replay.zig"));
    try std.testing.expect(try pathExists("drivers/net/virtio_net_throughput_parity.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_queue_resume.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_receive_refill_replay.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_transmit_recycle.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_post_reset_replay.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_throughput_parity.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_syntax_lab.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_syntax_lab_build.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_build.zig"));
    try std.testing.expect(!try pathExists("drivers/net/virtio_net.zig"));
    try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_net.zig"));

    const build_zig = try readFileAlloc("zigux/tests/phase12_build.zig", 32 * 1024);
    defer std.testing.allocator.free(build_zig);
    try std.testing.expectEqual(@as(usize, 11), std.mem.count(u8, build_zig, "b.createModule(.{"));
    try std.testing.expectEqual(@as(usize, 5), std.mem.count(u8, build_zig, ".addImport("));
    try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, build_zig, "b.addTest(.{"));
    try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, build_zig, "b.addRunArtifact("));
    try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, build_zig, "smoke_step.dependOn("));
    try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, build_zig, "test_step.dependOn("));
    try expectContains(build_zig, "phase12_virtio_net_queue_resume.zig");
    try expectContains(build_zig, "phase12_virtio_net_receive_refill_replay.zig");
    try expectContains(build_zig, "phase12_virtio_net_transmit_recycle.zig");
    try expectContains(build_zig, "phase12_virtio_net_post_reset_replay.zig");
    try expectContains(build_zig, "phase12_virtio_net_throughput_parity.zig");
    try expectContains(build_zig, "phase12_virtio_net_survey.zig");
    try expectContains(build_zig, "phase12-virtio-net-survey-tests");
    try expectNotContains(build_zig, "phase12_virtio_net.zig");
    try expectNotContains(build_zig, "phase12_virtio_net_syntax_lab.zig");

    const makefile = try readFileAlloc("zigux/Makefile", 32 * 1024);
    defer std.testing.allocator.free(makefile);
    try expectContains(makefile, "phase12-validate:");
    try expectContains(makefile, "phase12-smoke:");
    try expectContains(makefile, "phase12-test:");
    try expectContains(makefile, "phase12-virtio-net-syntax-lab-test:");
    try expectContains(makefile, "phase12: phase12-validate phase12-smoke phase12-test");
    try expectNotContains(makefile, "phase12-virtio-net-syntax-lab-smoke:");
}