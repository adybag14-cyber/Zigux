const virtio_input = @import("virtio_input");

pub const RegistrationPreflightSummary = virtio_input.RegistrationPreflightSummary;
pub const RegistrationBlocker = virtio_input.RegistrationBlocker;

pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {
    return device.registrationPreflightSummary();
}

pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {
    return @tagName(blocker);
}

pub fn queuePlanReady(summary: RegistrationPreflightSummary) bool {
    return summary.queue_plan_ready;
}

pub fn capabilitySetupReady(summary: RegistrationPreflightSummary) bool {
    return summary.capability_setup_ready;
}

pub fn multitouchSlotsReady(summary: RegistrationPreflightSummary) bool {
    return summary.multitouch_slots_ready;
}

pub fn waitingOnCapabilitySetup(summary: RegistrationPreflightSummary) bool {
    return summary.blocker == .capability_setup_incomplete;
}

pub fn waitingOnMultitouchSlots(summary: RegistrationPreflightSummary) bool {
    return summary.blocker == .multitouch_slots_unplanned;
}

pub fn readyForRegistration(summary: RegistrationPreflightSummary) bool {
    return summary.ready_for_registration;
}
