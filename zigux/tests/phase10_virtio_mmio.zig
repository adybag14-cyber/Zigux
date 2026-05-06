const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

test "phase10 virtio mmio descriptor stays anchored to virtio_mmio.c" {
    const descriptor = virtio_mmio.VirtioMmioLab.descriptor();

    try std.testing.expectEqualStrings("virtio_mmio_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_validation);
    try std.testing.expect(descriptor.touches_transport_mmio);
    try std.testing.expect(!descriptor.touches_dma_paths);
}

test "phase10 virtio mmio rejects unaligned or unsupported register offsets" {
    var device = try virtio_mmio.VirtioMmioLab.init(18, &[_]u16{ 8, 16 });

    try std.testing.expectError(error.UnalignedRegisterOffset, device.readOffset(0x031));
    try std.testing.expectError(error.UnsupportedRegisterOffset, device.readOffset(0x040));
    try std.testing.expectError(error.RegisterOffsetOutOfRange, device.writeOffset(virtio_mmio.mmio_window_bytes, 0));
}

test "phase10 virtio mmio exposes a queue-selected register window in memory only" {
    var device = try virtio_mmio.VirtioMmioLab.init(18, &[_]u16{ 8, 16 });

    var summary = try device.readRegister(.queue_num_max);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expectEqual(virtio_mmio.Register.queue_num_max, summary.register);
    try std.testing.expectEqual(@as(u16, 0), summary.selected_queue);
    try std.testing.expectEqual(@as(u32, 8), summary.value);

    _ = try device.writeOffset(@intFromEnum(virtio_mmio.Register.queue_sel), 1);
    summary = try device.readRegister(.queue_num_max);
    try std.testing.expectEqual(@as(u16, 1), summary.selected_queue);
    try std.testing.expectEqual(@as(u32, 16), summary.value);

    _ = try device.writeRegister(.queue_num, 8);
    _ = try device.writeRegister(.queue_ready, 1);

    summary = try device.readRegister(.queue_num);
    try std.testing.expectEqual(@as(u32, 8), summary.value);

    summary = try device.readRegister(.queue_ready);
    try std.testing.expectEqual(@as(u32, 1), summary.value);
}

test "phase10 virtio mmio summarizes selected-queue readiness before queue handoff" {
    var device = try virtio_mmio.VirtioMmioLab.init(19, &[_]u16{ 8, 16 });

    var summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 8), summary.queue_num_max);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_num);
    try std.testing.expect(!summary.queue_ready);
    try std.testing.expect(!summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 8);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_ready, 1);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expect(summary.queue_ready);
    try std.testing.expect(summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_sel, 1);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 1), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 16), summary.queue_num_max);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_num);
    try std.testing.expect(!summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);
}

test "phase10 virtio mmio exposes a bounded device-feature selector read window" {
    var device = try virtio_mmio.VirtioMmioLab.init(41, &[_]u16{ 8, 16 });

    try device.stageDeviceFeatureWord(0, 0xa5a5_0001);
    try device.stageDeviceFeatureWord(1, 0x5a5a_0002);

    var summary = try device.readRegister(.device_features);
    try std.testing.expectEqual(virtio_mmio.Register.device_features, summary.register);
    try std.testing.expectEqual(@as(u32, 0xa5a5_0001), summary.value);

    _ = try device.writeRegister(.device_features_sel, 1);
    summary = try device.readRegister(.device_features_sel);
    try std.testing.expectEqual(@as(u32, 1), summary.value);
    summary = try device.readRegister(.device_features);
    try std.testing.expectEqual(@as(u32, 0x5a5a_0002), summary.value);

    try std.testing.expectError(error.FeatureWordSelectionOutOfRange, device.writeRegister(.device_features_sel, 2));
    try std.testing.expectError(error.FeatureWordSelectionOutOfRange, device.stageDeviceFeatureWord(2, 0));
    try std.testing.expectError(error.ReadOnlyRegister, device.writeRegister(.device_features, 0));
}

