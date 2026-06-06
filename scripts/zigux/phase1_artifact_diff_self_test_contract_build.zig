const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase1_artifact_diff_self_test_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase1-artifact-diff-self-test-contract-tests",
        .root_module = module,
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-artifact-diff-self-test-contract",
        "Run the Phase 1 artifact-diff self-test source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 artifact-diff self-test contract");
    test_step.dependOn(&run_tests.step);
}
