const std = @import("std");
const throughput_parity = @import("virtio_net_throughput_parity");

test "phase12 throughput parity gate passes once queue restore refill recycle and replay align" {
    const summary = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 4,
        .queue_pairs_after_restore = 4,
        .receive_buffers_before_reset = 512,
        .receive_buffers_after_restore = 512,
        .receive_descriptors_reposted = true,
        .recycled_transmit_descriptors = 4,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_transmit_queue_restore,
        .expected_min_ratio_pct = 90,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(throughput_parity.ThroughputParityStatus.parity_gate_ready, summary.status);
    try std.testing.expectEqual(@as(u8, 100), summary.throughput_ratio_pct);
    try std.testing.expect(summary.control_queue_restore_ready);
    try std.testing.expect(summary.receive_descriptors_reposted);
    try std.testing.expect(summary.recycle_budget_ready);
    try std.testing.expect(summary.receive_refill_checkpoint_ready);
    try std.testing.expect(summary.receive_refill_ready);
    try std.testing.expect(summary.transmit_recycle_checkpoint_ready);
    try std.testing.expect(summary.transmit_recycle_ready);
    try std.testing.expect(summary.meets_expected_min_ratio);
    try std.testing.expect(!summary.requires_post_reset_probe_replay);
}

test "phase12 throughput parity gate keeps queue restore explicit when queue pairs drop after reset" {
    const summary = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 4,
        .queue_pairs_after_restore = 3,
        .receive_buffers_before_reset = 512,
        .receive_buffers_after_restore = 512,
        .receive_descriptors_reposted = true,
        .recycled_transmit_descriptors = 4,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_transmit_queue_restore,
        .expected_min_ratio_pct = 90,
    });

    try std.testing.expectEqual(throughput_parity.ThroughputParityStatus.needs_queue_restore, summary.status);
    try std.testing.expect(!summary.queue_pairs_preserved);
    try std.testing.expect(summary.control_queue_restore_ready);
    try std.testing.expect(summary.refill_budget_preserved);
    try std.testing.expect(summary.recycle_budget_ready);
    try std.testing.expectEqual(@as(u8, 75), summary.queue_pair_ratio_pct);
    try std.testing.expectEqual(@as(u8, 75), summary.throughput_ratio_pct);
    try std.testing.expect(!summary.meets_expected_min_ratio);
}

test "phase12 throughput parity gate keeps control queue restore explicit before receive refill begins" {
    const summary = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 2,
        .queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 256,
        .receive_buffers_after_restore = 256,
        .receive_descriptors_reposted = true,
        .recycled_transmit_descriptors = 0,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = false,
        .replay_checkpoint = .before_receive_refill,
        .expected_min_ratio_pct = 100,
    });

    try std.testing.expectEqual(throughput_parity.ThroughputParityStatus.needs_control_queue_restore, summary.status);
    try std.testing.expect(summary.requires_control_queue_restore);
    try std.testing.expect(!summary.control_queue_restore_ready);
    try std.testing.expect(!summary.receive_refill_checkpoint_ready);
    try std.testing.expect(!summary.receive_refill_ready);
    try std.testing.expect(!summary.transmit_recycle_checkpoint_ready);
    try std.testing.expect(!summary.transmit_recycle_ready);
    try std.testing.expect(summary.recycle_budget_ready);
    try std.testing.expect(summary.requires_post_reset_probe_replay);
    try std.testing.expectEqual(@as(u8, 100), summary.recycle_ratio_pct);
    try std.testing.expectEqual(@as(u8, 100), summary.throughput_ratio_pct);
    try std.testing.expect(!summary.meets_expected_min_ratio);
}

