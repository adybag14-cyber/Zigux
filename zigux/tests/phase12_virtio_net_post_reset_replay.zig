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
