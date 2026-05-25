const virtio_input = @import("virtio_input");

pub const TeardownObservationSummary = virtio_input.TeardownObservationSummary;
pub const DeviceIds = virtio_input.DeviceIds;

pub fn summarize(device: *const virtio_input.VirtioInputLab) TeardownObservationSummary {
    return device.teardownObservationSummary();
}

pub fn anchor(summary: TeardownObservationSummary) []const u8 {
    return summary.anchor;
}

pub fn name(summary: TeardownObservationSummary) []const u8 {
    return summary.name;
}

pub fn serial(summary: TeardownObservationSummary) []const u8 {
    return summary.serial;
}

pub fn phys(summary: TeardownObservationSummary) []const u8 {
    return summary.phys;
}

pub fn deviceIds(summary: TeardownObservationSummary) DeviceIds {
    return summary.ids;
}

pub fn eventQueueWasConfigured(summary: TeardownObservationSummary) bool {
    return summary.event_queue_was_configured;
}

pub fn statusQueueWasConfigured(summary: TeardownObservationSummary) bool {
    return summary.status_queue_was_configured;
}

pub fn queuedEventBufferCount(summary: TeardownObservationSummary) u16 {
    return summary.queued_event_buffer_count;
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

pub fn readyBeforeReset(summary: TeardownObservationSummary) bool {
    return summary.ready_before_reset;
}

pub fn multitouchWasEnabled(summary: TeardownObservationSummary) bool {
    return summary.multitouch_was_enabled;
}

pub fn plannedMultitouchSlots(summary: TeardownObservationSummary) u16 {
    return summary.planned_multitouch_slots;
}

pub fn queuedStatusCount(summary: TeardownObservationSummary) usize {
    return summary.queued_status_count;
}

pub fn suppressedStatusCount(summary: TeardownObservationSummary) usize {
    return summary.suppressed_status_count;
}
