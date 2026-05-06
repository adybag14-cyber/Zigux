const std = @import("std");
const virtio_input = @import("virtio_input");

test "virtio input wrapper-facing queue preflight advances in bounded order" {
    var device = try virtio_input.VirtioInputLab.init("verify-tablet", "verify-queue", 31, null);

    var summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqualStrings("event_queue_unconfigured", @tagName(summary.blocker.?));
    try std.testing.expect(!summary.ready_for_queue_callbacks);

    try device.configureEventQueue(16);
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqualStrings("status_queue_unconfigured", @tagName(summary.blocker.?));

    try device.configureStatusQueue(8);
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqualStrings("event_buffers_unfilled", @tagName(summary.blocker.?));

    _ = try device.fillEventBuffers();
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqualStrings("device_not_ready", @tagName(summary.blocker.?));
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);

    try device.markReady();
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.ready_for_queue_callbacks);
    try std.testing.expect(summary.blocker == null);
}

test "virtio input registration preflight keeps wrapper prerequisites ahead of registration claims" {
    var device = try virtio_input.VirtioInputLab.init("verify-touch", "verify-registration", 32, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();

    var summary = device.registrationPreflightSummary();
    try std.testing.expectEqualStrings("capability_setup_incomplete", @tagName(summary.blocker.?));
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(!summary.capability_setup_ready);
    try std.testing.expect(!summary.ready_for_registration);

    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 5,
    });

    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expectEqualStrings("multitouch_slots_unplanned", @tagName(summary.blocker.?));
    try std.testing.expect(!summary.multitouch_slots_ready);

    const slot_summary = try device.planMultitouchSlots();
    try std.testing.expectEqual(@as(u16, 6), slot_summary.planned_slot_count);

    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.multitouch_slots_ready);
    try std.testing.expect(summary.ready_for_registration);
    try std.testing.expect(summary.blocker == null);
}

test "virtio input registration preflight does not demand multitouch slots when ABS_MT_SLOT is absent" {
    var device = try virtio_input.VirtioInputLab.init("verify-tablet", "verify-no-mt", 33, null);

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
