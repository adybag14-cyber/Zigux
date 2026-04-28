const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input descriptor snapshots identity and supported config selects" {
    const descriptor = virtio_input.VirtioInputLab.descriptor();
    try std.testing.expectEqualStrings("virtio_input_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_validation);
    try std.testing.expect(!descriptor.touches_transport_mmio);
    try std.testing.expect(!descriptor.touches_dma_paths);

    var device = try virtio_input.VirtioInputLab.init(
        "tablet-with-a-name-longer-than-sixty-four-bytes-to-prove-capped-copying",
        "serial-0007",
        7,
        .{
            .bustype = 0x18,
            .vendor = 0x1234,
            .product = 0x5678,
            .version = 0x0001,
        },
    );
    const snapshot = device.configSnapshot();

    try std.testing.expectEqualStrings("tablet-with-a-name-longer-than-sixty-four-bytes-to-prove-capped-", snapshot.name);
    try std.testing.expectEqualStrings("serial-0007", snapshot.serial);
    try std.testing.expectEqualStrings("virtio7/input0", snapshot.phys);
    try std.testing.expectEqual(@as(u16, 0x18), snapshot.ids.bustype);
    try std.testing.expectEqual(@as(u16, 0x1234), snapshot.ids.vendor);
    try std.testing.expectEqual(@as(u16, 0x5678), snapshot.ids.product);
    try std.testing.expectEqual(@as(u16, 0x0001), snapshot.ids.version);
    try std.testing.expectEqual(virtio_input.ConfigSelect.id_name, snapshot.supported_selects[0]);
    try std.testing.expectEqual(virtio_input.ConfigSelect.abs_info, snapshot.supported_selects[5]);
}

test "phase10 virtio input plans events and status queues with capped event buffers" {
    var device = try virtio_input.VirtioInputLab.init("zigux-tablet", "serial-1", 1, null);

    try std.testing.expectError(error.EventQueueNotConfigured, device.markReady());
    try std.testing.expectError(error.EmptyDescriptorCount, device.configureEventQueue(0));
    try std.testing.expectError(error.DescriptorCountMustBePowerOfTwo, device.configureEventQueue(3));

    try device.configureEventQueue(128);
    try std.testing.expectError(error.StatusQueueNotConfigured, device.fillEventBuffers());

    try device.configureStatusQueue(8);
    var summary = try device.fillEventBuffers();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, virtio_input.event_queue_index), summary.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_input.status_queue_index), summary.status_queue_index);
    try std.testing.expectEqual(@as(u16, 128), summary.event_descriptor_count);
    try std.testing.expectEqual(@as(u16, 8), summary.status_descriptor_count);
    try std.testing.expectEqual(@as(u16, virtio_input.static_event_buffer_capacity), summary.queued_event_buffer_count);
    try std.testing.expect(!summary.ready);

    try device.markReady();
    summary = try device.queuePlanSummary();
    try std.testing.expect(summary.ready);
}

test "phase10 virtio input suppresses MSC_TIMESTAMP status loops for multitouch devices" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-2", 2, null);

    try device.configureEventQueue(32);
    try device.configureStatusQueue(4);
    try std.testing.expectError(error.DeviceNotReady, device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 77));

    _ = try device.fillEventBuffers();
    try device.markReady();
    device.setMultitouch(true);

    var summary = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 88);
    try std.testing.expect(!summary.sent);
    try std.testing.expect(summary.suppressed_msc_timestamp);
    try std.testing.expectEqual(@as(usize, 0), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);

    summary = try device.sendStatus(0x11, 0x00, 1);
    try std.testing.expect(summary.sent);
    try std.testing.expect(!summary.suppressed_msc_timestamp);
    try std.testing.expectEqual(@as(usize, 1), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);
}

