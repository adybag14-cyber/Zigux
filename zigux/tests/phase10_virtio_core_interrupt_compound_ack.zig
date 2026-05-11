const std = @import("std");
const virtio_core = @import("../../drivers/virtio/virtio.zig");

test "phase10 virtio core clears combined interrupt reasons in one acknowledgement" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 9, 16 });
    device.acknowledge();
    try device.attachDriver();

    try device.noteInterruptReason(
        virtio_core.VirtioInterruptReason.queue_used |
            virtio_core.VirtioInterruptReason.config_change,
    );

    var summary = device.interruptAckSummary();
    try std.testing.expect(summary.interrupt_pending);
    try std.testing.expectEqual(
        virtio_core.VirtioInterruptReason.queue_used |
            virtio_core.VirtioInterruptReason.config_change,
        summary.pending_reason_bits,
    );
    try std.testing.expectEqual(@as(u8, 0), summary.acknowledged_reason_bits);
    try std.testing.expectEqual(@as(usize, 0), summary.ack_count);
    try std.testing.expectEqual(@as(usize, 2), summary.unacknowledged_interrupt_count);

    try device.acknowledgeInterrupt(
        virtio_core.VirtioInterruptReason.queue_used |
            virtio_core.VirtioInterruptReason.config_change,
    );

    summary = device.interruptAckSummary();
    try std.testing.expect(!summary.interrupt_pending);
    try std.testing.expectEqual(@as(u8, 0), summary.pending_reason_bits);
    try std.testing.expectEqual(
        virtio_core.VirtioInterruptReason.queue_used |
            virtio_core.VirtioInterruptReason.config_change,
        summary.acknowledged_reason_bits,
    );
    try std.testing.expectEqual(@as(usize, 1), summary.ack_count);
    try std.testing.expectEqual(@as(usize, 2), summary.unacknowledged_interrupt_count);
}
