const std = @import("std");
const receive_refill_replay = @import("virtio_net_receive_refill_replay");

test "phase12 virtio net receive refill replay stays lab-only and fail-closed" {
    const blocked = try receive_refill_replay.summarizeReceiveRefillReplay(.{
        .reset_generation = 11,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .descriptors_posted_after_restore = 96,
        .control_queue_restored = true,
    });
    try std.testing.expectEqual(
        receive_refill_replay.ReceiveRefillReplayBlocker.descriptor_repost,
        blocked.blocker,
    );
    try std.testing.expectEqual(@as(u16, 0), blocked.missing_receive_buffers_after_restore);
    try std.testing.expectEqual(@as(u16, 32), blocked.descriptors_pending_repost);
    try std.testing.expect(!blocked.replay_ready);

    const ready = try receive_refill_replay.summarizeReceiveRefillReplay(.{
        .reset_generation = 12,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .descriptors_posted_after_restore = 128,
        .control_queue_restored = true,
    });
    try std.testing.expectEqual(
        receive_refill_replay.ReceiveRefillReplayBlocker.none,
        ready.blocker,
    );
    try std.testing.expect(ready.queue_pairs_preserved);
    try std.testing.expect(ready.refill_budget_preserved);
    try std.testing.expect(ready.descriptors_reposted);
    try std.testing.expectEqual(@as(u16, 0), ready.missing_receive_buffers_after_restore);
    try std.testing.expectEqual(@as(u16, 0), ready.descriptors_pending_repost);
    try std.testing.expect(ready.replay_ready);
}

test "phase12 virtio net receive refill replay reports refill shortfall before descriptor backlog" {
    const summary = try receive_refill_replay.summarizeReceiveRefillReplay(.{
        .reset_generation = 13,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 96,
        .descriptors_posted_after_restore = 80,
        .control_queue_restored = true,
    });

    try std.testing.expectEqual(
        receive_refill_replay.ReceiveRefillReplayBlocker.refill_budget_restore,
        summary.blocker,
    );
    try std.testing.expectEqual(@as(u16, 32), summary.missing_receive_buffers_after_restore);
    try std.testing.expectEqual(@as(u16, 16), summary.descriptors_pending_repost);
    try std.testing.expect(!summary.refill_budget_preserved);
    try std.testing.expect(!summary.descriptors_reposted);
    try std.testing.expect(!summary.replay_ready);
}

test "phase12 virtio net receive refill replay supports queue-less control-path packets" {
    const ready = try receive_refill_replay.summarizeReceiveRefillReplay(.{
        .reset_generation = 14,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .descriptors_posted_after_restore = 128,
        .control_queue_restored = false,
        .requires_control_queue_restore = false,
    });

    try std.testing.expect(!ready.requires_control_queue_restore);
    try std.testing.expectEqual(
        receive_refill_replay.ReceiveRefillReplayBlocker.none,
        ready.blocker,
    );
    try std.testing.expect(ready.queue_pairs_preserved);
    try std.testing.expect(ready.refill_budget_preserved);
    try std.testing.expect(ready.descriptors_reposted);
    try std.testing.expectEqual(@as(u16, 0), ready.missing_receive_buffers_after_restore);
    try std.testing.expectEqual(@as(u16, 0), ready.descriptors_pending_repost);
    try std.testing.expect(ready.replay_ready);
}
