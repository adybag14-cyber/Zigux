const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input descriptor and identity snapshot stay lab-only and bounded" {
    const descriptor = virtio_input.VirtioInputLab.descriptor();
    try std.testing.expectEqualStrings("virtio_input_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_validation);
    try std.testing.expect(!descriptor.touches_transport_mmio);
    try std.testing.expect(!descriptor.touches_dma_paths);

    const ids = virtio_input.DeviceIds{
        .vendor = 0x1af4,
        .product = 0x1052,
        .version = 7,
    };
    const device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-24", 3, ids);
    const snapshot = device.configSnapshot();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", snapshot.anchor);
    try std.testing.expectEqualStrings("Virtio Touch Lab", snapshot.name);
    try std.testing.expectEqualStrings("serial-24", snapshot.serial);
    try std.testing.expectEqualStrings("virtio3/input0", snapshot.phys);
    try std.testing.expectEqual(@as(u16, virtio_input.bus_virtual), snapshot.ids.bustype);
    try std.testing.expectEqual(@as(u16, 0x1af4), snapshot.ids.vendor);
    try std.testing.expectEqual(@as(u16, 0x1052), snapshot.ids.product);
    try std.testing.expectEqual(@as(u16, 7), snapshot.ids.version);
}

test "phase10 virtio input queue planning caps and refills event buffers" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-25", 4, null);

    try std.testing.expectError(error.EmptyDescriptorCount, device.configureEventQueue(0));
    try std.testing.expectError(error.DescriptorCountMustBePowerOfTwo, device.configureEventQueue(3));

    try device.configureEventQueue(128);
    try std.testing.expectError(error.StatusQueueNotConfigured, device.refillEventBuffers(8));
    try device.configureStatusQueue(8);

    const planned = try device.fillEventBuffers();
    try std.testing.expectEqual(@as(u16, virtio_input.event_queue_index), planned.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_input.status_queue_index), planned.status_queue_index);
    try std.testing.expectEqual(@as(u16, 128), planned.event_descriptor_count);
    try std.testing.expectEqual(@as(u16, 8), planned.status_descriptor_count);
    try std.testing.expectEqual(@as(u16, virtio_input.static_event_buffer_capacity), planned.queued_event_buffer_count);
    try std.testing.expect(!planned.ready);

    const refilled = try device.refillEventBuffers(8);
    try std.testing.expectEqual(@as(u16, virtio_input.static_event_buffer_capacity), refilled.queued_event_buffer_count_before);
    try std.testing.expectEqual(@as(u16, 72), refilled.queued_event_buffer_count_after);

    const saturated = try device.refillEventBuffers(512);
    try std.testing.expectEqual(@as(u16, 72), saturated.queued_event_buffer_count_before);
    try std.testing.expectEqual(@as(u16, 128), saturated.queued_event_buffer_count_after);

    try device.markReady();
    const summary = try device.queuePlanSummary();
    try std.testing.expect(summary.ready);
}

test "phase10 virtio input probe preflight keeps serial optional while name and phys drive identity" {
    var serial_optional = try virtio_input.VirtioInputLab.init("touch-panel", "", 33, null);

    const summary = serial_optional.probePreflightSummary();
    try std.testing.expect(summary.identity_ready);
    try std.testing.expect(!summary.queue_plan_ready);
    try std.testing.expect(!summary.device_ready);
    try std.testing.expect(!summary.capability_setup_ready);
    try std.testing.expect(!summary.multitouch_slots_ready);
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expect(!summary.ready_for_probe_handoff);
}