test "phase12 throughput parity gate skips control queue restore when the device has no control queue" {
    const summary = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 2,
        .queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 256,
        .receive_buffers_after_restore = 256,
        .receive_descriptors_reposted = true,
        .recycled_transmit_descriptors = 0,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = false,
        .replay_checkpoint = .before_receive_refill,
        .requires_control_queue_restore = false,
        .expected_min_ratio_pct = 100,
    });

    try std.testing.expectEqual(throughput_parity.ThroughputParityStatus.needs_receive_refill, summary.status);
    try std.testing.expect(!summary.requires_control_queue_restore);
    try std.testing.expect(summary.control_queue_restore_ready);
    try std.testing.expect(!summary.receive_refill_checkpoint_ready);
    try std.testing.expect(!summary.receive_refill_ready);
    try std.testing.expect(!summary.transmit_recycle_checkpoint_ready);
    try std.testing.expect(!summary.transmit_recycle_ready);
    try std.testing.expect(summary.recycle_budget_ready);
    try std.testing.expect(summary.requires_post_reset_probe_replay);
    try std.testing.expectEqual(@as(u8, 100), summary.recycle_ratio_pct);
    try std.testing.expectEqual(@as(u8, 100), summary.throughput_ratio_pct);
    try std.testing.expect(!summary.meets_expected_min_ratio);
}

test "phase12 throughput parity gate keeps descriptor repost explicit after refill counts return" {
    const summary = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 2,
        .queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 256,
        .receive_buffers_after_restore = 256,
        .receive_descriptors_reposted = false,
        .recycled_transmit_descriptors = 2,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_transmit_queue_restore,
        .expected_min_ratio_pct = 100,
    });

    try std.testing.expectEqual(throughput_parity.ThroughputParityStatus.needs_receive_refill, summary.status);
    try std.testing.expect(summary.control_queue_restore_ready);
    try std.testing.expect(summary.receive_refill_checkpoint_ready);
    try std.testing.expect(!summary.receive_refill_ready);
    try std.testing.expect(summary.transmit_recycle_checkpoint_ready);
    try std.testing.expect(summary.transmit_recycle_ready);
    try std.testing.expect(!summary.receive_descriptors_reposted);
    try std.testing.expectEqual(@as(u8, 100), summary.refill_ratio_pct);
    try std.testing.expectEqual(@as(u8, 100), summary.throughput_ratio_pct);
    try std.testing.expect(!summary.meets_expected_min_ratio);
    try std.testing.expect(!summary.requires_post_reset_probe_replay);
}

test "phase12 throughput parity gate keeps refill budget explicit when restored buffers shrink" {
    const summary = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 2,
        .queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 256,
        .receive_buffers_after_restore = 192,
        .receive_descriptors_reposted = true,
        .recycled_transmit_descriptors = 2,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_transmit_queue_restore,
        .expected_min_ratio_pct = 90,
    });

    try std.testing.expectEqual(throughput_parity.ThroughputParityStatus.needs_receive_refill, summary.status);
    try std.testing.expect(summary.queue_pairs_preserved);
    try std.testing.expect(summary.control_queue_restore_ready);
    try std.testing.expect(!summary.refill_budget_preserved);
    try std.testing.expect(summary.receive_refill_checkpoint_ready);
    try std.testing.expect(!summary.receive_refill_ready);
    try std.testing.expect(summary.transmit_recycle_checkpoint_ready);
    try std.testing.expect(summary.transmit_recycle_ready);
    try std.testing.expectEqual(@as(u8, 75), summary.refill_ratio_pct);
    try std.testing.expectEqual(@as(u8, 75), summary.throughput_ratio_pct);
    try std.testing.expect(!summary.meets_expected_min_ratio);
}

test "phase12 throughput parity gate blocks stopped transmit queues below the wake threshold" {
    const summary = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 2,
        .queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 256,
        .receive_buffers_after_restore = 256,
        .receive_descriptors_reposted = true,
        .recycled_transmit_descriptors = 1,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_transmit_queue_restore,
    });

    try std.testing.expectEqual(throughput_parity.ThroughputParityStatus.needs_transmit_recycle, summary.status);
    try std.testing.expect(summary.control_queue_restore_ready);
    try std.testing.expect(summary.receive_refill_checkpoint_ready);
    try std.testing.expect(summary.receive_refill_ready);
    try std.testing.expect(summary.transmit_recycle_checkpoint_ready);
    try std.testing.expect(!summary.transmit_recycle_ready);
    try std.testing.expectEqual(@as(u8, 50), summary.recycle_ratio_pct);
    try std.testing.expectEqual(@as(u8, 50), summary.throughput_ratio_pct);
    try std.testing.expect(!summary.recycle_budget_ready);
    try std.testing.expect(!summary.meets_expected_min_ratio);
}

