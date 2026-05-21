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

test "phase12 virtio net survey manifest tracks the shared-build quintet and throughput-review boundary truthfully" {
    const manifest_json = try readFileAlloc("zigux/tests/phase12_virtio_net_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P12-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("c36b21af252cf76160ba5ae9c8f84b2310f4b2e1", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("2026-05-21", manifest.verified_on);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.virtio_net_c_lines >= 7000);
    try std.testing.expectEqual(@as(usize, 7), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_queue_resume_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_receive_refill_replay_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_transmit_recycle_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_post_reset_replay_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_net_throughput_parity_zig_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_virtio_net_zig_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase12_virtio_net_zig_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase12_virtio_net_syntax_lab_present);

    try std.testing.expectEqualStrings(
        "split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present",
        manifest.roadmap_gap_check.queueing_correctness.status,
    );
    try expectContains(
        manifest.roadmap_gap_check.queueing_correctness.current_surface,
        "returned Phase 12 make entrypoints now keep the queue-resume, receive-refill replay, transmit-recycle, post-reset replay, and throughput-parity quintet",
    );
    try std.testing.expectEqualStrings(
        "throughput_parity_helper_present_review_only_runtime_completion_missing",
        manifest.roadmap_gap_check.throughput_and_recovery_parity.status,
    );
    try expectContains(
        manifest.roadmap_gap_check.throughput_and_recovery_parity.current_surface,
        "review-only throughput-ratio checks without claiming live transport execution or measured throughput evidence",
    );
    try std.testing.expectEqualStrings(
        "split_helper_packet_direct_replays_present_shared_route_quintet_complete",
        manifest.roadmap_gap_check.segmented_rollout.status,
    );
    try expectContains(
        manifest.roadmap_gap_check.segmented_rollout.current_surface,
        "shared Phase 12 smoke and test routes are present on current master for the full queue-resume, receive-refill replay, transmit-recycle, post-reset replay, and throughput-parity quintet",
    );

    var saw_build_gate = false;
    var saw_receive_refill = false;
    var saw_runtime_block = false;
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, "phase12-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings(
                "shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_and_throughput_replays",
                gap.status,
            );
            try expectContains(gap.why_now, "virtio_net_receive_refill_replay");
            try expectContains(gap.why_now, "virtio_net_post_reset_replay");
            try expectContains(gap.why_now, "virtio_net_throughput_parity");
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-receive-refill-replay-followup")) {
            saw_receive_refill = true;
            try expectContains(gap.why_now, "descriptor repost requirements");
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-throughput-parity-followup")) {
            try expectContains(gap.why_now, "review-only throughput-ratio summary");
            try expectContains(gap.why_now, "measured transport throughput evidence");
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-net-runtime-data-path")) {
            saw_runtime_block = true;
            try std.testing.expectEqualStrings("blocked_on_dma_transport_runtime", gap.status);
            try expectContains(gap.why_now, "measured transport throughput evidence");
        }
    }
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_receive_refill);
    try std.testing.expect(saw_runtime_block);
}

test "phase12 virtio net survey note reflects the quintet and preserved non-goals" {
    const survey_note = try readFileAlloc("Documentation/zigux/phase12-virtio-net-survey.md", 20 * 1024);
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "PHASE12_STATUS=split-helper-packet-present-shared-build-quintet-throughput-review-only");
    try expectContains(survey_note, "lane owner: `P12-L04`");
    try expectContains(survey_note, "c36b21af252cf76160ba5ae9c8f84b2310f4b2e1");
    try expectContains(survey_note, "drivers/net/virtio_net_receive_refill_replay.zig");
    try expectContains(survey_note, "drivers/net/virtio_net_throughput_parity.zig");
    try expectContains(survey_note, "summarizeReceiveRefillReplay()");
    try expectContains(survey_note, "summarizeThroughputParity()");
    try expectContains(survey_note, "review-only throughput-ratio checks");
    try expectContains(survey_note, "not measured transport throughput evidence");
    try expectContains(survey_note, "current `master` does not carry the older monolithic `drivers/net/virtio_net.zig` starter");
    try expectContains(survey_note, "`zigux/tests/phase12_build.zig` now keeps the dedicated `virtio_net_queue_resume`, `virtio_net_receive_refill_replay`, `virtio_net_transmit_recycle`, `virtio_net_post_reset_replay`, and `virtio_net_throughput_parity` replays reachable through the shared Phase 12 smoke and test routes");
    try expectContains(survey_note, "the shared Phase 12 build route reruns that quintet");
    try expectContains(survey_note, "still does not claim live DMA-safe receive ownership");
    try expectContains(survey_note, "performance-risk wording refresh");
}

