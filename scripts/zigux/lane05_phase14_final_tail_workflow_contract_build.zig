const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_phase14_final_tail_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract = b.addExecutable(.{
        .name = "lane05-phase14-final-tail-workflow-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_phase14_final_tail_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract = b.addRunArtifact(contract);
    run_contract.step.dependOn(&run_contract_tests.step);

    const contract_step = b.step("lane05-phase14-final-tail-workflow-contract", "Validate the Lane 05 Phase 14 final-tail workflow contract");
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Lane 05 Phase 14 final-tail workflow contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
