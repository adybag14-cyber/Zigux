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

test "phase12 nvme pci survey manifest keeps the bounded starter packet truthful" {
    const manifest_json = try readFileAlloc("zigux/tests/phase12_nvme_pci_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
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
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_gate_present);

    try std.testing.expectEqualStrings(
        "starter_verifier_direct_test_manifest_and_survey_gate_present_dedicated_build_present_shared_build_absent",
        manifest.roadmap_gap_check.queueing_correctness.status,
    );
    try std.testing.expectEqualStrings(
        "recovery_budget_summary_and_survey_gate_present_throughput_gate_missing",
        manifest.roadmap_gap_check.throughput_and_recovery_parity.status,
    );
    try std.testing.expectEqualStrings(
        "driver_local_slice_note_manifest_survey_note_and_survey_gate_present_dedicated_build_present_shared_build_absent",
        manifest.roadmap_gap_check.segmented_rollout.status,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            manifest.roadmap_gap_check.queueing_correctness.current_surface,
            "dedicated direct-build route",
        ) != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            manifest.roadmap_gap_check.queueing_correctness.current_surface,
            "`zigux/tests/phase12_build.zig` still stays virtio_net-only",
        ) != null,
    );

    var saw_direct = false;
    var saw_shared_build = false;
    var saw_survey_gate = false;

    try std.testing.expectEqual(@as(usize, 8), manifest.gaps.len);
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, "phase12-nvme-direct-replay")) {
            saw_direct = true;
            try std.testing.expectEqualStrings("landed_on_master_dedicated_build_present", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase12_nvme_pci.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase12-nvme-shared-build-route")) {
            saw_shared_build = true;
            try std.testing.expectEqualStrings(
                "shared_build_absent_dedicated_build_present_survey_gate_standalone",
                gap.status,
            );
            try std.testing.expect(
                std.mem.indexOf(u8, gap.why_now, "shared Phase 12 build route still excludes NVMe") != null,
            );
        }
        if (std.mem.eql(u8, gap.id, "phase12-nvme-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("survey_present_dedicated_route_retained", gap.status);
        }
    }

    try std.testing.expect(saw_direct);
    try std.testing.expect(saw_shared_build);
    try std.testing.expect(saw_survey_gate);
}

test "phase12 nvme pci survey note keeps the roadmap gap and dedicated-build split explicit" {
    const survey_note = try readFileAlloc("Documentation/zigux/phase12-nvme-pci-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_note);

    const manifest_json = try readFileAlloc("zigux/tests/phase12_nvme_pci_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_STATUS=starter_verifier_direct_replay_manifest_and_survey_gate_present_dedicated_build_present_shared_build_absent") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "lane owner: `P12-L08`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/nvme/host/pci.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/nvme/host/pci_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase12_nvme_pci.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase12_nvme_pci_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "dedicated `phase12-nvme-pci-direct-test` route in `zigux/tests/phase12_nvme_pci_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "dedicated `phase12-nvme-pci-survey-test` route in `zigux/tests/phase12_nvme_pci_survey_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase12-nvme-pci-direct-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase12-nvme-pci-survey-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`zigux/tests/phase12_build.zig` route still stays virtio-net-only") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "now wires the NVMe direct replay into the shared `phase12-smoke` and `phase12` routes") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "survey gate still stays packet-local") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "IO queue reservation sizing") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "recovery reservation replay debt") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PRP metadata budgeting") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "live DMA mapping") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "transport-backed queue execution") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, manifest.surveyed_commit) != null);
}

test "phase12 nvme pci reopen governance note keeps the dedicated direct replay and packet-local survey split explicit" {
    const reopen_note = try readFileAlloc("Documentation/zigux/phase12-nvme-pci-reopen-governance.md", 16 * 1024);
    defer std.testing.allocator.free(reopen_note);

    try std.testing.expect(std.mem.indexOf(
        u8,
        reopen_note,
        "dedicated `phase12-nvme-pci-direct-test` route in `zigux/tests/phase12_nvme_pci_build.zig`",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        reopen_note,
        "dedicated `phase12-nvme-pci-survey-test` route in `zigux/tests/phase12_nvme_pci_survey_build.zig`",
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, reopen_note, "make -C zigux phase12-nvme-pci-direct-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, reopen_note, "make -C zigux phase12-nvme-pci-survey-test") != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        reopen_note,
        "`zigux/tests/phase12_build.zig` still stays virtio_net-only",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        reopen_note,
        "must not promote the bounded NVMe starter beyond its current dedicated direct-build claim",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        reopen_note,
        "shares one bounded direct replay through the shared `phase12-smoke` and `phase12` routes",
    ) == null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        reopen_note,
        "`zigux/tests/phase12_build.zig` now wires the NVMe direct replay into the smoke-first shared route",
    ) == null);
}

