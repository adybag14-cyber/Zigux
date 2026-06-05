const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_artifact_diff_path_problem_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase1-artifact-diff-path-problem-contract-tests",
        .root_module = contract_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase1-artifact-diff-path-problem-contract",
        "Run the Phase 1 artifact_diff.py path-problem source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run this build-file's test suite");
    test_step.dependOn(&run_tests.step);
}
