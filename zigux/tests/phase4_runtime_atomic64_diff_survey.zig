const std = @import("std");
const current_surveyed_commit = "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3";
const expected_phase4_required_file_count: usize = 27;
const expected_phase4_required_marker_count: usize = 55;
const expected_phase4_gate_evidence_target_count: usize = 17;

const SurveySummary = struct {
    atomic64_test_c_lines: usize,
    runtime_atomic64_diff_lines: usize,
    roadmap_atomic64_diff_present: bool,
    roadmap_atomic64_wrapper_targets_runtime_diff: bool,
    runtime_atomic64_diff_present: bool,
    post_selftest_replay_present: bool,
    phase4_build_present: bool,
    phase4_build_uses_atomic64_wrapper: bool,
    phase9_build_present: bool,
    phase9_build_uses_runtime_atomic64_diff: bool,
    phase4_validator_runtime_atomic64_diff_present: bool,
    phase4_validator_atomic64_diff_present: bool,
    runtime_atomic64_sample_present: bool,
    phase4_validation_matrix_present: bool,
    tests_readme_runtime_atomic64_diff_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const ThresholdPlan = struct {
    owner: []const u8,
    rollback_owner: []const u8,
    posture: []const u8,
    status: []const u8,
    benchmark_command: []const u8,
    acceptable_limit: []const u8,
    scope: []const u8,
    why_not_approved_yet: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    threshold_plan: ThresholdPlan,
    gaps: []const Gap,
};

fn readWorkspaceFile(
    io: anytype,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

fn countLines(text: []const u8) usize {
    if (text.len == 0) return 0;

    var lines: usize = 0;
    for (text) |byte| {
        if (byte == '\n') lines += 1;
    }
    return if (text[text.len - 1] == '\n') lines else lines + 1;
}

fn lineContaining(text: []const u8, marker: []const u8) ?[]const u8 {
    const start = std.mem.indexOf(u8, text, marker) orelse return null;
    const line_start = std.mem.lastIndexOfScalar(u8, text[0..start], '\n');
    const slice_start = if (line_start) |index| index + 1 else 0;
    const line_end = std.mem.indexOfScalarPos(u8, text, start, '\n') orelse text.len;
    return text[slice_start..line_end];
}

fn expectLineContains(line: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, line, marker) != null);
}

fn expectAtomic64MatrixGovernanceRow(phase4_validation_matrix: []const u8) !void {
    const row = lineContaining(
        phase4_validation_matrix,
        "| `zigux/tests/atomic64_diff.zig` |",
    ) orelse return error.MissingAtomic64MatrixGovernanceRow;

    try expectLineContains(row, "| `ABI and Runtime Team` | `ABI and Runtime Team` |");
    try expectLineContains(row, "`make -C zigux phase4-runtime-atomic64-diff`");
    try expectLineContains(
        row,
        "`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig`",
    );
    try expectLineContains(row, "`threshold_pending_until_runtime_atomic64_scope_widens`");
    try expectLineContains(row, "`lib/atomic64_test.c` stays the source of truth");
}

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_broader_atomic64_surface");
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

fn expectGateEvidenceCount(
    gate_evidence: []const u8,
    marker: []const u8,
    expected: usize,
) !void {
    const start = std.mem.indexOf(u8, gate_evidence, marker) orelse return error.MissingGateEvidenceMarker;
    const value_start = start + marker.len;
    const value_end = std.mem.indexOfScalarPos(u8, gate_evidence, value_start, '`') orelse return error.UnterminatedGateEvidenceMarker;
    const value = try std.fmt.parseInt(usize, gate_evidence[value_start..value_end], 10);
    try std.testing.expectEqual(expected, value);
}

fn expectSourceHas(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn expectSourceLacks(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) == null);
}

