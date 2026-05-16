const std = @import("std");
const virtio_input = @import("virtio_input");
const virtio_input_registration_preflight = @import("virtio_input_registration_preflight");

test "phase10 virtio input registration preflight reports blockers before readiness" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-registration", 17, null);

    var summary = virtio_input_registration_preflight.summarize(&device);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expect(!summary.event_queue_configured);
    try std.testing.expect(!summary.status_queue_configured);
    try std.testing.expect(!summary.event_buffers_ready);
    try std.testing.expect(!summary.queue_plan_ready);
    try std.testing.expect(!summary.device_ready);
    try std.testing.expect(!summary.capability_setup_ready);
    try std.testing.expect(!summary.multitouch_slots_ready);
    try std.testing.expectEqual(
        virtio_input_registration_preflight.RegistrationPreflightBlocker.event_queue_unconfigured,
        summary.blocker.?,
    );
    try std.testing.expectEqualStrings("event_queue_unconfigured", @tagName(summary.blocker.?));
    try std.testing.expect(!summary.ready_for_registration);

    try device.configureEventQueue(16);
    summary = virtio_input_registration_preflight.summarize(&device);
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(!summary.status_queue_configured);
    try std.testing.expect(!summary.event_buffers_ready);
    try std.testing.expect(!summary.queue_plan_ready);
    try std.testing.expectEqualStrings("status_queue_unconfigured", @tagName(summary.blocker.?));

    try device.configureStatusQueue(8);
    summary = virtio_input_registration_preflight.summarize(&device);
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expect(!summary.event_buffers_ready);
    try std.testing.expect(!summary.queue_plan_ready);
    try std.testing.expectEqualStrings("event_buffers_unfilled", @tagName(summary.blocker.?));

    _ = try device.fillEventBuffers();
    summary = virtio_input_registration_preflight.summarize(&device);
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expectEqualStrings("device_not_ready", @tagName(summary.blocker.?));
    try std.testing.expect(!summary.device_ready);

    try device.markReady();
    summary = virtio_input_registration_preflight.summarize(&device);
    try std.testing.expect(summary.device_ready);
    try std.testing.expectEqualStrings("capability_setup_incomplete", @tagName(summary.blocker.?));
    try std.testing.expect(!summary.capability_setup_ready);

    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{ .minimum = 0, .maximum = 5 });

    summary = virtio_input_registration_preflight.summarize(&device);
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expect(!summary.multitouch_slots_ready);
    try std.testing.expectEqual(
        virtio_input_registration_preflight.RegistrationPreflightBlocker.multitouch_slots_unplanned,
        summary.blocker.?,
    );
    try std.testing.expectEqualStrings("multitouch_slots_unplanned", @tagName(summary.blocker.?));
    try std.testing.expect(!summary.ready_for_registration);

    const slot_summary = try device.planMultitouchSlots();
    try std.testing.expectEqual(@as(u16, virtio_input.abs_mt_slot), slot_summary.abs_code);
    try std.testing.expectEqual(@as(u16, 5), slot_summary.advertised_slot_max);
    try std.testing.expectEqual(@as(u16, 6), slot_summary.planned_slot_count);
    try std.testing.expect(slot_summary.multitouch_enabled);

    summary = virtio_input_registration_preflight.summarize(&device);
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expect(summary.multitouch_slots_ready);
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(summary.ready_for_registration);
}

test "phase10 virtio input registration preflight keeps slot planning bounded ahead of lifecycle claims" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-bounded", 18, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{ .minimum = 0, .maximum = 1 });

    var summary = virtio_input_registration_preflight.summarize(&device);
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expect(!summary.multitouch_slots_ready);
    try std.testing.expectEqual(
        virtio_input_registration_preflight.RegistrationPreflightBlocker.multitouch_slots_unplanned,
        summary.blocker.?,
    );
    try std.testing.expect(!summary.ready_for_registration);

    const slot_summary = try device.planMultitouchSlots();
    try std.testing.expectEqual(@as(u16, 2), slot_summary.planned_slot_count);

    summary = virtio_input_registration_preflight.summarize(&device);
    try std.testing.expect(summary.multitouch_slots_ready);
    try std.testing.expect(summary.ready_for_registration);
}
