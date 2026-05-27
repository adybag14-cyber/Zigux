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
    preexisting_phase12_survey_build_present: bool,
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

const FixtureManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    verified_on: []const u8,
    anchor: []const u8,
    fixture_kind: []const u8,
    source_manifest: []const u8,
    scope: []const u8,
    required_paths: []const []const u8,
    expected_absent_paths: []const []const u8,
    notes: []const []const u8,
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

test "phase12 virtio scsi survey manifest keeps the rollback-only packet truthful" {
    const manifest_json = try readFileAlloc("zigux/tests/phase12_virtio_scsi_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P12-L09", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("unresolved_on_master", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("2026-05-24", manifest.verified_on);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(!manifest.survey_summary.preexisting_virtio_scsi_zig_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase12_direct_test_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase12_syntax_lab_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase12_repeated_replan_gate_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase12_repeated_rollback_gate_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase12_support_packet_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_support_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_packet_checker_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_make_targets_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_fallback_catalog_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_build_present);

    try std.testing.expectEqualStrings("rollback_evidence_only_live_starter_missing", manifest.roadmap_gap_check.dma_safe_abstractions.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.dma_safe_abstractions.current_surface, "no longer serves a driver-local starter") != null);
    try std.testing.expectEqualStrings("rollback_evidence_present_no_live_queue_planner", manifest.roadmap_gap_check.queueing_correctness.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.queueing_correctness.current_surface, "support-bundle evidence only") != null);
    try std.testing.expectEqualStrings("rollback_evidence_present_no_runtime_recovery_replay", manifest.roadmap_gap_check.throughput_and_recovery_parity.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.throughput_and_recovery_parity.current_surface, "archival and survey evidence") != null);
    try std.testing.expectEqualStrings("survey_packet_and_fallback_present_driver_local_replay_missing", manifest.roadmap_gap_check.segmented_rollout.status);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_check.segmented_rollout.blocked_by, "repeated rollback gate") != null);

    var saw_driver_gap = false;
    var saw_direct_replay_gap = false;
    var saw_build_gate = false;
    var saw_survey_build_gap = false;
    var saw_survey_gate = false;
    var saw_runtime_gap = false;

    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-driver-starter")) {
            saw_driver_gap = true;
            try std.testing.expectEqualStrings("missing_on_master", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-direct-replay")) {
            saw_direct_replay_gap = true;
            try std.testing.expectEqualStrings("missing_on_master", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase12-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("shared_support_bundle_present", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "survey-gate tests") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-survey-build-route")) {
            saw_survey_build_gap = true;
            try std.testing.expectEqualStrings("rollback_evidence_present", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_scsi_survey_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("rollback_evidence_present", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase12-virtio-scsi-runtime-request-flow")) {
            saw_runtime_gap = true;
            try std.testing.expectEqualStrings("blocked_on_driver_return_dma_scsi_host_runtime", gap.status);
        }
    }

    try std.testing.expect(saw_driver_gap);
    try std.testing.expect(saw_direct_replay_gap);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_survey_build_gap);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_runtime_gap);
}

test "phase12 virtio scsi fixture manifest keeps rollback-only presence and absence explicit" {
    const fixture_json = try readFileAlloc("zigux/tests/fixtures/phase12_virtio_scsi_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(fixture_json);

    const parsed = try std.json.parseFromSlice(FixtureManifest, std.testing.allocator, fixture_json, .{});
    defer parsed.deinit();
    const fixture = parsed.value;

    try std.testing.expectEqualStrings("P12-L09", fixture.lane_key);
    try std.testing.expectEqualStrings("rollback_evidence_presence_manifest", fixture.fixture_kind);
    try std.testing.expectEqualStrings("2026-05-24", fixture.verified_on);
    try std.testing.expect(fixture.required_paths.len == 10);
    try std.testing.expect(fixture.expected_absent_paths.len == 5);

    var saw_survey_build = false;
    for (fixture.required_paths) |path| {
        if (std.mem.eql(u8, path, "zigux/tests/phase12_virtio_scsi_survey_build.zig")) saw_survey_build = true;
    }
    try std.testing.expect(saw_survey_build);
    try std.testing.expect(std.mem.indexOf(u8, fixture.scope, "driver-local starter and replay gates are absent") != null);
}

test "phase12 virtio scsi survey note stays aligned with rollback evidence" {
    const survey_note = try readFileAlloc("Documentation/zigux/phase12-virtio-scsi-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_STATUS=rollback-evidence-only-live-starter-missing") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_LANE=P12-L09") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "verified on: `2026-05-24`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no longer serves `drivers/scsi/virtio_scsi.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "throughput-parity, and survey-gate tests as support-bundle evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback-only split machine-checkable") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase12_virtio_scsi_survey_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test zigux/tests/phase12_virtio_scsi_survey.zig") != null);
}

test "phase12 virtio scsi fallback catalog keeps archival replay distinct from current-master rollback evidence" {
    const fallback_catalog = try readFileAlloc("Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md", 32 * 1024);
    defer std.testing.allocator.free(fallback_catalog);

    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "PHASE12_STATUS=archival-raw-read-fallback") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "commit pin: `ee64eec272a352da1d967999c99bb3c3560c9b97`") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "exact coverage evidence refreshed on `2026-05-25`") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "authenticated contents view now returns this refreshed archival catalog body on current `master`") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "public blob page and public raw `master` fallback now match the refreshed current-master body for this same path as of `2026-05-25`") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "scripts/zigux/check-phase12-cross-compile-smoke.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "check-phase12-cross-compile-smoke.py --self-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "current `master` no longer serves `drivers/scsi/virtio_scsi.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "archival commit-pinned history only") != null);
    try std.testing.expect(std.mem.indexOf(u8, fallback_catalog, "matching current-master archival evidence for this path") != null);
}

test "phase12 virtio scsi survey build boundary keeps the shared phase12 route virtio_net only" {
    const phase12_build = try readFileAlloc("zigux/tests/phase12_build.zig", 32 * 1024);
    defer std.testing.allocator.free(phase12_build);

    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_net_queue_resume.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_net_transmit_recycle.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_net_receive_refill_replay.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_net_post_reset_replay.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_net_throughput_parity.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_net_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12-virtio-net-queue-resume-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12-virtio-net-transmit-recycle-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12-virtio-net-receive-refill-replay-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12-virtio-net-post-reset-replay-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12-virtio-net-throughput-parity-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12-virtio-net-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "virtio_net queue-resume, transmit-recycle, receive-refill replay, post-reset replay, throughput-parity, and survey-gate") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_scsi_survey.zig") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12_virtio_scsi_survey_build.zig") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "phase12-virtio-scsi-survey-tests") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase12_build, "virtio_scsi") == null);
}

test "phase12 virtio scsi survey gate keeps present files present and missing files absent" {
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-scsi-slice.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-scsi-survey.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"));
    try std.testing.expect(try pathExists("zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_manifest.json"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_survey_build.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_survey.zig"));
    try std.testing.expect(try pathExists("scripts/zigux/check-phase12-virtio-scsi-packet.py"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_build.zig"));
    try std.testing.expect(try pathExists("zigux/Makefile"));
    try std.testing.expect(!try pathExists("drivers/scsi/virtio_scsi.zig"));
    try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_scsi.zig"));
    try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_scsi_syntax_lab.zig"));
    try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig"));
    try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig"));
}
