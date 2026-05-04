const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input drains queued status completions without touching suppressed multitouch counters" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-drain", 24, null);

    try std.testing.expectError(error.StatusQueueNotConfigured, device.drainStatusQueue(0));

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    device.setMultitouch(true);

    _ = try device.sendStatus(0x11, 0x01, 1);
    _ = try device.sendStatus(0x12, 0x02, 2);
    _ = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 3);

    var summary = try device.drainStatusQueue(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 1), summary.completed_status_count);
    try std.testing.expectEqual(@as(usize, 2), summary.pending_status_count_before);
    try std.testing.expectEqual(@as(usize, 1), summary.pending_status_count_after);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);
    try std.testing.expect(summary.ready);

    summary = try device.drainStatusQueue(1);
    try std.testing.expectEqual(@as(usize, 1), summary.completed_status_count);
    try std.testing.expectEqual(@as(usize, 1), summary.pending_status_count_before);
    try std.testing.expectEqual(@as(usize, 0), summary.pending_status_count_after);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);
    try std.testing.expect(summary.ready);

    try std.testing.expectError(error.StatusCompletionCountExceedsQueued, device.drainStatusQueue(1));
}