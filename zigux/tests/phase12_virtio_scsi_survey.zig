const std = @import("std");

const SurveySummary = struct {
    preexisting_virtio_scsi_zig_present: bool,
    preexisting_phase12_direct_test_present: bool,
    preexisting_phase12_syntax_lab_present: bool,
    preexisting_phase12_repeated_replan_gate_present: bool,
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

    try std.testing.expectEqualStrings("P12-L09", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("unresolved_on_master", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("2026-05-13", manifest.verified_on);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_scsi_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_direct_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_syntax_lab_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_repeated_replan_gate_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_support_packet_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_support_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_packet_checker_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_make_targets_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_fallback_catalog_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_gate_present);

    try std.testing.expectEqualStrings("starter_present_runtime_dma_blocked", manifest.roadmap_gap_check.dma_safe_abstractions.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.dma_safe_abstractions.current_surface, "completion-handback sequencing") != null);
    try std.testing.expectEqualStrings("starter_queue_submit_completion_host_limit_depth_io_map_recovery_present_direct_tests_present_shared_smoke_present", manifest.roadmap_gap_check.queueing_correctness.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.queueing_correctness.current_surface, "completion-handback sequencing") != null);
    try std.testing.expectEqualStrings("starter_completion_and_recovery_summary_present_runtime_execution_missing", manifest.roadmap_gap_check.throughput_and_recovery_parity.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.throughput_and_recovery_parity.current_surface, "completion-handback ordering") != null);
    try std.testing.expectEqualStrings("support_packet_survey_packet_submit_and_completion_summary_present", manifest.roadmap_gap_check.segmented_rollout.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.segmented_rollout.current_surface, "control-path governance") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.segmented_rollout.blocked_by, "Scsi_Host registration") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.segmented_rollout.blocked_by, "TMF execution") != null);

    var saw_support_packet = false;
    var saw_survey_note = false;
    var saw_survey_gate = false;
    var saw_queue_layout = false;
    var saw_host_limit = false;
    var saw_queue_depth = false;
    var saw_command_buffer = false;
    var saw_request_submit = false;
    var saw_completion_handback = false;
    var saw_io_map_recovery = false;
    var saw_runtime_gap = false;

    try std.testing.expectEqual(@as(usize, 15), manifest.gaps.len);
    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-support-packet")) {
            saw_support_packet = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_scsi_packet.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("survey_present", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-virtio-scsi-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "request-submit sequencing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fallback-path") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rollback-facing") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("survey_present", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_scsi_survey.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-queue-layout-starter")) {
            saw_queue_layout = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "planQueueLayout()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-host-limit-summary")) {
            saw_host_limit = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "captureHostLimitSummary()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-queue-depth-summary")) {
            saw_queue_depth = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "recoveryQueueDepthSummary()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-command-buffer-ownership-summary")) {
            saw_command_buffer = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "captureCommandBufferOwnershipSummary()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-request-submit-sequencing-summary")) {
            saw_request_submit = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "captureRequestSubmitSequencingSummary()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-completion-handback-sequencing-summary")) {
            saw_completion_handback = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "captureCompletionHandbackSummary()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-io-map-and-recovery-summary")) {
            saw_io_map_recovery = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "recoveryEventBufferOwnershipSummary()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "recoveryHostScanSummary()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-runtime-request-flow")) {
            saw_runtime_gap = true;
            try std.testing.expectEqualStrings("blocked_on_dma_scsi_host_runtime", gap.status);
        }
    }

    try std.testing.expect(saw_support_packet);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_queue_layout);
    try std.testing.expect(saw_host_limit);
    try std.testing.expect(saw_queue_depth);
    try std.testing.expect(saw_command_buffer);
    try std.testing.expect(saw_request_submit);
    try std.testing.expect(saw_completion_handback);
    try std.testing.expect(saw_io_map_recovery);
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

    try std.testing.expectEqualStrings("P12-L09", manifest.lane_key);
    try std.testing.expectEqualStrings("2026-05-13", manifest.verified_on);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_STATUS=starter-present-queue-submit-completion-and-recovery-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_LANE=P12-L09") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "current `master` now carries `drivers/scsi/virtio_scsi.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "captureProbeSnapshot()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "captureHostLimitSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "captureQueueDepthSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "captureRequestSubmitSequencingSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "captureCompletionHandbackSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "captureCommandBufferOwnershipSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "captureIoQueueMapSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "recoveryQueuePlan()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "recoveryEventBufferOwnershipSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "recoveryHostScanSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "request-queue selection") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "completion-handback ordering") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12_virtio_scsi_packet.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback owner: `P12-L09`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "fallback path: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "reversible-delivery evidence:") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback drill: when this packet moves") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig build smoke --build-file zigux/tests/phase12_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase12-smoke") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase12") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "still does not claim live DMA-safe request submission") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "control-path governance, command-buffer ownership, request-submit sequencing, completion-handback sequencing, and recovery ordering as already-landed bounded review surfaces") != null);
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
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_packet.zig"));
    try std.testing.expect(try pathExists("zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"));
    try std.testing.expect(try pathExists("scripts/zigux/check-phase12-virtio-scsi-packet.py"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-scsi-slice.md"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_build.zig"));
    try std.testing.expect(try pathExists("zigux/Makefile"));
}
