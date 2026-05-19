const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_core_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio.zig"),
        .target = target,
        .optimize = optimize,
    });
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
    const virtio_input_queue_callback_preflight_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_queue_callback_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_queue_callback_preflight_module.addImport("virtio_input", virtio_input_module);
    const virtio_input_registration_preflight_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_registration_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_registration_preflight_module.addImport("virtio_input", virtio_input_module);
    const virtio_input_status_drain_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_status_drain.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_status_drain_module.addImport("virtio_input", virtio_input_module);
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
    const virtio_mmio_verify_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_mmio_verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_mmio_verify_module.addImport("virtio_mmio", virtio_mmio_module);
    const virtio_ring_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_ring_verify_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_ring_verify_module.addImport("virtio_ring", virtio_ring_module);

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
    phase10_virtio_input_queue_callback_preflight_module.addImport(
        "virtio_input_queue_callback_preflight",
        virtio_input_queue_callback_preflight_module,
    );

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
    phase10_virtio_input_status_drain_module.addImport(
        "virtio_input_status_drain",
        virtio_input_status_drain_module,
    );

    const virtio_input_teardown_observation_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_teardown_observation.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_teardown_observation_module.addImport("virtio_input", virtio_input_module);

    const phase10_virtio_input_teardown_observation_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_teardown_observation.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_teardown_observation_module.addImport("virtio_input", virtio_input_module);
    virtio_input_verify_module.addImport(
        "virtio_input_teardown_observation",
        phase10_virtio_input_teardown_observation_module,
    );

    const phase10_virtio_input_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase10_virtio_ring_notification_data_readiness_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_notification_data_readiness.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_notification_data_readiness_module.addImport("virtio_ring", virtio_ring_module);

    const phase10_virtio_ring_prepare_kick_idempotent_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_prepare_kick_idempotent.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_prepare_kick_idempotent_module.addImport("virtio_ring", virtio_ring_module);

    const phase10_virtio_ring_reset_reuse_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_reset_reuse.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_reset_reuse_module.addImport("virtio_ring", virtio_ring_module);

    const phase10_virtio_ring_broken_queue_queue_discipline_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_broken_queue_queue_discipline.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_broken_queue_queue_discipline_module.addImport("virtio_ring", virtio_ring_module);

    const phase10_virtio_ring_delayed_callback_budget_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_delayed_callback_budget.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_delayed_callback_budget_module.addImport("virtio_ring", virtio_ring_module);

    const phase10_virtio_ring_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase10_virtio_mmio_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_mmio_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase10_virtio_core_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_core.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_core_module.addImport("virtio_core", virtio_core_module);

    const phase10_virtio_core_tests = b.addTest(.{
        .name = "phase10-virtio-core-tests",
        .root_module = phase10_virtio_core_module,
    });
    const run_phase10_virtio_core_tests = b.addRunArtifact(phase10_virtio_core_tests);

    const phase10_virtio_input_tests = b.addTest(.{ .name = "phase10-virtio-input-tests", .root_module = phase10_virtio_input_module });
    const run_phase10_virtio_input_tests = b.addRunArtifact(phase10_virtio_input_tests);

    const phase10_virtio_input_probe_preflight_tests = b.addTest(.{ .name = "phase10-virtio-input-probe-preflight-tests", .root_module = phase10_virtio_input_probe_preflight_module });
    const run_phase10_virtio_input_probe_preflight_tests = b.addRunArtifact(phase10_virtio_input_probe_preflight_tests);

    const phase10_virtio_input_queue_callback_preflight_tests = b.addTest(.{ .name = "phase10-virtio-input-queue-callback-preflight-tests", .root_module = phase10_virtio_input_queue_callback_preflight_module });
    const run_phase10_virtio_input_queue_callback_preflight_tests = b.addRunArtifact(phase10_virtio_input_queue_callback_preflight_tests);

    const phase10_virtio_input_registration_preflight_tests = b.addTest(.{ .name = "phase10-virtio-input-registration-preflight-tests", .root_module = phase10_virtio_input_registration_preflight_module });
    const run_phase10_virtio_input_registration_preflight_tests = b.addRunArtifact(phase10_virtio_input_registration_preflight_tests);

    const phase10_virtio_input_status_drain_tests = b.addTest(.{ .name = "phase10-virtio-input-status-drain-tests", .root_module = phase10_virtio_input_status_drain_module });
    const run_phase10_virtio_input_status_drain_tests = b.addRunArtifact(phase10_virtio_input_status_drain_tests);

    const phase10_virtio_input_teardown_observation_tests = b.addTest(.{ .name = "phase10-virtio-input-teardown-observation-tests", .root_module = phase10_virtio_input_teardown_observation_module });
    const run_phase10_virtio_input_teardown_observation_tests = b.addRunArtifact(phase10_virtio_input_teardown_observation_tests);

    const phase10_virtio_input_survey_tests = b.addTest(.{ .name = "phase10-virtio-input-survey-tests", .root_module = phase10_virtio_input_survey_module });
    const run_phase10_virtio_input_survey_tests = b.addRunArtifact(phase10_virtio_input_survey_tests);

    const phase10_virtio_input_verify_tests = b.addTest(.{ .name = "phase10-virtio-input-verify-tests", .root_module = virtio_input_verify_module });
    const run_phase10_virtio_input_verify_tests = b.addRunArtifact(phase10_virtio_input_verify_tests);

    const phase10_virtio_ring_notification_data_readiness_tests = b.addTest(.{ .name = "phase10-virtio-ring-notification-data-readiness-tests", .root_module = phase10_virtio_ring_notification_data_readiness_module });
    const run_phase10_virtio_ring_notification_data_readiness_tests = b.addRunArtifact(phase10_virtio_ring_notification_data_readiness_tests);

    const phase10_virtio_ring_verify_tests = b.addTest(.{ .name = "phase10-virtio-ring-verify-tests", .root_module = virtio_ring_verify_module });
    const run_phase10_virtio_ring_verify_tests = b.addRunArtifact(phase10_virtio_ring_verify_tests);

    const phase10_virtio_ring_prepare_kick_idempotent_tests = b.addTest(.{ .name = "phase10-virtio-ring-prepare-kick-idempotent-tests", .root_module = phase10_virtio_ring_prepare_kick_idempotent_module });
    const run_phase10_virtio_ring_prepare_kick_idempotent_tests = b.addRunArtifact(phase10_virtio_ring_prepare_kick_idempotent_tests);

    const phase10_virtio_ring_reset_reuse_tests = b.addTest(.{ .name = "phase10-virtio-ring-reset-reuse-tests", .root_module = phase10_virtio_ring_reset_reuse_module });
    const run_phase10_virtio_ring_reset_reuse_tests = b.addRunArtifact(phase10_virtio_ring_reset_reuse_tests);

    const phase10_virtio_ring_broken_queue_queue_discipline_tests = b.addTest(.{ .name = "phase10-virtio-ring-broken-queue-queue-discipline-tests", .root_module = phase10_virtio_ring_broken_queue_queue_discipline_module });
    const run_phase10_virtio_ring_broken_queue_queue_discipline_tests = b.addRunArtifact(phase10_virtio_ring_broken_queue_queue_discipline_tests);

    const phase10_virtio_ring_delayed_callback_budget_tests = b.addTest(.{ .name = "phase10-virtio-ring-delayed-callback-budget-tests", .root_module = phase10_virtio_ring_delayed_callback_budget_module });
    const run_phase10_virtio_ring_delayed_callback_budget_tests = b.addRunArtifact(phase10_virtio_ring_delayed_callback_budget_tests);

    const phase10_virtio_ring_survey_tests = b.addTest(.{ .name = "phase10-virtio-ring-survey-tests", .root_module = phase10_virtio_ring_survey_module });
    const run_phase10_virtio_ring_survey_tests = b.addRunArtifact(phase10_virtio_ring_survey_tests);

    const phase10_virtio_mmio_tests = b.addTest(.{ .name = "phase10-virtio-mmio-tests", .root_module = virtio_mmio_module });
    const run_phase10_virtio_mmio_tests = b.addRunArtifact(phase10_virtio_mmio_tests);
    const phase10_virtio_mmio_verify_tests = b.addTest(.{ .name = "phase10-virtio-mmio-verify-tests", .root_module = virtio_mmio_verify_module });
    const run_phase10_virtio_mmio_verify_tests = b.addRunArtifact(phase10_virtio_mmio_verify_tests);
    const phase10_virtio_mmio_survey_tests = b.addTest(.{ .name = "phase10-virtio-mmio-survey-tests", .root_module = phase10_virtio_mmio_survey_module });
    const run_phase10_virtio_mmio_survey_tests = b.addRunArtifact(phase10_virtio_mmio_survey_tests);

    const phase10_virtio_core_step = b.step(
        "phase10-virtio-core-tests",
        "Run the live Phase 10 virtio core wrapper tests",
    );
    phase10_virtio_core_step.dependOn(&run_phase10_virtio_core_tests.step);

    const test_step = b.step("test", "Run the live Phase 10 virtio core, input, ring, and MMIO lab validation tests");
    test_step.dependOn(&run_phase10_virtio_core_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_probe_preflight_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_queue_callback_preflight_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_registration_preflight_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_status_drain_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_teardown_observation_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_verify_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_notification_data_readiness_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_verify_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_prepare_kick_idempotent_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_reset_reuse_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_broken_queue_queue_discipline_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_delayed_callback_budget_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_verify_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_survey_tests.step);
}
