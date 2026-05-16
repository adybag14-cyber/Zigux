const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input queue callback preflight tracks queue and ready-state gating" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-28", 7, null);

    var summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expect(!summary.ready_for_queue_callbacks);

    try device.configureEventQueue(16);
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.status_queue_unconfigured, summary.blocker.?);

    try device.configureStatusQueue(8);
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.event_buffers_unfilled, summary.blocker.?);
    try std.testing.expectEqual(@as(u16, 0), summary.queued_event_buffer_count);

    _ = try device.fillEventBuffers();
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.device_not_ready, summary.blocker.?);
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);

    try device.markReady();
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqual(@as(?virtio_input.QueueCallbackPreflightBlocker, null), summary.blocker);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.ready_for_queue_callbacks);
}
