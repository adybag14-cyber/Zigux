const virtio_input = @import("virtio_input");

pub const QueueCallbackPreflightSummary = virtio_input.QueueCallbackPreflightSummary;
pub const QueueCallbackPreflightBlocker = virtio_input.QueueCallbackPreflightBlocker;

pub fn summarize(device: *const virtio_input.VirtioInputLab) QueueCallbackPreflightSummary {
    return device.queueCallbackPreflightSummary();
}

pub fn blockerTag(blocker: QueueCallbackPreflightBlocker) []const u8 {
    return @tagName(blocker);
}
