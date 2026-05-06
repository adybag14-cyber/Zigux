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
    const phase10_virtio_core_reset_queue_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_core_reset_queue.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_core_reset_queue_module.addImport("virtio_core", virtio_core_module);
    const phase10_virtio_core_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_core_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_driver_id_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_driver_id.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase10_virtio_driver_id_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_driver_id.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_driver_id_module.addImport("virtio_driver_id", virtio_driver_id_module);
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
    const phase10_virtio_input_status_drain_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_status_drain.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_status_drain_module.addImport("virtio_input", virtio_input_module);
    const phase10_virtio_input_verify_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_verify_module.addImport("virtio_input", virtio_input_module);
    const phase10_virtio_input_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase10_virtio_mmio_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_mmio_module.addImport("virtio_mmio", virtio_mmio_module);
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
    const phase10_virtio_core_reset_queue_tests = b.addTest(.{
        .name = "phase10-virtio-core-reset-queue-tests",
        .root_module = phase10_virtio_core_reset_queue_module,
    });
    const run_phase10_virtio_core_reset_queue_tests = b.addRunArtifact(phase10_virtio_core_reset_queue_tests);
    const phase10_virtio_core_survey_tests = b.addTest(.{
        .name = "phase10-virtio-core-survey-tests",
        .root_module = phase10_virtio_core_survey_module,
    });
    const run_phase10_virtio_core_survey_tests = b.addRunArtifact(phase10_virtio_core_survey_tests);
    const phase10_virtio_driver_id_tests = b.addTest(.{
        .name = "phase10-virtio-driver-id-tests",
        .root_module = phase10_virtio_driver_id_module,
    });
    const run_phase10_virtio_driver_id_tests = b.addRunArtifact(phase10_virtio_driver_id_tests);
    const phase10_virtio_ring_tests = b.addTest(.{
        .name = "phase10-virtio-ring-tests",
        .root_module = phase10_virtio_ring_module,
    });
    const run_phase10_virtio_ring_tests = b.addRunArtifact(phase10_virtio_ring_tests);
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
    const phase10_virtio_input_status_drain_tests = b.addTest(.{
        .name = "phase10-virtio-input-status-drain-tests",
        .root_module = phase10_virtio_input_status_drain_module,
    });
    const run_phase10_virtio_input_status_drain_tests = b.addRunArtifact(phase10_virtio_input_status_drain_tests);
    const phase10_virtio_input_verify_tests = b.addTest(.{
        .name = "phase10-virtio-input-verify-tests",
        .root_module = phase10_virtio_input_verify_module,
    });
    const run_phase10_virtio_input_verify_tests = b.addRunArtifact(phase10_virtio_input_verify_tests);
    const phase10_virtio_input_survey_tests = b.addTest(.{
        .name = "phase10-virtio-input-survey-tests",
        .root_module = phase10_virtio_input_survey_module,
    });
    const run_phase10_virtio_input_survey_tests = b.addRunArtifact(phase10_virtio_input_survey_tests);
    const phase10_virtio_mmio_tests = b.addTest(.{
        .name = "phase10-virtio-mmio-tests",
        .root_module = phase10_virtio_mmio_module,
    });
    const run_phase10_virtio_mmio_tests = b.addRunArtifact(phase10_virtio_mmio_tests);
    const phase10_virtio_mmio_survey_tests = b.addTest(.{
        .name = "phase10-virtio-mmio-survey-tests",
        .root_module = phase10_virtio_mmio_survey_module,
    });
    const run_phase10_virtio_mmio_survey_tests = b.addRunArtifact(phase10_virtio_mmio_survey_tests);

    const test_step = b.step("test", "Run Phase 10 virtio core, virtio ring, virtio input, virtio mmio, verifier, and survey tests");
    test_step.dependOn(&run_phase10_virtio_core_tests.step);
    test_step.dependOn(&run_phase10_virtio_core_reset_queue_tests.step);
    test_step.dependOn(&run_phase10_virtio_core_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_driver_id_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_status_drain_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_verify_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_survey_tests.step);
}
