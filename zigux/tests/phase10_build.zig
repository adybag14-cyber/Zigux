const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_core_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_driver_id_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_driver_id.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_driver_id_module.addImport("virtio_core", virtio_core_module);
    const virtio_core_verify_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_verify.zig"),
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
    const virtio_input_queue_callback_preflight_driver_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_queue_callback_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_queue_callback_preflight_driver_module.addImport("virtio_input", virtio_input_module);
    const virtio_input_registration_preflight_driver_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_registration_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_registration_preflight_driver_module.addImport("virtio_input", virtio_input_module);
    const virtio_input_status_drain_driver_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_status_drain.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_status_drain_driver_module.addImport("virtio_input", virtio_input_module);
    const virtio_input_teardown_preflight_driver_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_teardown_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_teardown_preflight_driver_module.addImport("virtio_input", virtio_input_module);
    const virtio_input_verify_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_verify_module.addImport("virtio_input", virtio_input_module);
    virtio_input_verify_module.addImport(
        "virtio_input_probe_preflight",
        virtio_input_probe_preflight_module,
    );
    virtio_input_verify_module.addImport(
        "virtio_input_queue_callback_preflight",
        virtio_input_queue_callback_preflight_driver_module,
    );
    virtio_input_verify_module.addImport(
        "virtio_input_registration_preflight",
        virtio_input_registration_preflight_driver_module,
    );
    virtio_input_verify_module.addImport(
        "virtio_input_status_drain",
        virtio_input_status_drain_driver_module,
    );
    virtio_input_verify_module.addImport(
        "virtio_input_teardown_preflight",
        virtio_input_teardown_preflight_driver_module,
    );
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
    const virtio_mmio_apply_observation_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_mmio_apply_observation.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_mmio_apply_observation_module.addImport("virtio_mmio", virtio_mmio_module);
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
    const virtio_ring_publish_readiness_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_publish_readiness.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_ring_publish_readiness_module.addImport("virtio_ring", virtio_ring_module);
    const virtio_ring_notification_data_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_notification_data.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_ring_notification_data_module.addImport("virtio_ring", virtio_ring_module);
    const virtio_ring_registration_summary_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_registration_summary.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_ring_registration_summary_module.addImport("virtio_ring", virtio_ring_module);
    const virtio_ring_used_buffer_poll_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_used_buffer_poll.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_ring_used_buffer_poll_module.addImport("virtio_ring", virtio_ring_module);
    const virtio_ring_reset_readiness_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_reset_readiness.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_ring_reset_readiness_module.addImport("virtio_ring", virtio_ring_module);

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
        virtio_input_queue_callback_preflight_driver_module,
    );

    const phase10_virtio_input_registration_preflight_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_registration_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_registration_preflight_module.addImport("virtio_input", virtio_input_module);
    phase10_virtio_input_registration_preflight_module.addImport(
        "virtio_input_registration_preflight",
        virtio_input_registration_preflight_driver_module,
    );

    const phase10_virtio_input_status_drain_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_status_drain.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_status_drain_module.addImport("virtio_input", virtio_input_module);
    phase10_virtio_input_status_drain_module.addImport(
        "virtio_input_status_drain",
        virtio_input_status_drain_driver_module,
    );

    const phase10_virtio_input_teardown_preflight_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_teardown_preflight.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_teardown_preflight_module.addImport("virtio_input", virtio_input_module);
    phase10_virtio_input_teardown_preflight_module.addImport(
        "virtio_input_teardown_preflight",
        virtio_input_teardown_preflight_driver_module,
    );

    const virtio_input_teardown_observation_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_teardown_observation.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_input_teardown_observation_module.addImport("virtio_input", virtio_input_module);
    virtio_input_verify_module.addImport(
        "virtio_input_teardown_observation",
        virtio_input_teardown_observation_module,
    );

    const phase10_virtio_input_teardown_observation_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_teardown_observation.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_input_teardown_observation_module.addImport("virtio_input", virtio_input_module);
    phase10_virtio_input_teardown_observation_module.addImport(
        "virtio_input_teardown_observation",
        virtio_input_teardown_observation_module,
    );

    const phase10_virtio_input_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase10_virtio_ring_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_module.addImport("virtio_ring", virtio_ring_module);

    const phase10_virtio_ring_notification_data_readiness_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_notification_data_readiness.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_notification_data_readiness_module.addImport("virtio_ring", virtio_ring_module);

    const phase10_virtio_ring_registration_replay_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_registration_replay.zig"),
        .target = target,
        .optimize = optimize,
    });

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

    const phase10_virtio_ring_reset_readiness_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_reset_readiness.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_reset_readiness_module.addImport("virtio_ring", virtio_ring_module);
    phase10_virtio_ring_reset_readiness_module.addImport(
        "virtio_ring_reset_readiness",
        virtio_ring_reset_readiness_module,
    );

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

    const phase10_virtio_ring_queue_build_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_queue_build_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase10_virtio_ring_survey_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_survey.zig"),
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

    const phase10_virtio_core_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_core.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_core_module.addImport("virtio_core", virtio_core_module);

    const phase10_virtio_core_interrupt_compound_ack_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_core_interrupt_compound_ack.zig"),
        .target = target,
        .optimize = optimize,
    });

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

    const phase10_virtio_driver_id_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_driver_id.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_driver_id_module.addImport("virtio_core", virtio_core_module);
    phase10_virtio_driver_id_module.addImport("virtio_driver_id", virtio_driver_id_module);

    const phase10_virtio_core_tests = b.addTest(.{
        .name = "phase10-virtio-core-tests",
        .root_module = phase10_virtio_core_module,
    });
    const run_phase10_virtio_core_tests = b.addRunArtifact(phase10_virtio_core_tests);

    const phase10_virtio_core_interrupt_compound_ack_tests = b.addTest(.{
        .name = "phase10-virtio-core-interrupt-compound-ack-tests",
        .root_module = phase10_virtio_core_interrupt_compound_ack_module,
    });
    const run_phase10_virtio_core_interrupt_compound_ack_tests = b.addRunArtifact(
        phase10_virtio_core_interrupt_compound_ack_tests,
    );

    const phase10_virtio_core_reset_queue_tests = b.addTest(.{
        .name = "phase10-virtio-core-reset-queue-tests",
        .root_module = phase10_virtio_core_reset_queue_module,
    });
    const run_phase10_virtio_core_reset_queue_tests = b.addRunArtifact(
        phase10_virtio_core_reset_queue_tests,
    );

    const phase10_virtio_core_verify_tests = b.addTest(.{
        .name = "phase10-virtio-core-verify-tests",
        .root_module = virtio_core_verify_module,
    });
    const run_phase10_virtio_core_verify_tests = b.addRunArtifact(phase10_virtio_core_verify_tests);

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

    const phase10_virtio_input_teardown_preflight_tests = b.addTest(.{ .name = "phase10-virtio-input-teardown-preflight-tests", .root_module = phase10_virtio_input_teardown_preflight_module });
    const run_phase10_virtio_input_teardown_preflight_tests = b.addRunArtifact(phase10_virtio_input_teardown_preflight_tests);

    const phase10_virtio_input_teardown_observation_tests = b.addTest(.{ .name = "phase10-virtio-input-teardown-observation-tests", .root_module = phase10_virtio_input_teardown_observation_module });
    const run_phase10_virtio_input_teardown_observation_tests = b.addRunArtifact(phase10_virtio_input_teardown_observation_tests);

    const phase10_virtio_input_survey_tests = b.addTest(.{ .name = "phase10-virtio-input-survey-tests", .root_module = phase10_virtio_input_survey_module });
    const run_phase10_virtio_input_survey_tests = b.addRunArtifact(phase10_virtio_input_survey_tests);

    const phase10_virtio_input_verify_tests = b.addTest(.{ .name = "phase10-virtio-input-verify-tests", .root_module = virtio_input_verify_module });
    const run_phase10_virtio_input_verify_tests = b.addRunArtifact(phase10_virtio_input_verify_tests);

    const phase10_virtio_ring_tests = b.addTest(.{ .name = "phase10-virtio-ring-tests", .root_module = phase10_virtio_ring_module });
    const run_phase10_virtio_ring_tests = b.addRunArtifact(phase10_virtio_ring_tests);

    const phase10_virtio_ring_notification_data_readiness_tests = b.addTest(.{ .name = "phase10-virtio-ring-notification-data-readiness-tests", .root_module = phase10_virtio_ring_notification_data_readiness_module });
    const run_phase10_virtio_ring_notification_data_readiness_tests = b.addRunArtifact(phase10_virtio_ring_notification_data_readiness_tests);

    const phase10_virtio_ring_registration_replay_tests = b.addTest(.{ .name = "phase10-virtio-ring-registration-replay-tests", .root_module = phase10_virtio_ring_registration_replay_module });
    const run_phase10_virtio_ring_registration_replay_tests = b.addRunArtifact(phase10_virtio_ring_registration_replay_tests);

    const phase10_virtio_ring_notification_data_wrapper_tests = b.addTest(.{ .name = "phase10-virtio-ring-notification-data-wrapper-tests", .root_module = virtio_ring_notification_data_module });
    const run_phase10_virtio_ring_notification_data_wrapper_tests = b.addRunArtifact(phase10_virtio_ring_notification_data_wrapper_tests);

    const phase10_virtio_ring_registration_summary_tests = b.addTest(.{ .name = "phase10-virtio-ring-registration-summary-tests", .root_module = virtio_ring_registration_summary_module });
    const run_phase10_virtio_ring_registration_summary_tests = b.addRunArtifact(phase10_virtio_ring_registration_summary_tests);

    const phase10_virtio_ring_used_buffer_poll_tests = b.addTest(.{ .name = "phase10-virtio-ring-used-buffer-poll-tests", .root_module = virtio_ring_used_buffer_poll_module });
    const run_phase10_virtio_ring_used_buffer_poll_tests = b.addRunArtifact(phase10_virtio_ring_used_buffer_poll_tests);

    const phase10_virtio_ring_verify_tests = b.addTest(.{ .name = "phase10-virtio-ring-verify-tests", .root_module = virtio_ring_verify_module });
    const run_phase10_virtio_ring_verify_tests = b.addRunArtifact(phase10_virtio_ring_verify_tests);

    const phase10_virtio_ring_publish_readiness_tests = b.addTest(.{ .name = "phase10-virtio-ring-publish-readiness-tests", .root_module = virtio_ring_publish_readiness_module });
    const run_phase10_virtio_ring_publish_readiness_tests = b.addRunArtifact(phase10_virtio_ring_publish_readiness_tests);

    const phase10_virtio_ring_prepare_kick_idempotent_tests = b.addTest(.{ .name = "phase10-virtio-ring-prepare-kick-idempotent-tests", .root_module = phase10_virtio_ring_prepare_kick_idempotent_module });
    const run_phase10_virtio_ring_prepare_kick_idempotent_tests = b.addRunArtifact(phase10_virtio_ring_prepare_kick_idempotent_tests);

    const phase10_virtio_ring_reset_reuse_tests = b.addTest(.{ .name = "phase10-virtio-ring-reset-reuse-tests", .root_module = phase10_virtio_ring_reset_reuse_module });
    const run_phase10_virtio_ring_reset_reuse_tests = b.addRunArtifact(phase10_virtio_ring_reset_reuse_tests);

    const phase10_virtio_ring_reset_readiness_tests = b.addTest(.{ .name = "phase10-virtio-ring-reset-readiness-tests", .root_module = phase10_virtio_ring_reset_readiness_module });
    const run_phase10_virtio_ring_reset_readiness_tests = b.addRunArtifact(phase10_virtio_ring_reset_readiness_tests);

    const phase10_virtio_ring_broken_queue_queue_discipline_tests = b.addTest(.{ .name = "phase10-virtio-ring-broken-queue-queue-discipline-tests", .root_module = phase10_virtio_ring_broken_queue_queue_discipline_module });
    const run_phase10_virtio_ring_broken_queue_queue_discipline_tests = b.addRunArtifact(phase10_virtio_ring_broken_queue_queue_discipline_tests);

    const phase10_virtio_ring_delayed_callback_budget_tests = b.addTest(.{ .name = "phase10-virtio-ring-delayed-callback-budget-tests", .root_module = phase10_virtio_ring_delayed_callback_budget_module });
    const run_phase10_virtio_ring_delayed_callback_budget_tests = b.addRunArtifact(phase10_virtio_ring_delayed_callback_budget_tests);

    const phase10_virtio_ring_queue_build_survey_tests = b.addTest(.{ .name = "phase10-virtio-ring-queue-build-survey-tests", .root_module = phase10_virtio_ring_queue_build_survey_module });
    const run_phase10_virtio_ring_queue_build_survey_tests = b.addRunArtifact(phase10_virtio_ring_queue_build_survey_tests);

    const phase10_virtio_ring_survey_tests = b.addTest(.{ .name = "phase10-virtio-ring-survey-tests", .root_module = phase10_virtio_ring_survey_module });
    const run_phase10_virtio_ring_survey_tests = b.addRunArtifact(phase10_virtio_ring_survey_tests);

    const phase10_virtio_mmio_tests = b.addTest(.{ .name = "phase10-virtio-mmio-tests", .root_module = virtio_mmio_module });
    const run_phase10_virtio_mmio_tests = b.addRunArtifact(phase10_virtio_mmio_tests);
    const phase10_virtio_mmio_lab_tests = b.addTest(.{ .name = "phase10-virtio-mmio-lab-tests", .root_module = phase10_virtio_mmio_module });
    const run_phase10_virtio_mmio_lab_tests = b.addRunArtifact(phase10_virtio_mmio_lab_tests);
    const phase10_virtio_mmio_verify_tests = b.addTest(.{ .name = "phase10-virtio-mmio-verify-tests", .root_module = virtio_mmio_verify_module });
    const run_phase10_virtio_mmio_verify_tests = b.addRunArtifact(phase10_virtio_mmio_verify_tests);
    const phase10_virtio_mmio_apply_observation_tests = b.addTest(.{ .name = "phase10-virtio-mmio-apply-observation-tests", .root_module = virtio_mmio_apply_observation_module });
    const run_phase10_virtio_mmio_apply_observation_tests = b.addRunArtifact(phase10_virtio_mmio_apply_observation_tests);
    const phase10_virtio_mmio_survey_tests = b.addTest(.{ .name = "phase10-virtio-mmio-survey-tests", .root_module = phase10_virtio_mmio_survey_module });
    const run_phase10_virtio_mmio_survey_tests = b.addRunArtifact(phase10_virtio_mmio_survey_tests);

    const phase10_virtio_core_step = b.step(
        "phase10-virtio-core-tests",
        "Run the live Phase 10 virtio core wrapper tests",
    );
    phase10_virtio_core_step.dependOn(&run_phase10_virtio_core_tests.step);

    const phase10_virtio_core_interrupt_compound_ack_step = b.step(
        "phase10-virtio-core-interrupt-compound-ack-tests",
        "Run the live Phase 10 virtio core interrupt-compound-ack tests",
    );
    phase10_virtio_core_interrupt_compound_ack_step.dependOn(
        &run_phase10_virtio_core_interrupt_compound_ack_tests.step,
    );

    const phase10_virtio_core_reset_queue_step = b.step(
        "phase10-virtio-core-reset-queue-tests",
        "Run the live Phase 10 virtio core reset-queue tests",
    );
    phase10_virtio_core_reset_queue_step.dependOn(&run_phase10_virtio_core_reset_queue_tests.step);

    const phase10_virtio_core_verify_step = b.step(
        "phase10-virtio-core-verify-tests",
        "Run the live Phase 10 virtio core verify tests",
    );
    phase10_virtio_core_verify_step.dependOn(&run_phase10_virtio_core_verify_tests.step);

    const phase10_virtio_core_survey_step = b.step(
        "phase10-virtio-core-survey-tests",
        "Run the live Phase 10 virtio core survey tests",
    );
    phase10_virtio_core_survey_step.dependOn(&run_phase10_virtio_core_survey_tests.step);

    const phase10_virtio_driver_id_step = b.step(
        "phase10-virtio-driver-id-tests",
        "Run the live Phase 10 virtio driver-id wrapper tests",
    );
    phase10_virtio_driver_id_step.dependOn(&run_phase10_virtio_driver_id_tests.step);

    const phase10_virtio_mmio_apply_observation_step = b.step(
        "phase10-virtio-mmio-apply-observation-tests",
        "Run the live Phase 10 virtio MMIO apply-observation wrapper tests",
    );
    phase10_virtio_mmio_apply_observation_step.dependOn(
        &run_phase10_virtio_mmio_apply_observation_tests.step,
    );

    const test_step = b.step("test", "Run the live Phase 10 virtio core, input, ring, and MMIO lab validation tests");
    test_step.dependOn(&run_phase10_virtio_core_tests.step);
    test_step.dependOn(&run_phase10_virtio_core_interrupt_compound_ack_tests.step);
    test_step.dependOn(&run_phase10_virtio_core_reset_queue_tests.step);
    test_step.dependOn(&run_phase10_virtio_core_verify_tests.step);
    test_step.dependOn(&run_phase10_virtio_core_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_driver_id_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_probe_preflight_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_queue_callback_preflight_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_registration_preflight_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_status_drain_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_teardown_preflight_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_teardown_observation_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_input_verify_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_notification_data_readiness_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_registration_replay_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_notification_data_wrapper_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_registration_summary_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_used_buffer_poll_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_verify_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_publish_readiness_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_prepare_kick_idempotent_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_reset_reuse_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_reset_readiness_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_broken_queue_queue_discipline_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_delayed_callback_budget_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_queue_build_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_survey_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_lab_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_verify_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_apply_observation_tests.step);
    test_step.dependOn(&run_phase10_virtio_mmio_survey_tests.step);
}
