const std = @import("std");

const SurveySummary = struct {
    preexisting_nvme_pci_zig_present: bool,
    preexisting_nvme_pci_verifier_present: bool,
    preexisting_phase12_direct_test_present: bool,
    preexisting_phase12_manifest_present: bool,
    preexisting_phase12_build_present: bool,
    preexisting_phase12_make_targets_present: bool,
    preexisting_phase12_fallback_note_present: bool,
    preexisting_phase12_reopen_governance_present: bool,
    preexisting_phase12_slice_note_present: bool,
    preexisting_phase12_survey_note_present: bool,
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

test "phase12 nvme pci survey manifest keeps the bounded queue-and-recovery packet truthful" {
    const manifest_json = try readFileAlloc("zigux/tests/phase12_nvme_pci_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P12-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("unresolved_on_master", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("2026-05-14", manifest.verified_on);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.preexisting_nvme_pci_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_nvme_pci_verifier_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_direct_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_make_targets_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_fallback_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_reopen_governance_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase12_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_gate_present);

    try std.testing.expectEqualStrings("starter_planner_present_runtime_dma_blocked", manifest.roadmap_gap_check.dma_safe_abstractions.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.dma_safe_abstractions.current_surface, "queue-pair planning") != null);
    try std.testing.expectEqualStrings("starter_verifier_direct_test_manifest_and_survey_gate_present_shared_build_unwired", manifest.roadmap_gap_check.queueing_correctness.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.queueing_correctness.current_surface, "dedicated survey gate") != null);
    try std.testing.expectEqualStrings("recovery_budget_summary_and_survey_gate_present_throughput_gate_missing", manifest.roadmap_gap_check.throughput_and_recovery_parity.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.throughput_and_recovery_parity.current_surface, "dropped-backlog retirement") != null);
    try std.testing.expectEqualStrings("driver_local_manifest_survey_note_and_survey_gate_present_slice_note_incomplete", manifest.roadmap_gap_check.segmented_rollout.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.segmented_rollout.blocked_by, "slice note") != null);

    var saw_direct_replay = false;
    var saw_manifest = false;
    var saw_shared_build = false;
    var saw_slice_note = false;
    var saw_survey_note = false;
    var saw_survey_gate = false;
    var saw_fallback = false;
    var saw_reopen = false;

    try std.testing.expectEqual(@as(usize, 8), manifest.gaps.len);
    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        if (std.mem.eql(u8, gap.id, "phase12-nvme-direct-replay")) {
            saw_direct_replay = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase12_nvme_pci.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase12-nvme-manifest-anchor")) {
            saw_manifest = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "survey gate") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-nvme-shared-build-route")) {
            saw_shared_build = true;
            try std.testing.expectEqualStrings("direct_replay_present_shared_build_unwired", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase12-nvme-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("absent_on_master", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-nvme-pci-slice.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase12-nvme-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("survey_present", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-nvme-pci-survey.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase12-nvme-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("survey_present", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase12_nvme_pci_survey.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase12-nvme-fallback-note")) {
            saw_fallback = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase12-nvme-reopen-governance")) {
            saw_reopen = true;
            try std.testing.expectEqualStrings("landed_on_master", gap.status);
        }
    }

    try std.testing.expect(saw_direct_replay);
    try std.testing.expect(saw_manifest);
    try std.testing.expect(saw_shared_build);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_fallback);
    try std.testing.expect(saw_reopen);
}

test "phase12 nvme pci survey note stays aligned with the bounded queue-and-recovery starter" {
    const survey_note = try readFileAlloc("Documentation/zigux/phase12-nvme-pci-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_note);

    const manifest_json = try readFileAlloc("zigux/tests/phase12_nvme_pci_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("2026-05-14", manifest.verified_on);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_STATUS=starter-present-direct-replay-survey-note-and-gate") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_LANE=P12-L08") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "current `master` now carries `drivers/nvme/host/pci.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "planAdminQueue()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "planIoQueue()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "planPrpBufferShape()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "beginReset()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "completeReset()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "recoveryQueueRestoreSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "summarizeDroppedIoRetirement()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "current `master` now carries `zigux/tests/phase12_nvme_pci_survey.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "still does not carry `Documentation/zigux/phase12-nvme-pci-slice.md`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "still does not wire the bounded NVMe direct replay into `zigux/tests/phase12_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "still does not claim live DMA mapping") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "driver-local surfaces") != null);
}

test "phase12 nvme pci survey gate keeps present lane files explicit" {
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci_manifest.json"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci_survey.zig"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-nvme-pci-survey.md"));
    try std.testing.expect(try pathExists("drivers/nvme/host/pci.zig"));
    try std.testing.expect(try pathExists("drivers/nvme/host/pci_verify.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci.zig"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-nvme-pci-reopen-governance.md"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_build.zig"));
    try std.testing.expect(try pathExists("zigux/Makefile"));
    try std.testing.expect(!(try pathExists("Documentation/zigux/phase12-nvme-pci-slice.md")));
}
