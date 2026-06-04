const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_phase9_phase11_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step("lane05-phase9-phase11-workflow-contract", "Run the Lane 05 Phase 9 through Phase 11 workflow contract");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 05 Phase 9 through Phase 11 workflow contract");
    test_step.dependOn(&run_tests.step);
}
