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

test "phase10 virtio input plans multitouch slots from ABS_MT_SLOT before registration work" {
    var missing_abs_device = try virtio_input.VirtioInputLab.init("tablet", "serial-8", 8, null);
    try std.testing.expectError(error.AbsCapabilitiesNotConfigured, missing_abs_device.planMultitouchSlots());

    var missing_slot_bit_device = try virtio_input.VirtioInputLab.init("tablet", "serial-9", 9, null);
    try missing_slot_bit_device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{0});
    try std.testing.expectError(error.MultitouchSlotCapabilityMissing, missing_slot_bit_device.planMultitouchSlots());

    var negative_max_device = try virtio_input.VirtioInputLab.init("tablet", "serial-10", 10, null);
    try negative_max_device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try negative_max_device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = -1,
        .maximum = -1,
    });
    try std.testing.expectError(error.MultitouchSlotMaximumNegative, negative_max_device.planMultitouchSlots());

    var nonzero_min_device = try virtio_input.VirtioInputLab.init("tablet", "serial-11", 11, null);
    try nonzero_min_device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try nonzero_min_device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 1,
        .maximum = 4,
    });
    try std.testing.expectError(error.MultitouchSlotMinimumMustBeZero, nonzero_min_device.planMultitouchSlots());

    var oversized_device = try virtio_input.VirtioInputLab.init("tablet", "serial-12", 12, null);
    try oversized_device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try oversized_device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = virtio_input.multitouch_slot_capacity,
    });
    try std.testing.expectError(error.MultitouchSlotCountTooLarge, oversized_device.planMultitouchSlots());

    var ready_device = try virtio_input.VirtioInputLab.init("tablet", "serial-13", 13, null);
    try ready_device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{ 0, virtio_input.abs_mt_slot });
    try ready_device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 9,
    });

    const slot_summary = try ready_device.planMultitouchSlots();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", slot_summary.anchor);
    try std.testing.expectEqual(@as(u16, virtio_input.abs_mt_slot), slot_summary.abs_code);
    try std.testing.expectEqual(@as(u16, 9), slot_summary.advertised_slot_max);
    try std.testing.expectEqual(@as(u16, 10), slot_summary.planned_slot_count);
    try std.testing.expect(slot_summary.multitouch_enabled);

    try ready_device.configureEventQueue(8);
    try ready_device.configureStatusQueue(4);
    _ = try ready_device.fillEventBuffers();
    try ready_device.markReady();

    const status_summary = try ready_device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 1);
    try std.testing.expect(!status_summary.sent);
    try std.testing.expect(status_summary.suppressed_msc_timestamp);
    try std.testing.expectEqual(@as(usize, 1), status_summary.suppressed_status_count);
}

test "phase10 virtio input queue-callback preflight reports blockers before queue callbacks are enabled" {
    var device = try virtio_input.VirtioInputLab.init("tablet", "serial-13b", 13, null);

    var summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expect(!summary.event_queue_configured);
    try std.testing.expect(!summary.status_queue_configured);
    try std.testing.expectEqual(@as(u16, 0), summary.queued_event_buffer_count);
    try std.testing.expect(!summary.event_buffers_ready);
    try std.testing.expect(!summary.device_ready);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expect(!summary.ready_for_queue_callbacks);

    try device.configureEventQueue(8);
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.event_queue_configured);
    try std.testing.expect(!summary.status_queue_configured);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.status_queue_unconfigured, summary.blocker.?);

    try device.configureStatusQueue(4);
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.status_queue_configured);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.event_buffers_unfilled, summary.blocker.?);

    _ = try device.fillEventBuffers();
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expectEqual(@as(u16, 8), summary.queued_event_buffer_count);
    try std.testing.expect(summary.event_buffers_ready);
    try std.testing.expectEqual(virtio_input.QueueCallbackPreflightBlocker.device_not_ready, summary.blocker.?);
    try std.testing.expect(!summary.ready_for_queue_callbacks);

    try device.markReady();
    summary = device.queueCallbackPreflightSummary();
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(summary.ready_for_queue_callbacks);
    try std.testing.expect(summary.blocker == null);
}

