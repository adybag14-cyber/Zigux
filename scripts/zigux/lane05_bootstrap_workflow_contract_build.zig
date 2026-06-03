const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_bootstrap_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);

    const contract_step = b.step("lane05-bootstrap-workflow-contract", "Run the Lane 05 bootstrap workflow viability contract");
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Lane 05 bootstrap workflow viability contract");
    test_step.dependOn(&run_contract.step);
}
