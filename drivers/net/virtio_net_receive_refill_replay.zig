const std = @import("std");

pub const ReceiveRefillReplayBlocker = enum {
    none,
    control_queue_restore,
    queue_pair_restore,
    refill_budget_restore,
    descriptor_repost,
};

pub const ReceiveRefillReplayRequest = struct {
    reset_generation: u32,
    receive_queue_pairs_before_reset: u16,
    receive_queue_pairs_after_restore: u16,
    receive_buffers_before_reset: u16,
    receive_buffers_after_restore: u16,
    descriptors_posted_after_restore: u16,
    control_queue_restored: bool,
    requires_control_queue_restore: bool = true,
};

pub const ReceiveRefillReplaySummary = struct {
    anchor: []const u8,
    reset_generation: u32,
    receive_queue_pairs_before_reset: u16,
    receive_queue_pairs_after_restore: u16,
    receive_buffers_before_reset: u16,
    receive_buffers_after_restore: u16,
    missing_receive_buffers_after_restore: u16,
    descriptors_posted_after_restore: u16,
    descriptors_pending_repost: u16,
    control_queue_restored: bool,
    requires_control_queue_restore: bool,
    queue_pairs_preserved: bool,
    refill_budget_preserved: bool,
    descriptors_reposted: bool,
    blocker: ReceiveRefillReplayBlocker,
    replay_ready: bool,
};

pub fn summarizeReceiveRefillReplay(
    request: ReceiveRefillReplayRequest,
) !ReceiveRefillReplaySummary {
    if (request.receive_queue_pairs_before_reset == 0) {
        return error.QueuePairsBeforeResetMissing;
    }
    if (request.receive_buffers_before_reset == 0) {
        return error.ReceiveBuffersBeforeResetMissing;
    }

    const queue_pairs_preserved =
        request.receive_queue_pairs_after_restore >= request.receive_queue_pairs_before_reset;
    const missing_receive_buffers_after_restore =
        request.receive_buffers_before_reset -
        @min(request.receive_buffers_after_restore, request.receive_buffers_before_reset);
    const descriptors_pending_repost =
        request.receive_buffers_after_restore -
        @min(request.descriptors_posted_after_restore, request.receive_buffers_after_restore);
    const refill_budget_preserved = missing_receive_buffers_after_restore == 0;
    const descriptors_reposted = descriptors_pending_repost == 0;

    const blocker: ReceiveRefillReplayBlocker = blk: {
        if (request.requires_control_queue_restore and !request.control_queue_restored) {
            break :blk .control_queue_restore;
        }
        if (!queue_pairs_preserved) break :blk .queue_pair_restore;
        if (!refill_budget_preserved) break :blk .refill_budget_restore;
        if (!descriptors_reposted) break :blk .descriptor_repost;
        break :blk .none;
    };

    return .{
        .anchor = "drivers/net/virtio_net.c",
        .reset_generation = request.reset_generation,
        .receive_queue_pairs_before_reset = request.receive_queue_pairs_before_reset,
        .receive_queue_pairs_after_restore = request.receive_queue_pairs_after_restore,
        .receive_buffers_before_reset = request.receive_buffers_before_reset,
        .receive_buffers_after_restore = request.receive_buffers_after_restore,
        .missing_receive_buffers_after_restore = missing_receive_buffers_after_restore,
        .descriptors_posted_after_restore = request.descriptors_posted_after_restore,
        .descriptors_pending_repost = descriptors_pending_repost,
        .control_queue_restored = request.control_queue_restored,
        .requires_control_queue_restore = request.requires_control_queue_restore,
        .queue_pairs_preserved = queue_pairs_preserved,
        .refill_budget_preserved = refill_budget_preserved,
        .descriptors_reposted = descriptors_reposted,
        .blocker = blocker,
        .replay_ready = blocker == .none,
    };
}

test "receive refill replay rejects missing pre-reset queue pairs" {
    try std.testing.expectError(error.QueuePairsBeforeResetMissing, summarizeReceiveRefillReplay(.{
        .reset_generation = 1,
        .receive_queue_pairs_before_reset = 0,
        .receive_queue_pairs_after_restore = 0,
        .receive_buffers_before_reset = 64,
        .receive_buffers_after_restore = 64,
        .descriptors_posted_after_restore = 64,
        .control_queue_restored = true,
    }));
}

test "receive refill replay rejects missing pre-reset receive buffers" {
    try std.testing.expectError(
        error.ReceiveBuffersBeforeResetMissing,
        summarizeReceiveRefillReplay(.{
            .reset_generation = 1,
            .receive_queue_pairs_before_reset = 1,
            .receive_queue_pairs_after_restore = 1,
            .receive_buffers_before_reset = 0,
            .receive_buffers_after_restore = 0,
            .descriptors_posted_after_restore = 0,
            .control_queue_restored = true,
        }),
    );
}