test "phase10 virtio mmio exposes a bounded config-word window before irq or lifecycle work" {
    var device = try virtio_mmio.VirtioMmioLab.init(52, &[_]u16{ 8, 16 });

    try device.stageConfigBytes(&[_]u8{
        0x78, 0x56, 0x34, 0x12,
        0xef, 0xcd, 0xab, 0x90,
    });
    device.bumpConfigGeneration();
    device.bumpConfigGeneration();

    var config_summary = try device.readConfigOffset(virtio_mmio.mmio_window_bytes);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", config_summary.anchor);
    try std.testing.expectEqual(virtio_mmio.mmio_window_bytes, config_summary.absolute_offset);
    try std.testing.expectEqual(@as(u32, 0), config_summary.relative_offset);
    try std.testing.expectEqual(@as(u32, 2), config_summary.config_generation);
    try std.testing.expectEqual(@as(u32, 0x1234_5678), config_summary.value);

    config_summary = try device.readConfigOffset(virtio_mmio.mmio_window_bytes + 4);
    try std.testing.expectEqual(@as(u32, 4), config_summary.relative_offset);
    try std.testing.expectEqual(@as(u32, 0x90ab_cdef), config_summary.value);

    try std.testing.expectError(error.ConfigOffsetBeforeWindow, device.readConfigOffset(@intFromEnum(virtio_mmio.Register.status)));
    try std.testing.expectError(error.UnalignedConfigOffset, device.readConfigOffset(virtio_mmio.mmio_window_bytes + 2));
    try std.testing.expectError(error.ConfigWindowReadOutOfRange, device.readConfigOffset(virtio_mmio.mmio_window_bytes + 8));
    try std.testing.expectError(error.ConfigWindowTooLarge, device.stageConfigBytes(&[_]u8{0} ** (virtio_mmio.config_window_capacity + 1)));
}

test "phase10 virtio mmio clears stale config words when a shorter window is restaged" {
    var device = try virtio_mmio.VirtioMmioLab.init(53, &[_]u16{ 8, 16 });

    try device.stageConfigBytes(&[_]u8{
        0x78, 0x56, 0x34, 0x12,
        0xef, 0xcd, 0xab, 0x90,
    });
    var config_summary = try device.readConfigOffset(virtio_mmio.mmio_window_bytes + 4);
    try std.testing.expectEqual(@as(u32, 0x90ab_cdef), config_summary.value);

    try device.stageConfigBytes(&[_]u8{
        0xaa, 0xbb, 0xcc, 0xdd,
    });
    config_summary = try device.readConfigOffset(virtio_mmio.mmio_window_bytes);
    try std.testing.expectEqual(@as(u32, 0xddcc_bbaa), config_summary.value);
    try std.testing.expectError(error.ConfigWindowReadOutOfRange, device.readConfigOffset(virtio_mmio.mmio_window_bytes + 4));
}

test "phase10 virtio mmio plans a bounded config-word write without mutating config space" {
    var device = try virtio_mmio.VirtioMmioLab.init(54, &[_]u16{ 8, 16 });

    try device.stageConfigBytes(&[_]u8{
        0x78, 0x56, 0x34, 0x12,
        0xef, 0xcd, 0xab, 0x90,
    });
    device.bumpConfigGeneration();

    const plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x1122_3344);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", plan.anchor);
    try std.testing.expectEqual(virtio_mmio.mmio_window_bytes + 4, plan.absolute_offset);
    try std.testing.expectEqual(@as(u32, 4), plan.relative_offset);
    try std.testing.expectEqual(@as(u32, 1), plan.config_generation);
    try std.testing.expectEqual(@as(u32, 0x90ab_cdef), plan.previous_value);
    try std.testing.expectEqual(@as(u32, 0x1122_3344), plan.planned_value);

    const config_summary = try device.readConfigOffset(virtio_mmio.mmio_window_bytes + 4);
    try std.testing.expectEqual(@as(u32, 0x90ab_cdef), config_summary.value);
    try std.testing.expectEqual(@as(u32, 1), config_summary.config_generation);

    try std.testing.expectError(error.ConfigOffsetBeforeWindow, device.planConfigWriteOffset(@intFromEnum(virtio_mmio.Register.status), 0));
    try std.testing.expectError(error.UnalignedConfigOffset, device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 2, 0));
    try std.testing.expectError(error.ConfigWindowReadOutOfRange, device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 8, 0));
}

