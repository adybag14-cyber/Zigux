const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_artifact_diff_self_test_roster_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase1-artifact-diff-self-test-roster-contract",
        .root_module = contract_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-artifact-diff-self-test-roster-contract",
        "Validate the artifact_diff.py self-test roster source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the artifact diff self-test roster contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
