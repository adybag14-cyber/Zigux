const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane05_phase9_phase10_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane05-phase9-phase10-workflow-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane05-phase9-phase10-workflow-contract",
        "Validate the Lane 05 Phase 9/Phase 7/Phase 10 bootstrap workflow handoff.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 05 Phase 9/Phase 10 workflow contract tests.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(contract_step);
}
