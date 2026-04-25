const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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
    const runtime_atomic64_module = b.createModule(.{
        .root_source_file = b.path("runtime_atomic64_module.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_module.addImport("runtime_atomic64_sample", runtime_atomic64_sample_module);

    const runtime_atomic64_survey_module = b.createModule(.{
        .root_source_file = b.path("runtime_atomic64_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_atomic64_module_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-module-tests",
        .root_module = runtime_atomic64_module,
    });
    const run_runtime_atomic64_module_tests = b.addRunArtifact(runtime_atomic64_module_tests);

    const runtime_atomic64_survey_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-survey-tests",
        .root_module = runtime_atomic64_survey_module,
    });
    const run_runtime_atomic64_survey_tests = b.addRunArtifact(runtime_atomic64_survey_tests);

    const test_step = b.step("test", "Run Phase 9 runtime atomic64 pilot-module tests");
    test_step.dependOn(&run_runtime_atomic64_module_tests.step);
    test_step.dependOn(&run_runtime_atomic64_survey_tests.step);
}
