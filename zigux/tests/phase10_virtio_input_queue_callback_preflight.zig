const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input queue callback preflight reports blockers before callback handoff" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-queue", 25, null);

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

    try device.configureEventQueue(16);
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(!summary.status_queue_configured);
    try std.testing.expectEqual(
        virtio_input.QueueCallbackPreflightBlocker.status_queue_unconfigured,
        summary.blocker.?,
    );
    try std.testing.expect(!summary.ready_for_queue_callbacks);

    try device.configureStatusQueue(8);
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expectEqual(
        virtio_input.QueueCallbackPreflightBlocker.event_buffers_unfilled,
        summary.blocker.?,
    );
    try std.testing.expect(!summary.event_buffers_ready);

    _ = try device.fillEventBuffers();
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);
    try std.testing.expectEqual(
        virtio_input.QueueCallbackPreflightBlocker.device_not_ready,
        summary.blocker.?,
    );
    try std.testing.expect(!summary.device_ready);
    try std.testing.expect(!summary.ready_for_queue_callbacks);

    try device.markReady();
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(summary.ready_for_queue_callbacks);
}

test "phase10 virtio input queue callback preflight stays ready across bounded refill bookkeeping" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-refill", 26, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();

    var summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(summary.ready_for_queue_callbacks);

    const refill = try device.refillEventBuffers(2);
    try std.testing.expectEqual(@as(u16, 8), refill.queued_event_buffer_count_before);
    try std.testing.expectEqual(@as(u16, 8), refill.queued_event_buffer_count_after);

    summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqual(@as(u16, 8), summary.queued_event_buffer_count);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(summary.ready_for_queue_callbacks);
}
