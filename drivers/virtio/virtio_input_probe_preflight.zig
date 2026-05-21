const virtio_input = @import("virtio_input");

pub const ProbePreflightSummary = virtio_input.ProbePreflightSummary;
pub const ProbePreflightBlocker = virtio_input.ProbePreflightBlocker;

pub fn summarize(device: *const virtio_input.VirtioInputLab) ProbePreflightSummary {
    return device.probePreflightSummary();
}

pub fn blockerTag(blocker: ProbePreflightBlocker) []const u8 {
    return @tagName(blocker);
}

pub fn identityReady(summary: ProbePreflightSummary) bool {
    return summary.identity_ready;
}

pub fn queuePlanReady(summary: ProbePreflightSummary) bool {
    return summary.queue_plan_ready;
}

pub fn capabilitySetupReady(summary: ProbePreflightSummary) bool {
    return summary.capability_setup_ready;
}

pub fn multitouchSlotsReady(summary: ProbePreflightSummary) bool {
    return summary.multitouch_slots_ready;
}

pub fn waitingOnIdentity(summary: ProbePreflightSummary) bool {
    return summary.blocker == .identity_incomplete;
}

pub fn readyForProbeHandoff(summary: ProbePreflightSummary) bool {
    return summary.ready_for_probe_handoff;
}
