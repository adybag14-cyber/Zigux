const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input registration preflight keeps queue, ready, capability, and slot blockers explicit" {
    var device = try virtio_input.VirtioInputLab.init("probe-tablet", "registration-serial", 23, null);

    var summary = device.registrationPreflightSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expect(!summary.queue_plan_ready);
    try std.testing.expect(!summary.device_ready);
    try std.testing.expect(!summary.capability_setup_ready);
    try std.testing.expect(!summary.multitouch_slots_ready);
    try std.testing.expect(!summary.ready_for_registration);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();

    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expect(!summary.device_ready);
    try std.testing.expect(!summary.capability_setup_ready);
    try std.testing.expect(!summary.multitouch_slots_ready);
    try std.testing.expect(!summary.ready_for_registration);

    try device.markReady();
    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 5,
    });

    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expect(!summary.multitouch_slots_ready);
    try std.testing.expect(!summary.ready_for_registration);

    _ = try device.planMultitouchSlots();

    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expect(summary.multitouch_slots_ready);
    try std.testing.expect(summary.ready_for_registration);
}
