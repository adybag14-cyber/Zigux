const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_phase3_phase4_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step("lane05-phase3-phase4-workflow-contract", "Run the Lane 05 Phase 3 to Phase 4 workflow contract");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 05 Phase 3 to Phase 4 workflow contract");
    test_step.dependOn(&run_tests.step);
}