test "phase10 virtio input records bounded config bitmap summaries for property and event selectors" {
    var device = try virtio_input.VirtioInputLab.init("tablet", "serial-4", 4, null);

    try std.testing.expectError(
        error.UnsupportedConfigBitmapSelect,
        device.configureConfigBitmap(.abs_info, 0, &[_]u16{0}),
    );
    try std.testing.expectError(
        error.EmptyConfigBitmap,
        device.configureConfigBitmap(.prop_bits, 0, &[_]u16{}),
    );
    try std.testing.expectError(
        error.ConfigBitmapBitDuplicate,
        device.configureConfigBitmap(.prop_bits, 2, &[_]u16{ 1, 1 }),
    );
    try std.testing.expectError(
        error.ConfigBitmapBitOutOfRange,
        device.configureConfigBitmap(.prop_bits, 1, &[_]u16{virtio_input.config_bitmap_bit_capacity}),
    );

    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{ 0, 1, 5 });
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_msc, &[_]u16{ virtio_input.msc_timestamp, 0x06 });

    const prop_summary = try device.configBitmapSummary(.prop_bits, 0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", prop_summary.anchor);
    try std.testing.expectEqual(virtio_input.ConfigSelect.prop_bits, prop_summary.select);
    try std.testing.expectEqual(@as(u8, 0), prop_summary.subsel);
    try std.testing.expectEqual(@as(usize, 3), prop_summary.supported_bit_count);
    try std.testing.expect(!prop_summary.surfaces_selected_event_type);

    const event_summary = try device.configBitmapSummary(.ev_bits, virtio_input.ev_msc);
    try std.testing.expectEqual(virtio_input.ConfigSelect.ev_bits, event_summary.select);
    try std.testing.expectEqual(@as(u8, virtio_input.ev_msc), event_summary.subsel);
    try std.testing.expectEqual(@as(usize, 2), event_summary.supported_bit_count);
    try std.testing.expect(event_summary.surfaces_selected_event_type);
    try std.testing.expect(try device.configBitmapSupportsBit(.ev_bits, virtio_input.ev_msc, virtio_input.msc_timestamp));
    try std.testing.expect(!(try device.configBitmapSupportsBit(.prop_bits, 0, 9)));
    try std.testing.expectError(
        error.ConfigBitmapAlreadyConfigured,
        device.configureConfigBitmap(.ev_bits, virtio_input.ev_msc, &[_]u16{7}),
    );
    try std.testing.expectError(
        error.ConfigBitmapNotConfigured,
        device.configBitmapSummary(.ev_bits, 0x11),
    );
}

test "phase10 virtio input records bounded ABS metadata for configured axes" {
    var device = try virtio_input.VirtioInputLab.init("tablet", "serial-5", 5, null);

    try std.testing.expectError(
        error.AbsInfoRangeInvalid,
        device.configureAbsInfo(0x00, .{
            .minimum = 10,
            .maximum = 9,
        }),
    );
    try std.testing.expectError(
        error.AbsInfoNegativeFuzz,
        device.configureAbsInfo(0x00, .{
            .minimum = 0,
            .maximum = 100,
            .fuzz = -1,
        }),
    );
    try std.testing.expectError(
        error.AbsInfoNegativeResolution,
        device.configureAbsInfo(0x00, .{
            .minimum = 0,
            .maximum = 100,
            .resolution = -1,
        }),
    );

    try device.configureAbsInfo(0x00, .{
        .minimum = -2048,
        .maximum = 2047,
        .fuzz = 4,
        .flat = 8,
        .resolution = 32,
    });
    try device.configureAbsInfo(0x01, .{
        .minimum = 0,
        .maximum = 4095,
        .fuzz = 1,
        .flat = 0,
        .resolution = 48,
    });

    const x_summary = try device.absInfoSummary(0x00);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", x_summary.anchor);
    try std.testing.expectEqual(@as(u16, 0x00), x_summary.abs_code);
    try std.testing.expectEqual(@as(i32, -2048), x_summary.minimum);
    try std.testing.expectEqual(@as(i32, 2047), x_summary.maximum);
    try std.testing.expectEqual(@as(i32, 4), x_summary.fuzz);
    try std.testing.expectEqual(@as(i32, 8), x_summary.flat);
    try std.testing.expectEqual(@as(i32, 32), x_summary.resolution);

    const y_summary = try device.absInfoSummary(0x01);
    try std.testing.expectEqual(@as(u16, 0x01), y_summary.abs_code);
    try std.testing.expectEqual(@as(i32, 4095), y_summary.maximum);
    try std.testing.expectEqual(@as(i32, 48), y_summary.resolution);

    try std.testing.expectError(
        error.AbsInfoAlreadyConfigured,
        device.configureAbsInfo(0x00, .{
            .minimum = 0,
            .maximum = 1,
        }),
    );
    try std.testing.expectError(
        error.AbsInfoNotConfigured,
        device.absInfoSummary(0x02),
    );
}

