const blocked_on_risky_transport = "blocked_on_risky_transport";

pub const RegistrationBlockerState = struct {
    anchor: []const u8 = "drivers/virtio/virtio_input.c",
    registration_preflight_ready: bool,
    queue_callback_ready: bool,
    probe_handoff_ready: bool,
};

pub const RegistrationBlockerSummary = struct {
    anchor: []const u8,
    registration_preflight_ready: bool,
    queue_callback_ready: bool,
    probe_handoff_ready: bool,
    input_registration_lifecycle_blocked: bool,
    transport_queue_callbacks_blocked: bool,
    freeze_restore_blocked: bool,
    probe_remove_blocked: bool,
    risky_transport_posture: []const u8,
};

pub fn summarize(state: RegistrationBlockerState) RegistrationBlockerSummary {
    return .{
        .anchor = state.anchor,
        .registration_preflight_ready = state.registration_preflight_ready,
        .queue_callback_ready = state.queue_callback_ready,
        .probe_handoff_ready = state.probe_handoff_ready,
        .input_registration_lifecycle_blocked = true,
        .transport_queue_callbacks_blocked = true,
        .freeze_restore_blocked = true,
        .probe_remove_blocked = true,
        .risky_transport_posture = blocked_on_risky_transport,
    };
}
