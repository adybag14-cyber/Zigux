const std = @import("std");

pub const default_wake_threshold: u16 = 2;

pub const PostResetProbeReplayCheckpoint = enum {
    before_receive_refill,
    after_receive_refill,
    after_control_queue_restore,
    after_transmit_queue_restore,
};

pub const ThroughputParityStatus = enum {
    needs_queue_restore,
    needs_receive_refill,
    needs_transmit_recycle,
    needs_post_reset_probe_replay,
    parity_gate_ready,
};

pub const ThroughputParityRequest = struct {
    queue_pairs_before_reset: u16,
    queue_pairs_after_restore: u16,
    receive_buffers_before_reset: u16,
    receive_buffers_after_restore: u16,
    recycled_transmit_descriptors: u16,
    wake_threshold: u16 = default_wake_threshold,
    transmit_queue_was_stopped: bool = false,
    replay_checkpoint: PostResetProbeReplayCheckpoint = .after_transmit_queue_restore,
    expected_min_ratio_pct: u8 = 90,
};

pub const ThroughputParitySummary = struct {
    anchor: []const u8,
    queue_pairs_before_reset: u16,
    queue_pairs_after_restore: u16,
    receive_buffers_before_reset: u16,
    receive_buffers_after_restore: u16,
    recycled_transmit_descriptors: u16,
    wake_threshold: u16,
    transmit_queue_was_stopped: bool,
    replay_checkpoint: PostResetProbeReplayCheckpoint,
    queue_pair_ratio_pct: u8,
    refill_ratio_pct: u8,
    recycle_ratio_pct: u8,
    throughput_ratio_pct: u8,
    queue_pairs_preserved: bool,
    refill_budget_preserved: bool,
    recycle_budget_ready: bool,
    requires_post_reset_probe_replay: bool,
    meets_expected_min_ratio: bool,
    status: ThroughputParityStatus,
};

pub fn summarizeThroughputParity(request: ThroughputParityRequest) !ThroughputParitySummary {
    if (request.queue_pairs_before_reset == 0) return error.QueuePairsBeforeResetMissing;
    if (request.receive_buffers_before_reset == 0) return error.ReceiveBuffersBeforeResetMissing;
    if (request.expected_min_ratio_pct > 100) return error.ExpectedRatioOutOfRange;

    const queue_pair_ratio_pct = ratioPct(
        request.queue_pairs_after_restore,
        request.queue_pairs_before_reset,
    );
    const refill_ratio_pct = ratioPct(
        request.receive_buffers_after_restore,
        request.receive_buffers_before_reset,
    );
    const recycle_ratio_pct = recycleRatioPct(
        request.recycled_transmit_descriptors,
        request.wake_threshold,
        request.transmit_queue_was_stopped,
    );

    const throughput_ratio_pct = min3(queue_pair_ratio_pct, refill_ratio_pct, recycle_ratio_pct);
    const queue_pairs_preserved = request.queue_pairs_after_restore >= request.queue_pairs_before_reset;
    const refill_budget_preserved = request.receive_buffers_after_restore >= request.receive_buffers_before_reset;
    const recycle_budget_ready = !request.transmit_queue_was_stopped or
        request.recycled_transmit_descriptors >= request.wake_threshold;
    const requires_post_reset_probe_replay = switch (request.replay_checkpoint) {
        .after_transmit_queue_restore => false,
        .after_control_queue_restore => request.transmit_queue_was_stopped,
        .after_receive_refill, .before_receive_refill => true,
    };

    const status: ThroughputParityStatus = if (!queue_pairs_preserved)
        .needs_queue_restore
    else if (!refill_budget_preserved)
        .needs_receive_refill
    else if (!recycle_budget_ready)
        .needs_transmit_recycle
    else if (requires_post_reset_probe_replay)
        .needs_post_reset_probe_replay
    else
        .parity_gate_ready;

    return .{
        .anchor = "drivers/net/virtio_net.c",
        .queue_pairs_before_reset = request.queue_pairs_before_reset,
        .queue_pairs_after_restore = request.queue_pairs_after_restore,
        .receive_buffers_before_reset = request.receive_buffers_before_reset,
        .receive_buffers_after_restore = request.receive_buffers_after_restore,
        .recycled_transmit_descriptors = request.recycled_transmit_descriptors,
        .wake_threshold = request.wake_threshold,
        .transmit_queue_was_stopped = request.transmit_queue_was_stopped,
        .replay_checkpoint = request.replay_checkpoint,
        .queue_pair_ratio_pct = queue_pair_ratio_pct,
        .refill_ratio_pct = refill_ratio_pct,
        .recycle_ratio_pct = recycle_ratio_pct,
        .throughput_ratio_pct = throughput_ratio_pct,
        .queue_pairs_preserved = queue_pairs_preserved,
        .refill_budget_preserved = refill_budget_preserved,
        .recycle_budget_ready = recycle_budget_ready,
        .requires_post_reset_probe_replay = requires_post_reset_probe_replay,
        .meets_expected_min_ratio = status == .parity_gate_ready and
            throughput_ratio_pct >= request.expected_min_ratio_pct,
        .status = status,
    };
}

