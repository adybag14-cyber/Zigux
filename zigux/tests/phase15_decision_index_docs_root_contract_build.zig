const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase15_decision_index_docs_root_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase15-decision-index-docs-root-contract-test",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const test_step = b.step(
        "phase15-decision-index-docs-root-contract",
        "Run the Phase 15 decision-index docs-root contract.",
    );
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}
