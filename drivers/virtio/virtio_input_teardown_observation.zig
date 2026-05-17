const virtio_input = @import("virtio_input");

pub const TeardownObservationSummary = virtio_input.TeardownObservationSummary;

pub fn summarize(device: *const virtio_input.VirtioInputLab) TeardownObservationSummary {
    return device.teardownObservationSummary();
}

pub fn runtimeStateArmed(summary: TeardownObservationSummary) bool {
    return summary.clears_runtime_state;
}

pub fn capabilityStateArmed(summary: TeardownObservationSummary) bool {
    return summary.clears_capability_state;
}

pub fn preservesIdentity(summary: TeardownObservationSummary) bool {
    return summary.preserves_identity;
}
