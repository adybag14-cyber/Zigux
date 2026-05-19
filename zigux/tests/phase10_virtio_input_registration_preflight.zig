const std = @import("std");
const virtio_input = @import("virtio_input");
const registration = @import("virtio_input_registration_preflight");

test "phase10 virtio input registration preflight helper exposes blocker tags and ready transition" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-29", 8, null);

    var summary = registration.summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expectEqualStrings("event_queue_unconfigured", registration.blockerTag(summary.blocker.?));
    try std.testing.expect(!registration.queuePlanReady(summary));
    try std.testing.expect(!registration.capabilitySetupReady(summary));
    try std.testing.expect(!registration.multitouchSlotsReady(summary));
    try std.testing.expect(!registration.waitingOnCapabilitySetup(summary));
    try std.testing.expect(!registration.waitingOnMultitouchSlots(summary));
    try std.testing.expect(!registration.readyForRegistration(summary));

    try device.configureEventQueue(16);
    summary = registration.summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.status_queue_unconfigured, summary.blocker.?);
    try std.testing.expect(!registration.queuePlanReady(summary));

    try device.configureStatusQueue(8);
    summary = registration.summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.event_buffers_unfilled, summary.blocker.?);
    try std.testing.expect(!registration.queuePlanReady(summary));

    _ = try device.fillEventBuffers();
    summary = registration.summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.device_not_ready, summary.blocker.?);
    try std.testing.expect(registration.queuePlanReady(summary));
    try std.testing.expect(!registration.waitingOnCapabilitySetup(summary));

    try device.markReady();
    summary = registration.summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.capability_setup_incomplete, summary.blocker.?);
    try std.testing.expect(registration.queuePlanReady(summary));
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(!registration.capabilitySetupReady(summary));
    try std.testing.expect(registration.waitingOnCapabilitySetup(summary));
    try std.testing.expect(!registration.waitingOnMultitouchSlots(summary));

    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 3,
    });
    summary = registration.summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.multitouch_slots_unplanned, summary.blocker.?);
    try std.testing.expect(registration.capabilitySetupReady(summary));
    try std.testing.expect(!registration.multitouchSlotsReady(summary));
    try std.testing.expect(!registration.waitingOnCapabilitySetup(summary));
    try std.testing.expect(registration.waitingOnMultitouchSlots(summary));

    const slot_plan = try device.planMultitouchSlots();
    try std.testing.expectEqual(@as(u16, 4), slot_plan.planned_slot_count);

    summary = registration.summarize(&device);
    try std.testing.expect(registration.queuePlanReady(summary));
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(registration.capabilitySetupReady(summary));
    try std.testing.expect(registration.multitouchSlotsReady(summary));
    try std.testing.expect(!registration.waitingOnCapabilitySetup(summary));
    try std.testing.expect(!registration.waitingOnMultitouchSlots(summary));
    try std.testing.expectEqual(@as(?virtio_input.RegistrationBlocker, null), summary.blocker);
    try std.testing.expect(registration.readyForRegistration(summary));
}
