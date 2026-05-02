const std = @import("std");
const current_surveyed_commit = "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3";

const SurveySummary = struct {
    test_fsmount_c_lines: usize,
    vfs_makefile_replay_present: bool,
    zig_sample_present: bool,
    phase4_build_present: bool,
    phase4_validator_present: bool,
    phase4_validation_matrix_present: bool,
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
    owner: []const u8,
    rollback_owner: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    current_replay: []const u8,
    isolated_survey_replay: []const u8,
    shared_build_replay: []const u8,
    threshold_posture: []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

const RuntimeAtomic64SiblingManifest = struct {
    phase: []const u8,
    surveyed_commit: []const u8,
};

const PerfBaselineSiblingManifest = struct {
    phase: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    surveyed_commit: []const u8,
};

fn countLines(text: []const u8) usize {
    if (text.len == 0) return 0;

    var lines: usize = 0;
    for (text) |byte| {
        if (byte == '\n') lines += 1;
    }
    return if (text[text.len - 1] == '\n') lines else lines + 1;
}

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next");
}

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

fn gitBlobShaHex(payload: []const u8) [40]u8 {
    var hasher = std.crypto.hash.Sha1.init(.{});
    var header_buf: [64]u8 = undefined;
    const header = std.fmt.bufPrint(&header_buf, "blob {d}\x00", .{payload.len}) catch unreachable;
    hasher.update(header);
    hasher.update(payload);

    var digest: [20]u8 = undefined;
    hasher.final(&digest);

    return std.fmt.bytesToHex(digest, .lower);
}

fn expectGateEvidenceBlob(
    gate_evidence: []const u8,
    marker: []const u8,
    payload: []const u8,
) !void {
    const digest = gitBlobShaHex(payload);
    var line_buf: [128]u8 = undefined;
    const line = try std.fmt.bufPrint(&line_buf, "`{s}={s}`", .{ marker, &digest });
    try std.testing.expect(std.mem.indexOf(u8, gate_evidence, line) != null);
}