fn ratioPct(numerator: u16, denominator: u16) u8 {
    const pct = (@as(u32, numerator) * 100) / denominator;
    return @intCast(@min(pct, 100));
}

fn recycleRatioPct(recycled: u16, wake_threshold: u16, queue_was_stopped: bool) u8 {
    if (!queue_was_stopped) return 100;
    if (wake_threshold == 0) return 100;
    return ratioPct(recycled, wake_threshold);
}

fn min3(lhs: u8, mid: u8, rhs: u8) u8 {
    return @min(lhs, @min(mid, rhs));
}

test "summarizeThroughputParity passes once queue restore refill recycle and replay align" {
    const summary = try summarizeThroughputParity(.{
        .queue_pairs_before_reset = 4,
        .queue_pairs_after_restore = 4,
        .receive_buffers_before_reset = 512,
        .receive_buffers_after_restore = 512,
        .recycled_transmit_descriptors = 4,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_transmit_queue_restore,
        .expected_min_ratio_pct = 90,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(ThroughputParityStatus.parity_gate_ready, summary.status);
    try std.testing.expectEqual(@as(u8, 100), summary.throughput_ratio_pct);
    try std.testing.expect(summary.recycle_budget_ready);
    try std.testing.expect(summary.meets_expected_min_ratio);
    try std.testing.expect(!summary.requires_post_reset_probe_replay);
}

test "summarizeThroughputParity blocks stopped transmit queues below the wake threshold" {
    const summary = try summarizeThroughputParity(.{
        .queue_pairs_before_reset = 2,
        .queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 256,
        .receive_buffers_after_restore = 256,
        .recycled_transmit_descriptors = 1,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_control_queue_restore,
    });

    try std.testing.expectEqual(ThroughputParityStatus.needs_transmit_recycle, summary.status);
    try std.testing.expectEqual(@as(u8, 50), summary.recycle_ratio_pct);
    try std.testing.expectEqual(@as(u8, 50), summary.throughput_ratio_pct);
    try std.testing.expect(!summary.recycle_budget_ready);
    try std.testing.expect(!summary.meets_expected_min_ratio);
}

test "summarizeThroughputParity keeps post reset replay explicit when restore stops after refill" {
    const summary = try summarizeThroughputParity(.{
        .queue_pairs_before_reset = 1,
        .queue_pairs_after_restore = 1,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .recycled_transmit_descriptors = 2,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_receive_refill,
    });

    try std.testing.expectEqual(ThroughputParityStatus.needs_post_reset_probe_replay, summary.status);
    try std.testing.expect(summary.requires_post_reset_probe_replay);
    try std.testing.expectEqual(@as(u8, 100), summary.throughput_ratio_pct);
}
