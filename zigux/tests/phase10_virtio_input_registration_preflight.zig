const std = @import("std");
const virtio_input = @import("virtio_input");
const registration = @import("virtio_input_registration_preflight");

test "phase10 virtio input registration preflight helper exposes blocker tags and ready transition" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-29", 8, null);

    var summary = registration.summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expectEqualStrings("event_queue_unconfigured", registration.blockerTag(summary.blocker.?));
    try std.testing.expect(!summary.ready_for_registration);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();

    summary = registration.summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.capability_setup_incomplete, summary.blocker.?);

    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 3,
    });
    summary = registration.summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.multitouch_slots_unplanned, summary.blocker.?);

    const slot_plan = try device.planMultitouchSlots();
    try std.testing.expectEqual(@as(u16, 4), slot_plan.planned_slot_count);

    summary = registration.summarize(&device);
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expect(summary.multitouch_slots_ready);
    try std.testing.expectEqual(@as(?virtio_input.RegistrationBlocker, null), summary.blocker);
    try std.testing.expect(summary.ready_for_registration);
}
