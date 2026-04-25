const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase14_ring_buffer_survey_module = b.createModule(.{
        .root_source_file = b.path("phase14_ring_buffer_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const workqueue_bridge_module = b.createModule(.{
        .root_source_file = b.path("../../kernel/workqueue_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });

    const skbuff_bridge_module = b.createModule(.{
        .root_source_file = b.path("../../net/core/skbuff_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase14_workqueue_bridge_module = b.createModule(.{
        .root_source_file = b.path("phase14_workqueue_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase14_workqueue_bridge_module.addImport("workqueue_bridge", workqueue_bridge_module);

    const phase14_skbuff_bridge_module = b.createModule(.{
        .root_source_file = b.path("phase14_skbuff_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase14_skbuff_bridge_module.addImport("skbuff_bridge", skbuff_bridge_module);

    const phase14_workqueue_bridge_tests = b.addTest(.{
        .name = "phase14-workqueue-bridge-tests",
        .root_module = phase14_workqueue_bridge_module,
    });
    const run_phase14_workqueue_bridge_tests = b.addRunArtifact(phase14_workqueue_bridge_tests);

    const phase14_skbuff_bridge_tests = b.addTest(.{
        .name = "phase14-skbuff-bridge-tests",
        .root_module = phase14_skbuff_bridge_module,
    });
    const run_phase14_skbuff_bridge_tests = b.addRunArtifact(phase14_skbuff_bridge_tests);

    const phase14_ring_buffer_survey_tests = b.addTest(.{
        .name = "phase14-ring-buffer-survey-tests",
        .root_module = phase14_ring_buffer_survey_module,
    });
    const run_phase14_ring_buffer_survey_tests = b.addRunArtifact(phase14_ring_buffer_survey_tests);

    const test_step = b.step("test", "Run Phase 14 bounded internal bridge tests");
    test_step.dependOn(&run_phase14_workqueue_bridge_tests.step);
    test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);
    test_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);
}