test "phase10 virtio input stages capability setup from config bitmaps and ABS metadata" {
    var device = try virtio_input.VirtioInputLab.init("tablet", "serial-6", 6, null);

    try std.testing.expectError(
        error.CapabilityConfigNotConfigured,
        device.capabilitySetupSummary(),
    );

    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{ 0, 5 });
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_msc, &[_]u16{ virtio_input.msc_timestamp, 0x06 });
    try device.configureAbsInfo(0x00, .{
        .minimum = 0,
        .maximum = 1024,
        .resolution = 8,
    });
    try std.testing.expectError(
        error.AbsCapabilitiesNotConfigured,
        device.capabilitySetupSummary(),
    );

    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{1});
    try std.testing.expectError(
        error.AbsAxisMissingCapabilityBit,
        device.capabilitySetupSummary(),
    );

    var ready_device = try virtio_input.VirtioInputLab.init("tablet", "serial-7", 7, null);
    try ready_device.configureConfigBitmap(.prop_bits, 0, &[_]u16{ 0, 5 });
    try ready_device.configureConfigBitmap(.ev_bits, virtio_input.ev_msc, &[_]u16{ virtio_input.msc_timestamp, 0x06 });
    try ready_device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{ 0, 1 });
    try ready_device.configureAbsInfo(0x00, .{
        .minimum = -2048,
        .maximum = 2047,
        .fuzz = 4,
        .flat = 8,
        .resolution = 32,
    });
    try ready_device.configureAbsInfo(0x01, .{
        .minimum = 0,
        .maximum = 4095,
        .resolution = 48,
    });

    const summary = try ready_device.capabilitySetupSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 2), summary.property_bit_count);
    try std.testing.expectEqual(@as(usize, 2), summary.staged_event_type_count);
    try std.testing.expectEqual(@as(usize, 4), summary.staged_capability_count);
    try std.testing.expectEqual(@as(usize, 2), summary.staged_abs_param_count);
    try std.testing.expect(summary.stages_abs_params);
}

test "phase10 virtio input plans multitouch slots from ABS_MT_SLOT metadata" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-8", 8, null);

    try std.testing.expectError(
        error.CapabilityConfigNotConfigured,
        device.multitouchSlotPlanSummary(),
    );

    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try std.testing.expectError(
        error.MultitouchSlotAbsInfoNotConfigured,
        device.multitouchSlotPlanSummary(),
    );

    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = -1,
        .maximum = 7,
    });
    try std.testing.expectError(
        error.MultitouchSlotMinimumNegative,
        device.multitouchSlotPlanSummary(),
    );

    var ready_device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-9", 9, null);
    try ready_device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try ready_device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{ virtio_input.abs_mt_slot, 0x30 });
    try ready_device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 7,
    });

    const summary = try ready_device.multitouchSlotPlanSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqual(virtio_input.abs_mt_slot, summary.abs_code);
    try std.testing.expectEqual(@as(i32, 0), summary.minimum);
    try std.testing.expectEqual(@as(i32, 7), summary.maximum);
    try std.testing.expectEqual(@as(usize, 8), summary.slot_count);
    try std.testing.expectEqual(@as(usize, 1), summary.staged_abs_param_count);
    try std.testing.expect(summary.initializes_slots);
}

