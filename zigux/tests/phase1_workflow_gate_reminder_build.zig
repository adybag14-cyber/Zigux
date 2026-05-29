const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_workflow_gate_reminder.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase1-workflow-gate-reminder-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const focused = b.step(
        "phase1-workflow-gate-reminder",
        "Run the Phase 1 helper workflow gate reminder tests",
    );
    focused.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 helper workflow gate reminder tests");
    test_step.dependOn(&run_tests.step);
}