test "phase4 test_fsmount survey manifest records the landed survey packet and remaining sample gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_test_fsmount_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P4-L19", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.rollback_owner);
    try std.testing.expect(isLowerHexSha(current_surveyed_commit));
    try std.testing.expectEqualStrings(current_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/vfs/test-fsmount.c", manifest.anchor);
    try std.testing.expectEqualStrings("make M=samples/vfs", manifest.current_replay);
    try std.testing.expectEqualStrings("make -C zigux phase4-test-fsmount-survey", manifest.isolated_survey_replay);
    try std.testing.expectEqualStrings("phase4-test-fsmount-survey-tests", manifest.shared_build_replay);
    try std.testing.expectEqualStrings("c_anchor_only_until_test_fsmount_starter_lands", manifest.threshold_posture);
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("samples/zigux/test_fsmount.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.survey_summary.test_fsmount_c_lines >= 100);
    try std.testing.expect(manifest.survey_summary.vfs_makefile_replay_present);
    try std.testing.expect(!manifest.survey_summary.zig_sample_present);
    try std.testing.expect(manifest.survey_summary.phase4_build_present);
    try std.testing.expect(manifest.survey_summary.phase4_validator_present);
    try std.testing.expect(manifest.survey_summary.phase4_validation_matrix_present);
    try std.testing.expectEqual(@as(usize, 4), manifest.gaps.len);

    const runtime_atomic64_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(runtime_atomic64_manifest_json);
    const runtime_atomic64_parsed = try std.json.parseFromSlice(
        RuntimeAtomic64SiblingManifest,
        std.testing.allocator,
        runtime_atomic64_manifest_json,
        .{ .ignore_unknown_fields = true },
    );
    defer runtime_atomic64_parsed.deinit();
    const runtime_atomic64_manifest = runtime_atomic64_parsed.value;
    try std.testing.expectEqualStrings("Phase 4", runtime_atomic64_manifest.phase);
    try std.testing.expectEqualStrings(current_surveyed_commit, runtime_atomic64_manifest.surveyed_commit);
    try std.testing.expect(isLowerHexSha(runtime_atomic64_manifest.surveyed_commit));

    const perf_baseline_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_perf_baseline_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(perf_baseline_manifest_json);
    const perf_baseline_parsed = try std.json.parseFromSlice(
        PerfBaselineSiblingManifest,
        std.testing.allocator,
        perf_baseline_manifest_json,
        .{ .ignore_unknown_fields = true },
    );
    defer perf_baseline_parsed.deinit();
    const perf_baseline_manifest = perf_baseline_parsed.value;
    try std.testing.expectEqualStrings("Phase 4", perf_baseline_manifest.phase);
    try std.testing.expectEqualStrings("Validation and Perf Team", perf_baseline_manifest.owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", perf_baseline_manifest.rollback_owner);
    try std.testing.expectEqualStrings(current_surveyed_commit, perf_baseline_manifest.surveyed_commit);
    try std.testing.expect(isLowerHexSha(perf_baseline_manifest.surveyed_commit));

    const anchor = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/vfs/test-fsmount.c",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(anchor);
    const vfs_makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/vfs/Makefile",
        std.testing.allocator,
        .limited(8 * 1024),
    );
    defer std.testing.allocator.free(vfs_makefile);
    const phase4_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase4_build);
    const phase4_validator = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/validate-phase4.py",
        std.testing.allocator,
        .limited(96 * 1024),
    );
    defer std.testing.allocator.free(phase4_validator);
    const phase4_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-validation-matrix.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase4_matrix);
    const phase4_gate_evidence = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-gate-evidence.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase4_gate_evidence);
    const phase4_test_fsmount_survey = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_test_fsmount_survey.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase4_test_fsmount_survey);
    const doc_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(doc_readme);
    const script_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(script_readme);
    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);

    const zig_sample_present = blk: {
        std.Io.Dir.cwd().access(io_instance.io(), "samples/zigux/test_fsmount.zig", .{}) catch |err| switch (err) {
            error.FileNotFound => break :blk false,
            else => return err,
        };
        break :blk true;
    };

    const live_summary = SurveySummary{
        .test_fsmount_c_lines = countLines(anchor),
        .vfs_makefile_replay_present = std.mem.indexOf(u8, vfs_makefile, "userprogs-always-y += test-fsmount") != null,
        .zig_sample_present = zig_sample_present,
        .phase4_build_present = std.mem.indexOf(u8, phase4_build, "phase4_test_fsmount_survey.zig") != null and
            std.mem.indexOf(u8, phase4_build, manifest.shared_build_replay) != null,
        .phase4_validator_present = std.mem.indexOf(u8, phase4_validator, "phase4_test_fsmount_manifest.json") != null and
            std.mem.indexOf(u8, phase4_validator, "phase4_test_fsmount_survey.zig") != null,
        .phase4_validation_matrix_present = std.mem.indexOf(u8, phase4_matrix, "phase4_test_fsmount_manifest.json") != null and
            std.mem.indexOf(u8, phase4_matrix, manifest.shared_build_replay) != null and
            std.mem.indexOf(u8, phase4_matrix, manifest.isolated_survey_replay) != null and
            std.mem.indexOf(u8, phase4_matrix, manifest.threshold_posture) != null and
            std.mem.indexOf(u8, phase4_matrix, "`make M=samples/vfs`") != null and
            std.mem.indexOf(u8, phase4_matrix, "C-anchor-only") != null,
    };
    try std.testing.expectEqualDeep(live_summary, manifest.survey_summary);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_manifest_gap = false;
    var saw_gate_gap = false;
    var saw_anchor_gap = false;
    var saw_sample_gap = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase4-test-fsmount-survey-manifest")) {
            saw_manifest_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase4_test_fsmount_manifest.json", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "manifest-backed survey packet") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "C-anchor-only") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-test-fsmount-survey-gate")) {
            saw_gate_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase4_test_fsmount_survey.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 4 build") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "prose-only") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-test-fsmount-c-anchor-replay")) {
            saw_anchor_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/vfs/test-fsmount.c", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`make M=samples/vfs`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "C-anchor-only") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-test-fsmount-zig-sample")) {
            saw_sample_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/test_fsmount.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "still absent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "starter under `samples/zigux/`") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 3), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expect(saw_manifest_gap);
    try std.testing.expect(saw_gate_gap);
    try std.testing.expect(saw_anchor_gap);
    try std.testing.expect(saw_sample_gap);

    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "manifest-backed survey gate now lives in `zigux/tests/phase4_test_fsmount_manifest.json`") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "| `zigux/tests/phase4_test_fsmount_survey.zig` |") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, manifest.shared_build_replay) != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, manifest.isolated_survey_replay) != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, manifest.threshold_posture) != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "| `samples/zigux/test_fsmount.zig` |") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "the Zig lab matrix remains C-anchor-only") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "`make M=samples/vfs` replay contract before claiming this anchor as active Phase 4 work") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_EVIDENCE_MODE=github_connector_readback") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions") != null);
    try expectGateEvidenceBlob(
        phase4_gate_evidence,
        "PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA",
        manifest_json,
    );
    try expectGateEvidenceBlob(
        phase4_gate_evidence,
        "PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA",
        phase4_test_fsmount_survey,
    );
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, current_surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "phase4_test_fsmount_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, manifest.shared_build_replay) != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, manifest.threshold_posture) != null);
    try std.testing.expect(std.mem.indexOf(u8, doc_readme, "phase4-test-fsmount-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, doc_readme, "phase4-test-fsmount-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "make -C zigux phase4-test-fsmount-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "phase4-test-fsmount-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase4_test_fsmount_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase4_test_fsmount_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "make -C zigux phase4-test-fsmount-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "c_anchor_only_until_test_fsmount_starter_lands") != null);
}
