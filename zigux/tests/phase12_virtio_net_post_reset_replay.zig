const std = @import("std");
const post_reset_replay = @import("virtio_net_post_reset_replay");

test "phase12 virtio net post reset replay stays lab-only and fail-closed" {
    const blocked = try post_reset_replay.summarizePostResetReplay(.{
        .reset_generation = 9,
        .receive_queue_pairs = 4,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = false,
    });
    try std.testing.expectEqual(
        post_reset_replay.PostResetReplayBlocker.probe_snapshot_replay,
        blocked.blocker,
    );
    try std.testing.expectEqual(
        post_reset_replay.PostResetReplayCheckpoint.after_probe_snapshot_replay,
        blocked.next_checkpoint,
    );
    try std.testing.expect(!blocked.can_resume_queues);

    const ready = try post_reset_replay.summarizePostResetReplay(.{
        .reset_generation = 10,
        .receive_queue_pairs = 4,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });
    try std.testing.expectEqual(post_reset_replay.PostResetReplayBlocker.none, ready.blocker);
    try std.testing.expectEqual(
        post_reset_replay.PostResetReplayCheckpoint.queues_may_resume,
        ready.next_checkpoint,
    );
    try std.testing.expect(ready.replay_complete);
    try std.testing.expect(ready.can_resume_queues);
}

test "phase12 virtio net post reset replay keeps parked optional gates resumable" {
    const summary = try post_reset_replay.summarizePostResetReplay(.{
        .reset_generation = 11,
        .receive_queue_pairs = 2,
        .control_queue_restored = false,
        .receive_refill_replayed = false,
        .transmit_recycle_ready = false,
        .probe_snapshot_replayed = false,
        .requires_control_queue_restore = false,
        .requires_receive_refill_replay = false,
        .requires_transmit_recycle = false,
        .requires_probe_snapshot_replay = false,
    });

    try std.testing.expectEqual(post_reset_replay.PostResetReplayBlocker.none, summary.blocker);
    try std.testing.expectEqual(
        post_reset_replay.PostResetReplayCheckpoint.queues_may_resume,
        summary.next_checkpoint,
    );
    try std.testing.expect(!summary.requires_control_queue_restore);
    try std.testing.expect(!summary.requires_receive_refill_replay);
    try std.testing.expect(!summary.requires_transmit_recycle);
    try std.testing.expect(!summary.requires_probe_snapshot_replay);
    try std.testing.expect(summary.replay_complete);
    try std.testing.expect(summary.can_resume_queues);
}

test "phase12 virtio net post reset ownership splits receive and transmit ownership until replay fully clears" {
    const split = try post_reset_replay.summarizePostResetOwnership(.{
        .reset_generation = 12,
        .receive_queue_pairs = 4,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = false,
        .probe_snapshot_replayed = true,
    });

    try std.testing.expectEqual(
        post_reset_replay.PostResetReplayBlocker.transmit_recycle,
        split.blocker,
    );
    try std.testing.expectEqual(
        post_reset_replay.PostResetReplayCheckpoint.after_transmit_recycle,
        split.next_checkpoint,
    );
    try std.testing.expect(split.resumes_receive_submission);
    try std.testing.expect(!split.resumes_transmit_submission);
    try std.testing.expectEqual(
        post_reset_replay.QueueSubmissionOwner.driver,
        split.receive_submission_owner,
    );
    try std.testing.expectEqual(
        post_reset_replay.QueueSubmissionOwner.recovery,
        split.transmit_submission_owner,
    );
    try std.testing.expect(!split.queues_ready_for_driver_ownership);

    const parked = try post_reset_replay.summarizePostResetOwnership(.{
        .reset_generation = 13,
        .receive_queue_pairs = 4,
        .control_queue_restored = false,
        .receive_refill_replayed = false,
        .transmit_recycle_ready = false,
        .probe_snapshot_replayed = false,
        .requires_control_queue_restore = false,
        .requires_receive_refill_replay = false,
        .requires_transmit_recycle = false,
        .requires_probe_snapshot_replay = false,
    });

    try std.testing.expectEqual(post_reset_replay.PostResetReplayBlocker.none, parked.blocker);
    try std.testing.expectEqual(
        post_reset_replay.PostResetReplayCheckpoint.queues_may_resume,
        parked.next_checkpoint,
    );
    try std.testing.expect(parked.resumes_receive_submission);
    try std.testing.expect(parked.resumes_transmit_submission);
    try std.testing.expectEqual(
        post_reset_replay.QueueSubmissionOwner.driver,
        parked.receive_submission_owner,
    );
    try std.testing.expectEqual(
        post_reset_replay.QueueSubmissionOwner.driver,
        parked.transmit_submission_owner,
    );
    try std.testing.expect(parked.queues_ready_for_driver_ownership);
}
