const std = @import("std");

const SurveyedGate = struct {
    surface: []const u8,
    gate_owner: []const u8,
    gate_rollback_owner: []const u8,
    threshold_posture: []const u8,
};

const SurveySummary = struct {
    phase4_build_step_present: bool,
    phase4_validation_matrix_present: bool,
    shared_phase4_test_step_includes_survey: bool,
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

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    surveyed_gates: []const SurveyedGate,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next");
}

test "phase4 perf baseline survey manifest keeps the current unapproved threshold posture explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const parsed = try std.json.parseFromSlice(
        Manifest,
        std.testing.allocator,
        @embedFile("phase4_perf_baseline_manifest.json"),
        .{},
    );
    defer parsed.deinit();

    const manifest = parsed.value;
    const phase4_build = @embedFile("phase4_build.zig");
    const phase4_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-validation-matrix.md",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(phase4_matrix);
    const phase4_gate_evidence = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-gate-evidence.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(phase4_gate_evidence);
    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(makefile);
    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);
    const doc_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(doc_readme);
    const script_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(script_readme);
    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    try std.testing.expectEqualStrings("P4-L20", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.rollback_owner);
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

    const live_summary = SurveySummary{
        .phase4_build_step_present = std.mem.indexOf(u8, phase4_build, "phase4_perf_baseline_survey.zig") != null and
            std.mem.indexOf(u8, phase4_build, "phase4-perf-baseline-survey-tests") != null and
            std.mem.indexOf(u8, phase4_build, "phase4-perf-baseline-survey") != null,
        .phase4_validation_matrix_present = std.mem.indexOf(u8, phase4_matrix, "zigux/tests/phase4_perf_baseline_manifest.json") != null and
            std.mem.indexOf(u8, phase4_matrix, "zigux/tests/phase4_perf_baseline_survey.zig") != null and
            std.mem.indexOf(u8, phase4_matrix, "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig") != null and
            std.mem.indexOf(u8, phase4_matrix, "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land") != null and
            std.mem.indexOf(u8, phase4_matrix, "The dedicated perf-baseline survey stays outside the shared `phase4-test` entrypoint") != null,
        .shared_phase4_test_step_includes_survey = std.mem.indexOf(u8, phase4_build, "test_step.dependOn(&run_perf_baseline_survey_tests.step);") != null,
        .benchmark_command_unapproved = std.mem.indexOf(u8, phase4_matrix, "benchmark command and acceptable limit are still unapproved for both landed gates") != null or
            std.mem.indexOf(u8, phase4_matrix, "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land") != null,
        .acceptable_limit_unapproved = std.mem.indexOf(u8, phase4_matrix, "benchmark command and acceptable limit are still unapproved for both landed gates") != null or
            std.mem.indexOf(u8, phase4_matrix, "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land") != null,
    };
    try std.testing.expectEqualDeep(live_summary, manifest.survey_summary);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_manifest_gap = false;
    var saw_gate_gap = false;
    var saw_atomic64_gap = false;
    var saw_bitmap_gap = false;

    for (manifest.gaps) |gap| {
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared CI perf approval") != null);
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
    }

    try std.testing.expectEqual(@as(usize, 2), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 2), ready_next_count);
    try std.testing.expect(saw_manifest_gap);
    try std.testing.expect(saw_gate_gap);
    try std.testing.expect(saw_atomic64_gap);
    try std.testing.expect(saw_bitmap_gap);

    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "Documentation/zigux/phase4-validation-matrix.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "Documentation/zigux/phase4-gate-evidence.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "scripts/zigux/validate-phase4.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase4_perf_baseline_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase4_perf_baseline_survey.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, doc_readme, "Phase 4 notes") != null);
    try std.testing.expect(std.mem.indexOf(u8, doc_readme, "Documentation/zigux/phase4-validation-matrix.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, doc_readme, "Documentation/zigux/phase4-gate-evidence.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, doc_readme, "intentionally unapproved perf-threshold posture") != null);

    try std.testing.expect(std.mem.indexOf(u8, script_readme, "Phase 4 flow") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "zigux/tests/phase4_perf_baseline_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "zigux/tests/phase4_perf_baseline_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "intentionally unapproved perf-threshold posture") != null);

    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "if the change touches the shared Phase 4 validation packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "Documentation/zigux/phase4-validation-matrix.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "Documentation/zigux/phase4-gate-evidence.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "intentionally unapproved perf-threshold posture") != null);

    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase4-perf-baseline-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase4-perf-baseline-survey:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "$(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "`zigux/tests/phase4_perf_baseline_survey.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "threshold_pending_until_runtime_atomic64_scope_widens") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "zigux/tests/phase4_perf_baseline_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "zigux/tests/phase4_perf_baseline_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "dedicated local-only perf-baseline posture packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "still-unapproved benchmark-command and acceptable-limit posture machine-checked locally") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "The dedicated exact-readback checker now also rereads that shipped perf-baseline manifest-and-survey pair") != null);
}
