const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_atomic64_survey_module = b.createModule(.{
        .root_source_file = b.path("runtime_atomic64_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_atomic64_survey_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-survey-tests",
        .root_module = runtime_atomic64_survey_module,
    });
    const run_runtime_atomic64_survey_tests = b.addRunArtifact(runtime_atomic64_survey_tests);

    const test_step = b.step("test", "Run Phase 9 runtime pilot-module survey tests");
    test_step.dependOn(&run_runtime_atomic64_survey_tests.step);
}
