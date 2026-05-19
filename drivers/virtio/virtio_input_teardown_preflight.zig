const virtio_input = @import("virtio_input");

pub const TeardownPreflightBlocker = enum {
    pending_status_drain,
};

pub const TeardownPreflightSummary = struct {
    anchor: []const u8,
    queued_status_count: usize,
    suppressed_status_count: usize,
    preserves_identity: bool,
    runtime_state_armed: bool,
    capability_state_armed: bool,
    blocker: ?TeardownPreflightBlocker,
    ready_for_teardown: bool,
};

pub fn summarize(device: *const virtio_input.VirtioInputLab) TeardownPreflightSummary {
    const observation = device.teardownObservationSummary();
    const blocker: ?TeardownPreflightBlocker = if (observation.queued_status_count != 0)
        .pending_status_drain
    else
        null;

    return .{
        .anchor = observation.anchor,
        .queued_status_count = observation.queued_status_count,
        .suppressed_status_count = observation.suppressed_status_count,
        .preserves_identity = observation.preserves_identity,
        .runtime_state_armed = observation.clears_runtime_state,
        .capability_state_armed = observation.clears_capability_state,
        .blocker = blocker,
        .ready_for_teardown = blocker == null,
    };
}

pub fn blockerTag(blocker: TeardownPreflightBlocker) []const u8 {
    return @tagName(blocker);
}

pub fn runtimeStateArmed(summary: TeardownPreflightSummary) bool {
    return summary.runtime_state_armed;
}

pub fn capabilityStateArmed(summary: TeardownPreflightSummary) bool {
    return summary.capability_state_armed;
}

pub fn preservesIdentity(summary: TeardownPreflightSummary) bool {
    return summary.preserves_identity;
}
