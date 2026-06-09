const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_artifact_diff_channel_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const named_step = b.step(
        "phase1-artifact-diff-channel-contract",
        "Run Lane 09 artifact-diff stdout/stderr channel contract",
    );
    named_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Lane 09 artifact-diff channel contract tests");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