test "phase12 nvme pci slice note keeps the bounded recovery-preflight packet explicit" {
    const slice_note = try readFileAlloc("Documentation/zigux/phase12-nvme-pci-slice.md", 8 * 1024);
    defer std.testing.allocator.free(slice_note);

    try std.testing.expect(std.mem.indexOf(u8, slice_note, "IO queue reservation sizing") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "recovery reservation replay preflight") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "PRP metadata budgeting") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "dropped-backlog retirement review") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "rollback-gate review") != null);
}

test "phase12 nvme pci survey gate keeps present packet files explicit" {
    try std.testing.expect(try pathExists("drivers/nvme/host/pci.zig"));
    try std.testing.expect(try pathExists("drivers/nvme/host/pci_verify.zig"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-nvme-pci-reopen-governance.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-nvme-pci-slice.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-nvme-pci-survey.md"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci_build.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci_survey_build.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci_manifest.json"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci_survey.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_build.zig"));
    try std.testing.expect(try pathExists("zigux/Makefile"));
}

test "phase12 nvme pci survey gate keeps the dedicated direct route driver-local for NVMe" {
    const shared_build = try readFileAlloc("zigux/tests/phase12_build.zig", 16 * 1024);
    defer std.testing.allocator.free(shared_build);

    const direct_build = try readFileAlloc("zigux/tests/phase12_nvme_pci_build.zig", 16 * 1024);
    defer std.testing.allocator.free(direct_build);

    const survey_build = try readFileAlloc("zigux/tests/phase12_nvme_pci_survey_build.zig", 16 * 1024);
    defer std.testing.allocator.free(survey_build);

    try std.testing.expect(std.mem.indexOf(u8, shared_build, "phase12_virtio_net_queue_resume.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, shared_build, "phase12_virtio_net_transmit_recycle.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, shared_build, "phase12_nvme_pci.zig") == null);
    try std.testing.expect(std.mem.indexOf(u8, shared_build, "phase12-nvme-pci-direct-tests") == null);
    try std.testing.expect(std.mem.indexOf(u8, shared_build, "phase12_nvme_pci_survey.zig") == null);
    try std.testing.expect(std.mem.indexOf(u8, shared_build, "phase12_nvme_pci_survey_build.zig") == null);
    try std.testing.expect(std.mem.indexOf(u8, shared_build, "phase12-nvme-pci-survey-tests") == null);
    try std.testing.expect(std.mem.indexOf(u8, shared_build, "phase12-nvme-pci-survey-test") == null);
    try std.testing.expectEqual(@as(usize, 11), std.mem.count(u8, shared_build, "b.createModule(.{"));
    try std.testing.expectEqual(@as(usize, 5), std.mem.count(u8, shared_build, ".addImport("));
    try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, shared_build, "b.addTest(.{"));
    try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, shared_build, "b.addRunArtifact("));
    try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, shared_build, "smoke_step.dependOn("));
    try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, shared_build, "test_step.dependOn("));

    try std.testing.expect(std.mem.indexOf(u8, direct_build, "phase12_nvme_pci.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_build, "phase12-nvme-pci-direct-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_build, "phase12_nvme_pci_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_build, "phase12-nvme-pci-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_build, "phase12-nvme-pci-survey-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_build, "run_tests.setCwd(b.path(\"../..\"));") != null);
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, survey_build, "b.addTest(.{"));
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, survey_build, "b.addRunArtifact("));
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, survey_build, "test_step.dependOn("));
}

test "phase12 nvme pci survey gate keeps the make wrapper surface explicit" {
    const makefile = try readFileAlloc("zigux/Makefile", 16 * 1024);
    defer std.testing.allocator.free(makefile);

    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-validate:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-smoke:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-test:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-nvme-pci-direct-test:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-nvme-pci-survey-test:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12: phase12-validate phase12-smoke phase12-test") != null);
}

test "phase12 nvme pci survey gate keeps the current recovery helper packet explicit" {
    const helper_source = try readFileAlloc("drivers/nvme/host/pci.zig", 32 * 1024);
    defer std.testing.allocator.free(helper_source);

    const direct_replay = try readFileAlloc("zigux/tests/phase12_nvme_pci.zig", 32 * 1024);
    defer std.testing.allocator.free(direct_replay);

    try std.testing.expect(std.mem.indexOf(u8, helper_source, "planRecoveryReservationReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "recoveryReservationReplayDebtSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "recoveryQueueRestoreSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "summarizeDroppedIoRetirement") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "recoveryRollbackGateSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "queueRestartSummary") == null);

    try std.testing.expect(std.mem.indexOf(u8, direct_replay, "phase12 nvme pci direct replay keeps stale recovery reservation debt explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_replay, "phase12 nvme pci direct replay keeps rollback-gate parity explicit through recovery") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_replay, "phase12 nvme pci direct replay keeps dropped backlog retirement blocked until admin replay completes even after IO parity recovers") != null);
}