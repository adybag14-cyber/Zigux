const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_input_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_input_probe_preflight_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_probe_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_probe_preflight_module.addImport("virtio_input", virtio_input_module);
    const virtio_input_registration_preflight_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_registration_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_registration_preflight_module.addImport("virtio_input", virtio_input_module);
    const virtio_input_verify_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_verify_module.addImport("virtio_input", virtio_input_module);

    const virtio_mmio_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_mmio.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase10_virtio_input_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_module.addImport("virtio_input", virtio_input_module);

    const phase10_virtio_input_probe_preflight_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_probe_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_probe_preflight_module.addImport("virtio_input", virtio_input_module);
    phase10_virtio_input_probe_preflight_module.addImport(
        "virtio_input_probe_preflight",
        virtio_input_probe_preflight_module,
    );

    const phase10_virtio_input_queue_callback_preflight_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_queue_callback_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_queue_callback_preflight_module.addImport("virtio_input", virtio_input_module);

    const phase10_virtio_input_registration_preflight_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_registration_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_registration_preflight_module.addImport("virtio_input", virtio_input_module);
    phase10_virtio_input_registration_preflight_module.addImport(
        "virtio_input_registration_preflight",
        virtio_input_registration_preflight_module,
    );

    const phase10_virtio_input_status_drain_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_status_drain.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_status_drain_module.addImport("virtio_input", virtio_input_module);

    const phase10_virtio_input_teardown_observation_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_teardown_observation.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_teardown_observation_module.addImport("virtio_input", virtio_input_module);

    const phase10_virtio_input_tests = b.addTest(.{
        .name = "phase10-virtio-input-tests",
        .root_module = phase10_virtio_input_module,
    });
    const run_phase10_virtio_input_tests = b.addRunArtifact(phase10_virtio_input_tests);

    const phase10_virtio_input_probe_preflight_tests = b.addTest(.{
        .name = "phase10-virtio-input-probe-preflight-tests",
        .root_module = phase10_virtio_input_probe_preflight_module,
    });
    const run_phase10_virtio_input_probe_preflight_tests =
        b.addRunArtifact(phase10_virtio_input_probe_preflight_tests);

    const phase10_virtio_input_queue_callback_preflight_tests = b.addTest(.{
        .name = "phase10-virtio-input-queue-callback-preflight-tests",
        .root_module = phase10_virtio_input_queue_callback_preflight_module,
    });
    const run_phase10_virtio_input_queue_callback_preflight_tests =
        b.addRunArtifact(phase10_virtio_input_queue_callback_preflight_tests);

    const phase10_virtio_input_registration_preflight_tests = b.addTest(.{
        .name = "phase10-virtio-input-registration-preflight-tests",
        .root_module = phase10_virtio_input_registration_preflight_module,
    });
    const run_phase10_virtio_input_registration_preflight_tests =
        b.addRunArtifact(phase10_virtio_input_registration_preflight_tests);

    const phase10_virtio_input_status_drain_tests = b.addTest(.{
        .name = "phase10-virtio-input-status-drain-tests",
        .root_module = phase10_virtio_input_status_drain_module,
    });
    const run_phase10_virtio_input_status_drain_tests =
        b.addRunArtifact(phase10_virtio_input_status_drain_tests);

    const phase10_virtio_input_teardown_observation_tests = b.addTest(.{
        .name = "phase10-virtio-input-teardown-observation-tests",
        .root_module = phase10_virtio_input_teardown_observation_module,
    });
    const run_phase10_virtio_input_teardown_observation_tests =
        b.addRunArtifact(phase10_virtio_input_teardown_observation_tests);

    const phase10_virtio_input_verify_tests = b.addTest(.{
        .name = "phase10-virtio-input-verify-tests",
        .root_module = virtio_input_verify_module,
    });
    const run_phase10_virtio_input_verify_tests =
        b.addRunArtifact(phase10_virtio_input_verify_tests);

    const phase10_virtio_mmio_tests = b.addTest(.{
        .name = "phase10-virtio-mmio-tests",
        .root_module = virtio_mmio_module,
    });
    const run_phase10_virtio_mmio_tests = b.addRunArtifact(phase10_virtio_mmio_tests);

    const test_step = b.step(
        "test",
        "Run the live Phase 10 virtio input, verify, and MMIO lab validation tests",
    );
    test_step.dependOn(&run_phase10_virtio_input_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_probe_preflight_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_queue_callback_preflight_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_registration_preflight_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_status_drain_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_teardown_observation_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_verify_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_tests.step);
}
