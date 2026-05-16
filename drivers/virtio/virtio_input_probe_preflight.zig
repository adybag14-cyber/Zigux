const virtio_input = @import("virtio_input");

pub const ProbePreflightSummary = virtio_input.ProbePreflightSummary;
pub const ProbePreflightBlocker = virtio_input.ProbePreflightBlocker;

pub fn summarize(device: *const virtio_input.VirtioInputLab) ProbePreflightSummary {
    return device.probePreflightSummary();
}

pub fn blockerTag(blocker: ProbePreflightBlocker) []const u8 {
    return @tagName(blocker);
}
