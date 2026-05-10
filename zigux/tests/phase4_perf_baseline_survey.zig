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
    atomic64_benchmark_command_approved: bool,
    atomic64_acceptable_limit_approved: bool,
    bitmap_benchmark_command_approved: bool,
    bitmap_acceptable_limit_approved: bool,
};

const DeterministicReplay = struct {
    iterations: usize,
    checksum: u64,
    final_counter: i64,
};

const Atomic64CommandEvidence = struct {
    evidence_status: []const u8,
    benchmark_command: []const u8,
    acceptable_limit_status: []const u8,
    acceptable_limit_metric: []const u8,
    acceptable_limit_iterations: usize,
    acceptable_limit_sample_count: usize,
    acceptable_limit_max_elapsed_ns: u64,
    deterministic_replays: []const DeterministicReplay,
};

const BitmapDeterministicReplay = struct {
    iterations: usize,
    checksum: u64,
    final_first_set: u32,
    final_first_zero: u32,
    final_weight: u32,
    final_nth_seven: u32,
};

const BitmapCommandEvidence = struct {
    evidence_status: []const u8,
    benchmark_command: []const u8,
    acceptable_limit_status: []const u8,
    acceptable_limit_metric: []const u8,
    acceptable_limit_iterations: usize,
    acceptable_limit_sample_count: usize,
    acceptable_limit_max_elapsed_ns: u64,
    deterministic_replays: []const BitmapDeterministicReplay,
};

const CommandEvidence = struct {
    atomic64: Atomic64CommandEvidence,
    bitmap: BitmapCommandEvidence,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    benchmark_command: ?[]const u8 = null,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    shared_promotion_decision_owner: []const u8,
    shared_promotion_coordination_owners: []const []const u8,
    shared_promotion_scope: []const u8,
    shared_promotion_matrix_path: []const u8,
    shared_promotion_review_checklist_path: []const u8,
    surveyed_gates: []const SurveyedGate,
    survey_summary: SurveySummary,
    command_evidence: CommandEvidence,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next");
}

