const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_net_queue_resume_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_queue_resume.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_queue_resume_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_queue_resume.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_queue_resume_root_module.addImport(
        "virtio_net_queue_resume",
        virtio_net_queue_resume_module,
    );

    const virtio_net_transmit_recycle_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_transmit_recycle.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_transmit_recycle_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_transmit_recycle.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_transmit_recycle_root_module.addImport(
        "virtio_net_transmit_recycle",
        virtio_net_transmit_recycle_module,
    );

    const virtio_net_receive_refill_replay_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_receive_refill_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_receive_refill_replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_receive_refill_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_receive_refill_replay_root_module.addImport(
        "virtio_net_receive_refill_replay",
        virtio_net_receive_refill_replay_module,
    );

    const virtio_net_post_reset_replay_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_post_reset_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_post_reset_replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_post_reset_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_post_reset_replay_root_module.addImport(
        "virtio_net_post_reset_replay",
        virtio_net_post_reset_replay_module,
    );

    const virtio_net_throughput_parity_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_throughput_parity.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_throughput_parity_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_throughput_parity.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_throughput_parity_root_module.addImport(
        "virtio_net_throughput_parity",
        virtio_net_throughput_parity_module,
    );

    const virtio_net_survey_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase12_virtio_net_queue_resume_tests = b.addTest(.{
        .name = "phase12-virtio-net-queue-resume-tests",
        .root_module = virtio_net_queue_resume_root_module,
    });
    const run_virtio_net_queue_resume_tests = b.addRunArtifact(
        phase12_virtio_net_queue_resume_tests,
    );

    const phase12_virtio_net_transmit_recycle_tests = b.addTest(.{
        .name = "phase12-virtio-net-transmit-recycle-tests",
        .root_module = virtio_net_transmit_recycle_root_module,
    });
    const run_virtio_net_transmit_recycle_tests = b.addRunArtifact(
        phase12_virtio_net_transmit_recycle_tests,
    );

    const phase12_virtio_net_receive_refill_replay_tests = b.addTest(.{
        .name = "phase12-virtio-net-receive-refill-replay-tests",
        .root_module = virtio_net_receive_refill_replay_root_module,
    });
    const run_virtio_net_receive_refill_replay_tests = b.addRunArtifact(
        phase12_virtio_net_receive_refill_replay_tests,
    );

    const phase12_virtio_net_post_reset_replay_tests = b.addTest(.{
        .name = "phase12-virtio-net-post-reset-replay-tests",
        .root_module = virtio_net_post_reset_replay_root_module,
    });
    const run_virtio_net_post_reset_replay_tests = b.addRunArtifact(
        phase12_virtio_net_post_reset_replay_tests,
    );

    const phase12_virtio_net_throughput_parity_tests = b.addTest(.{
        .name = "phase12-virtio-net-throughput-parity-tests",
        .root_module = virtio_net_throughput_parity_root_module,
    });
    const run_virtio_net_throughput_parity_tests = b.addRunArtifact(
        phase12_virtio_net_throughput_parity_tests,
    );
    const throughput_parity_tests = run_virtio_net_throughput_parity_tests;

    const phase12_virtio_net_survey_tests = b.addTest(.{
        .name = "phase12-virtio-net-survey-tests",
        .root_module = virtio_net_survey_root_module,
    });
    const run_virtio_net_survey_tests = b.addRunArtifact(
        phase12_virtio_net_survey_tests,
    );

    const smoke_step = b.step(
        "smoke",
        "Run the Phase 12 virtio_net replay packet smoke tests",
    );
    smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);
    smoke_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);
    smoke_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);
    smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);
    smoke_step.dependOn(&run_virtio_net_survey_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 12 virtio_net replay packet tests",
    );
    test_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);
    test_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);
    test_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);
    test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);
    test_step.dependOn(&run_virtio_net_survey_tests.step);

    const throughput_parity_step = b.step(
        "phase12-virtio-net-throughput-parity",
        "Run the Phase 12 virtio_net throughput-parity replay in isolation",
    );
    throughput_parity_step.dependOn(&throughput_parity_tests.step);
}
