const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_module.addImport("find_bit", find_bit_module);
    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_atomic64_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_atomic64.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_sample_module.addImport("atomic", atomic_module);
    // Keep the shared runtime_atomic64_diff.zig replay explicit beside the wrapper entrypoint.
    const atomic64_diff_module = b.createModule(.{
        .root_source_file = b.path("atomic64_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    atomic64_diff_module.addImport("runtime_atomic64_sample", runtime_atomic64_sample_module);
    const runtime_atomic64_diff_survey_module = b.createModule(.{
        .root_source_file = b.path("phase4_runtime_atomic64_diff_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const perf_baseline_survey_module = b.createModule(.{
        .root_source_file = b.path("phase4_perf_baseline_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const test_fsmount_survey_module = b.createModule(.{
        .root_source_file = b.path("phase4_test_fsmount_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_diff_module = b.createModule(.{
        .root_source_file = b.path("bitmap_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_diff_survey_module = b.createModule(.{
        .root_source_file = b.path("phase4_bitmap_diff_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_live_helper_replay_module = b.createModule(.{
        .root_source_file = b.path("phase4_bitmap_live_helper_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_live_helper_replay_module.addImport("bitmap", bitmap_module);
    bitmap_live_helper_replay_module.addImport("find_bit", find_bit_module);

    const atomic64_diff_tests = b.addTest(.{
        .name = "phase4-runtime-atomic64-diff-tests",
        .root_module = atomic64_diff_module,
    });
    const run_atomic64_diff_tests = b.addRunArtifact(atomic64_diff_tests);

    const runtime_atomic64_diff_survey_tests = b.addTest(.{
        .name = "phase4-runtime-atomic64-diff-survey-tests",
        .root_module = runtime_atomic64_diff_survey_module,
    });
    const run_runtime_atomic64_diff_survey_tests = b.addRunArtifact(runtime_atomic64_diff_survey_tests);

    const perf_baseline_survey_tests = b.addTest(.{
        .name = "phase4-perf-baseline-survey-tests",
        .root_module = perf_baseline_survey_module,
    });
    const run_perf_baseline_survey_tests = b.addRunArtifact(perf_baseline_survey_tests);

    const test_fsmount_survey_tests = b.addTest(.{
        .name = "phase4-test-fsmount-survey-tests",
        .root_module = test_fsmount_survey_module,
    });
    const run_test_fsmount_survey_tests = b.addRunArtifact(test_fsmount_survey_tests);

    const bitmap_diff_tests = b.addTest(.{
        .name = "phase4-bitmap-diff-tests",
        .root_module = bitmap_diff_module,
    });
    const run_bitmap_diff_tests = b.addRunArtifact(bitmap_diff_tests);

    const bitmap_diff_survey_tests = b.addTest(.{
        .name = "phase4-bitmap-diff-survey-tests",
        .root_module = bitmap_diff_survey_module,
    });
    const run_bitmap_diff_survey_tests = b.addRunArtifact(bitmap_diff_survey_tests);

    const bitmap_live_helper_replay_tests = b.addTest(.{
        .name = "phase4-bitmap-live-helper-replay-tests",
        .root_module = bitmap_live_helper_replay_module,
    });
    const run_bitmap_live_helper_replay_tests = b.addRunArtifact(bitmap_live_helper_replay_tests);

    const test_step = b.step("test", "Run Phase 4 differential validation tests");
    test_step.dependOn(&run_atomic64_diff_tests.step);
    test_step.dependOn(&run_runtime_atomic64_diff_survey_tests.step);
    test_step.dependOn(&run_perf_baseline_survey_tests.step);
    test_step.dependOn(&run_test_fsmount_survey_tests.step);
    test_step.dependOn(&run_bitmap_diff_tests.step);
    test_step.dependOn(&run_bitmap_diff_survey_tests.step);
    test_step.dependOn(&run_bitmap_live_helper_replay_tests.step);

    const runtime_atomic64_diff_step = b.step(
        "phase4-runtime-atomic64-diff",
        "Run the isolated Phase 4 runtime atomic64 diff replay",
    );
    runtime_atomic64_diff_step.dependOn(&run_atomic64_diff_tests.step);

    const runtime_atomic64_diff_survey_step = b.step(
        "phase4-runtime-atomic64-diff-survey",
        "Run the manifest-backed Phase 4 runtime atomic64 handoff survey",
    );
    runtime_atomic64_diff_survey_step.dependOn(&run_runtime_atomic64_diff_survey_tests.step);

    const perf_baseline_survey_step = b.step(
        "phase4-perf-baseline-survey",
        "Run the dedicated Phase 4 perf-baseline posture survey without widening the shared correctness-first packet",
    );
    perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);

    const test_fsmount_survey_step = b.step(
        "phase4-test-fsmount-survey",
        "Run the dedicated Phase 4 test_fsmount gap survey without promoting a shipped Zig starter",
    );
    test_fsmount_survey_step.dependOn(&run_test_fsmount_survey_tests.step);

    const bitmap_diff_step = b.step("phase4-bitmap-diff", "Run the isolated Phase 4 bitmap diff replay");
    bitmap_diff_step.dependOn(&run_bitmap_diff_tests.step);

    const bitmap_diff_survey_step = b.step(
        "phase4-bitmap-diff-survey",
        "Run the manifest-backed Phase 4 bitmap rollback survey",
    );
    bitmap_diff_survey_step.dependOn(&run_bitmap_diff_survey_tests.step);

    const bitmap_live_helper_replay_step = b.step(
        "phase4-bitmap-live-helper-replay",
        "Run the helper-backed Phase 4 bitmap rollback replay",
    );
    bitmap_live_helper_replay_step.dependOn(&run_bitmap_live_helper_replay_tests.step);
}
