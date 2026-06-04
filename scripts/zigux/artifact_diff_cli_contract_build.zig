const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("artifact_diff_cli_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "artifact-diff-cli-contract-tests",
        .root_module = contract_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "artifact-diff-cli-contract",
        "Run the artifact_diff.py CLI parser and digest-mode Zig contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run artifact_diff.py CLI contract tests");
    test_step.dependOn(&run_tests.step);
}
