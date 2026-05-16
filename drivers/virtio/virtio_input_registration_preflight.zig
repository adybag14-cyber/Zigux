const virtio_input = @import("virtio_input");

pub const RegistrationPreflightSummary = virtio_input.RegistrationPreflightSummary;
pub const RegistrationBlocker = virtio_input.RegistrationBlocker;

pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {
    return device.registrationPreflightSummary();
}

pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {
    return @tagName(blocker);
}
