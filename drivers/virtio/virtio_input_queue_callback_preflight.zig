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

pub fn eventQueueConfigured(summary: QueueCallbackPreflightSummary) bool {
    return summary.event_queue_configured;
}

pub fn statusQueueConfigured(summary: QueueCallbackPreflightSummary) bool {
    return summary.status_queue_configured;
}

pub fn eventBuffersReady(summary: QueueCallbackPreflightSummary) bool {
    return summary.event_buffers_ready;
}

pub fn deviceReady(summary: QueueCallbackPreflightSummary) bool {
    return summary.device_ready;
}

pub fn queuedEventBufferCount(summary: QueueCallbackPreflightSummary) u16 {
    return summary.queued_event_buffer_count;
}

pub fn waitingOnEventQueue(summary: QueueCallbackPreflightSummary) bool {
    return summary.blocker == .event_queue_unconfigured;
}

pub fn waitingOnStatusQueue(summary: QueueCallbackPreflightSummary) bool {
    return summary.blocker == .status_queue_unconfigured;
}

pub fn waitingOnEventBuffers(summary: QueueCallbackPreflightSummary) bool {
    return summary.blocker == .event_buffers_unfilled;
}

pub fn waitingOnDeviceReady(summary: QueueCallbackPreflightSummary) bool {
    return summary.blocker == .device_not_ready;
}

pub fn readyForQueueCallbacks(summary: QueueCallbackPreflightSummary) bool {
    return summary.ready_for_queue_callbacks;
}

test "phase10 virtio input queue callback preflight helper exposes blocker predicates across staged readiness" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-28", 7, null);

    var summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expectEqualStrings("event_queue_unconfigured", blockerTag(summary.blocker.?));
    try std.testing.expect(!eventQueueConfigured(summary));
    try std.testing.expect(!statusQueueConfigured(summary));
    try std.testing.expect(!eventBuffersReady(summary));
    try std.testing.expect(!deviceReady(summary));
    try std.testing.expect(waitingOnEventQueue(summary));
    try std.testing.expect(!waitingOnStatusQueue(summary));
    try std.testing.expect(!waitingOnEventBuffers(summary));
    try std.testing.expect(!waitingOnDeviceReady(summary));
    try std.testing.expect(!readyForQueueCallbacks(summary));

    try device.configureEventQueue(16);
    summary = summarize(&device);
    try std.testing.expect(eventQueueConfigured(summary));
    try std.testing.expect(!statusQueueConfigured(summary));
    try std.testing.expect(waitingOnStatusQueue(summary));

    try device.configureStatusQueue(8);
    summary = summarize(&device);
    try std.testing.expect(eventQueueConfigured(summary));
    try std.testing.expect(statusQueueConfigured(summary));
    try std.testing.expect(!eventBuffersReady(summary));
    try std.testing.expect(waitingOnEventBuffers(summary));
    try std.testing.expectEqual(@as(u16, 0), queuedEventBufferCount(summary));

    _ = try device.fillEventBuffers();
    summary = summarize(&device);
    try std.testing.expect(eventQueueConfigured(summary));
    try std.testing.expect(statusQueueConfigured(summary));
    try std.testing.expect(eventBuffersReady(summary));
    try std.testing.expect(!deviceReady(summary));
    try std.testing.expect(waitingOnDeviceReady(summary));
    try std.testing.expectEqual(@as(u16, 16), queuedEventBufferCount(summary));

    try device.markReady();
    summary = summarize(&device);
    try std.testing.expect(deviceReady(summary));
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(readyForQueueCallbacks(summary));
}

test "phase10 virtio input queue callback preflight helper keeps predicates aligned across incremental refill and reset" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-29", 8, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);

    var summary = summarize(&device);
    try std.testing.expect(waitingOnEventBuffers(summary));
    try std.testing.expectEqual(@as(u16, 0), queuedEventBufferCount(summary));
    try std.testing.expect(!eventBuffersReady(summary));

    const refill = try device.refillEventBuffers(2);
    try std.testing.expectEqual(@as(u16, 0), refill.queued_event_buffer_count_before);
    try std.testing.expectEqual(@as(u16, 2), refill.queued_event_buffer_count_after);

    summary = summarize(&device);
    try std.testing.expect(eventBuffersReady(summary));
    try std.testing.expect(waitingOnDeviceReady(summary));
    try std.testing.expectEqual(@as(u16, 2), queuedEventBufferCount(summary));
    try std.testing.expect(!deviceReady(summary));
    try std.testing.expect(!readyForQueueCallbacks(summary));

    try device.markReady();
    summary = summarize(&device);
    try std.testing.expect(deviceReady(summary));
    try std.testing.expect(readyForQueueCallbacks(summary));

    device.reset();
    summary = summarize(&device);
    try std.testing.expect(waitingOnEventQueue(summary));
    try std.testing.expect(!eventQueueConfigured(summary));
    try std.testing.expect(!statusQueueConfigured(summary));
    try std.testing.expect(!eventBuffersReady(summary));
    try std.testing.expect(!deviceReady(summary));
    try std.testing.expectEqual(@as(u16, 0), queuedEventBufferCount(summary));
    try std.testing.expect(!readyForQueueCallbacks(summary));
}
