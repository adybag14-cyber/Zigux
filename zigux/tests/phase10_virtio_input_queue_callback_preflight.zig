const std = @import("std");
const virtio_input = @import("virtio_input");

pub const QueueCallbackPreflightSummary = virtio_input.QueueCallbackPreflightSummary;
pub const QueueCallbackPreflightBlocker = virtio_input.QueueCallbackPreflightBlocker;

pub fn summarize(device: *const virtio_input.VirtioInputLab) QueueCallbackPreflightSummary {
    return device.queueCallbackPreflightSummary();
}

pub fn blockerTag(blocker: QueueCallbackPreflightBlocker) []const u8 {
    return @tagName(blocker);
}

test "phase10 virtio input queue callback preflight helper tracks queue and ready-state gating" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-28", 7, null);

    var summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "event_queue_unconfigured",
        blockerTag(summary.blocker.?),
    );
    try std.testing.expect(!summary.ready_for_queue_callbacks);

    try device.configureEventQueue(16);
    summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.status_queue_unconfigured, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "status_queue_unconfigured",
        blockerTag(summary.blocker.?),
    );

    try device.configureStatusQueue(8);
    summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.event_buffers_unfilled, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "event_buffers_unfilled",
        blockerTag(summary.blocker.?),
    );
    try std.testing.expectEqual(@as(u16, 0), summary.queued_event_buffer_count);

    _ = try device.fillEventBuffers();
    summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.device_not_ready, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "device_not_ready",
        blockerTag(summary.blocker.?),
    );
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);

    try device.markReady();
    summary = summarize(&device);
    try std.testing.expectEqual(@as(?virtio_input.QueueCallbackPreflightBlocker, null), summary.blocker);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.ready_for_queue_callbacks);
}

test "phase10 virtio input queue callback preflight helper accepts incremental refills before ready-state handoff" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-29", 8, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);

    var summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.event_buffers_unfilled, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "event_buffers_unfilled",
        blockerTag(summary.blocker.?),
    );
    try std.testing.expectEqual(@as(u16, 0), summary.queued_event_buffer_count);
    try std.testing.expect(!summary.event_buffers_ready);

    const refill = try device.refillEventBuffers(2);
    try std.testing.expectEqual(@as(u16, 0), refill.queued_event_buffer_count_before);
    try std.testing.expectEqual(@as(u16, 2), refill.queued_event_buffer_count_after);

    summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.device_not_ready, summary.blocker.?);
    try std.testing.expectEqualStrings(
        "device_not_ready",
        blockerTag(summary.blocker.?),
    );
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expectEqual(@as(u16, 2), summary.queued_event_buffer_count);
    try std.testing.expect(!summary.device_ready);
    try std.testing.expect(!summary.ready_for_queue_callbacks);

    try device.markReady();
    summary = summarize(&device);
    try std.testing.expectEqual(@as(?virtio_input.QueueCallbackPreflightBlocker, null), summary.blocker);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.ready_for_queue_callbacks);
}