test "phase10 virtio mmio summarizes a planned config-word write disposition without mutating config space" {
    var device = try virtio_mmio.VirtioMmioLab.init(54, &[_]u16{ 8, 16 });

    try device.stageConfigBytes(&[_]u8{
        0x78, 0x56, 0x34, 0x12,
        0xef, 0xcd, 0xab, 0x90,
    });
    device.bumpConfigGeneration();

    try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());

    const plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x1122_3344);
    try std.testing.expectEqual(@as(u32, 1), plan.config_generation);

    const disposition = try device.configWriteDispositionSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", disposition.anchor);
    try std.testing.expectEqual(virtio_mmio.mmio_window_bytes + 4, disposition.absolute_offset);
    try std.testing.expectEqual(@as(u32, 4), disposition.relative_offset);
    try std.testing.expectEqual(virtio_mmio.mmio_window_bytes + 8, disposition.end_offset);
    try std.testing.expectEqual(@as(u32, 1), disposition.config_generation);
    try std.testing.expectEqual(@as(u32, 0x90ab_cdef), disposition.previous_value);
    try std.testing.expectEqual(@as(u32, 0x1122_3344), disposition.planned_value);
    try std.testing.expectEqual(@as(u8, 0b1111), disposition.changed_byte_mask);

    const config_summary = try device.readConfigOffset(virtio_mmio.mmio_window_bytes + 4);
    try std.testing.expectEqual(@as(u32, 0x90ab_cdef), config_summary.value);
    try std.testing.expectEqual(@as(u32, 1), config_summary.config_generation);

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x90ab_cdef);
    const same_value = try device.configWriteDispositionSummary();
    try std.testing.expectEqual(@as(u8, 0), same_value.changed_byte_mask);

    device.bumpConfigGeneration();
    try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());
}

test "phase10 virtio mmio summarizes transport identity before lifecycle work" {
    var device = try virtio_mmio.VirtioMmioLab.init(55, &[_]u16{ 8, 16 });

    var summary = device.transportIdentitySummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, virtio_mmio.mmio_magic_value), summary.magic_value);
    try std.testing.expectEqual(@as(u32, virtio_mmio.mmio_version_modern), summary.version);
    try std.testing.expectEqual(@as(u32, 55), summary.device_id);
    try std.testing.expectEqual(@as(u32, virtio_mmio.default_vendor_id), summary.vendor_id);
    try std.testing.expect(summary.magic_matches);
    try std.testing.expect(summary.version_supported);
    try std.testing.expect(summary.device_present);
    try std.testing.expect(summary.vendor_id_present);
    try std.testing.expect(!summary.requires_legacy_guest_page_size);

    device.device_id = 0;
    device.vendor_id = 0;
    summary = device.transportIdentitySummary();
    try std.testing.expect(!summary.device_present);
    try std.testing.expect(!summary.vendor_id_present);
}

test "phase10 virtio mmio summarizes bounded probe preflight readiness before lifecycle work" {
    var device = try virtio_mmio.VirtioMmioLab.init(55, &[_]u16{ 8, 16 });

    const identity = device.transportIdentitySummary();
    const summary = device.probePreflightSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expectEqual(identity.magic_matches, summary.magic_matches);
    try std.testing.expectEqual(identity.version_supported, summary.version_supported);
    try std.testing.expectEqual(identity.device_present, summary.device_present);
    try std.testing.expectEqual(identity.vendor_id_present, summary.vendor_id_present);
    try std.testing.expectEqual(identity.requires_legacy_guest_page_size, summary.requires_legacy_guest_page_size);
    try std.testing.expect(summary.legacy_guest_page_size_register_ready);
    try std.testing.expect(summary.bounded_queue_register_window_ready);
    try std.testing.expect(summary.interrupt_ack_ready);
    try std.testing.expect(summary.ready_for_probe_handoff);
}

test "phase10 virtio mmio keeps the legacy probe preflight path ready when transport identity stays aligned" {
    var device = try virtio_mmio.VirtioMmioLab.init(72, &[_]u16{ 8, 16 });

    device.seedTransportIdentity(
        virtio_mmio.mmio_magic_value,
        virtio_mmio.mmio_version_legacy,
        72,
        virtio_mmio.default_vendor_id,
    );

    const summary = device.probePreflightSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expect(summary.magic_matches);
    try std.testing.expect(summary.version_supported);
    try std.testing.expect(summary.device_present);
    try std.testing.expect(summary.vendor_id_present);
    try std.testing.expect(summary.requires_legacy_guest_page_size);
    try std.testing.expect(summary.legacy_guest_page_size_register_ready);
    try std.testing.expect(summary.bounded_queue_register_window_ready);
    try std.testing.expect(summary.interrupt_ack_ready);
    try std.testing.expect(summary.ready_for_probe_handoff);
}

