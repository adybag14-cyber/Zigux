const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("validate_bootstrap_phase2_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "validate-bootstrap-phase2-workflow-contract-tests",
        .root_module = contract_module,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "validate-bootstrap-phase2-workflow-contract",
        "Run the validate-bootstrap Phase 2 workflow contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run validate-bootstrap Phase 2 workflow contract tests");
    test_step.dependOn(&run_contract.step);
}
