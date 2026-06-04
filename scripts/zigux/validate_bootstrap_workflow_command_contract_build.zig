const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "validate-bootstrap-workflow-command-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("validate_bootstrap_workflow_command_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "validate-bootstrap-workflow-command-contract",
        "Run the validate-bootstrap workflow command roster contract tests",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the validate-bootstrap workflow command roster contract tests");
    test_step.dependOn(&run_tests.step);
}
