const std = @import("std");
const virtio_input = @import("virtio_input");

pub const RegistrationHandoffSummary = virtio_input.RegistrationHandoffSummary;
pub const DeviceIds = virtio_input.DeviceIds;

pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationHandoffSummary {
    return device.registrationHandoffSummary();
}

pub fn anchor(summary: RegistrationHandoffSummary) []const u8 {
    return summary.anchor;
}

pub fn name(summary: RegistrationHandoffSummary) []const u8 {
    return summary.name;
}

pub fn serial(summary: RegistrationHandoffSummary) []const u8 {
    return summary.serial;
}

pub fn phys(summary: RegistrationHandoffSummary) []const u8 {
    return summary.phys;
}

pub fn deviceIds(summary: RegistrationHandoffSummary) DeviceIds {
    return summary.ids;
}

pub fn eventQueueIndex(summary: RegistrationHandoffSummary) u16 {
    return summary.event_queue_index;
}

pub fn statusQueueIndex(summary: RegistrationHandoffSummary) u16 {
    return summary.status_queue_index;
}

pub fn eventDescriptorCount(summary: RegistrationHandoffSummary) u16 {
    return summary.event_descriptor_count;
}

pub fn statusDescriptorCount(summary: RegistrationHandoffSummary) u16 {
    return summary.status_descriptor_count;
}

pub fn queuedEventBufferCount(summary: RegistrationHandoffSummary) u16 {
    return summary.queued_event_buffer_count;
}

pub fn capabilitySetupReady(summary: RegistrationHandoffSummary) bool {
    return summary.capability_setup_ready;
}

pub fn multitouchSlotsReady(summary: RegistrationHandoffSummary) bool {
    return summary.multitouch_slots_ready;
}

pub fn readyForRegistration(summary: RegistrationHandoffSummary) bool {
    return summary.ready_for_registration;
}

test "phase10 virtio input registration handoff helper keeps plain-device identity and queue plan explicit" {
    const ids = DeviceIds{
        .vendor = 0x1af4,
        .product = 0x1052,
        .version = 9,
    };
    var device = try virtio_input.VirtioInputLab.init("virtio-tablet", "handoff-plain", 9, ids);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.ev_bits, 0x02, &[_]u16{ 0x00, 0x01 });

    const summary = summarize(&device);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", anchor(summary));
    try std.testing.expectEqualStrings("virtio-tablet", name(summary));
    try std.testing.expectEqualStrings("handoff-plain", serial(summary));
    try std.testing.expectEqualStrings("virtio9/input0", phys(summary));
    try std.testing.expectEqualDeep(ids, deviceIds(summary));
    try std.testing.expectEqual(virtio_input.event_queue_index, eventQueueIndex(summary));
    try std.testing.expectEqual(virtio_input.status_queue_index, statusQueueIndex(summary));
    try std.testing.expectEqual(@as(u16, 8), eventDescriptorCount(summary));
    try std.testing.expectEqual(@as(u16, 4), statusDescriptorCount(summary));
    try std.testing.expectEqual(@as(u16, 8), queuedEventBufferCount(summary));
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(readyForRegistration(summary));
}

test "phase10 virtio input registration handoff helper keeps multitouch slot planning explicit" {
    var device = try virtio_input.VirtioInputLab.init("virtio-touch", "handoff-mt", 11, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 3,
    });

    var summary = summarize(&device);
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(!multitouchSlotsReady(summary));
    try std.testing.expect(!readyForRegistration(summary));
    try std.testing.expectEqualStrings("virtio11/input0", phys(summary));

    _ = try device.planMultitouchSlots();

    summary = summarize(&device);
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(readyForRegistration(summary));
}
