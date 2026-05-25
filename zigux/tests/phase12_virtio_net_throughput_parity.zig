const std = @import("std");
const throughput_parity = @import("virtio_net_throughput_parity");

test "phase12 throughput parity gate counts preexisting free descriptors toward stopped-queue wake readiness" {
    const summary = try throughput_parity.summarizeThroughputParity(.{
        .queue_pairs_before_reset = 4,
        .queue_pairs_after_restore = 4,
        .receive_buffers_before_reset = 512,
        .receive_buffers_after_restore = 512,
        .receive_descriptors_reposted = true,
        .free_transmit_descriptors_before_recycle = 1,
        .recycled_transmit_descriptors = 1,
        .wake_threshold = 2,
        .transmit_queue_was_stopped = true,
        .replay_checkpoint = .after_transmit_queue_restore,
        .expected_min_ratio_pct = 90,
    });

    try std.testing.expectEqual(@as(u16, 1), summary.free_transmit_descriptors_before_recycle);
    try std.testing.expectEqual(@as(u16, 2), summary.free_transmit_descriptors_after_recycle);
    try std.testing.expect(summary.recycle_budget_ready);
    try std.testing.expect(summary.transmit_recycle_ready);
    try std.testing.expectEqual(
        throughput_parity.ThroughputParityStatus.parity_gate_ready,
        summary.status,
    );
    try std.testing.expect(summary.meets_expected_min_ratio);
}
