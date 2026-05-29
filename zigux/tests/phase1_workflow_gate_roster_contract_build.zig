const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_workflow_gate_roster_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase1-workflow-gate-roster-contract-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const roster_step = b.step(
        "phase1-workflow-gate-roster-contract",
        "Run the Lane 07 Phase 1 workflow gate roster contract",
    );
    roster_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 07 Phase 1 workflow gate roster contract");
    test_step.dependOn(&run_tests.step);
}