test "phase10 virtio input registration preflight reports blockers before readiness" {
    var device = try virtio_input.VirtioInputLab.init("tablet", "serial-14", 14, null);

    var summary = device.registrationPreflightSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expect(!summary.queue_plan_ready);
    try std.testing.expect(!summary.ready_for_registration);

    try device.configureEventQueue(8);
    summary = device.registrationPreflightSummary();
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.status_queue_unconfigured, summary.blocker.?);

    try device.configureStatusQueue(4);
    summary = device.registrationPreflightSummary();
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.event_buffers_unfilled, summary.blocker.?);

    _ = try device.fillEventBuffers();
    summary = device.registrationPreflightSummary();
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.device_not_ready, summary.blocker.?);
    try std.testing.expect(summary.queue_plan_ready);

    try device.markReady();
    summary = device.registrationPreflightSummary();
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.capability_setup_incomplete, summary.blocker.?);
    try std.testing.expect(summary.device_ready);

    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 3,
    });

    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.capability_setup_ready);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.multitouch_slots_unplanned, summary.blocker.?);
    try std.testing.expect(!summary.multitouch_slots_ready);

    _ = try device.planMultitouchSlots();
    summary = device.registrationPreflightSummary();
    try std.testing.expect(summary.multitouch_slots_ready);
    try std.testing.expect(summary.ready_for_registration);
    try std.testing.expect(summary.blocker == null);
}

test "phase10 virtio input teardown observation keeps identity while surfacing reset-local state" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-15", 15, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.prop_bits, 0, &[_]u16{0});
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 3,
    });
    _ = try device.planMultitouchSlots();
    _ = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 1);
    _ = try device.sendStatus(0x11, 0x00, 7);

    const summary = device.teardownObservationSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqualStrings("touch-panel", summary.name);
    try std.testing.expectEqualStrings("serial-15", summary.serial);
    try std.testing.expectEqualStrings("virtio15/input0", summary.phys);
    try std.testing.expect(summary.event_queue_was_configured);
    try std.testing.expect(summary.status_queue_was_configured);
    try std.testing.expectEqual(@as(u16, 8), summary.queued_event_buffer_count);
    try std.testing.expectEqual(@as(usize, 1), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);
    try std.testing.expect(summary.ready_before_reset);
    try std.testing.expect(summary.multitouch_was_enabled);
    try std.testing.expectEqual(@as(u16, 4), summary.planned_multitouch_slots);
    try std.testing.expect(summary.preserves_identity);
    try std.testing.expect(summary.clears_runtime_state);
    try std.testing.expect(summary.clears_capability_state);
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
    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 7,
        .resolution = 16,
    });
    _ = try device.planMultitouchSlots();

    device.reset();

    const reset_snapshot = device.configSnapshot();
    try std.testing.expectEqualStrings(snapshot.anchor, reset_snapshot.anchor);
    try std.testing.expectEqualStrings(snapshot.name, reset_snapshot.name);
    try std.testing.expectEqualStrings(snapshot.serial, reset_snapshot.serial);
    try std.testing.expectEqualStrings(snapshot.phys, reset_snapshot.phys);
    try std.testing.expectEqual(snapshot.ids.bustype, reset_snapshot.ids.bustype);
    try std.testing.expectEqual(snapshot.ids.vendor, reset_snapshot.ids.vendor);
    try std.testing.expectEqual(snapshot.ids.product, reset_snapshot.ids.product);
    try std.testing.expectEqual(snapshot.ids.version, reset_snapshot.ids.version);
    try std.testing.expectEqual(@as(u16, virtio_input.bus_virtual), reset_snapshot.ids.bustype);
    try std.testing.expectError(error.EventQueueNotConfigured, device.queuePlanSummary());
    try std.testing.expectError(error.StatusQueueNotConfigured, device.sendStatus(0x11, 0x01, 1));
    try std.testing.expectError(error.ConfigBitmapNotConfigured, device.configBitmapSummary(.prop_bits, 0));
    try std.testing.expectError(error.AbsInfoNotConfigured, device.absInfoSummary(virtio_input.abs_mt_slot));
    try std.testing.expectError(error.CapabilityConfigNotConfigured, device.capabilitySetupSummary());
    try std.testing.expectError(error.AbsCapabilitiesNotConfigured, device.planMultitouchSlots());

    const preflight = device.registrationPreflightSummary();
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.event_queue_unconfigured, preflight.blocker.?);
    try std.testing.expect(!preflight.queue_plan_ready);
    try std.testing.expect(!preflight.device_ready);
    try std.testing.expect(!preflight.ready_for_registration);
}
