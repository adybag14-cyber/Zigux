const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input probe preflight keeps identity and capability staging ahead of registration claims" {
    var anonymous = try virtio_input.VirtioInputLab.init("", "", 31, null);

    var summary = anonymous.probePreflightSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.identity_incomplete, summary.blocker.?);
    try std.testing.expect(!summary.identity_ready);
    try std.testing.expect(!summary.queue_plan_ready);
    try std.testing.expect(!summary.capability_setup_ready);
    try std.testing.expect(!summary.ready_for_probe_handoff);

    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-direct", 32, null);

    summary = device.probePreflightSummary();
    try std.testing.expect(summary.identity_ready);
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.event_queue_unconfigured, summary.blocker.?);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();

    summary = device.probePreflightSummary();
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.capability_setup_incomplete, summary.blocker.?);
    try std.testing.expect(summary.queue_plan_ready);
    try std.testing.expect(!summary.device_ready);

    try device.markReady();
    summary = device.probePreflightSummary();
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.capability_setup_incomplete, summary.blocker.?);

    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{ .minimum = 0, .maximum = 5 });
    _ = try device.planMultitouchSlots();

    summary = device.probePreflightSummary();
    try std.testing.expect(summary.ready_for_probe_handoff);
    try std.testing.expect(summary.blocker == null);
}

test "phase10 virtio input probe preflight keeps serial optional while name and phys drive identity" {
    var serial_optional = try virtio_input.VirtioInputLab.init("touch-panel", "", 33, null);

    const summary = serial_optional.probePreflightSummary();
    try std.testing.expect(summary.identity_ready);
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expect(!summary.ready_for_probe_handoff);
}

test "phase10 virtio input registration preflight reports blockers before readiness" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-registration", 34, null);

    var summary = device.registrationPreflightSummary();
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expect(!summary.queue_plan_ready);
    try std.testing.expect(!summary.ready_for_registration);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{ .minimum = 0, .maximum = 3 });

    summary = device.registrationPreflightSummary();
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.multitouch_slots_unplanned, summary.blocker.?);
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expect(!summary.multitouch_slots_ready);

    _ = try device.planMultitouchSlots();
    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.ready_for_registration);
    try std.testing.expect(summary.blocker == null);
}

test "phase10 virtio input teardown observation keeps identity while surfacing reset-local state" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-teardown", 35, null);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{ .minimum = 0, .maximum = 5 });
    _ = try device.planMultitouchSlots();
    _ = try device.sendStatus(0x11, 0x01, 1);
    device.setMultitouch(true);
    _ = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 3);

    const summary = device.teardownObservationSummary();
    try std.testing.expect(summary.preserves_identity);
    try std.testing.expect(summary.clears_runtime_state);
    try std.testing.expect(summary.clears_capability_state);
    try std.testing.expectEqualStrings("touch-panel", summary.name);
}

test "phase10 virtio input reset clears queue plan and returns to default bus identity" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-reset", 36, null);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();

    const refill = try device.refillEventBuffers(4);
    try std.testing.expectEqual(@as(u16, 16), refill.queued_event_buffer_count_before);
    try std.testing.expectEqual(@as(u16, 16), refill.queued_event_buffer_count_after);

    device.reset();

    try std.testing.expectError(error.EventQueueNotConfigured, device.queuePlanSummary());

    const summary = device.teardownObservationSummary();
    try std.testing.expect(summary.preserves_identity);
    try std.testing.expect(!summary.clears_runtime_state);
    try std.testing.expect(!summary.clears_capability_state);

    const snapshot = device.configSnapshot();
    try std.testing.expectEqual(@as(u16, virtio_input.bus_virtual), snapshot.ids.bustype);
    try std.testing.expectEqual(@as(u16, 0), snapshot.ids.vendor);
    try std.testing.expectEqual(@as(u16, 0), snapshot.ids.product);
}
