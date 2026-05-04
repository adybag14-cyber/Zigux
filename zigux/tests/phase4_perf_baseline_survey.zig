const std = @import("std");
const current_surveyed_commit = "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3";

const SurveyedGate = struct {
    surface: []const u8,
    gate_owner: []const u8,
    gate_rollback_owner: []const u8,
    threshold_posture: []const u8,
};

const SurveySummary = struct {
    phase4_build_present: bool,
    phase4_validator_present: bool,
    phase4_validation_matrix_present: bool,
    benchmark_command_unapproved: bool,
    acceptable_limit_unapproved: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const PendingThresholdPlan = struct {
    surface: []const u8,
    gate_owner: []const u8,
    gate_rollback_owner: []const u8,
    threshold_posture: []const u8,
    current_correctness_replay: []const u8,
    threshold_ready_surface: []const u8,
    benchmark_command: []const u8,
    acceptable_limit: []const u8,
    next_threshold_step: []const u8,
    status: []const u8,
    why_not_approved_yet: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    surveyed_commit: []const u8,
    surveyed_gates: []const SurveyedGate,
    survey_summary: SurveySummary,
    pending_threshold_plans: []const PendingThresholdPlan,
    gaps: []const Gap,
};

const Atomic64ThresholdPlan = struct {
    owner: []const u8,
    rollback_owner: []const u8,
    posture: []const u8,
    status: []const u8,
    benchmark_command: []const u8,
    acceptable_limit: []const u8,
    scope: []const u8,
    why_not_approved_yet: []const u8,
};

const Atomic64Manifest = struct {
    surveyed_commit: []const u8,
    threshold_plan: Atomic64ThresholdPlan,
};

const TestFsmountManifest = struct {
    phase: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    surveyed_commit: []const u8,
    current_replay: []const u8,
};

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

fn expectedCorrectnessReplay(surface: []const u8) ?[]const u8 {
    if (std.mem.eql(u8, surface, "zigux/tests/atomic64_diff.zig")) {
        return "make -C zigux phase4-runtime-atomic64-diff";
    }
    if (std.mem.eql(u8, surface, "zigux/tests/bitmap_diff.zig")) {
        return "make -C zigux phase4-bitmap-diff";
    }
    return null;
}

fn expectedPendingStatus(posture: []const u8) ?[]const u8 {
    if (std.mem.eql(u8, posture, "threshold_pending_until_runtime_atomic64_scope_widens")) {
        return "pending_scope_widening";
    }
    if (std.mem.eql(u8, posture, "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks")) {
        return "pending_bounded_benchmark";
    }
    return null;
}

fn expectedUnapprovedPlaceholder(posture: []const u8) ?[]const u8 {
    if (std.mem.eql(u8, posture, "threshold_pending_until_runtime_atomic64_scope_widens")) {
        return "unapproved_until_runtime_atomic64_scope_widens";
    }
    if (std.mem.eql(u8, posture, "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks")) {
        return "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks";
    }
    return null;
}

fn findSurveyedGate(manifest: Manifest, surface: []const u8) ?SurveyedGate {
    for (manifest.surveyed_gates) |surveyed_gate| {
        if (std.mem.eql(u8, surveyed_gate.surface, surface)) return surveyed_gate;
    }
    return null;
}

fn findPendingThresholdPlan(manifest: Manifest, surface: []const u8) ?PendingThresholdPlan {
    for (manifest.pending_threshold_plans) |pending_plan| {
        if (std.mem.eql(u8, pending_plan.surface, surface)) return pending_plan;
    }
    return null;
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

test "phase4 perf baseline survey manifest keeps the current unapproved threshold posture explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_perf_baseline_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P4-L20", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.rollback_owner);
    try std.testing.expect(isLowerHexSha(current_surveyed_commit));
    try std.testing.expectEqualStrings(current_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqual(@as(usize, 2), manifest.surveyed_gates.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.gaps.len);

    try std.testing.expectEqualStrings(
        "zigux/tests/atomic64_diff.zig",
        manifest.surveyed_gates[0].surface,
    );
    try std.testing.expectEqualStrings(
        "ABI and Runtime Team",
        manifest.surveyed_gates[0].gate_owner,
    );
    try std.testing.expectEqualStrings(
        "ABI and Runtime Team",
        manifest.surveyed_gates[0].gate_rollback_owner,
    );
    try std.testing.expectEqualStrings(
        "threshold_pending_until_runtime_atomic64_scope_widens",
        manifest.surveyed_gates[0].threshold_posture,
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/bitmap_diff.zig",
        manifest.surveyed_gates[1].surface,
    );
    try std.testing.expectEqualStrings(
        "Shared Subsystems Pod",
        manifest.surveyed_gates[1].gate_owner,
    );
    try std.testing.expectEqualStrings(
        "Shared Subsystems Pod",
        manifest.surveyed_gates[1].gate_rollback_owner,
    );
    try std.testing.expectEqualStrings(
        "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        manifest.surveyed_gates[1].threshold_posture,
    );
    try std.testing.expectEqual(@as(usize, 2), manifest.pending_threshold_plans.len);

    for (manifest.surveyed_gates) |surveyed_gate| {
        const pending_plan = findPendingThresholdPlan(manifest, surveyed_gate.surface) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings(surveyed_gate.gate_owner, pending_plan.gate_owner);
        try std.testing.expectEqualStrings(surveyed_gate.gate_rollback_owner, pending_plan.gate_rollback_owner);
        try std.testing.expectEqualStrings(surveyed_gate.threshold_posture, pending_plan.threshold_posture);
    }

    for (manifest.pending_threshold_plans) |pending_plan| {
        const surveyed_gate = findSurveyedGate(manifest, pending_plan.surface) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings(surveyed_gate.gate_owner, pending_plan.gate_owner);
        try std.testing.expectEqualStrings(surveyed_gate.gate_rollback_owner, pending_plan.gate_rollback_owner);
        try std.testing.expectEqualStrings(surveyed_gate.threshold_posture, pending_plan.threshold_posture);

        const expected_replay = expectedCorrectnessReplay(pending_plan.surface) orelse unreachable;
        try std.testing.expectEqualStrings(expected_replay, pending_plan.current_correctness_replay);

        const expected_status = expectedPendingStatus(pending_plan.threshold_posture) orelse unreachable;
        try std.testing.expectEqualStrings(expected_status, pending_plan.status);

        const expected_placeholder = expectedUnapprovedPlaceholder(pending_plan.threshold_posture) orelse unreachable;
        try std.testing.expectEqualStrings(expected_placeholder, pending_plan.benchmark_command);
        try std.testing.expectEqualStrings(expected_placeholder, pending_plan.acceptable_limit);

        if (std.mem.eql(u8, pending_plan.surface, "zigux/tests/atomic64_diff.zig")) {
            try std.testing.expectEqualStrings(
                "zigux/tests/runtime_atomic64_diff.zig keeps the post-selftest replay explicit for the current rollback gate",
                pending_plan.threshold_ready_surface,
            );
            try std.testing.expect(std.mem.indexOf(u8, pending_plan.next_threshold_step, "broader atomic64 benchmark entrypoint") != null);
            try std.testing.expect(std.mem.indexOf(u8, pending_plan.next_threshold_step, "benchmark command and one acceptable limit") != null);
        } else if (std.mem.eql(u8, pending_plan.surface, "zigux/tests/bitmap_diff.zig")) {
            try std.testing.expectEqualStrings(
                "zigux/tests/bitmap_diff.zig exposes runThresholdReplay() as the deterministic bitmap threshold batch for future perf-baseline work",
                pending_plan.threshold_ready_surface,
            );
            try std.testing.expect(std.mem.indexOf(u8, pending_plan.next_threshold_step, "isolated bitmap benchmark route") != null);
            try std.testing.expect(std.mem.indexOf(u8, pending_plan.next_threshold_step, "benchmark command and one acceptable limit") != null);
        } else {
            return error.TestUnexpectedResult;
        }
    }

    try std.testing.expectEqualStrings(
        "zigux/tests/atomic64_diff.zig",
        manifest.pending_threshold_plans[0].surface,
    );
    try std.testing.expectEqualStrings(
        "ABI and Runtime Team",
        manifest.pending_threshold_plans[0].gate_owner,
    );
    try std.testing.expectEqualStrings(
        "ABI and Runtime Team",
        manifest.pending_threshold_plans[0].gate_rollback_owner,
    );
    try std.testing.expectEqualStrings(
        "threshold_pending_until_runtime_atomic64_scope_widens",
        manifest.pending_threshold_plans[0].threshold_posture,
    );
    try std.testing.expectEqualStrings(
        "make -C zigux phase4-runtime-atomic64-diff",
        manifest.pending_threshold_plans[0].current_correctness_replay,
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/runtime_atomic64_diff.zig keeps the post-selftest replay explicit for the current rollback gate",
        manifest.pending_threshold_plans[0].threshold_ready_surface,
    );
    try std.testing.expectEqualStrings(
        "pending_scope_widening",
        manifest.pending_threshold_plans[0].status,
    );
    try std.testing.expectEqualStrings(
        "unapproved_until_runtime_atomic64_scope_widens",
        manifest.pending_threshold_plans[0].benchmark_command,
    );
    try std.testing.expectEqualStrings(
        "unapproved_until_runtime_atomic64_scope_widens",
        manifest.pending_threshold_plans[0].acceptable_limit,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_threshold_plans[0].next_threshold_step, "broader atomic64 benchmark entrypoint") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_threshold_plans[0].next_threshold_step, "benchmark command and one acceptable limit") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_threshold_plans[0].why_not_approved_yet, "correctness-only coverage") != null);
    try std.testing.expectEqualStrings(
        "zigux/tests/bitmap_diff.zig",
        manifest.pending_threshold_plans[1].surface,
    );
    try std.testing.expectEqualStrings(
        "Shared Subsystems Pod",
        manifest.pending_threshold_plans[1].gate_owner,
    );
    try std.testing.expectEqualStrings(
        "Shared Subsystems Pod",
        manifest.pending_threshold_plans[1].gate_rollback_owner,
    );
    try std.testing.expectEqualStrings(
        "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        manifest.pending_threshold_plans[1].threshold_posture,
    );
    try std.testing.expectEqualStrings(
        "make -C zigux phase4-bitmap-diff",
        manifest.pending_threshold_plans[1].current_correctness_replay,
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/bitmap_diff.zig exposes runThresholdReplay() as the deterministic bitmap threshold batch for future perf-baseline work",
        manifest.pending_threshold_plans[1].threshold_ready_surface,
    );
    try std.testing.expectEqualStrings(
        "pending_bounded_benchmark",
        manifest.pending_threshold_plans[1].status,
    );
    try std.testing.expectEqualStrings(
        "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        manifest.pending_threshold_plans[1].benchmark_command,
    );
    try std.testing.expectEqualStrings(
        "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        manifest.pending_threshold_plans[1].acceptable_limit,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_threshold_plans[1].next_threshold_step, "isolated bitmap benchmark route") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_threshold_plans[1].next_threshold_step, "benchmark command and one acceptable limit") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_threshold_plans[1].why_not_approved_yet, "correctness-first rollback packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_threshold_plans[1].why_not_approved_yet, "acceptable limit") != null);

    const atomic64_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(atomic64_manifest_json);
    const atomic64_parsed = try std.json.parseFromSlice(
        Atomic64Manifest,
        std.testing.allocator,
        atomic64_manifest_json,
        .{ .ignore_unknown_fields = true },
    );
    defer atomic64_parsed.deinit();
    const atomic64_manifest = atomic64_parsed.value;
    try std.testing.expectEqualStrings(current_surveyed_commit, atomic64_manifest.surveyed_commit);
    try std.testing.expect(isLowerHexSha(atomic64_manifest.surveyed_commit));
    try std.testing.expectEqualStrings(
        "ABI and Runtime Team",
        atomic64_manifest.threshold_plan.owner,
    );
    try std.testing.expectEqualStrings(
        "ABI and Runtime Team",
        atomic64_manifest.threshold_plan.rollback_owner,
    );
    try std.testing.expectEqualStrings(
        "threshold_pending_until_runtime_atomic64_scope_widens",
        atomic64_manifest.threshold_plan.posture,
    );
    try std.testing.expectEqualStrings(
        "pending_scope_widening",
        atomic64_manifest.threshold_plan.status,
    );
    try std.testing.expectEqualStrings(
        "unapproved_until_runtime_atomic64_scope_widens",
        atomic64_manifest.threshold_plan.benchmark_command,
    );
    try std.testing.expectEqualStrings(
        "unapproved_until_runtime_atomic64_scope_widens",
        atomic64_manifest.threshold_plan.acceptable_limit,
    );
    try std.testing.expect(std.mem.indexOf(u8, atomic64_manifest.threshold_plan.scope, "selftest-family plus post-selftest replay set") != null);
    try std.testing.expect(std.mem.indexOf(u8, atomic64_manifest.threshold_plan.why_not_approved_yet, "correctness-only coverage") != null);

    const test_fsmount_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_test_fsmount_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(test_fsmount_manifest_json);
    const test_fsmount_parsed = try std.json.parseFromSlice(
        TestFsmountManifest,
        std.testing.allocator,
        test_fsmount_manifest_json,
        .{ .ignore_unknown_fields = true },
    );
    defer test_fsmount_parsed.deinit();
    const test_fsmount_manifest = test_fsmount_parsed.value;
    try std.testing.expectEqualStrings("Phase 4", test_fsmount_manifest.phase);
    try std.testing.expectEqualStrings("Validation and Perf Team", test_fsmount_manifest.owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", test_fsmount_manifest.rollback_owner);
    try std.testing.expectEqualStrings(current_surveyed_commit, test_fsmount_manifest.surveyed_commit);
    try std.testing.expect(isLowerHexSha(test_fsmount_manifest.surveyed_commit));
    try std.testing.expectEqualStrings("make M=samples/vfs", test_fsmount_manifest.current_replay);

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
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(phase4_validator);
    const phase4_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-validation-matrix.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase4_matrix);
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
    const phase4_gate_evidence = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-gate-evidence.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase4_gate_evidence);
    const phase4_perf_baseline_survey = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_perf_baseline_survey.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase4_perf_baseline_survey);

    const live_summary = SurveySummary{
        .phase4_build_present = std.mem.indexOf(u8, phase4_build, "phase4_perf_baseline_survey.zig") != null and
            std.mem.indexOf(u8, phase4_build, "phase4-perf-baseline-survey-tests") != null and
            std.mem.indexOf(u8, phase4_build, "phase4-perf-baseline-survey") != null,
        .phase4_validator_present = std.mem.indexOf(u8, phase4_validator, "phase4_perf_baseline_manifest.json") != null and
            std.mem.indexOf(u8, phase4_validator, "phase4_perf_baseline_survey.zig") != null and
            std.mem.indexOf(u8, phase4_validator, "phase4-perf-baseline-survey-tests") != null and
            std.mem.indexOf(u8, phase4_validator, "phase4-perf-baseline-survey") != null,
        .phase4_validation_matrix_present = std.mem.indexOf(u8, phase4_matrix, "phase4_perf_baseline_manifest.json") != null and
            std.mem.indexOf(u8, phase4_matrix, "phase4-perf-baseline-survey-tests") != null and
            std.mem.indexOf(u8, phase4_matrix, "make -C zigux phase4-perf-baseline-survey") != null and
            std.mem.indexOf(u8, phase4_matrix, "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land") != null and
            std.mem.indexOf(u8, phase4_matrix, "benchmark command is still unapproved for both landed gates") != null and
            std.mem.indexOf(u8, phase4_matrix, "acceptable limit is still unapproved for both landed gates") != null and
            std.mem.indexOf(u8, phase4_matrix, "land one bounded benchmark command and one acceptable limit per gate before Phase 4 claims perf coverage") != null,
        .benchmark_command_unapproved = std.mem.eql(
            u8,
            atomic64_manifest.threshold_plan.benchmark_command,
            "unapproved_until_runtime_atomic64_scope_widens",
        ) and std.mem.eql(
            u8,
            manifest.pending_threshold_plans[1].benchmark_command,
            "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        ) and std.mem.indexOf(u8, phase4_matrix, "benchmark command is still unapproved for both landed gates") != null,
        .acceptable_limit_unapproved = std.mem.eql(
            u8,
            atomic64_manifest.threshold_plan.acceptable_limit,
            "unapproved_until_runtime_atomic64_scope_widens",
        ) and std.mem.eql(
            u8,
            manifest.pending_threshold_plans[1].acceptable_limit,
            "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        ) and std.mem.indexOf(u8, phase4_matrix, "acceptable limit is still unapproved for both landed gates") != null,
    };
    try std.testing.expectEqualDeep(live_summary, manifest.survey_summary);

    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_EVIDENCE_MODE=github_connector_readback") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_GATE_EVIDENCE_SELF_TEST=pass") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_GATE_EVIDENCE_CHECK=pass") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_GATE_EVIDENCE_TARGET_COUNT=17") != null);
    try expectGateEvidenceBlob(phase4_gate_evidence, "PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA", manifest_json);
    try expectGateEvidenceBlob(phase4_gate_evidence, "PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA", phase4_perf_baseline_survey);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, current_surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "phase4_perf_baseline_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "pending threshold-plan record per shipped rollback gate") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "make -C zigux phase4-runtime-atomic64-diff") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "make -C zigux phase4-bitmap-diff") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "zigux/tests/runtime_atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "runThresholdReplay()") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "threshold_pending_until_runtime_atomic64_scope_widens") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "pending_scope_widening") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "unapproved_until_runtime_atomic64_scope_widens") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "pending_bounded_benchmark") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "broader atomic64 benchmark entrypoint") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "isolated bitmap benchmark route") != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_manifest_gap = false;
    var saw_gate_gap = false;
    var saw_atomic64_gap = false;
    var saw_bitmap_gap = false;

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

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-survey-manifest")) {
            saw_manifest_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase4_perf_baseline_manifest.json", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "manifest-backed survey packet") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "without inventing numbers") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-survey-gate")) {
            saw_gate_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase4_perf_baseline_survey.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "correctness-only posture") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "prose-only matrix guidance") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-atomic64-command")) {
            saw_atomic64_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/atomic64_diff.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "benchmark command plus one acceptable limit") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-bitmap-command")) {
            saw_bitmap_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "benchmark command plus one acceptable limit") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 2), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 2), ready_next_count);
    try std.testing.expect(saw_manifest_gap);
    try std.testing.expect(saw_gate_gap);
    try std.testing.expect(saw_atomic64_gap);
    try std.testing.expect(saw_bitmap_gap);

    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "| `zigux/tests/phase4_perf_baseline_survey.zig` |") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "phase4-perf-baseline-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "make -C zigux phase4-perf-baseline-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "threshold_pending_until_runtime_atomic64_scope_widens") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "zigux/tests/runtime_atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "runThresholdReplay()") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "broader atomic64 benchmark entrypoint") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "isolated bitmap benchmark route") != null);
    try std.testing.expect(std.mem.indexOf(u8, doc_readme, "phase4_perf_baseline_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, doc_readme, "make -C zigux phase4-perf-baseline-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, doc_readme, "phase4-perf-baseline-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, doc_readme, "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "make -C zigux phase4-perf-baseline-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "validate-phase4.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase4_perf_baseline_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase4_perf_baseline_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "make -C zigux phase4-perf-baseline-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land") != null);
}
