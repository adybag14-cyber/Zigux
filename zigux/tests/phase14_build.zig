const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const workqueue_bridge_module = b.createModule(.{
        .root_source_file = b.path("../../kernel/workqueue_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase14_workqueue_bridge_module = b.createModule(.{
        .root_source_file = b.path("phase14_workqueue_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase14_workqueue_bridge_module.addImport("workqueue_bridge", workqueue_bridge_module);

    const phase14_workqueue_bridge_tests = b.addTest(.{
        .name = "phase14-workqueue-bridge-tests",
        .root_module = phase14_workqueue_bridge_module,
    });
    const run_phase14_workqueue_bridge_tests = b.addRunArtifact(phase14_workqueue_bridge_tests);

    const test_step = b.step("test", "Run Phase 14 boundary-map tests");
    test_step.dependOn(&run_phase14_workqueue_bridge_tests.step);
}
