const std = @import("std");
const virtio_input = @import("virtio_input");
const queue_callback_preflight = @import("virtio_input_queue_callback_preflight");

test "phase10 virtio input queue callback preflight helper tracks queue and ready-state gating" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-28", 7, null);

    var summary = queue_callback_preflight.summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "event_queue_unconfigured",
        queue_callback_preflight.blockerTag(summary.blocker.?),
    );
    try std.testing.expect(!summary.ready_for_queue_callbacks);

    try device.configureEventQueue(16);
    summary = queue_callback_preflight.summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.status_queue_unconfigured, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "status_queue_unconfigured",
        queue_callback_preflight.blockerTag(summary.blocker.?),
    );

    try device.configureStatusQueue(8);
    summary = queue_callback_preflight.summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.event_buffers_unfilled, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "event_buffers_unfilled",
        queue_callback_preflight.blockerTag(summary.blocker.?),
    );
    try std.testing.expectEqual(@as(u16, 0), summary.queued_event_buffer_count);

    _ = try device.fillEventBuffers();
    summary = queue_callback_preflight.summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.device_not_ready, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "device_not_ready",
        queue_callback_preflight.blockerTag(summary.blocker.?),
    );
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);

    try device.markReady();
    summary = queue_callback_preflight.summarize(&device);
    try std.testing.expectEqual(@as(?virtio_input.QueueCallbackPreflightBlocker, null), summary.blocker);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.ready_for_queue_callbacks);
}

test "phase10 virtio input queue callback preflight helper accepts incremental refills before ready-state handoff" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-29", 8, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);

    var summary = queue_callback_preflight.summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.event_buffers_unfilled, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "event_buffers_unfilled",
        queue_callback_preflight.blockerTag(summary.blocker.?),
    );
    try std.testing.expectEqual(@as(u16, 0), summary.queued_event_buffer_count);
    try std.testing.expect(!summary.event_buffers_ready);

    const refill = try device.refillEventBuffers(2);
    try std.testing.expectEqual(@as(u16, 0), refill.queued_event_buffer_count_before);
    try std.testing.expectEqual(@as(u16, 2), refill.queued_event_buffer_count_after);

    summary = queue_callback_preflight.summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.device_not_ready, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "device_not_ready",
        queue_callback_preflight.blockerTag(summary.blocker.?),
    );
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expectEqual(@as(u16, 2), summary.queued_event_buffer_count);
    try std.testing.expect(!summary.device_ready);
    try std.testing.expect(!summary.ready_for_queue_callbacks);

    try device.markReady();
    summary = queue_callback_preflight.summarize(&device);
    try std.testing.expectEqual(@as(?virtio_input.QueueCallbackPreflightBlocker, null), summary.blocker);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.ready_for_queue_callbacks);
}
