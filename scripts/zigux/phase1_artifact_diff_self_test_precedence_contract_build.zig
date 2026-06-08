const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_artifact_diff_self_test_precedence_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase1-artifact-diff-self-test-precedence-contract",
        "Validate artifact_diff.py self-test precedence source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run artifact diff self-test precedence contract tests");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
