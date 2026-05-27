const std = @import("std");
const virtio_input = @import("virtio_input");
const registration_handoff = @import("virtio_input_registration_handoff");

test "phase10 virtio input registration handoff helper exposes identity and queue plan for ready plain devices" {
    const ids = registration_handoff.DeviceIds{
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

    const summary = registration_handoff.summarize(&device);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", registration_handoff.anchor(summary));
    try std.testing.expectEqualStrings("virtio-tablet", registration_handoff.name(summary));
    try std.testing.expectEqualStrings("handoff-plain", registration_handoff.serial(summary));
    try std.testing.expectEqualStrings("virtio9/input0", registration_handoff.phys(summary));
    try std.testing.expectEqualDeep(ids, registration_handoff.deviceIds(summary));
    try std.testing.expectEqual(virtio_input.event_queue_index, registration_handoff.eventQueueIndex(summary));
    try std.testing.expectEqual(virtio_input.status_queue_index, registration_handoff.statusQueueIndex(summary));
    try std.testing.expectEqual(@as(u16, 8), registration_handoff.eventDescriptorCount(summary));
    try std.testing.expectEqual(@as(u16, 4), registration_handoff.statusDescriptorCount(summary));
    try std.testing.expectEqual(@as(u16, 8), registration_handoff.queuedEventBufferCount(summary));
    try std.testing.expect(registration_handoff.capabilitySetupReady(summary));
    try std.testing.expect(registration_handoff.multitouchSlotsReady(summary));
    try std.testing.expect(registration_handoff.readyForRegistration(summary));
}

test "phase10 virtio input registration handoff helper keeps multitouch slot planning visible before and after slot setup" {
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

    var summary = registration_handoff.summarize(&device);
    try std.testing.expect(registration_handoff.capabilitySetupReady(summary));
    try std.testing.expect(!registration_handoff.multitouchSlotsReady(summary));
    try std.testing.expect(!registration_handoff.readyForRegistration(summary));
    try std.testing.expectEqualStrings("virtio11/input0", registration_handoff.phys(summary));

    _ = try device.planMultitouchSlots();

    summary = registration_handoff.summarize(&device);
    try std.testing.expect(registration_handoff.capabilitySetupReady(summary));
    try std.testing.expect(registration_handoff.multitouchSlotsReady(summary));
    try std.testing.expect(registration_handoff.readyForRegistration(summary));
}
