const std = @import("std");

const SurveySummary = struct {
    preexisting_virtio_scsi_zig_present: bool,
    preexisting_phase12_direct_test_present: bool,
    preexisting_phase12_syntax_lab_present: bool,
    preexisting_phase12_repeated_replan_gate_present: bool,
    preexisting_phase12_repeated_rollback_gate_present: bool,
    preexisting_phase12_support_packet_present: bool,
    preexisting_phase12_support_manifest_present: bool,
    preexisting_phase12_packet_checker_present: bool,
    preexisting_phase12_slice_note_present: bool,
    preexisting_phase12_build_present: bool,
    preexisting_phase12_make_targets_present: bool,
    preexisting_phase12_survey_note_present: bool,
    preexisting_phase12_fallback_catalog_present: bool,
    preexisting_phase12_survey_gate_present: bool,
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

test "phase12 virtio scsi survey manifest keeps the bounded queue-and-recovery packet truthful" {
    const manifest_json = try readFileAlloc("zigux/tests/phase12_virtio_scsi_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P12-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("unresolved_on_master", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("2026-05-19", manifest.verified_on);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_scsi_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_direct_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_syntax_lab_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_repeated_replan_gate_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_repeated_rollback_gate_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase12_support_packet_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_support_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_packet_checker_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_make_targets_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_fallback_catalog_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_gate_present);

    try std.testing.expectEqualStrings("starter_present_runtime_dma_blocked", manifest.roadmap_gap_check.dma_safe_abstractions.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.dma_safe_abstractions.current_surface, "control-path governance") != null);
    try std.testing.expectEqualStrings("starter_queue_submit_completion_host_limit_depth_io_map_recovery_present_lane_local_validation_present_shared_build_missing", manifest.roadmap_gap_check.queueing_correctness.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.queueing_correctness.current_surface, "shared phase12 build route no longer replays the virtio_scsi packet") != null);
    try std.testing.expectEqualStrings("starter_completion_and_recovery_summary_present_runtime_execution_missing", manifest.roadmap_gap_check.throughput_and_recovery_parity.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.throughput_and_recovery_parity.current_surface, "control-path restore reviewability") != null);
    try std.testing.expectEqualStrings("survey_packet_direct_replay_and_rollback_validation_present_support_packet_removed", manifest.roadmap_gap_check.segmented_rollout.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.segmented_rollout.current_surface, "older support replay was removed") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.segmented_rollout.blocked_by, "Scsi_Host registration") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.segmented_rollout.blocked_by, "TMF execution") != null);

    var saw_build_gap = false;
    var saw_survey_gate = false;
    var saw_support_packet = false;
    var saw_runtime_gap = false;

    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        if (std.mem.eql(u8, gap.id, "phase12-build-gate")) {
            saw_build_gap = true;
            try std.testing.expectEqualStrings("lane_local_validation_present_shared_build_missing", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtio_net queue-resume") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("lane_local_validation_present", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "removed support packet") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-support-packet")) {
            saw_support_packet = true;
            try std.testing.expectEqualStrings("support_packet_removed_survey_manifest_present", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_scsi_manifest.json", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-runtime-request-flow")) {
            saw_runtime_gap = true;
            try std.testing.expectEqualStrings("blocked_on_dma_scsi_host_runtime", gap.status);
        }
    }

    try std.testing.expect(saw_build_gap);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_support_packet);
    try std.testing.expect(saw_runtime_gap);
}

test "phase12 virtio scsi survey note stays aligned with the bounded queue-and-recovery starter" {
    const survey_note = try readFileAlloc("Documentation/zigux/phase12-virtio-scsi-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_note);

    const manifest_json = try readFileAlloc("zigux/tests/phase12_virtio_scsi_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P12-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("2026-05-19", manifest.verified_on);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_STATUS=starter-present-queue-submit-completion-and-recovery-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_LANE=P12-L13") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "verified on: `2026-05-19`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "recoveryControlPathGovernanceSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "support-manifest reminder surfaces") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared build route now covers only the `virtio_net`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rather than replaying the `virtio_scsi` lane-local packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/check-phase12-virtio-scsi-packet.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test zigux/tests/phase12_virtio_scsi_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "support packet") == null);
}

test "phase12 virtio scsi fallback catalog keeps commit-pinned raw replay distinct from current-master survey companions" {
    const fallback_catalog = try readFileAlloc("Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md", 32 * 1024);
    defer std.testing.allocator.free(fallback_catalog);

    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "commit pin: `ee64eec272a352da1d967999c99bb3c3560c9b97`") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "shared-tree current-master survey companions") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "historical fallback snapshot for the pinned raw-read packet") != null);
}

test "phase12 virtio scsi survey gate keeps present lane files explicit" {
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_manifest.json"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_survey.zig"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-scsi-survey.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"));
    try std.testing.expect(try pathExists("drivers/scsi/virtio_scsi.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_syntax_lab.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig"));
    try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_scsi_packet.zig"));
    try std.testing.expect(try pathExists("zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"));
    try std.testing.expect(try pathExists("scripts/zigux/check-phase12-virtio-scsi-packet.py"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-scsi-slice.md"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_build.zig"));
    try std.testing.expect(try pathExists("zigux/Makefile"));
}
