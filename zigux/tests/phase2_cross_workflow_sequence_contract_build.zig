const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_workflow_sequence_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const contract_step = b.step("phase2-cross-workflow-sequence-contract", "Run Phase 2 cross workflow sequence contract");
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Phase 2 cross workflow sequence contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
