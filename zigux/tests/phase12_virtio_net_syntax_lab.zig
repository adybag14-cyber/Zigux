const std = @import("std");
const virtio = @import("virtio");
const queue_resume = @import("virtio_net_queue_resume");
const receive_refill_replay = @import("virtio_net_receive_refill_replay");
const transmit_recycle = @import("virtio_net_transmit_recycle");
const post_reset_replay = @import("virtio_net_post_reset_replay");
const throughput_parity = @import("virtio_net_throughput_parity");

const CompileSmokeEnvelope = struct {
    queue_registration_ready: bool,
    queue_resume_ready: bool,
    refill_replay_ready: bool,
    post_reset_driver_ready: bool,
    throughput_ready: bool,
    runtime_execution_claimed: bool,
};

test "phase12 virtio net syntax lab keeps refill replay ahead of queue resume" {
    var core = try virtio.VirtioCoreLab.init(0x1041, 4);
    core.setStatusBits(virtio.status_acknowledge | virtio.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(1);

    const lifecycle = core.lifecycleGuardSummary();
    const refill = try receive_refill_replay.summarizeReceiveRefillReplay(.{
        .reset_generation = 11,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 96,
        .descriptors_posted_after_restore = 96,
        .control_queue_restored = true,
    });
    const queue_resume_summary = try queue_resume.summarizeQueueResume(.{
        .reset_generation = 11,
        .receive_queue_pairs = 2,
        .refill_replay_ready = refill.replay_ready,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });
    const envelope = CompileSmokeEnvelope{
        .queue_registration_ready = lifecycle.queue_registration_ready,
        .queue_resume_ready = queue_resume_summary.can_resume_queues,
        .refill_replay_ready = refill.replay_ready,
        .post_reset_driver_ready = false,
        .throughput_ready = false,
        .runtime_execution_claimed = false,
    };

    try std.testing.expect(lifecycle.queue_registration_ready);
    try std.testing.expectEqual(
        receive_refill_replay.ReceiveRefillReplayBlocker.refill_budget_restore,
        refill.blocker,
    );
    try std.testing.expectEqual(
        queue_resume.QueueResumeBlocker.refill_replay,
        queue_resume_summary.blocker,
    );
    try std.testing.expect(!envelope.queue_resume_ready);
    try std.testing.expect(!envelope.runtime_execution_claimed);
}

test "phase12 virtio net syntax lab keeps transmit recycle and post-reset ownership review-only" {
    const recycle = try transmit_recycle.summarizeTransmitRecycle(.{
        .in_flight_descriptors = 5,
        .free_descriptors_before = 1,
        .completed_descriptors = 2,
        .queue_stopped = true,
    });
    const ownership = try post_reset_replay.summarizePostResetOwnership(.{
        .reset_generation = 12,
        .receive_queue_pairs = 2,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = recycle.returns_completed_ownership_to_driver,
        .probe_snapshot_replayed = false,
    });
    const envelope = CompileSmokeEnvelope{
        .queue_registration_ready = false,
        .queue_resume_ready = false,
        .refill_replay_ready = true,
        .post_reset_driver_ready = ownership.queues_ready_for_driver_ownership,
        .throughput_ready = false,
        .runtime_execution_claimed = false,
    };

    try std.testing.expectEqual(
        transmit_recycle.RecycleDisposition.wake_queue,
        recycle.disposition,
    );
    try std.testing.expect(recycle.wakes_transmit_queue);
    try std.testing.expectEqual(
        post_reset_replay.PostResetReplayBlocker.probe_snapshot_replay,
        ownership.blocker,
    );
    try std.testing.expectEqual(
        post_reset_replay.QueueSubmissionOwner.recovery,
        ownership.receive_submission_owner,
    );
    try std.testing.expect(!envelope.post_reset_driver_ready);
    try std.testing.expect(!envelope.runtime_execution_claimed);
}

test "phase12 virtio net syntax lab keeps throughput parity in compile-smoke territory" {
    const queue_resume_summary = try queue_resume.summarizeQueueResume(.{
        .reset_generation = 13,
        .receive_queue_pairs = 4,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });
    const replay = try post_reset_replay.summarizePostResetReplay(.{
        .reset_generation = 13,
        .receive_queue_pairs = 4,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });
    const parity = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 4,
        .queue_pairs_after_restore = 4,
        .receive_buffers_before_reset = 256,
        .receive_buffers_after_restore = 256,
        .receive_descriptors_reposted = true,
        .recycled_transmit_descriptors = 2,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_transmit_queue_restore,
        .expected_min_ratio_pct = 90,
    });
    const envelope = CompileSmokeEnvelope{
        .queue_registration_ready = true,
        .queue_resume_ready = queue_resume_summary.can_resume_queues,
        .refill_replay_ready = true,
        .post_reset_driver_ready = replay.can_resume_queues,
        .throughput_ready = parity.status == .parity_gate_ready,
        .runtime_execution_claimed = false,
    };

    try std.testing.expectEqual(
        queue_resume.QueueResumeBlocker.none,
        queue_resume_summary.blocker,
    );
    try std.testing.expect(replay.can_resume_queues);
    try std.testing.expectEqual(
        throughput_parity.ThroughputParityStatus.parity_gate_ready,
        parity.status,
    );
    try std.testing.expect(parity.meets_expected_min_ratio);
    try std.testing.expect(envelope.throughput_ready);
    try std.testing.expect(!envelope.runtime_execution_claimed);
}

