const virtio_input = @import("virtio_input");

pub const ProbePreflightBlocker = enum {
    identity_incomplete,
    queue_plan_incomplete,
    device_not_ready,
    capability_setup_incomplete,
    multitouch_slots_unplanned,
};

pub const ProbePreflightSummary = struct {
    anchor: []const u8,
    name_ready: bool,
    serial_ready: bool,
    phys_ready: bool,
    identity_ready: bool,
    queue_plan_ready: bool,
    device_ready: bool,
    capability_setup_ready: bool,
    multitouch_slots_ready: bool,
    registration_preflight_ready: bool,
    blocker: ?ProbePreflightBlocker,
    ready_for_probe_handoff: bool,
};

pub fn summarize(device: *const virtio_input.VirtioInputLab) ProbePreflightSummary {
    const registration = device.registrationPreflightSummary();
    const name_ready = device.name_len != 0;
    const serial_ready = device.serial_len != 0;
    const phys_ready = device.phys_len != 0;
    const identity_ready = name_ready and serial_ready and phys_ready;

    const blocker: ?ProbePreflightBlocker = if (!identity_ready)
        .identity_incomplete
    else if (!registration.queue_plan_ready)
        .queue_plan_incomplete
    else if (!registration.device_ready)
        .device_not_ready
    else if (!registration.capability_setup_ready)
        .capability_setup_incomplete
    else if (!registration.multitouch_slots_ready)
        .multitouch_slots_unplanned
    else
        null;

    return .{
        .anchor = virtio_input.VirtioInputLab.descriptor().anchor,
        .name_ready = name_ready,
        .serial_ready = serial_ready,
        .phys_ready = phys_ready,
        .identity_ready = identity_ready,
        .queue_plan_ready = registration.queue_plan_ready,
        .device_ready = registration.device_ready,
        .capability_setup_ready = registration.capability_setup_ready,
        .multitouch_slots_ready = registration.multitouch_slots_ready,
        .registration_preflight_ready = registration.ready_for_registration,
        .blocker = blocker,
        .ready_for_probe_handoff = blocker == null,
    };
}