test "phase10 virtio mmio marks probe preflight incomplete when identity presence falls away" {
    var device = try virtio_mmio.VirtioMmioLab.init(0, &[_]u16{8});
    device.vendor_id = 0;

    const identity = device.transportIdentitySummary();
    const summary = device.probePreflightSummary();
    try std.testing.expect(summary.magic_matches);
    try std.testing.expect(summary.version_supported);
    try std.testing.expect(!identity.device_present);
    try std.testing.expect(!identity.vendor_id_present);
    try std.testing.expect(!summary.device_present);
    try std.testing.expect(!summary.vendor_id_present);
    try std.testing.expect(summary.bounded_queue_register_window_ready);
    try std.testing.expect(summary.interrupt_ack_ready);
    try std.testing.expect(!summary.ready_for_probe_handoff);
}

test "phase10 virtio mmio marks probe preflight incomplete when transport identity drifts" {
    var device = try virtio_mmio.VirtioMmioLab.init(71, &[_]u16{ 8, 16 });

    device.seedTransportIdentity(0x0, 0x3, 71, virtio_mmio.default_vendor_id);

    const identity = device.transportIdentitySummary();
    const summary = device.probePreflightSummary();
    try std.testing.expect(!identity.magic_matches);
    try std.testing.expect(!identity.version_supported);
    try std.testing.expect(identity.device_present);
    try std.testing.expect(identity.vendor_id_present);
    try std.testing.expect(!identity.requires_legacy_guest_page_size);
    try std.testing.expect(!summary.magic_matches);
    try std.testing.expect(!summary.version_supported);
    try std.testing.expect(summary.device_present);
    try std.testing.expect(summary.vendor_id_present);
    try std.testing.expect(summary.bounded_queue_register_window_ready);
    try std.testing.expect(summary.interrupt_ack_ready);
    try std.testing.expect(!summary.ready_for_probe_handoff);
}

test "phase10 virtio mmio bounds queue selection and queue sizing before lifecycle work" {
    var device = try virtio_mmio.VirtioMmioLab.init(24, &[_]u16{8});

    try std.testing.expectError(error.QueueSelectionOutOfRange, device.writeRegister(.queue_sel, 1));
    try std.testing.expectError(error.EmptyQueueSize, device.writeRegister(.queue_num, 0));
    try std.testing.expectError(error.QueueSizeMustBePowerOfTwo, device.writeRegister(.queue_num, 3));
    try std.testing.expectError(error.QueueSizeExceedsMaximum, device.writeRegister(.queue_num, 16));
    try std.testing.expectError(error.QueueReadyValueOutOfRange, device.writeRegister(.queue_ready, 2));
}

test "phase10 virtio mmio keeps status and config-generation bookkeeping inside the helper" {
    var device = try virtio_mmio.VirtioMmioLab.init(33, &[_]u16{ 8, 32 });

    _ = try device.writeRegister(.status, 3);
    _ = try device.writeRegister(.driver_features, 0x55aa);
    _ = try device.writeRegister(.device_features_sel, 1);
    device.stageInterruptStatus(0x3);
    device.bumpConfigGeneration();
    device.bumpConfigGeneration();

    const summary = device.windowSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 2), summary.configured_queue_count);
    try std.testing.expectEqual(@as(u32, 1), summary.selected_device_feature_word);
    try std.testing.expectEqual(@as(u8, 3), summary.status);
    try std.testing.expectEqual(@as(u32, 0x3), summary.interrupt_status);
    try std.testing.expectEqual(@as(u32, 2), summary.config_generation);

    var read_summary = try device.readRegister(.driver_features);
    try std.testing.expectEqual(@as(u32, 0x55aa), read_summary.value);
    read_summary = try device.readRegister(.interrupt_status);
    try std.testing.expectEqual(@as(u32, 0x3), read_summary.value);
    read_summary = try device.readRegister(.config_generation);
    try std.testing.expectEqual(@as(u32, 2), read_summary.value);

    try std.testing.expectError(error.ReadOnlyRegister, device.writeRegister(.interrupt_status, 0));
    try std.testing.expectError(error.ReadOnlyRegister, device.writeRegister(.queue_num_max, 8));
}
