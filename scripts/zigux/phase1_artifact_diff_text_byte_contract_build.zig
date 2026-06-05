const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_artifact_diff_text_byte_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase1-artifact-diff-text-byte-contract-tests",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase1-artifact-diff-text-byte-contract",
        "Run the Lane 09 artifact-diff text byte contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 09 artifact-diff text byte contract tests.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}
