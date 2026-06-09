const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_setup_python_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane17-phase1-setup-python-workflow-contract",
        .root_module = contract_module,
    });

    const run_contract = b.addRunArtifact(contract_tests);
    const contract_step = b.step("lane17-phase1-setup-python-workflow-contract", "Run the Lane 17 Phase 1 setup Python workflow contract");
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 1 setup Python workflow contract");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}
