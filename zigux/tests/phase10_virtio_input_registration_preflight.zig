const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input registration preflight reports bounded blockers before registration handoff" {
    var device = try virtio_input.VirtioInputLab.init("tablet", "serial-registration", 41, null);

    var summary = device.registrationPreflightSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqual(
        virtio_input.RegistrationBlocker.event_queue_unconfigured,
        summary.blocker.?,
    );
    try std.testing.expect(!summary.queue_plan_ready);
    try std.testing.expect(!summary.device_ready);
    try std.testing.expect(!summary.capability_setup_ready);
    try std.testing.expect(summary.multitouch_slots_ready);
    try std.testing.expect(!summary.ready_for_registration);

    try device.configureEventQueue(8);
    summary = device.registrationPreflightSummary();
    try std.testing.expectEqual(
        virtio_input.RegistrationBlocker.status_queue_unconfigured,
        summary.blocker.?,
    );

    try device.configureStatusQueue(4);
    summary = device.registrationPreflightSummary();
    try std.testing.expectEqual(
        virtio_input.RegistrationBlocker.event_buffers_unfilled,
        summary.blocker.?,
    );

    _ = try device.fillEventBuffers();
    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expectEqual(
        virtio_input.RegistrationBlocker.device_not_ready,
        summary.blocker.?,
    );

    try device.markReady();
    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.device_ready);
    try std.testing.expectEqual(
        virtio_input.RegistrationBlocker.capability_setup_incomplete,
        summary.blocker.?,
    );

    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 5,
    });

    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expectEqual(
        virtio_input.RegistrationBlocker.multitouch_slots_unplanned,
        summary.blocker.?,
    );
    try std.testing.expect(!summary.multitouch_slots_ready);
    try std.testing.expect(!summary.ready_for_registration);

    const slot_summary = try device.planMultitouchSlots();
    try std.testing.expectEqual(@as(u16, 6), slot_summary.planned_slot_count);

    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.multitouch_slots_ready);
    try std.testing.expect(summary.ready_for_registration);
    try std.testing.expect(summary.blocker == null);
}

test "phase10 virtio input registration preflight does not require multitouch slots when ABS_MT_SLOT is absent" {
    var device = try virtio_input.VirtioInputLab.init("tablet", "serial-registration-no-mt", 42, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();

    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{0});
    try device.configureAbsInfo(0x00, .{
        .minimum = 0,
        .maximum = 1024,
        .resolution = 16,
    });

    const summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expect(summary.multitouch_slots_ready);
    try std.testing.expect(summary.ready_for_registration);
    try std.testing.expect(summary.blocker == null);
}