test "phase4 perf baseline survey manifest keeps the current benchmark-command posture explicit" {
    const parsed = try std.json.parseFromSlice(
        Manifest,
        std.testing.allocator,
        @embedFile("phase4_perf_baseline_manifest.json"),
        .{},
    );
    defer parsed.deinit();

    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P4-L20", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.rollback_owner);
    try std.testing.expectEqualStrings(
        "Validation and Perf Team",
        manifest.shared_promotion_decision_owner,
    );
    try std.testing.expectEqual(@as(usize, 2), manifest.shared_promotion_coordination_owners.len);
    try std.testing.expectEqualStrings(
        "ABI and Runtime Team",
        manifest.shared_promotion_coordination_owners[0],
    );
    try std.testing.expectEqualStrings(
        "Shared Subsystems Pod",
        manifest.shared_promotion_coordination_owners[1],
    );
    try std.testing.expectEqualStrings(
        "approved_local_only_limits_vs_shared_ci_perf_coverage",
        manifest.shared_promotion_scope,
    );
    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase4-validation-matrix.md",
        manifest.shared_promotion_matrix_path,
    );
    try std.testing.expectEqualStrings(
        "Documentation/zigux/review-checklist.md",
        manifest.shared_promotion_review_checklist_path,
    );
    try std.testing.expectEqual(@as(usize, 2), manifest.surveyed_gates.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.gaps.len);

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

    try std.testing.expect(manifest.survey_summary.phase4_build_step_present);
    try std.testing.expect(manifest.survey_summary.phase4_validation_matrix_present);
    try std.testing.expect(!manifest.survey_summary.shared_phase4_test_step_includes_survey);
    try std.testing.expect(!manifest.survey_summary.benchmark_command_unapproved);
    try std.testing.expect(!manifest.survey_summary.acceptable_limit_unapproved);
    try std.testing.expect(manifest.survey_summary.atomic64_benchmark_command_approved);
    try std.testing.expect(manifest.survey_summary.atomic64_acceptable_limit_approved);
    try std.testing.expect(manifest.survey_summary.bitmap_benchmark_command_approved);
    try std.testing.expect(manifest.survey_summary.bitmap_acceptable_limit_approved);

    try std.testing.expectEqualStrings(
        "benchmark_command_approved",
        manifest.command_evidence.atomic64.evidence_status,
    );
    try std.testing.expectEqualStrings(
        "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
        manifest.command_evidence.atomic64.benchmark_command,
    );
    try std.testing.expectEqualStrings(
        "approved_local_only",
        manifest.command_evidence.atomic64.acceptable_limit_status,
    );
    try std.testing.expectEqualStrings(
        "median_elapsed_ns",
        manifest.command_evidence.atomic64.acceptable_limit_metric,
    );
    try std.testing.expectEqual(@as(usize, 4), manifest.command_evidence.atomic64.acceptable_limit_iterations);
    try std.testing.expectEqual(@as(usize, 7), manifest.command_evidence.atomic64.acceptable_limit_sample_count);
    try std.testing.expectEqual(@as(u64, 8192), manifest.command_evidence.atomic64.acceptable_limit_max_elapsed_ns);
    try std.testing.expectEqual(@as(usize, 2), manifest.command_evidence.atomic64.deterministic_replays.len);
    try std.testing.expectEqual(@as(usize, 1), manifest.command_evidence.atomic64.deterministic_replays[0].iterations);
    try std.testing.expectEqual(@as(u64, 3626254113632800175), manifest.command_evidence.atomic64.deterministic_replays[0].checksum);
    try std.testing.expectEqual(@as(i64, 130322557735600377), manifest.command_evidence.atomic64.deterministic_replays[0].final_counter);
    try std.testing.expectEqual(@as(usize, 4), manifest.command_evidence.atomic64.deterministic_replays[1].iterations);
    try std.testing.expectEqual(@as(u64, 9210681150676220922), manifest.command_evidence.atomic64.deterministic_replays[1].checksum);
    try std.testing.expectEqual(@as(i64, 130322557735600376), manifest.command_evidence.atomic64.deterministic_replays[1].final_counter);
    try std.testing.expectEqualStrings(
        "benchmark_command_approved",
        manifest.command_evidence.bitmap.evidence_status,
    );
    try std.testing.expectEqualStrings(
        "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
        manifest.command_evidence.bitmap.benchmark_command,
    );
    try std.testing.expectEqualStrings(
        "approved_local_only",
        manifest.command_evidence.bitmap.acceptable_limit_status,
    );
    try std.testing.expectEqualStrings(
        "median_elapsed_ns",
        manifest.command_evidence.bitmap.acceptable_limit_metric,
    );
    try std.testing.expectEqual(@as(usize, 4), manifest.command_evidence.bitmap.acceptable_limit_iterations);
    try std.testing.expectEqual(@as(usize, 7), manifest.command_evidence.bitmap.acceptable_limit_sample_count);
    try std.testing.expectEqual(@as(u64, 131072), manifest.command_evidence.bitmap.acceptable_limit_max_elapsed_ns);
    try std.testing.expectEqual(@as(usize, 2), manifest.command_evidence.bitmap.deterministic_replays.len);
    try std.testing.expectEqual(@as(usize, 1), manifest.command_evidence.bitmap.deterministic_replays[0].iterations);
    try std.testing.expectEqual(@as(u64, 5216946504564592253), manifest.command_evidence.bitmap.deterministic_replays[0].checksum);
    try std.testing.expectEqual(@as(u32, 0), manifest.command_evidence.bitmap.deterministic_replays[0].final_first_set);
    try std.testing.expectEqual(@as(u32, 109), manifest.command_evidence.bitmap.deterministic_replays[0].final_first_zero);
    try std.testing.expectEqual(@as(u32, 1005), manifest.command_evidence.bitmap.deterministic_replays[0].final_weight);
    try std.testing.expectEqual(@as(u32, 123), manifest.command_evidence.bitmap.deterministic_replays[0].final_nth_seven);
    try std.testing.expectEqual(@as(usize, 4), manifest.command_evidence.bitmap.deterministic_replays[1].iterations);
    try std.testing.expectEqual(@as(u64, 7942141539243507472), manifest.command_evidence.bitmap.deterministic_replays[1].checksum);
    try std.testing.expectEqual(@as(u32, 0), manifest.command_evidence.bitmap.deterministic_replays[1].final_first_set);
    try std.testing.expectEqual(@as(u32, 109), manifest.command_evidence.bitmap.deterministic_replays[1].final_first_zero);
    try std.testing.expectEqual(@as(u32, 1005), manifest.command_evidence.bitmap.deterministic_replays[1].final_weight);
    try std.testing.expectEqual(@as(u32, 123), manifest.command_evidence.bitmap.deterministic_replays[1].final_nth_seven);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_manifest_gap = false;
    var saw_gate_gap = false;
    var saw_atomic64_command_evidence_gap = false;
    var saw_atomic64_command_gap = false;
    var saw_atomic64_acceptable_limit_gap = false;
    var saw_bitmap_command_evidence_gap = false;
    var saw_bitmap_command_gap = false;
    var saw_bitmap_acceptable_limit_gap = false;
    var saw_shared_promotion_decision_gap = false;

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
            try std.testing.expectEqualStrings("survey_manifest", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase4_perf_baseline_manifest.json", gap.zigux_destination);
            try std.testing.expect(gap.benchmark_command == null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "manifest-backed survey packet") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "acceptable limits for both landed rollback gates") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-survey-gate")) {
            saw_gate_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("validation", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase4_perf_baseline_survey.zig", gap.zigux_destination);
            try std.testing.expect(gap.benchmark_command == null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "correctness-only posture") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bitmap acceptable-limit edge") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-atomic64-command-evidence")) {
            saw_atomic64_command_evidence_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("survey_evidence", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase4_perf_baseline_manifest.json", gap.zigux_destination);
            try std.testing.expect(gap.benchmark_command == null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "exact-pins") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "runThresholdReplay(1)") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "3626254113632800175") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "130322557735600377") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "runThresholdReplay(4)") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "9210681150676220922") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "130322557735600376") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-atomic64-command")) {
            saw_atomic64_command_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("perf_command", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/atomic64_diff.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings(
                "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
                gap.benchmark_command.?,
            );
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "approved for local Phase 4 perf review") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared CI perf approval") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-atomic64-acceptable-limit")) {
            saw_atomic64_acceptable_limit_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("perf_threshold", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/atomic64_diff.zig", gap.zigux_destination);
            try std.testing.expect(gap.benchmark_command == null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "8192") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "seven monotonic samples") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "attached Zig toolchain") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-bitmap-command-evidence")) {
            saw_bitmap_command_evidence_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("survey_evidence", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase4_perf_baseline_manifest.json", gap.zigux_destination);
            try std.testing.expect(gap.benchmark_command == null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "exact-pins") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "runThresholdReplay(1)") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "5216946504564592253") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "final first-set `0`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "final first-zero `109`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "final weight `1005`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "final nth-seven `123`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "runThresholdReplay(4)") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "7942141539243507472") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-bitmap-command")) {
            saw_bitmap_command_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("perf_command", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings(
                "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
                gap.benchmark_command.?,
            );
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "approved for local Phase 4 perf review") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "acceptable limit now stays explicitly local-only") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-bitmap-acceptable-limit")) {
            saw_bitmap_acceptable_limit_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("perf_threshold", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", gap.zigux_destination);
            try std.testing.expect(gap.benchmark_command == null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "131072") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "79135") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "121289") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared CI perf coverage") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-perf-baseline-shared-promotion-decision")) {
            saw_shared_promotion_decision_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("perf_policy", gap.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase4-validation-matrix.md", gap.zigux_destination);
            try std.testing.expect(gap.benchmark_command == null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "approved local benchmark commands") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "approved local-only acceptable limits") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "keep those limits local-only or intentionally promote a broader shared CI perf-coverage claim") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "without widening the current validator-first packet by accident") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Validation and Perf Team") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ABI and Runtime Team") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Shared Subsystems Pod") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Documentation/zigux/phase4-validation-matrix.md") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Documentation/zigux/review-checklist.md") != null);
        }
    }

    try std.testing.expectEqual(@as(usize, 8), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expect(saw_manifest_gap);
    try std.testing.expect(saw_gate_gap);
    try std.testing.expect(saw_atomic64_command_evidence_gap);
    try std.testing.expect(saw_atomic64_command_gap);
    try std.testing.expect(saw_atomic64_acceptable_limit_gap);
    try std.testing.expect(saw_bitmap_command_evidence_gap);
    try std.testing.expect(saw_bitmap_command_gap);
    try std.testing.expect(saw_bitmap_acceptable_limit_gap);
    try std.testing.expect(saw_shared_promotion_decision_gap);
}

