const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input teardown observation captures reset-local cleanup cues without widening into remove lifecycle" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-teardown", 25, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{ virtio_input.abs_mt_slot, 0x30 });
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 5,
    });
    _ = try device.planMultitouchSlots();
    _ = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 7);
    _ = try device.sendStatus(0x11, 0x01, 9);

    const summary = device.teardownObservationSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqualStrings("touch-panel", summary.name);
    try std.testing.expectEqualStrings("serial-teardown", summary.serial);
    try std.testing.expectEqualStrings("virtio25/input0", summary.phys);
    try std.testing.expect(summary.event_queue_was_configured);
    try std.testing.expect(summary.status_queue_was_configured);
    try std.testing.expectEqual(@as(u16, 8), summary.queued_event_buffer_count);
    try std.testing.expectEqual(@as(usize, 1), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);
    try std.testing.expect(summary.ready_before_reset);
    try std.testing.expect(summary.multitouch_was_enabled);
    try std.testing.expectEqual(@as(u16, 6), summary.planned_multitouch_slots);
    try std.testing.expect(summary.preserves_identity);
    try std.testing.expect(summary.clears_runtime_state);
    try std.testing.expect(summary.clears_capability_state);

    device.reset();

    const registration = device.registrationPreflightSummary();
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.event_queue_unconfigured, registration.blocker.?);
    try std.testing.expect(!registration.queue_plan_ready);
    try std.testing.expect(!registration.device_ready);
    try std.testing.expect(!registration.capability_setup_ready);
    try std.testing.expect(registration.multitouch_slots_ready);
    try std.testing.expect(!registration.ready_for_registration);
}