test "phase12 throughput parity gate keeps receive refill explicit after control queue restore even when descriptors are already reposted" {
    const summary = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 2,
        .queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 256,
        .receive_buffers_after_restore = 256,
        .receive_descriptors_reposted = true,
        .recycled_transmit_descriptors = 0,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = false,
        .replay_checkpoint = .after_control_queue_restore,
        .expected_min_ratio_pct = 100,
    });

    try std.testing.expectEqual(throughput_parity.ThroughputParityStatus.needs_receive_refill, summary.status);
    try std.testing.expect(summary.control_queue_restore_ready);
    try std.testing.expect(!summary.receive_refill_checkpoint_ready);
    try std.testing.expect(!summary.receive_refill_ready);
    try std.testing.expect(!summary.transmit_recycle_checkpoint_ready);
    try std.testing.expect(!summary.transmit_recycle_ready);
    try std.testing.expect(summary.recycle_budget_ready);
    try std.testing.expect(summary.requires_post_reset_probe_replay);
    try std.testing.expectEqual(@as(u8, 100), summary.recycle_ratio_pct);
    try std.testing.expectEqual(@as(u8, 100), summary.throughput_ratio_pct);
    try std.testing.expect(!summary.meets_expected_min_ratio);
}

test "phase12 throughput parity gate keeps transmit recycle explicit after receive refill for stopped queues" {
    const summary = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 1,
        .queue_pairs_after_restore = 1,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .receive_descriptors_reposted = true,
        .recycled_transmit_descriptors = 2,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_receive_refill,
    });

    try std.testing.expectEqual(throughput_parity.ThroughputParityStatus.needs_transmit_recycle, summary.status);
    try std.testing.expect(summary.control_queue_restore_ready);
    try std.testing.expect(summary.receive_refill_checkpoint_ready);
    try std.testing.expect(summary.receive_refill_ready);
    try std.testing.expect(!summary.transmit_recycle_checkpoint_ready);
    try std.testing.expect(!summary.transmit_recycle_ready);
    try std.testing.expect(summary.requires_post_reset_probe_replay);
    try std.testing.expectEqual(@as(u8, 100), summary.throughput_ratio_pct);
}

test "phase12 throughput parity gate keeps post reset replay explicit after receive refill when transmit never stopped" {
    const summary = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 1,
        .queue_pairs_after_restore = 1,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .receive_descriptors_reposted = true,
        .recycled_transmit_descriptors = 0,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = false,
        .replay_checkpoint = .after_receive_refill,
    });

    try std.testing.expectEqual(throughput_parity.ThroughputParityStatus.needs_post_reset_probe_replay, summary.status);
    try std.testing.expect(summary.control_queue_restore_ready);
    try std.testing.expect(summary.receive_refill_checkpoint_ready);
    try std.testing.expect(summary.receive_refill_ready);
    try std.testing.expect(summary.transmit_recycle_checkpoint_ready);
    try std.testing.expect(summary.transmit_recycle_ready);
    try std.testing.expect(summary.requires_post_reset_probe_replay);
    try std.testing.expectEqual(@as(u8, 100), summary.throughput_ratio_pct);
}

test "phase12 throughput parity gate rejects missing queue restore baselines" {
    try std.testing.expectError(error.QueuePairsBeforeResetMissing, throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 0,
        .queue_pairs_after_restore = 0,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .recycled_transmit_descriptors = 0,
    }));
}

test "phase12 throughput parity gate rejects missing refill baselines" {
    try std.testing.expectError(error.ReceiveBuffersBeforeResetMissing, throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 1,
        .queue_pairs_after_restore = 1,
        .receive_buffers_before_reset = 0,
        .receive_buffers_after_restore = 0,
        .recycled_transmit_descriptors = 0,
    }));
}

test "phase12 throughput parity gate rejects zero wake thresholds for stopped queues" {
    try std.testing.expectError(error.StoppedQueueWakeThresholdMissing, throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 1,
        .queue_pairs_after_restore = 1,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .recycled_transmit_descriptors = 0,
        .wake_threshold = 0,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_transmit_queue_restore,
    }));
}

test "phase12 throughput parity gate rejects out-of-range target ratios" {
    try std.testing.expectError(error.ExpectedRatioOutOfRange, throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 1,
        .queue_pairs_after_restore = 1,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .recycled_transmit_descriptors = 0,
        .expected_min_ratio_pct = 101,
    }));
}
