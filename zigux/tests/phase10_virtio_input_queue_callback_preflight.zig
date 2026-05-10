const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input queue callback preflight reports queue and ready blockers and resets cleanly" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-callback", 24, null);

    var summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expect(!summary.event_queue_configured);
    try std.testing.expect(!summary.status_queue_configured);
    try std.testing.expectEqual(@as(u16, 0), summary.queued_event_buffer_count);
    try std.testing.expect(!summary.event_buffers_ready);
    try std.testing.expect(!summary.device_ready);
    try std.testing.expectEqual(
        virtio_input.QueueCallbackPreflightBlocker.event_queue_unconfigured,
        summary.blocker.?,
    );
    try std.testing.expect(!summary.ready_for_queue_callbacks);

    try device.configureEventQueue(8);
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(!summary.status_queue_configured);
    try std.testing.expectEqual(
        virtio_input.QueueCallbackPreflightBlocker.status_queue_unconfigured,
        summary.blocker.?,
    );

    try device.configureStatusQueue(4);
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expectEqual(
        virtio_input.QueueCallbackPreflightBlocker.event_buffers_unfilled,
        summary.blocker.?,
    );

    _ = try device.fillEventBuffers();
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqual(@as(u16, 8), summary.queued_event_buffer_count);
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expectEqual(
        virtio_input.QueueCallbackPreflightBlocker.device_not_ready,
        summary.blocker.?,
    );

    try device.markReady();
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.ready_for_queue_callbacks);
    try std.testing.expect(summary.blocker == null);

    device.reset();
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(!summary.event_queue_configured);
    try std.testing.expect(!summary.status_queue_configured);
    try std.testing.expectEqual(@as(u16, 0), summary.queued_event_buffer_count);
    try std.testing.expect(!summary.event_buffers_ready);
    try std.testing.expect(!summary.device_ready);
    try std.testing.expectEqual(
        virtio_input.QueueCallbackPreflightBlocker.event_queue_unconfigured,
        summary.blocker.?,
    );
    try std.testing.expect(!summary.ready_for_queue_callbacks);
}

test "phase10 virtio input queue callback preflight keeps refill replay ready after the queue plan is live" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-refill", 25, null);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();

    var summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.ready_for_queue_callbacks);
    try std.testing.expect(summary.blocker == null);

    const refill = try device.refillEventBuffers(5);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", refill.anchor);
    try std.testing.expectEqual(@as(u16, 5), refill.completed_event_count);
    try std.testing.expectEqual(@as(u16, 16), refill.queued_event_buffer_count_before);
    try std.testing.expectEqual(@as(u16, 16), refill.queued_event_buffer_count_after);
    try std.testing.expect(refill.ready);

    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.ready_for_queue_callbacks);
    try std.testing.expect(summary.blocker == null);
}
