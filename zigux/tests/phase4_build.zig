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
    // Phase 4 now uses the roadmap-named wrapper while keeping the existing
    // runtime_* implementation as the single underlying replay body.
    const atomic64_diff_module = b.createModule(.{
        .root_source_file = b.path("atomic64_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    atomic64_diff_module.addImport("runtime_atomic64_sample", runtime_atomic64_sample_module);
    const atomic64_diff_survey_module = b.createModule(.{
        .root_source_file = b.path("phase4_runtime_atomic64_diff_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const test_fsmount_survey_module = b.createModule(.{
        .root_source_file = b.path("phase4_test_fsmount_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const kprobe_example_survey_module = b.createModule(.{
        .root_source_file = b.path("phase4_kprobe_example_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const perf_baseline_survey_module = b.createModule(.{
        .root_source_file = b.path("phase4_perf_baseline_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_diff_module = b.createModule(.{
        .root_source_file = b.path("bitmap_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_diff_module.addImport("bitmap", bitmap_module);
    bitmap_diff_module.addImport("find_bit", find_bit_module);
    const bitmap_bench_module = b.createModule(.{
        .root_source_file = b.path("phase4_bitmap_bench.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_bench_module.addImport("bitmap_diff", bitmap_diff_module);

    const atomic64_diff_tests = b.addTest(.{
        .name = "phase4-runtime-atomic64-diff-tests",
        .root_module = atomic64_diff_module,
    });
    const run_atomic64_diff_tests = b.addRunArtifact(atomic64_diff_tests);
    const atomic64_diff_survey_tests = b.addTest(.{
        .name = "phase4-runtime-atomic64-diff-survey-tests",
        .root_module = atomic64_diff_survey_module,
    });
    const run_atomic64_diff_survey_tests = b.addRunArtifact(atomic64_diff_survey_tests);
    const test_fsmount_survey_tests = b.addTest(.{
        .name = "phase4-test-fsmount-survey-tests",
        .root_module = test_fsmount_survey_module,
    });
    const run_test_fsmount_survey_tests = b.addRunArtifact(test_fsmount_survey_tests);
    const kprobe_example_survey_tests = b.addTest(.{
        .name = "phase4-kprobe-example-survey-tests",
        .root_module = kprobe_example_survey_module,
    });
    const run_kprobe_example_survey_tests = b.addRunArtifact(kprobe_example_survey_tests);
    const perf_baseline_survey_tests = b.addTest(.{
        .name = "phase4-perf-baseline-survey-tests",
        .root_module = perf_baseline_survey_module,
    });
    const run_perf_baseline_survey_tests = b.addRunArtifact(perf_baseline_survey_tests);

    const atomic64_step = b.step(
        "phase4-runtime-atomic64-diff",
        "Run the bounded Phase 4 runtime atomic64 diff gate and its survey evidence",
    );
    atomic64_step.dependOn(&run_atomic64_diff_tests.step);
    atomic64_step.dependOn(&run_atomic64_diff_survey_tests.step);
    const test_fsmount_step = b.step(
        "phase4-test-fsmount-survey",
        "Run the Phase 4 test_fsmount survey gate without claiming a landed Zig sample",
    );
    test_fsmount_step.dependOn(&run_test_fsmount_survey_tests.step);
    const kprobe_example_step = b.step(
        "phase4-kprobe-example-survey",
        "Run the Phase 4 kprobe example survey gate without claiming a landed Zig sample",
    );
    kprobe_example_step.dependOn(&run_kprobe_example_survey_tests.step);
    const perf_baseline_step = b.step(
        "phase4-perf-baseline-survey",
        "Run the Phase 4 perf-baseline survey gate while benchmark commands and limits stay intentionally unapproved",
    );
    perf_baseline_step.dependOn(&run_perf_baseline_survey_tests.step);

    const bitmap_diff_tests = b.addTest(.{
        .name = "phase4-bitmap-diff-tests",
        .root_module = bitmap_diff_module,
    });
    const run_bitmap_diff_tests = b.addRunArtifact(bitmap_diff_tests);
    const bitmap_step = b.step(
        "phase4-bitmap-diff",
        "Run the bounded Phase 4 bitmap diff gate in isolation",
    );
    bitmap_step.dependOn(&run_bitmap_diff_tests.step);

    const bitmap_bench = b.addExecutable(.{
        .name = "phase4-bitmap-bench",
        .root_module = bitmap_bench_module,
    });
    const run_bitmap_bench = b.addRunArtifact(bitmap_bench);
    run_bitmap_bench.skip_foreign_checks = true;
    const bitmap_bench_step = b.step(
        "phase4-bitmap-bench",
        "Run the isolated Phase 4 bitmap benchmark route for the deterministic threshold batch",
    );
    bitmap_bench_step.dependOn(&run_bitmap_bench.step);

    const test_step = b.step("test", "Run Phase 4 differential validation and survey tests");
    test_step.dependOn(&run_atomic64_diff_tests.step);
    test_step.dependOn(&run_atomic64_diff_survey_tests.step);
    test_step.dependOn(&run_test_fsmount_survey_tests.step);
    test_step.dependOn(&run_kprobe_example_survey_tests.step);
    test_step.dependOn(&run_perf_baseline_survey_tests.step);
    test_step.dependOn(&run_bitmap_diff_tests.step);
}