test "phase10 virtio input teardown summary keeps reset cleanup and identity preservation explicit" {
    var device = try virtio_input.VirtioInputLab.init("keyboard", "serial-10", 10, null);
    const identity_before = device.configSnapshot();

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    _ = try device.sendStatus(0x11, 0x01, 1);
    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{ 0, 5 });
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{0});
    try device.configureAbsInfo(0x00, .{
        .minimum = 0,
        .maximum = 1024,
        .resolution = 16,
    });
    device.setMultitouch(true);

    var summary = device.teardownPlanSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expect(summary.ready);
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);
    try std.testing.expectEqual(@as(usize, 1), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 0), summary.suppressed_status_count);
    try std.testing.expectEqual(@as(usize, 2), summary.config_bitmap_count);
    try std.testing.expectEqual(@as(usize, 1), summary.abs_info_count);
    try std.testing.expect(summary.multitouch_enabled);
    try std.testing.expect(summary.clears_queue_plan_on_reset);
    try std.testing.expect(summary.clears_status_counters_on_reset);
    try std.testing.expect(summary.clears_config_on_reset);
    try std.testing.expect(summary.clears_abs_info_on_reset);
    try std.testing.expect(summary.clears_multitouch_on_reset);
    try std.testing.expect(summary.preserves_identity_strings);

    device.reset();

    summary = device.teardownPlanSummary();
    try std.testing.expect(!summary.ready);
    try std.testing.expectEqual(@as(u16, 0), summary.queued_event_buffer_count);
    try std.testing.expectEqual(@as(usize, 0), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 0), summary.suppressed_status_count);
    try std.testing.expectEqual(@as(usize, 0), summary.config_bitmap_count);
    try std.testing.expectEqual(@as(usize, 0), summary.abs_info_count);
    try std.testing.expect(!summary.multitouch_enabled);
    try std.testing.expect(summary.clears_queue_plan_on_reset);
    try std.testing.expect(summary.clears_status_counters_on_reset);
    try std.testing.expect(summary.clears_config_on_reset);
    try std.testing.expect(summary.clears_abs_info_on_reset);
    try std.testing.expect(summary.clears_multitouch_on_reset);
    try std.testing.expect(summary.preserves_identity_strings);

    const identity_after = device.configSnapshot();
    try std.testing.expectEqualStrings(identity_before.name, identity_after.name);
    try std.testing.expectEqualStrings(identity_before.serial, identity_after.serial);
    try std.testing.expectEqualStrings(identity_before.phys, identity_after.phys);
    try std.testing.expectEqual(identity_before.ids.bustype, identity_after.ids.bustype);
}

test "phase10 virtio input reset clears queue plan and returns to default bus identity" {
    var device = try virtio_input.VirtioInputLab.init("keyboard", "serial-3", 3, null);
    const snapshot = device.configSnapshot();
    try std.testing.expectEqual(@as(u16, virtio_input.bus_virtual), snapshot.ids.bustype);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    _ = try device.sendStatus(0x11, 0x01, 1);
    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{ 0, 5 });
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{0});
    try device.configureAbsInfo(0x00, .{
        .minimum = 0,
        .maximum = 1024,
        .resolution = 16,
    });
    device.setMultitouch(true);

    device.reset();

    try std.testing.expectError(error.EventQueueNotConfigured, device.queuePlanSummary());
    try std.testing.expectError(error.StatusQueueNotConfigured, device.sendStatus(0x11, 0x01, 1));
    try std.testing.expectError(error.ConfigBitmapNotConfigured, device.configBitmapSummary(.prop_bits, 0));
    try std.testing.expectError(error.AbsInfoNotConfigured, device.absInfoSummary(0x00));
    try std.testing.expectError(error.CapabilityConfigNotConfigured, device.capabilitySetupSummary());
    try std.testing.expectError(error.CapabilityConfigNotConfigured, device.multitouchSlotPlanSummary());
}
