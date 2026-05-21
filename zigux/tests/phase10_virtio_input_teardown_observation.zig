const std = @import("std");
const virtio_input = @import("virtio_input");
const teardown = @import("virtio_input_teardown_observation");

test "phase10 virtio input teardown observation keeps identity while resettable runtime state stays explicit" {
    const ids = virtio_input.DeviceIds{
        .vendor = 0x1af4,
        .product = 0x1052,
        .version = 7,
    };
    var device = try virtio_input.VirtioInputLab.init(
        "Virtio Touch Lab",
        "serial-24",
        3,
        ids,
    );

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();

    const sent = try device.sendStatus(1, 2, 3);
    try std.testing.expect(sent.sent);
    try std.testing.expectEqual(@as(usize, 1), sent.queued_status_count);

    const summary = teardown.summarize(&device);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqualStrings("Virtio Touch Lab", summary.name);
    try std.testing.expectEqualStrings("serial-24", summary.serial);
    try std.testing.expectEqualStrings("virtio3/input0", summary.phys);
    try std.testing.expect(teardown.idsMatch(summary, ids));
    try std.testing.expect(teardown.eventQueueConfigured(summary));
    try std.testing.expect(teardown.statusQueueConfigured(summary));
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);
    try std.testing.expectEqual(@as(usize, 1), teardown.queuedStatusCount(summary));
    try std.testing.expectEqual(@as(usize, 0), teardown.suppressedStatusCount(summary));
    try std.testing.expect(teardown.readyBeforeReset(summary));
    try std.testing.expect(teardown.preservesIdentity(summary));
    try std.testing.expect(teardown.runtimeStateArmed(summary));
    try std.testing.expect(!teardown.capabilityStateArmed(summary));

    device.reset();

    const post_reset = teardown.summarize(&device);
    const snapshot = device.configSnapshot();
    try std.testing.expectEqualStrings("Virtio Touch Lab", snapshot.name);
    try std.testing.expectEqualStrings("serial-24", snapshot.serial);
    try std.testing.expectEqualStrings("virtio3/input0", snapshot.phys);
    try std.testing.expectEqual(@as(u16, virtio_input.bus_virtual), snapshot.ids.bustype);
    try std.testing.expect(teardown.idsMatch(post_reset, ids));
    try std.testing.expect(!teardown.eventQueueConfigured(post_reset));
    try std.testing.expect(!teardown.statusQueueConfigured(post_reset));
    try std.testing.expectEqual(@as(usize, 0), teardown.queuedStatusCount(post_reset));
    try std.testing.expectEqual(@as(usize, 0), teardown.suppressedStatusCount(post_reset));
    try std.testing.expect(!teardown.readyBeforeReset(post_reset));
    try std.testing.expect(!teardown.runtimeStateArmed(post_reset));
    try std.testing.expect(!teardown.capabilityStateArmed(post_reset));
}

test "phase10 virtio input teardown observation reports capability and suppressed-status cleanup before reset" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-25", 4, null);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 5,
    });

    const slot_plan = try device.planMultitouchSlots();
    try std.testing.expect(slot_plan.multitouch_enabled);
    try std.testing.expectEqual(@as(u16, 6), slot_plan.planned_slot_count);

    const suppressed = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 88);
    try std.testing.expect(!suppressed.sent);
    try std.testing.expect(suppressed.suppressed_msc_timestamp);
    try std.testing.expectEqual(@as(usize, 0), suppressed.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), suppressed.suppressed_status_count);

    const summary = teardown.summarize(&device);
    try std.testing.expect(teardown.eventQueueConfigured(summary));
    try std.testing.expect(teardown.statusQueueConfigured(summary));
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);
    try std.testing.expectEqual(@as(usize, 0), teardown.queuedStatusCount(summary));
    try std.testing.expectEqual(@as(usize, 1), teardown.suppressedStatusCount(summary));
    try std.testing.expect(teardown.readyBeforeReset(summary));
    try std.testing.expect(summary.multitouch_was_enabled);
    try std.testing.expectEqual(@as(u16, 6), teardown.plannedMultitouchSlots(summary));
    try std.testing.expect(teardown.runtimeStateArmed(summary));
    try std.testing.expect(teardown.capabilityStateArmed(summary));

    device.reset();

    const post_reset = teardown.summarize(&device);
    try std.testing.expect(!teardown.eventQueueConfigured(post_reset));
    try std.testing.expect(!teardown.statusQueueConfigured(post_reset));
    try std.testing.expectEqual(@as(usize, 0), teardown.queuedStatusCount(post_reset));
    try std.testing.expectEqual(@as(usize, 0), teardown.suppressedStatusCount(post_reset));
    try std.testing.expectEqual(@as(u16, 0), teardown.plannedMultitouchSlots(post_reset));
    try std.testing.expect(!teardown.readyBeforeReset(post_reset));
    try std.testing.expect(!teardown.runtimeStateArmed(post_reset));
    try std.testing.expect(!teardown.capabilityStateArmed(post_reset));
}
