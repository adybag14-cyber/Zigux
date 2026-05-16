const virtio_input = @import("virtio_input");

pub const RegistrationPreflightBlocker = virtio_input.RegistrationBlocker;

pub const RegistrationPreflightSummary = struct {
    anchor: []const u8,
    event_queue_configured: bool,
    status_queue_configured: bool,
    event_buffers_ready: bool,
    queue_plan_ready: bool,
    device_ready: bool,
    capability_setup_ready: bool,
    multitouch_slots_ready: bool,
    blocker: ?RegistrationPreflightBlocker,
    ready_for_registration: bool,
};

pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {
    const registration = device.registrationPreflightSummary();
    const event_queue_configured = device.event_descriptor_count != 0;
    const status_queue_configured = device.status_descriptor_count != 0;
    const event_buffers_ready = device.queued_event_buffer_count != 0;

    return .{
        .anchor = virtio_input.VirtioInputLab.descriptor().anchor,
        .event_queue_configured = event_queue_configured,
        .status_queue_configured = status_queue_configured,
        .event_buffers_ready = event_buffers_ready,
        .queue_plan_ready = registration.queue_plan_ready,
        .device_ready = registration.device_ready,
        .capability_setup_ready = registration.capability_setup_ready,
        .multitouch_slots_ready = registration.multitouch_slots_ready,
        .blocker = registration.blocker,
        .ready_for_registration = registration.ready_for_registration,
    };
}
