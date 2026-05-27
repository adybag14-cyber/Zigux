const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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
    const virtio_ring_callback_enable_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_callback_enable.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_ring_callback_enable_module.addImport("virtio_ring", virtio_ring_module);
    const virtio_ring_registration_summary_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_registration_summary.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_ring_registration_summary_module.addImport("virtio_ring", virtio_ring_module);
    const virtio_ring_reset_readiness_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_reset_readiness.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_ring_reset_readiness_module.addImport("virtio_ring", virtio_ring_module);

    const phase10_virtio_ring_publish_readiness_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_publish_readiness.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_publish_readiness_module.addImport("virtio_ring", virtio_ring_module);
    phase10_virtio_ring_publish_readiness_module.addImport(
        "virtio_ring_publish_readiness",
        virtio_ring_publish_readiness_module,
    );

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

    const phase10_virtio_ring_verify_tests = b.addTest(.{
        .name = "phase10-virtio-ring-verify-tests",
        .root_module = virtio_ring_verify_module,
    });
    const run_phase10_virtio_ring_verify_tests = b.addRunArtifact(phase10_virtio_ring_verify_tests);

    const phase10_virtio_ring_publish_readiness_tests = b.addTest(.{
        .name = "phase10-virtio-ring-publish-readiness-tests",
        .root_module = virtio_ring_publish_readiness_module,
    });
    const run_phase10_virtio_ring_publish_readiness_tests = b.addRunArtifact(
        phase10_virtio_ring_publish_readiness_tests,
    );

    const phase10_virtio_ring_publish_readiness_replay_tests = b.addTest(.{
        .name = "phase10-virtio-ring-publish-readiness-replay-tests",
        .root_module = phase10_virtio_ring_publish_readiness_module,
    });
    const run_phase10_virtio_ring_publish_readiness_replay_tests = b.addRunArtifact(
        phase10_virtio_ring_publish_readiness_replay_tests,
    );

    const phase10_virtio_ring_notification_data_readiness_tests = b.addTest(.{
        .name = "phase10-virtio-ring-notification-data-readiness-tests",
        .root_module = phase10_virtio_ring_notification_data_readiness_module,
    });
    const run_phase10_virtio_ring_notification_data_readiness_tests = b.addRunArtifact(
        phase10_virtio_ring_notification_data_readiness_tests,
    );

    const phase10_virtio_ring_registration_replay_tests = b.addTest(.{
        .name = "phase10-virtio-ring-registration-replay-tests",
        .root_module = phase10_virtio_ring_registration_replay_module,
    });
    const run_phase10_virtio_ring_registration_replay_tests = b.addRunArtifact(
        phase10_virtio_ring_registration_replay_tests,
    );

    const phase10_virtio_ring_notification_data_wrapper_tests = b.addTest(.{
        .name = "phase10-virtio-ring-notification-data-wrapper-tests",
        .root_module = virtio_ring_notification_data_module,
    });
    const run_phase10_virtio_ring_notification_data_wrapper_tests = b.addRunArtifact(
        phase10_virtio_ring_notification_data_wrapper_tests,
    );

    const phase10_virtio_ring_callback_enable_tests = b.addTest(.{
        .name = "phase10-virtio-ring-callback-enable-tests",
        .root_module = virtio_ring_callback_enable_module,
    });
    const run_phase10_virtio_ring_callback_enable_tests = b.addRunArtifact(
        phase10_virtio_ring_callback_enable_tests,
    );

    const phase10_virtio_ring_registration_summary_tests = b.addTest(.{
        .name = "phase10-virtio-ring-registration-summary-tests",
        .root_module = virtio_ring_registration_summary_module,
    });
    const run_phase10_virtio_ring_registration_summary_tests = b.addRunArtifact(
        phase10_virtio_ring_registration_summary_tests,
    );

    const phase10_virtio_ring_prepare_kick_idempotent_tests = b.addTest(.{
        .name = "phase10-virtio-ring-prepare-kick-idempotent-tests",
        .root_module = phase10_virtio_ring_prepare_kick_idempotent_module,
    });
    const run_phase10_virtio_ring_prepare_kick_idempotent_tests = b.addRunArtifact(
        phase10_virtio_ring_prepare_kick_idempotent_tests,
    );

    const phase10_virtio_ring_reset_reuse_tests = b.addTest(.{
        .name = "phase10-virtio-ring-reset-reuse-tests",
        .root_module = phase10_virtio_ring_reset_reuse_module,
    });
    const run_phase10_virtio_ring_reset_reuse_tests = b.addRunArtifact(
        phase10_virtio_ring_reset_reuse_tests,
    );

    const phase10_virtio_ring_reset_readiness_tests = b.addTest(.{
        .name = "phase10-virtio-ring-reset-readiness-tests",
        .root_module = phase10_virtio_ring_reset_readiness_module,
    });
    const run_phase10_virtio_ring_reset_readiness_tests = b.addRunArtifact(
        phase10_virtio_ring_reset_readiness_tests,
    );

    const phase10_virtio_ring_broken_queue_queue_discipline_tests = b.addTest(.{
        .name = "phase10-virtio-ring-broken-queue-queue-discipline-tests",
        .root_module = phase10_virtio_ring_broken_queue_queue_discipline_module,
    });
    const run_phase10_virtio_ring_broken_queue_queue_discipline_tests = b.addRunArtifact(
        phase10_virtio_ring_broken_queue_queue_discipline_tests,
    );

    const phase10_virtio_ring_delayed_callback_budget_tests = b.addTest(.{
        .name = "phase10-virtio-ring-delayed-callback-budget-tests",
        .root_module = phase10_virtio_ring_delayed_callback_budget_module,
    });
    const run_phase10_virtio_ring_delayed_callback_budget_tests = b.addRunArtifact(
        phase10_virtio_ring_delayed_callback_budget_tests,
    );

    const phase10_virtio_ring_queue_build_survey_tests = b.addTest(.{
        .name = "phase10-virtio-ring-queue-build-survey-tests",
        .root_module = phase10_virtio_ring_queue_build_survey_module,
    });
    const run_phase10_virtio_ring_queue_build_survey_tests = b.addRunArtifact(
        phase10_virtio_ring_queue_build_survey_tests,
    );

    const phase10_virtio_ring_queue_tests = b.step(
        "phase10-virtio-ring-queue-tests",
        "Run the focused Phase 10 virtio ring queue-handling packet tests",
    );
    phase10_virtio_ring_queue_tests.dependOn(&run_phase10_virtio_ring_verify_tests.step);
    phase10_virtio_ring_queue_tests.dependOn(&run_phase10_virtio_ring_publish_readiness_tests.step);
    phase10_virtio_ring_queue_tests.dependOn(&run_phase10_virtio_ring_publish_readiness_replay_tests.step);
    phase10_virtio_ring_queue_tests.dependOn(
        &run_phase10_virtio_ring_notification_data_readiness_tests.step,
    );
    phase10_virtio_ring_queue_tests.dependOn(
        &run_phase10_virtio_ring_registration_replay_tests.step,
    );
    phase10_virtio_ring_queue_tests.dependOn(
        &run_phase10_virtio_ring_notification_data_wrapper_tests.step,
    );
    phase10_virtio_ring_queue_tests.dependOn(
        &run_phase10_virtio_ring_callback_enable_tests.step,
    );
    phase10_virtio_ring_queue_tests.dependOn(
        &run_phase10_virtio_ring_registration_summary_tests.step,
    );
    phase10_virtio_ring_queue_tests.dependOn(
        &run_phase10_virtio_ring_prepare_kick_idempotent_tests.step,
    );
    phase10_virtio_ring_queue_tests.dependOn(&run_phase10_virtio_ring_reset_reuse_tests.step);
    phase10_virtio_ring_queue_tests.dependOn(
        &run_phase10_virtio_ring_reset_readiness_tests.step,
    );
    phase10_virtio_ring_queue_tests.dependOn(
        &run_phase10_virtio_ring_broken_queue_queue_discipline_tests.step,
    );
    phase10_virtio_ring_queue_tests.dependOn(
        &run_phase10_virtio_ring_delayed_callback_budget_tests.step,
    );
    phase10_virtio_ring_queue_tests.dependOn(
        &run_phase10_virtio_ring_queue_build_survey_tests.step,
    );

    const test_step = b.step(
        "test",
        "Run the focused Phase 10 virtio ring queue-handling packet tests",
    );
    test_step.dependOn(&run_phase10_virtio_ring_verify_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_publish_readiness_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_publish_readiness_replay_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_notification_data_readiness_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_registration_replay_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_notification_data_wrapper_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_callback_enable_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_registration_summary_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_prepare_kick_idempotent_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_reset_reuse_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_reset_readiness_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_broken_queue_queue_discipline_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_delayed_callback_budget_tests.step);
    test_step.dependOn(&run_phase10_virtio_ring_queue_build_survey_tests.step);
}
