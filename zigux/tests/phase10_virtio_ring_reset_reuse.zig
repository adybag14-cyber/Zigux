const std = @import("std");
const virtio_ring = @import("virtio_ring");

test "phase10 virtio ring drained reset clears the broken flag so the queue can be reused" {
    var ring = virtio_ring.VirtioRingLab{};
    try ring.defineQueue(2, 8, .packed_ring, true, true);

    _ = try ring.breakQueue(2);
    try std.testing.expectError(error.QueueBroken, ring.publishDescriptorChain(2));

    const guard_summary = try ring.resetGuardSummary(2);
    try std.testing.expect(guard_summary.reset_allowed);

    const reset_summary = try ring.resetQueue(2);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", reset_summary.anchor);
    try std.testing.expect(reset_summary.callback_enabled);
    try std.testing.expectEqual(@as(u16, 0), reset_summary.avail_idx_shadow);

    const broken_summary = try ring.brokenSummary(2);
    try std.testing.expect(!broken_summary.broken);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.pending_used_chain_count);
    try std.testing.expectEqual(@as(u16, 0), broken_summary.unpublished_chain_count);

    try ring.publishDescriptorChain(2);
    const notification_summary = try ring.notificationSummary(2);
    try std.testing.expectEqual(@as(u16, 1), notification_summary.avail_idx_shadow);
    try std.testing.expectEqual(@as(u16, 1), notification_summary.outstanding_chain_count);
    try std.testing.expectEqual(@as(u16, 1), notification_summary.num_added);
}
