const std = @import("std");
const virtio_input = @import("virtio_input");
const teardown_observation = @import("virtio_input_teardown_observation");

test "phase10 virtio input teardown observation keeps identity while resettable runtime state stays explicit" {
    var device = try virtio_input.VirtioInputLab.init(
        "Virtio Touch Lab",
        "serial-24",
        3,
        .{
            .vendor = 0x1af4,
            .product = 0x1052,
            .version = 7,
        },
    );

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();

    const sent = try device.sendStatus(1, 2, 3);
    try std.testing.expect(sent.sent);
    try std.testing.expectEqual(@as(usize, 1), sent.queued_status_count);

    const summary = teardown_observation.summarize(&device);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", teardown_observation.anchor(summary));
    try std.testing.expectEqualStrings("Virtio Touch Lab", teardown_observation.name(summary));
    try std.testing.expectEqualStrings("serial-24", teardown_observation.serial(summary));
    try std.testing.expectEqualStrings("virtio3/input0", teardown_observation.phys(summary));
    const ids = teardown_observation.deviceIds(summary);
    try std.testing.expectEqual(@as(u16, virtio_input.bus_virtual), ids.bustype);
    try std.testing.expectEqual(@as(u16, 0x1af4), ids.vendor);
    try std.testing.expectEqual(@as(u16, 0x1052), ids.product);
    try std.testing.expectEqual(@as(u16, 7), ids.version);
    try std.testing.expect(teardown_observation.eventQueueWasConfigured(summary));
    try std.testing.expect(teardown_observation.statusQueueWasConfigured(summary));
    try std.testing.expectEqual(@as(u16, 16), teardown_observation.queuedEventBufferCount(summary));
    try std.testing.expectEqual(@as(usize, 1), teardown_observation.queuedStatusCount(summary));
    try std.testing.expectEqual(@as(usize, 0), teardown_observation.suppressedStatusCount(summary));
    try std.testing.expect(teardown_observation.readyBeforeReset(summary));
    try std.testing.expect(teardown_observation.preservesIdentity(summary));
    try std.testing.expect(teardown_observation.runtimeStateArmed(summary));
    try std.testing.expect(!teardown_observation.capabilityStateArmed(summary));

    device.reset();

    const snapshot = device.configSnapshot();
    try std.testing.expectEqualStrings("Virtio Touch Lab", snapshot.name);
    try std.testing.expectEqualStrings("serial-24", snapshot.serial);
    try std.testing.expectEqualStrings("virtio3/input0", snapshot.phys);
    try std.testing.expectEqual(@as(u16, virtio_input.bus_virtual), snapshot.ids.bustype);
    try std.testing.expectEqual(@as(u16, 0x1af4), snapshot.ids.vendor);
    try std.testing.expectEqual(@as(u16, 0x1052), snapshot.ids.product);
    try std.testing.expectEqual(@as(u16, 7), snapshot.ids.version);
    try std.testing.expectEqual(@as(u16, 0), device.event_descriptor_count);
    try std.testing.expectEqual(@as(u16, 0), device.status_descriptor_count);
    try std.testing.expectEqual(@as(u16, 0), device.queued_event_buffer_count);
    try std.testing.expectEqual(@as(usize, 0), device.queued_status_count);
    try std.testing.expect(!device.ready);
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

    const summary = teardown_observation.summarize(&device);
    try std.testing.expect(teardown_observation.eventQueueWasConfigured(summary));
    try std.testing.expect(teardown_observation.statusQueueWasConfigured(summary));
    try std.testing.expectEqual(@as(u16, 16), teardown_observation.queuedEventBufferCount(summary));
    try std.testing.expectEqual(@as(usize, 0), teardown_observation.queuedStatusCount(summary));
    try std.testing.expectEqual(@as(usize, 1), teardown_observation.suppressedStatusCount(summary));
    try std.testing.expect(teardown_observation.readyBeforeReset(summary));
    try std.testing.expect(teardown_observation.multitouchWasEnabled(summary));
    try std.testing.expectEqual(@as(u16, 6), teardown_observation.plannedMultitouchSlots(summary));
    try std.testing.expect(teardown_observation.runtimeStateArmed(summary));
    try std.testing.expect(teardown_observation.capabilityStateArmed(summary));

    device.reset();

    try std.testing.expectEqual(@as(usize, 0), device.suppressed_status_count);
    try std.testing.expectEqual(@as(usize, 0), device.config_bitmap_count);
    try std.testing.expectEqual(@as(usize, 0), device.abs_info_count);
    try std.testing.expectEqual(@as(u16, 0), device.planned_multitouch_slots);
    try std.testing.expect(!device.multitouch_enabled);

    const post_reset = teardown_observation.summarize(&device);
    try std.testing.expect(!teardown_observation.runtimeStateArmed(post_reset));
    try std.testing.expect(!teardown_observation.capabilityStateArmed(post_reset));
    try std.testing.expect(!teardown_observation.readyBeforeReset(post_reset));
    try std.testing.expect(!teardown_observation.multitouchWasEnabled(post_reset));
    try std.testing.expectEqual(@as(u16, 0), teardown_observation.plannedMultitouchSlots(post_reset));
    try std.testing.expectEqual(@as(usize, 0), teardown_observation.queuedStatusCount(post_reset));
    try std.testing.expectEqual(@as(usize, 0), teardown_observation.suppressedStatusCount(post_reset));
}
