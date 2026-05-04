const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_core_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase10_virtio_core_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_core.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_core_module.addImport("virtio_core", virtio_core_module);
    const phase10_virtio_core_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_core_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_ring_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_input_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_mmio_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase10_virtio_ring_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_module.addImport("virtio_ring", virtio_ring_module);
    const phase10_virtio_ring_reset_reuse_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_reset_reuse.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_reset_reuse_module.addImport("virtio_ring", virtio_ring_module);
    const phase10_virtio_ring_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase10_virtio_input_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_module.addImport("virtio_input", virtio_input_module);
    const phase10_virtio_input_multitouch_preflight_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_multitouch_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_multitouch_preflight_module.addImport("virtio_input", virtio_input_module);
    const phase10_virtio_input_status_drain_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_status_drain.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_status_drain_module.addImport("virtio_input", virtio_input_module);
    const phase10_virtio_mmio_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_mmio_module.addImport("virtio_mmio", virtio_mmio_module);
    const phase10_virtio_mmio_queue_isolation_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_mmio_queue_isolation.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_mmio_queue_isolation_module.addImport("virtio_mmio", virtio_mmio_module);
    const phase10_virtio_input_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase10_virtio_mmio_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_mmio_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase10_virtio_core_tests = b.addTest(.{
        .name = "phase10-virtio-core-tests",
        .root_module = phase10_virtio_core_module,
    });
    const run_phase10_virtio_core_tests = b.addRunArtifact(phase10_virtio_core_tests);
    const phase10_virtio_core_survey_tests = b.addTest(.{
        .name = "phase10-virtio-core-survey-tests",
        .root_module = phase10_virtio_core_survey_module,
    });
    const run_phase10_virtio_core_survey_tests = b.addRunArtifact(phase10_virtio_core_survey_tests);
    const phase10_virtio_ring_tests = b.addTest(.{
        .name = "phase10-virtio-ring-tests",
        .root_module = phase10_virtio_ring_module,
    });
    const run_phase10_virtio_ring_tests = b.addRunArtifact(phase10_virtio_ring_tests);
    const phase10_virtio_ring_reset_reuse_tests = b.addTest(.{
        .name = "phase10-virtio-ring-reset-reuse-tests",
        .root_module = phase10_virtio_ring_reset_reuse_module,
    });
    const run_phase10_virtio_ring_reset_reuse_tests = b.addRunArtifact(phase10_virtio_ring_reset_reuse_tests);
    const phase10_virtio_ring_survey_tests = b.addTest(.{
        .name = "phase10-virtio-ring-survey-tests",
        .root_module = phase10_virtio_ring_survey_module,
    });
    const run_phase10_virtio_ring_survey_tests = b.addRunArtifact(phase10_virtio_ring_survey_tests);
    const phase10_virtio_input_tests = b.addTest(.{
        .name = "phase10-virtio-input-tests",
        .root_module = phase10_virtio_input_module,
    });
    const run_phase10_virtio_input_tests = b.addRunArtifact(phase10_virtio_input_tests);
    const phase10_virtio_input_multitouch_preflight_tests = b.addTest(.{
        .name = "phase10-virtio-input-multitouch-preflight-tests",
        .root_module = phase10_virtio_input_multitouch_preflight_module,
    });
    const run_phase10_virtio_input_multitouch_preflight_tests = b.addRunArtifact(phase10_virtio_input_multitouch_preflight_tests);
    const phase10_virtio_input_status_drain_tests = b.addTest(.{
        .name = "phase10-virtio-input-status-drain-tests",
        .root_module = phase10_virtio_input_status_drain_module,
    });
    const run_phase10_virtio_input_status_drain_tests = b.addRunArtifact(phase10_virtio_input_status_drain_tests);
    const phase10_virtio_mmio_tests = b.addTest(.{
        .name = "phase10-virtio-mmio-tests",
        .root_module = phase10_virtio_mmio_module,
    });
    const run_phase10_virtio_mmio_tests = b.addRunArtifact(phase10_virtio_mmio_tests);
    const phase10_virtio_mmio_queue_isolation_tests = b.addTest(.{
        .name = "phase10-virtio-mmio-queue-isolation-tests",
        .root_module = phase10_virtio_mmio_queue_isolation_module,
    });
    const run_phase10_virtio_mmio_queue_isolation_tests = b.addRunArtifact(phase10_virtio_mmio_queue_isolation_tests);
    const phase10_virtio_input_survey_tests = b.addTest(.{
        .name = "phase10-virtio-input-survey-tests",
        .root_module = phase10_virtio_input_survey_module,
    });
    const run_phase10_virtio_input_survey_tests = b.addRunArtifact(phase10_virtio_input_survey_tests);
    const phase10_virtio_mmio_survey_tests = b.addTest(.{
        .name = "phase10-virtio-mmio-survey-tests",
        .root_module = phase10_virtio_mmio_survey_module,
    });
    const run_phase10_virtio_mmio_survey_tests = b.addRunArtifact(phase10_virtio_mmio_survey_tests);

    const test_step = b.step("test", "Run Phase 10 virtio core, virtio core survey, virtio ring, virtio ring reset reuse, virtio input, virtio input multitouch preflight, virtio input status drain, virtio mmio, virtio mmio queue isolation, virtio_input survey, virtio_ring survey, and virtio_mmio survey tests");
    test_step.dependOn(&run_phase10_virtio_core_tests.step);
    test_step.dependOn(&run_phase10_virtio_core_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_reset_reuse_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_multitouch_preflight_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_status_drain_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_queue_isolation_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_survey_tests.step);
}