test "phase4 runtime atomic64 survey manifest records the shipped bounded gate, roadmap entrypoint, and remaining broader-surface gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P4-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", manifest.anchor);
    try std.testing.expect(isLowerHexSha(current_surveyed_commit));
    try std.testing.expectEqualStrings(current_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("zigux/tests/atomic64_diff.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.survey_summary.atomic64_test_c_lines >= 250);
    try std.testing.expect(manifest.survey_summary.runtime_atomic64_diff_lines >= 200);
    try std.testing.expectEqual(true, manifest.survey_summary.roadmap_atomic64_diff_present);
    try std.testing.expect(manifest.survey_summary.roadmap_atomic64_wrapper_targets_runtime_diff);
    try std.testing.expect(manifest.survey_summary.runtime_atomic64_diff_present);
    try std.testing.expect(manifest.survey_summary.post_selftest_replay_present);
    try std.testing.expect(manifest.survey_summary.phase4_build_present);
    try std.testing.expect(manifest.survey_summary.phase4_build_uses_atomic64_wrapper);
    try std.testing.expect(manifest.survey_summary.phase9_build_present);
    try std.testing.expect(manifest.survey_summary.phase9_build_uses_runtime_atomic64_diff);
    try std.testing.expect(manifest.survey_summary.phase4_validator_runtime_atomic64_diff_present);
    try std.testing.expect(manifest.survey_summary.phase4_validator_atomic64_diff_present);
    try std.testing.expect(manifest.survey_summary.runtime_atomic64_sample_present);
    try std.testing.expect(manifest.survey_summary.phase4_validation_matrix_present);
    try std.testing.expect(manifest.survey_summary.tests_readme_runtime_atomic64_diff_present);
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.threshold_plan.owner);
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.threshold_plan.rollback_owner);
    try std.testing.expectEqualStrings(
        "threshold_pending_until_runtime_atomic64_scope_widens",
        manifest.threshold_plan.posture,
    );
    try std.testing.expectEqualStrings(
        "pending_scope_widening",
        manifest.threshold_plan.status,
    );
    try std.testing.expectEqualStrings(
        "unapproved_until_runtime_atomic64_scope_widens",
        manifest.threshold_plan.benchmark_command,
    );
    try std.testing.expectEqualStrings(
        "unapproved_until_runtime_atomic64_scope_widens",
        manifest.threshold_plan.acceptable_limit,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.threshold_plan.scope, "selftest-family plus post-selftest replay set") != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.threshold_plan.scope, "sub") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.threshold_plan.scope, "bitwise") != null);
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.threshold_plan.why_not_approved_yet, "correctness-only coverage") != null,
    );
    try std.testing.expectEqual(@as(usize, 6), manifest.gaps.len);

    const atomic64_test_c = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "lib/atomic64_test.c",
        64 * 1024,
    );
    defer std.testing.allocator.free(atomic64_test_c);
    const runtime_atomic64_diff = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/runtime_atomic64_diff.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(runtime_atomic64_diff);
    const atomic64_diff = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/atomic64_diff.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(atomic64_diff);
    const phase4_build = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase4_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase4_build);
    const phase9_build = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase9_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);
    const phase4_validator = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "scripts/zigux/validate-phase4.py",
        64 * 1024,
    );
    defer std.testing.allocator.free(phase4_validator);
    const runtime_atomic64_sample = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_atomic64.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(runtime_atomic64_sample);
    const phase4_validation_matrix = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase4-validation-matrix.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase4_validation_matrix);
    const tests_readme = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/README.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(tests_readme);
    const phase4_gate_evidence = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase4-gate-evidence.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase4_gate_evidence);
    const runtime_atomic64_diff_survey = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(runtime_atomic64_diff_survey);
    const test_fsmount_manifest_json = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase4_test_fsmount_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(test_fsmount_manifest_json);
    const test_fsmount_survey = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase4_test_fsmount_survey.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(test_fsmount_survey);
    const perf_baseline_manifest_json = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase4_perf_baseline_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(perf_baseline_manifest_json);
    const phase4_perf_baseline_survey = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase4_perf_baseline_survey.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(phase4_perf_baseline_survey);
    const doc_readme = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/README.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(doc_readme);
    const script_readme = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "scripts/zigux/README.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(script_readme);

    const live_summary = SurveySummary{
        .atomic64_test_c_lines = countLines(atomic64_test_c),
        .runtime_atomic64_diff_lines = countLines(runtime_atomic64_diff),
        .roadmap_atomic64_diff_present = blk: {
            std.Io.Dir.cwd().access(
                io_instance.io(),
                "zigux/tests/atomic64_diff.zig",
                .{},
            ) catch |err| switch (err) {
                error.FileNotFound => break :blk false,
                else => return err,
            };
            break :blk true;
        },
        .roadmap_atomic64_wrapper_targets_runtime_diff = std.mem.indexOf(
            u8,
            atomic64_diff,
            "@import(\"runtime_atomic64_diff.zig\")",
        ) != null,
        .runtime_atomic64_diff_present = std.mem.indexOf(u8, runtime_atomic64_diff, "runtime atomic64 diff gate replays bounded atomic64_test.c") != null,
        .post_selftest_replay_present = std.mem.indexOf(u8, runtime_atomic64_diff, "runtime atomic64 diff gate keeps post-selftest replay explicit") != null,
        .phase4_build_present = std.mem.indexOf(u8, phase4_build, "atomic64_diff.zig") != null and
            std.mem.indexOf(u8, phase4_build, "phase4-runtime-atomic64-diff-tests") != null,
        .phase4_build_uses_atomic64_wrapper = std.mem.indexOf(
            u8,
            phase4_build,
            ".root_source_file = b.path(\"atomic64_diff.zig\")",
        ) != null,
        .phase9_build_present = std.mem.indexOf(u8, phase9_build, "runtime_atomic64_diff.zig") != null and
            std.mem.indexOf(u8, phase9_build, "phase9-runtime-atomic64-diff-tests") != null,
        .phase9_build_uses_runtime_atomic64_diff = std.mem.indexOf(
            u8,
            phase9_build,
            ".root_source_file = b.path(\"runtime_atomic64_diff.zig\")",
        ) != null,
        .phase4_validator_runtime_atomic64_diff_present = std.mem.indexOf(u8, phase4_validator, "zigux/tests/runtime_atomic64_diff.zig") != null,
        .phase4_validator_atomic64_diff_present = std.mem.indexOf(u8, phase4_validator, "zigux/tests/atomic64_diff.zig") != null,
        .runtime_atomic64_sample_present = std.mem.indexOf(u8, runtime_atomic64_sample, "provides_selftest_hook = true") != null and
            std.mem.indexOf(u8, runtime_atomic64_sample, "pub fn addCounter") != null,
        .phase4_validation_matrix_present = std.mem.indexOf(u8, phase4_validation_matrix, "zigux/tests/runtime_atomic64_diff.zig") != null and
            std.mem.indexOf(u8, phase4_validation_matrix, "threshold_pending_until_runtime_atomic64_scope_widens") != null,
        .tests_readme_runtime_atomic64_diff_present = std.mem.indexOf(u8, tests_readme, "zigux/tests/runtime_atomic64_diff.zig") != null,
    };

    try std.testing.expectEqualDeep(live_summary, manifest.survey_summary);
    try expectAtomic64MatrixGovernanceRow(phase4_validation_matrix);
    try expectSourceHas(atomic64_diff, "@import(\"runtime_atomic64_diff.zig\")");
    try expectSourceLacks(atomic64_diff, "@import(\"runtime_atomic64_sample\")");
    try expectSourceLacks(atomic64_diff, "runSelftest()");
    try expectSourceLacks(atomic64_diff, "post_selftest_summary");
    try expectSourceHas(phase4_build, ".root_source_file = b.path(\"atomic64_diff.zig\")");
    try expectSourceLacks(phase4_build, ".root_source_file = b.path(\"runtime_atomic64_diff.zig\")");
    try expectSourceHas(phase9_build, ".root_source_file = b.path(\"runtime_atomic64_diff.zig\")");
    try expectSourceLacks(phase9_build, ".root_source_file = b.path(\"atomic64_diff.zig\")");
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            phase4_validation_matrix,
            "`lib/atomic64_test.c` stays the source of truth",
        ) != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            phase4_validation_matrix,
            "removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move",
        ) != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            phase4_validation_matrix,
            "`runtime_atomic64_diff.zig` remains the single replay body",
        ) != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            phase4_validation_matrix,
            "the existing Phase 9 runtime atomic64 starter remains the forward path",
        ) != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_EVIDENCE_MODE=github_connector_readback") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_VALIDATOR_SELF_TEST=pass") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_VALIDATION=pass") != null);
    try expectGateEvidenceCount(
        phase4_gate_evidence,
        "PHASE4_REQUIRED_FILE_COUNT=",
        expected_phase4_required_file_count,
    );
    try expectGateEvidenceCount(
        phase4_gate_evidence,
        "PHASE4_REQUIRED_MARKER_COUNT=",
        expected_phase4_required_marker_count,
    );
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_GATE_EVIDENCE_SELF_TEST=pass") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_GATE_EVIDENCE_CHECK=pass") != null);
    try expectGateEvidenceCount(
        phase4_gate_evidence,
        "PHASE4_GATE_EVIDENCE_TARGET_COUNT=",
        expected_phase4_gate_evidence_target_count,
    );
    try expectGateEvidenceBlob(phase4_gate_evidence, "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA", manifest_json);
    try expectGateEvidenceBlob(phase4_gate_evidence, "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA", runtime_atomic64_diff_survey);
    try expectGateEvidenceBlob(phase4_gate_evidence, "PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA", test_fsmount_manifest_json);
    try expectGateEvidenceBlob(phase4_gate_evidence, "PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA", test_fsmount_survey);
    try expectGateEvidenceBlob(phase4_gate_evidence, "PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA", perf_baseline_manifest_json);
    try expectGateEvidenceBlob(phase4_gate_evidence, "PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA", phase4_perf_baseline_survey);
    try expectGateEvidenceBlob(phase4_gate_evidence, "PHASE4_DOC_README_BLOB_SHA", doc_readme);
    try expectGateEvidenceBlob(phase4_gate_evidence, "PHASE4_SCRIPT_README_BLOB_SHA", script_readme);
    try expectGateEvidenceBlob(phase4_gate_evidence, "PHASE4_TESTS_README_BLOB_SHA", tests_readme);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, current_surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "phase4_runtime_atomic64_diff_survey.zig") != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_live_gate = false;
    var saw_runtime_sample = false;
    var saw_shared_build = false;
    var saw_matrix_note = false;
    var saw_path_gap = false;
    var saw_broader_surface_gap = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_broader_atomic64_surface")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase4-runtime-atomic64-diff-gate")) {
            saw_live_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sub") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bitwise") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "selftest-family") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "post-selftest replay") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-runtime-atomic64-sample-starter")) {
            saw_runtime_sample = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "selftest-hook replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "post-selftest replay") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-shared-build-entrypoint")) {
            saw_shared_build = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase4_build.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "roadmap-named atomic64 wrapper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bitmap gate") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rollback surface") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-validation-matrix-note")) {
            saw_matrix_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase4-validation-matrix.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rollback owner") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "threshold posture") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "threshold_pending_until_runtime_atomic64_scope_widens") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reversible-delivery evidence") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`lib/atomic64_test.c` anchor") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared `phase4_build.zig` entrypoint") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-roadmap-path-alignment")) {
            saw_path_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/atomic64_diff.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "canonical entrypoint") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "@import(\"runtime_atomic64_diff.zig\")") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared `phase4_build.zig` replay now runs that wrapper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`validate-phase4.py` tracks both") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`phase9_build.zig` still compiles `runtime_atomic64_diff.zig` directly") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "wrapper-versus-runtime-body split") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-broader-atomic64-surface")) {
            saw_broader_surface_gap = true;
            try std.testing.expectEqualStrings("blocked_on_broader_atomic64_surface", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sub") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bitwise") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "full wider atomic64_test.c surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "perf threshold") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "post-selftest replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "threshold_pending_until_runtime_atomic64_scope_widens") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 5), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_live_gate);
    try std.testing.expect(saw_runtime_sample);
    try std.testing.expect(saw_shared_build);
    try std.testing.expect(saw_matrix_note);
    try std.testing.expect(saw_path_gap);
    try std.testing.expect(saw_broader_surface_gap);
}
