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
    preexisting_virtio_net_transmit_recycle_zig_present: bool,
    preexisting_virtio_net_post_reset_replay_zig_present: bool,
    preexisting_virtio_net_throughput_parity_zig_present: bool,
    preexisting_phase12_virtio_net_queue_resume_present: bool,
    preexisting_phase12_virtio_net_transmit_recycle_present: bool,
    preexisting_phase12_virtio_net_post_reset_replay_present: bool,
    preexisting_phase12_virtio_net_throughput_parity_present: bool,
    preexisting_virtio_net_zig_present: bool,
    preexisting_phase12_virtio_net_zig_present: bool,
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

test "phase12 virtio net survey manifest keeps the split helper packet truthful" {
    const manifest_json = try readFileAlloc("zigux/tests/phase12_virtio_net_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P12-L02", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("4578c45f2ac8ed5cd61412e1140b48d8a7a73628", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("2026-05-19", manifest.verified_on);
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
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_queue_resume_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_transmit_recycle_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_post_reset_replay_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_throughput_parity_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_queue_resume_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_transmit_recycle_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_post_reset_replay_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_throughput_parity_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_virtio_net_zig_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase12_virtio_net_zig_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase12_virtio_net_syntax_lab_present);

    try std.testing.expectEqualStrings(
        "split_queue_resume_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present",
        manifest.roadmap_gap_check.queueing_correctness.status,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            manifest.roadmap_gap_check.queueing_correctness.current_surface,
            "returned Phase 12 make entrypoints still keep the queue-resume and transmit-recycle pair",
        ) != null,
    );
    try std.testing.expectEqualStrings(
        "throughput_parity_helper_present_runtime_completion_missing",
        manifest.roadmap_gap_check.throughput_and_recovery_parity.status,
    );
    try std.testing.expectEqualStrings(
        "split_helper_packet_direct_replays_present_shared_route_partial",
        manifest.roadmap_gap_check.segmented_rollout.status,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            manifest.roadmap_gap_check.segmented_rollout.current_surface,
            "shared build route still keeps only the queue-resume and transmit-recycle pair",
        ) != null,
    );

    var saw_build_gap = false;
    var saw_throughput_gap = false;
    var saw_runtime_gap = false;
    var saw_syntax_gap = false;

    try std.testing.expectEqual(@as(usize, 8), manifest.gaps.len);
    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);

        if (std.mem.eql(u8, gap.id, "phase12-build-gate")) {
            saw_build_gap = true;
            try std.testing.expectEqualStrings(
                "shared_build_present_with_queue_resume_and_transmit_recycle_replays_post_reset_and_throughput_direct_only",
                gap.status,
            );
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtio_net_queue_resume") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "throughput-parity checks still remain direct driver-local tests") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-throughput-parity-followup")) {
            saw_throughput_gap = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
            try std.testing.expectEqualStrings("drivers/net/virtio_net_throughput_parity.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "transmit wake-threshold readiness") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-runtime-data-path")) {
            saw_runtime_gap = true;
            try std.testing.expectEqualStrings("blocked_on_dma_transport_runtime", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-syntax-lab-gate")) {
            saw_syntax_gap = true;
        }
    }

    try std.testing.expect(saw_build_gap);
    try std.testing.expect(saw_throughput_gap);
    try std.testing.expect(saw_runtime_gap);
    try std.testing.expect(!saw_syntax_gap);
}

