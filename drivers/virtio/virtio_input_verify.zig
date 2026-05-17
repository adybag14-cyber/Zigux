const std = @import("std");
const virtio_input = @import("virtio_input");
const teardown_observation = @import("virtio_input_teardown_observation");

test "phase10 virtio input verify keeps wrapper-facing queue preflight ordering explicit" {
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

test "phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims" {
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

test "phase10 virtio input verify keeps teardown wrapper parity explicit across reset" {
    var device = try virtio_input.VirtioInputLab.init("verify-teardown", "verify-reset", 33, null);
    const identity_before = device.configSnapshot();

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 3,
    });
    _ = try device.planMultitouchSlots();
    _ = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 1);
    _ = try device.sendStatus(0x02, 0x01, 7);

    const before_reset = teardown_observation.summarize(&device);
    try std.testing.expect(teardown_observation.preservesIdentity(before_reset));
    try std.testing.expect(teardown_observation.runtimeStateArmed(before_reset));
    try std.testing.expect(teardown_observation.capabilityStateArmed(before_reset));
    try std.testing.expect(before_reset.ready_before_reset);
    try std.testing.expect(before_reset.multitouch_was_enabled);
    try std.testing.expectEqual(@as(u16, 4), before_reset.planned_multitouch_slots);
    try std.testing.expectEqual(@as(usize, 1), before_reset.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), before_reset.suppressed_status_count);

    device.reset();

    const after_reset = teardown_observation.summarize(&device);
    const identity_after = device.configSnapshot();
    try std.testing.expect(teardown_observation.preservesIdentity(after_reset));
    try std.testing.expect(!teardown_observation.runtimeStateArmed(after_reset));
    try std.testing.expect(!teardown_observation.capabilityStateArmed(after_reset));
    try std.testing.expectEqual(@as(u16, 0), after_reset.queued_event_buffer_count);
    try std.testing.expectEqual(@as(usize, 0), after_reset.queued_status_count);
    try std.testing.expectEqual(@as(usize, 0), after_reset.suppressed_status_count);
    try std.testing.expect(!after_reset.ready_before_reset);
    try std.testing.expect(!after_reset.multitouch_was_enabled);
    try std.testing.expectEqual(@as(u16, 0), after_reset.planned_multitouch_slots);
    try std.testing.expectEqualDeep(identity_before.ids, identity_after.ids);
    try std.testing.expectEqualStrings(identity_before.name, identity_after.name);
    try std.testing.expectEqualStrings(identity_before.serial, identity_after.serial);
    try std.testing.expectEqualStrings(identity_before.phys, identity_after.phys);
}