test "receive refill replay keeps control queue restore ahead of later refill work" {
    const summary = try summarizeReceiveRefillReplay(.{
        .reset_generation = 2,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .descriptors_posted_after_restore = 128,
        .control_queue_restored = false,
    });

    try std.testing.expectEqual(
        ReceiveRefillReplayBlocker.control_queue_restore,
        summary.blocker,
    );
    try std.testing.expectEqual(@as(u16, 0), summary.missing_receive_buffers_after_restore);
    try std.testing.expectEqual(@as(u16, 0), summary.descriptors_pending_repost);
    try std.testing.expect(!summary.replay_ready);
}

test "receive refill replay skips control queue restore when the packet says no control queue is present" {
    const summary = try summarizeReceiveRefillReplay(.{
        .reset_generation = 2,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .descriptors_posted_after_restore = 128,
        .control_queue_restored = false,
        .requires_control_queue_restore = false,
    });

    try std.testing.expect(!summary.requires_control_queue_restore);
    try std.testing.expect(summary.queue_pairs_preserved);
    try std.testing.expect(summary.refill_budget_preserved);
    try std.testing.expect(summary.descriptors_reposted);
    try std.testing.expectEqual(@as(u16, 0), summary.missing_receive_buffers_after_restore);
    try std.testing.expectEqual(@as(u16, 0), summary.descriptors_pending_repost);
    try std.testing.expectEqual(ReceiveRefillReplayBlocker.none, summary.blocker);
    try std.testing.expect(summary.replay_ready);
}

test "receive refill replay requires queue-pair restore before budget replay" {
    const summary = try summarizeReceiveRefillReplay(.{
        .reset_generation = 3,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 1,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .descriptors_posted_after_restore = 128,
        .control_queue_restored = true,
    });

    try std.testing.expectEqual(
        ReceiveRefillReplayBlocker.queue_pair_restore,
        summary.blocker,
    );
    try std.testing.expect(!summary.queue_pairs_preserved);
    try std.testing.expect(summary.refill_budget_preserved);
    try std.testing.expectEqual(@as(u16, 0), summary.missing_receive_buffers_after_restore);
}

test "receive refill replay keeps refill budget restoration explicit" {
    const summary = try summarizeReceiveRefillReplay(.{
        .reset_generation = 4,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 96,
        .descriptors_posted_after_restore = 96,
        .control_queue_restored = true,
    });

    try std.testing.expectEqual(
        ReceiveRefillReplayBlocker.refill_budget_restore,
        summary.blocker,
    );
    try std.testing.expect(summary.queue_pairs_preserved);
    try std.testing.expect(!summary.refill_budget_preserved);
    try std.testing.expectEqual(@as(u16, 32), summary.missing_receive_buffers_after_restore);
    try std.testing.expectEqual(@as(u16, 0), summary.descriptors_pending_repost);
}

test "receive refill replay keeps descriptor repost explicit after the refill budget is restored" {
    const summary = try summarizeReceiveRefillReplay(.{
        .reset_generation = 5,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .descriptors_posted_after_restore = 96,
        .control_queue_restored = true,
    });

    try std.testing.expectEqual(
        ReceiveRefillReplayBlocker.descriptor_repost,
        summary.blocker,
    );
    try std.testing.expect(summary.refill_budget_preserved);
    try std.testing.expect(!summary.descriptors_reposted);
    try std.testing.expectEqual(@as(u16, 0), summary.missing_receive_buffers_after_restore);
    try std.testing.expectEqual(@as(u16, 32), summary.descriptors_pending_repost);
    try std.testing.expect(!summary.replay_ready);
}

test "receive refill replay clears once queue pairs buffers and reposted descriptors are restored" {
    const summary = try summarizeReceiveRefillReplay(.{
        .reset_generation = 6,
        .receive_queue_pairs_before_reset = 4,
        .receive_queue_pairs_after_restore = 4,
        .receive_buffers_before_reset = 256,
        .receive_buffers_after_restore = 256,
        .descriptors_posted_after_restore = 256,
        .control_queue_restored = true,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(ReceiveRefillReplayBlocker.none, summary.blocker);
    try std.testing.expect(summary.queue_pairs_preserved);
    try std.testing.expect(summary.refill_budget_preserved);
    try std.testing.expect(summary.descriptors_reposted);
    try std.testing.expectEqual(@as(u16, 0), summary.missing_receive_buffers_after_restore);
    try std.testing.expectEqual(@as(u16, 0), summary.descriptors_pending_repost);
    try std.testing.expect(summary.replay_ready);
}
