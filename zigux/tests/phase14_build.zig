const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase14_end_to_end_smoke_module = b.createModule(.{
        .root_source_file = b.path("phase14_end_to_end_smoke_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase14_ring_buffer_survey_module = b.createModule(.{
        .root_source_file = b.path("phase14_ring_buffer_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase14_rcu_tree_survey_module = b.createModule(.{
        .root_source_file = b.path("phase14_rcu_tree_survey.zig"),
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

    const phase14_workqueue_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase14_workqueue_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });

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

    const phase14_workqueue_reviewability_tests = b.addTest(.{
        .name = "phase14-workqueue-reviewability-tests",
        .root_module = phase14_workqueue_reviewability_module,
    });
    const run_phase14_workqueue_reviewability_tests = b.addRunArtifact(phase14_workqueue_reviewability_tests);

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

    const phase14_rcu_tree_survey_tests = b.addTest(.{
        .name = "phase14-rcu-tree-survey-tests",
        .root_module = phase14_rcu_tree_survey_module,
    });
    const run_phase14_rcu_tree_survey_tests = b.addRunArtifact(phase14_rcu_tree_survey_tests);

    const phase14_end_to_end_smoke_tests = b.addTest(.{
        .name = "phase14-end-to-end-smoke-tests",
        .root_module = phase14_end_to_end_smoke_module,
    });
    const run_phase14_end_to_end_smoke_tests = b.addRunArtifact(phase14_end_to_end_smoke_tests);

    const smoke_step = b.step("phase14-smoke", "Run the focused Phase 14 smoke shard");
    smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);

    const test_step = b.step("test", "Run the full Phase 14 bounded bridge and survey bundle");
    test_step.dependOn(&run_phase14_workqueue_bridge_tests.step);
    test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);
    test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);
    test_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);
    test_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);
    test_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);
}