test "phase12 virtio net survey note stays aligned with the split helper packet" {
    const survey_note = try readFileAlloc("Documentation/zigux/phase12-virtio-net-survey.md", 20 * 1024);
    defer std.testing.allocator.free(survey_note);

    const manifest_json = try readFileAlloc("zigux/tests/phase12_virtio_net_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("2026-05-19", manifest.verified_on);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_STATUS=split-helper-packet-present-throughput-parity-followup") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "lane owner: `P12-L02`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/net/virtio_net_throughput_parity.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "summarizeThroughputParity()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "current `master` does not carry the older monolithic `drivers/net/virtio_net.zig` starter") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12_virtio_net_syntax_lab.zig` shard anymore") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`zigux/Makefile` still exposes `phase12-smoke`, `phase12-test`, and `phase12` convenience entrypoints") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the post-reset replay and throughput-parity checks remain dedicated driver-local tests outside that shared build route") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the packet now exposes queue resume, transmit recycle, post-reset replay, and throughput-parity reviewability") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "still does not claim live DMA-safe receive ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "one bounded complex-driver or segmented-helper step") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "4578c45f2ac8ed5cd61412e1140b48d8a7a73628") != null);
}

test "phase12 virtio net survey gate keeps present lane files and stale scaffold absences explicit" {
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_manifest.json"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_survey.zig"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-net-survey.md"));
    try std.testing.expect(try pathExists("drivers/net/virtio_net_queue_resume.zig"));
    try std.testing.expect(try pathExists("drivers/net/virtio_net_transmit_recycle.zig"));
    try std.testing.expect(try pathExists("drivers/net/virtio_net_post_reset_replay.zig"));
    try std.testing.expect(try pathExists("drivers/net/virtio_net_throughput_parity.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_queue_resume.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_transmit_recycle.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_post_reset_replay.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_throughput_parity.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_build.zig"));
    try std.testing.expect(!try pathExists("drivers/net/virtio_net.zig"));
    try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_net.zig"));
    try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_net_syntax_lab.zig"));
}

test "phase12 virtio net survey gate keeps shared build surface explicit about direct-only follow-ups" {
    const build_zig = try readFileAlloc("zigux/tests/phase12_build.zig", 32 * 1024);
    defer std.testing.allocator.free(build_zig);

    try std.testing.expect(std.mem.indexOf(u8, build_zig, "phase12_virtio_net_queue_resume.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_zig, "phase12_virtio_net_transmit_recycle.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_zig, "phase12-virtio-net-queue-resume-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_zig, "phase12-virtio-net-transmit-recycle-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_zig, "phase12_virtio_net_post_reset_replay.zig") == null);
    try std.testing.expect(std.mem.indexOf(u8, build_zig, "phase12-virtio-net-post-reset-replay-tests") == null);
    try std.testing.expect(std.mem.indexOf(u8, build_zig, "phase12_virtio_net_throughput_parity.zig") == null);
    try std.testing.expect(std.mem.indexOf(u8, build_zig, "phase12-virtio-net-throughput-parity-tests") == null);
}

test "phase12 virtio net survey gate keeps shared make routes explicit" {
    const makefile = try readFileAlloc("zigux/Makefile", 32 * 1024);
    defer std.testing.allocator.free(makefile);

    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-smoke:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-test:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12: phase12-smoke phase12-test") != null);
}

test "phase12 virtio net survey gate keeps throughput parity helper and replay markers explicit" {
    const helper = try readFileAlloc("drivers/net/virtio_net_throughput_parity.zig", 16 * 1024);
    defer std.testing.allocator.free(helper);

    const replay = try readFileAlloc("zigux/tests/phase12_virtio_net_throughput_parity.zig", 16 * 1024);
    defer std.testing.allocator.free(replay);

    try std.testing.expect(std.mem.indexOf(u8, helper, "pub const default_wake_threshold: u16 = 2;") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper, "pub const ThroughputParityStatus = enum") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper, ".needs_post_reset_probe_replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper, ".parity_gate_ready") != null);
    try std.testing.expect(std.mem.indexOf(u8, replay, "phase12 throughput parity gate passes once queue restore refill recycle and replay align") != null);
    try std.testing.expect(std.mem.indexOf(u8, replay, "phase12 throughput parity gate keeps post reset replay explicit when restore stops after refill") != null);
}

test "phase12 virtio net survey gate keeps transmit recycle helper and replay markers explicit" {
    const helper = try readFileAlloc("drivers/net/virtio_net_transmit_recycle.zig", 16 * 1024);
    defer std.testing.allocator.free(helper);

    const replay = try readFileAlloc("zigux/tests/phase12_virtio_net_transmit_recycle.zig", 16 * 1024);
    defer std.testing.allocator.free(replay);

    try std.testing.expect(std.mem.indexOf(u8, helper, "pub const default_wake_threshold: u16 = 2;") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper, "pub const RecycleDisposition = enum") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper, ".wake_queue") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper, ".keep_stopped") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper, ".keep_running") != null);
    try std.testing.expect(std.mem.indexOf(u8, replay, "phase12 virtio net transmit recycle summary stays anchored to virtio_net.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, replay, "phase12 virtio net transmit recycle keeps a stopped queue parked below the wake threshold") != null);
}