test "phase12 virtio net survey gate keeps the present files and shared routes explicit" {
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_manifest.json"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_survey.zig"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-net-survey.md"));
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
    try std.testing.expect(try pathExists("zigux/tests/phase12_build.zig"));
    try std.testing.expect(!try pathExists("drivers/net/virtio_net.zig"));
    try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_net.zig"));
    try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_net_syntax_lab.zig"));

    const build_zig = try readFileAlloc("zigux/tests/phase12_build.zig", 32 * 1024);
    defer std.testing.allocator.free(build_zig);
    try std.testing.expectEqual(@as(usize, 10), std.mem.count(u8, build_zig, "b.createModule(.{"));
    try std.testing.expectEqual(@as(usize, 5), std.mem.count(u8, build_zig, ".addImport("));
    try std.testing.expectEqual(@as(usize, 5), std.mem.count(u8, build_zig, "b.addTest(.{"));
    try std.testing.expectEqual(@as(usize, 5), std.mem.count(u8, build_zig, "b.addRunArtifact("));
    try std.testing.expectEqual(@as(usize, 5), std.mem.count(u8, build_zig, "smoke_step.dependOn("));
    try std.testing.expectEqual(@as(usize, 5), std.mem.count(u8, build_zig, "test_step.dependOn("));
    try expectContains(build_zig, "phase12_virtio_net_queue_resume.zig");
    try expectContains(build_zig, "phase12_virtio_net_receive_refill_replay.zig");
    try expectContains(build_zig, "phase12_virtio_net_transmit_recycle.zig");
    try expectContains(build_zig, "phase12_virtio_net_post_reset_replay.zig");
    try expectContains(build_zig, "phase12_virtio_net_throughput_parity.zig");
    try expectContains(build_zig, "phase12-virtio-net-queue-resume-tests");
    try expectContains(build_zig, "phase12-virtio-net-receive-refill-replay-tests");
    try expectContains(build_zig, "phase12-virtio-net-transmit-recycle-tests");
    try expectContains(build_zig, "phase12-virtio-net-post-reset-replay-tests");
    try expectContains(build_zig, "phase12-virtio-net-throughput-parity-tests");
    try expectNotContains(build_zig, "phase12_virtio_net.zig");
    try expectNotContains(build_zig, "phase12_virtio_net_syntax_lab.zig");

    const makefile = try readFileAlloc("zigux/Makefile", 32 * 1024);
    defer std.testing.allocator.free(makefile);
    try expectContains(makefile, "phase12-smoke:");
    try expectContains(makefile, "phase12-test:");
    try expectContains(makefile, "phase12: phase12-smoke phase12-test");
    try expectNotContains(makefile, "phase12-validate:");
    try expectNotContains(makefile, "phase12: phase12-validate phase12-smoke phase12-test");
}

