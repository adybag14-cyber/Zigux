const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_workflow_trigger_paths_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "lane17-phase1-workflow-trigger-paths-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase1-workflow-trigger-paths-contract",
        "Run Lane 17 Phase 1 workflow trigger path contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 workflow trigger path contract");
    test_step.dependOn(&run_tests.step);
}