test "phase12 virtio net syntax lab keeps no-control-queue recovery in compile-smoke review territory" {
    var core = try virtio.VirtioCoreLab.init(0x1041, 2);
    core.setStatusBits(virtio.status_acknowledge | virtio.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(0);

    const lifecycle = core.lifecycleGuardSummary();
    const refill = try receive_refill_replay.summarizeReceiveRefillReplay(.{
        .reset_generation = 14,
        .receive_queue_pairs_before_reset = 1,
        .receive_queue_pairs_after_restore = 1,
        .receive_buffers_before_reset = 64,
        .receive_buffers_after_restore = 64,
        .descriptors_posted_after_restore = 64,
        .control_queue_restored = false,
        .requires_control_queue_restore = false,
    });
    const queue_resume_summary = try queue_resume.summarizeQueueResume(.{
        .reset_generation = 14,
        .receive_queue_pairs = 1,
        .refill_replay_ready = refill.replay_ready,
        .control_queue_restored = false,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = false,
        .requires_control_queue_restore = false,
    });
    const ownership = try post_reset_replay.summarizePostResetOwnership(.{
        .reset_generation = 14,
        .receive_queue_pairs = 1,
        .control_queue_restored = false,
        .receive_refill_replayed = refill.replay_ready,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = false,
        .requires_control_queue_restore = false,
    });
    const parity = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 1,
        .queue_pairs_after_restore = 1,
        .receive_buffers_before_reset = 64,
        .receive_buffers_after_restore = 64,
        .receive_descriptors_reposted = true,
        .recycled_transmit_descriptors = 0,
        .transmit_queue_was_stopped = false,
        .replay_checkpoint = .after_receive_refill,
        .requires_control_queue_restore = false,
    });
    const envelope = CompileSmokeEnvelope{
        .queue_registration_ready = lifecycle.queue_registration_ready,
        .queue_resume_ready = queue_resume_summary.can_resume_queues,
        .refill_replay_ready = refill.replay_ready,
        .post_reset_driver_ready = ownership.queues_ready_for_driver_ownership,
        .throughput_ready = parity.status == .parity_gate_ready,
        .runtime_execution_claimed = false,
    };

    try std.testing.expect(lifecycle.queue_registration_ready);
    try std.testing.expectEqual(
        receive_refill_replay.ReceiveRefillReplayBlocker.none,
        refill.blocker,
    );
    try std.testing.expect(refill.replay_ready);
    try std.testing.expectEqual(
        queue_resume.QueueResumeBlocker.probe_snapshot_replay,
        queue_resume_summary.blocker,
    );
    try std.testing.expect(!queue_resume_summary.requires_control_queue_restore);
    try std.testing.expect(!queue_resume_summary.can_resume_queues);
    try std.testing.expectEqual(
        post_reset_replay.PostResetReplayBlocker.probe_snapshot_replay,
        ownership.blocker,
    );
    try std.testing.expectEqual(
        post_reset_replay.QueueSubmissionOwner.recovery,
        ownership.receive_submission_owner,
    );
    try std.testing.expectEqual(
        post_reset_replay.QueueSubmissionOwner.recovery,
        ownership.transmit_submission_owner,
    );
    try std.testing.expectEqual(
        throughput_parity.ThroughputParityStatus.needs_post_reset_probe_replay,
        parity.status,
    );
    try std.testing.expect(!parity.requires_control_queue_restore);
    try std.testing.expect(parity.control_queue_restore_ready);
    try std.testing.expect(parity.receive_refill_ready);
    try std.testing.expect(parity.transmit_recycle_ready);
    try std.testing.expect(parity.requires_post_reset_probe_replay);
    try std.testing.expect(!envelope.queue_resume_ready);
    try std.testing.expect(!envelope.post_reset_driver_ready);
    try std.testing.expect(!envelope.throughput_ready);
    try std.testing.expect(!envelope.runtime_execution_claimed);
}
