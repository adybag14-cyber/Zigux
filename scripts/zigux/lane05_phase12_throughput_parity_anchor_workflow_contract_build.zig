const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_phase12_throughput_parity_anchor_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const named_step = b.step(
        "lane05-phase12-throughput-parity-anchor-workflow-contract",
        "Validate the Lane 05 terminal Phase 12 throughput-parity workflow anchor",
    );
    named_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 05 throughput-parity anchor workflow contract");
    test_step.dependOn(&run_contract_tests.step);
}