test "phase4 perf baseline survey keeps the shared matrix and reviewer packet on the current local-only perf posture" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const phase4_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-validation-matrix.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase4_matrix);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const docs_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(docs_readme);

    const scripts_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(scripts_readme);

    const required_matrix_markers = [_][]const u8{
        "zigux/tests/phase4_perf_baseline_manifest.json",
        "zigux/tests/phase4_perf_baseline_survey.zig",
        "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
        "local_only_commands_and_limits_approved_shared_ci_perf_promotion_pending",
        "The dedicated perf-baseline survey stays outside the shared `phase4-test` entrypoint",
        "the approved local benchmark commands and the approved local-only acceptable limits for both rollback gates explicit until a later Phase 4 lane intentionally decides whether any broader shared perf promotion belongs in the shipped packet.",
        "the dedicated perf-baseline survey may keep the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked",
        "keep the current local-only acceptable limits survey-only until a later bounded lane intentionally decides whether the existing bounds should stay local-only or support a broader shared CI perf-coverage claim",
    };

    for (required_matrix_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, marker) != null);
    }

    const required_review_checklist_markers = [_][]const u8{
        "zigux/tests/phase4_perf_baseline_manifest.json",
        "zigux/tests/phase4_perf_baseline_survey.zig",
        "the dedicated local-only perf-baseline survey packet",
        "the approved local-only benchmark commands and acceptable limits it carries",
        "the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
        "the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners",
        "the still-pending shared-CI perf-promotion posture",
    };

    for (required_review_checklist_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, review_checklist, marker) != null);
    }

    const required_docs_readme_markers = [_][]const u8{
        "zigux/tests/phase4_perf_baseline_manifest.json",
        "zigux/tests/phase4_perf_baseline_survey.zig",
        "the dedicated local-only perf-baseline survey packet's approved benchmark commands and acceptable limits",
        "the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
        "the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
        "the intentionally unapproved shared-CI perf-threshold posture explicit for the shipped Phase 4 gates",
    };

    for (required_docs_readme_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, docs_readme, marker) != null);
    }

    const required_scripts_readme_markers = [_][]const u8{
        "zigux/tests/phase4_perf_baseline_manifest.json",
        "zigux/tests/phase4_perf_baseline_survey.zig",
        "approved local-only benchmark commands and acceptable limits",
        "the Validation and Perf Team stays named here as the decision owner for any broader shared-CI perf promotion",
        "the ABI and Runtime Team plus Shared Subsystems Pod stay named here as the coordination owners for that policy call",
        "the shared reminder surfaces keep that promotion explicitly pending",
    };

    for (required_scripts_readme_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, scripts_readme, marker) != null);
    }
}

test "phase4 perf baseline survey keeps the local wrapper and gate-evidence split explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const gate_evidence = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-gate-evidence.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(gate_evidence);

    const required_makefile_markers = [_][]const u8{
        "phase4-perf-baseline-survey:",
        "$(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    };

    for (required_makefile_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, makefile, marker) != null);
    }

    const required_gate_evidence_markers = [_][]const u8{
        "zigux/tests/phase4_perf_baseline_manifest.json",
        "zigux/tests/phase4_perf_baseline_survey.zig",
        "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
        "make -C zigux phase4-perf-baseline-survey",
        "approved local-only command-and-limit evidence for both rollback gates remains intentionally separate from shared CI perf approval",
        "stays the bounded replay route outside the shared validator-backed exact-readback target set",
    };

    for (required_gate_evidence_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, gate_evidence, marker) != null);
    }
}