test "phase12 virtio net survey gate keeps split helper markers explicit" {
    const queue_resume_helper = try readFileAlloc("drivers/net/virtio_net_queue_resume.zig", 16 * 1024);
    defer std.testing.allocator.free(queue_resume_helper);
    const queue_resume_replay = try readFileAlloc("zigux/tests/phase12_virtio_net_queue_resume.zig", 16 * 1024);
    defer std.testing.allocator.free(queue_resume_replay);
    const receive_refill_helper = try readFileAlloc("drivers/net/virtio_net_receive_refill_replay.zig", 16 * 1024);
    defer std.testing.allocator.free(receive_refill_helper);
    const receive_refill_replay = try readFileAlloc("zigux/tests/phase12_virtio_net_receive_refill_replay.zig", 16 * 1024);
    defer std.testing.allocator.free(receive_refill_replay);
    const post_reset_helper = try readFileAlloc("drivers/net/virtio_net_post_reset_replay.zig", 16 * 1024);
    defer std.testing.allocator.free(post_reset_helper);
    const post_reset_replay = try readFileAlloc("zigux/tests/phase12_virtio_net_post_reset_replay.zig", 16 * 1024);
    defer std.testing.allocator.free(post_reset_replay);
    const throughput_helper = try readFileAlloc("drivers/net/virtio_net_throughput_parity.zig", 16 * 1024);
    defer std.testing.allocator.free(throughput_helper);
    const throughput_replay = try readFileAlloc("zigux/tests/phase12_virtio_net_throughput_parity.zig", 16 * 1024);
    defer std.testing.allocator.free(throughput_replay);
    const transmit_helper = try readFileAlloc("drivers/net/virtio_net_transmit_recycle.zig", 16 * 1024);
    defer std.testing.allocator.free(transmit_helper);
    const transmit_replay = try readFileAlloc("zigux/tests/phase12_virtio_net_transmit_recycle.zig", 16 * 1024);
    defer std.testing.allocator.free(transmit_replay);

    try expectContains(queue_resume_helper, "pub const QueueResumeBlocker = enum");
    try expectContains(queue_resume_helper, ".control_queue_restore");
    try expectContains(queue_resume_helper, ".refill_replay");
    try expectContains(queue_resume_helper, ".transmit_recycle");
    try expectContains(queue_resume_helper, ".probe_snapshot_replay");
    try expectContains(queue_resume_replay, "phase12 virtio net queue resume stays lab-only and fail-closed");
    try expectContains(queue_resume_replay, "QueueResumeBlocker.probe_snapshot_replay");
    try expectContains(queue_resume_replay, "QueueResumeBlocker.none");

    try expectContains(receive_refill_helper, "pub const ReceiveRefillReplayBlocker = enum");
    try expectContains(receive_refill_helper, ".control_queue_restore");
    try expectContains(receive_refill_helper, ".queue_pair_restore");
    try expectContains(receive_refill_helper, ".refill_budget_restore");
    try expectContains(receive_refill_helper, ".descriptor_repost");
    try expectContains(receive_refill_replay, "phase12 virtio net receive refill replay stays lab-only and fail-closed");
    try expectContains(receive_refill_replay, "ReceiveRefillReplayBlocker.descriptor_repost");
    try expectContains(receive_refill_replay, "ReceiveRefillReplayBlocker.none");

    try expectContains(post_reset_helper, "pub const PostResetReplayBlocker = enum");
    try expectContains(post_reset_helper, "pub const PostResetReplayCheckpoint = enum");
    try expectContains(post_reset_helper, ".after_control_queue_restore");
    try expectContains(post_reset_helper, ".after_receive_refill_replay");
    try expectContains(post_reset_helper, ".after_transmit_recycle");
    try expectContains(post_reset_helper, ".after_probe_snapshot_replay");
    try expectContains(post_reset_replay, "phase12 virtio net post reset replay stays lab-only and fail-closed");
    try expectContains(post_reset_replay, "PostResetReplayCheckpoint.after_probe_snapshot_replay");
    try expectContains(post_reset_replay, "PostResetReplayCheckpoint.queues_may_resume");

    try expectContains(throughput_helper, "pub const default_wake_threshold: u16 = 2;");
    try expectContains(throughput_helper, "pub const ThroughputParityStatus = enum");
    try expectContains(throughput_helper, ".needs_post_reset_probe_replay");
    try expectContains(throughput_helper, ".parity_gate_ready");
    try expectContains(throughput_replay, "phase12 throughput parity gate passes once queue restore refill recycle and replay align");
    try expectContains(throughput_replay, "phase12 throughput parity gate keeps receive refill explicit after control queue restore even when transmit never stopped");

    try expectContains(transmit_helper, "pub const default_wake_threshold: u16 = 2;");
    try expectContains(transmit_helper, "pub const RecycleDisposition = enum");
    try expectContains(transmit_helper, ".wake_queue");
    try expectContains(transmit_helper, ".keep_stopped");
    try expectContains(transmit_helper, ".keep_running");
    try expectContains(transmit_replay, "phase12 virtio net transmit recycle summary stays anchored to virtio_net.c");
    try expectContains(transmit_replay, "phase12 virtio net transmit recycle keeps a stopped queue parked below the wake threshold");
}
