const std = @import("std");
const virtio_ring = @import("virtio_ring");

test "phase10 virtio ring repeated prepareKick stays idle until new descriptors are published" {
    var ring = virtio_ring.VirtioRingLab{};

    try ring.defineQueue(1, 8, .split, true, false);

    try ring.publishDescriptorChain(1);

    var kick_summary = try ring.prepareKick(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", kick_summary.anchor);
    try std.testing.expectEqual(@as(u16, 1), kick_summary.queue_index);
    try std.testing.expect(kick_summary.needs_kick);
    try std.testing.expectEqual(@as(u16, 1), kick_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), kick_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), kick_summary.num_added);
    try std.testing.expectEqual(@as(usize, 1), kick_summary.notification_count);

    kick_summary = try ring.prepareKick(1);
    try std.testing.expect(!kick_summary.needs_kick);
    try std.testing.expectEqual(@as(u16, 1), kick_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), kick_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), kick_summary.num_added);
    try std.testing.expectEqual(@as(usize, 1), kick_summary.notification_count);

    try ring.recordUsedChains(1, 1);
    const poll_summary = try ring.pollUsedBuffers(1);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.last_used_idx);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.last_polled_used_idx);
    try std.testing.expectEqual(@as(u16, 1), poll_summary.newly_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), poll_summary.outstanding_chain_count);
    try std.testing.expect(poll_summary.has_newly_used_chains);

    kick_summary = try ring.prepareKick(1);
    try std.testing.expect(!kick_summary.needs_kick);
    try std.testing.expectEqual(@as(u16, 1), kick_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 0), kick_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), kick_summary.num_added);
    try std.testing.expectEqual(@as(usize, 1), kick_summary.notification_count);

    try ring.publishDescriptorChain(1);
    kick_summary = try ring.prepareKick(1);
    try std.testing.expect(kick_summary.needs_kick);
    try std.testing.expectEqual(@as(u16, 2), kick_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), kick_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), kick_summary.num_added);
    try std.testing.expectEqual(@as(usize, 2), kick_summary.notification_count);
}
