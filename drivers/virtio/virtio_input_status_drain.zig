const virtio_input = @import("virtio_input");

pub const StatusDrainSummary = virtio_input.StatusDrainSummary;

pub fn summarize(
    device: *virtio_input.VirtioInputLab,
    completed_count: usize,
) !StatusDrainSummary {
    return device.drainStatusQueue(completed_count);
}
