const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

test "phase10 virtio mmio descriptor stays anchored to virtio_mmio.c" {
    const descriptor = virtio_mmio.VirtioMmioRegisterWindowLab.descriptor();

    try std.testing.expectEqualStrings("virtio_mmio_register_window_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_validation);
    try std.testing.expect(descriptor.touches_transport_mmio);
    try std.testing.expect(!descriptor.touches_dma_paths);
}

test "phase10 virtio mmio snapshots transport identity without claiming probe parity" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.init(.{ 0, 0 }, 0);

    var identity = window.deviceIdentitySummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", identity.anchor);
    try std.testing.expectEqual(@as(u32, virtio_mmio.expected_magic_value), identity.magic_value);
    try std.testing.expectEqual(@as(u32, virtio_mmio.modern_transport_version), identity.version);
    try std.testing.expectEqual(@as(u32, 0), identity.device_id);
    try std.testing.expectEqual(@as(u32, 0), identity.vendor_id);
    try std.testing.expect(identity.magic_matches);
    try std.testing.expect(identity.version_supported);
    try std.testing.expect(!identity.device_present);

    identity = window.seedTransportIdentity(virtio_mmio.expected_magic_value, virtio_mmio.legacy_transport_version, 16, 0x554d4551);
    try std.testing.expect(identity.magic_matches);
    try std.testing.expect(identity.version_supported);
    try std.testing.expect(identity.device_present);
    try std.testing.expectEqual(@as(u32, 16), identity.device_id);
    try std.testing.expectEqual(@as(u32, 0x554d4551), identity.vendor_id);

    identity = window.seedTransportIdentity(0, 3, 0, 0x1234);
    try std.testing.expect(!identity.magic_matches);
    try std.testing.expect(!identity.version_supported);
    try std.testing.expect(!identity.device_present);
    try std.testing.expectEqual(@as(u32, 0x1234), identity.vendor_id);
}

test "phase10 virtio mmio selects feature pages and records driver feature writes" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.init(.{ 0x89abcdef, 0x01234567 }, 7);

    var summary = try window.featureWindowSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 0), summary.selected_device_page);
    try std.testing.expectEqual(@as(u32, 0), summary.selected_driver_page);
    try std.testing.expectEqual(@as(u32, 0x89abcdef), summary.selected_device_features);
    try std.testing.expectEqual(@as(u32, 0), summary.selected_driver_features);

    try window.selectDeviceFeaturePage(1);
    try window.selectDriverFeaturePage(1);
    summary = try window.writeSelectedDriverFeatures(0x0000ffff);

    try std.testing.expectEqual(@as(u32, 1), summary.selected_device_page);
    try std.testing.expectEqual(@as(u32, 1), summary.selected_driver_page);
    try std.testing.expectEqual(@as(u32, 0x01234567), summary.selected_device_features);
    try std.testing.expectEqual(@as(u32, 0x0000ffff), summary.selected_driver_features);

    try std.testing.expectError(error.FeaturePageOutOfRange, window.selectDeviceFeaturePage(virtio_mmio.supported_feature_pages));
    try std.testing.expectError(error.FeaturePageOutOfRange, window.selectDriverFeaturePage(virtio_mmio.supported_feature_pages));
}

test "phase10 virtio mmio plans queue registers without claiming queue setup" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.initWithQueueMaximums(
        .{ 0, 0 },
        0,
        .{ 8, 16 },
    );

    var queue = try window.queueRegisterSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", queue.anchor);
    try std.testing.expectEqual(@as(u32, 0), queue.selected_queue);
    try std.testing.expectEqual(@as(u16, 8), queue.selected_queue_size_max);
    try std.testing.expectEqual(@as(u16, 0), queue.selected_queue_size);
    try std.testing.expect(!queue.selected_queue_ready);

    queue = try window.selectQueue(1);
    try std.testing.expectEqual(@as(u32, 1), queue.selected_queue);
    try std.testing.expectEqual(@as(u16, 16), queue.selected_queue_size_max);
    try std.testing.expectEqual(@as(u16, 0), queue.selected_queue_size);
    try std.testing.expect(!queue.selected_queue_ready);

    try std.testing.expectError(error.QueueIndexOutOfRange, window.selectQueue(virtio_mmio.supported_queues));
    try std.testing.expectError(error.QueueReadyRequiresConfiguredSize, window.writeSelectedQueueReady(true));

    queue = try window.writeSelectedQueueSize(12);
    try std.testing.expectEqual(@as(u16, 12), queue.selected_queue_size);
    try std.testing.expect(!queue.selected_queue_ready);

    try std.testing.expectError(error.QueueSizeExceedsMaximum, window.writeSelectedQueueSize(17));

    queue = try window.writeSelectedQueueReady(true);
    try std.testing.expect(queue.selected_queue_ready);

    try std.testing.expectError(error.QueueReadyBlocksResize, window.writeSelectedQueueSize(8));

    queue = try window.writeSelectedQueueReady(false);
    try std.testing.expect(!queue.selected_queue_ready);
    queue = try window.writeSelectedQueueSize(8);
    try std.testing.expectEqual(@as(u16, 8), queue.selected_queue_size);
}

test "phase10 virtio mmio snapshots queue notify without claiming side effects" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.initWithQueueMaximums(
        .{ 0, 0 },
        0,
        .{ 8, 16 },
    );

    try std.testing.expectError(error.QueueNotifyRequiresConfiguredSize, window.notifySelectedQueue());

    _ = try window.selectQueue(1);
    _ = try window.writeSelectedQueueSize(12);
    try std.testing.expectError(error.QueueNotifyRequiresReadyQueue, window.notifySelectedQueue());

    _ = try window.writeSelectedQueueReady(true);
    var notify = try window.notifySelectedQueue();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", notify.anchor);
    try std.testing.expectEqual(@as(u32, 1), notify.selected_queue);
    try std.testing.expectEqual(@as(u32, 1), notify.notified_queue);
    try std.testing.expectEqual(@as(u16, 12), notify.queue_size);
    try std.testing.expect(notify.queue_ready_before_notify);
    try std.testing.expectEqual(@as(usize, 1), notify.notification_count);

    notify = try window.notifySelectedQueue();
    try std.testing.expectEqual(@as(usize, 2), notify.notification_count);
}

test "phase10 virtio mmio plans queue address windows without claiming queue setup" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.initWithQueueMaximums(
        .{ 0, 0 },
        0,
        .{ 8, 16 },
    );

    try std.testing.expectError(error.QueueAddressRequiresConfiguredSize, window.planLegacyQueueAddress(4096, 4096, 0x1234));

    _ = try window.selectQueue(1);
    _ = try window.writeSelectedQueueSize(12);

    try std.testing.expectError(error.LegacyGuestPageSizeMustBeNonZero, window.planLegacyQueueAddress(0, 4096, 0x1234));
    try std.testing.expectError(error.LegacyQueueAlignMustBeNonZero, window.planLegacyQueueAddress(4096, 0, 0x1234));
    try std.testing.expectError(error.LegacyQueuePfnMustBeNonZero, window.planLegacyQueueAddress(4096, 4096, 0));

    const legacy = try window.planLegacyQueueAddress(4096, 4096, 0x1234);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", legacy.anchor);
    try std.testing.expectEqual(@as(u32, 1), legacy.selected_queue);
    try std.testing.expectEqual(virtio_mmio.QueueAddressKind.legacy, legacy.kind);
    try std.testing.expectEqual(@as(?u32, 4096), legacy.legacy_guest_page_size);
    try std.testing.expectEqual(@as(?u32, 4096), legacy.legacy_queue_align);
    try std.testing.expectEqual(@as(?u32, 0x1234), legacy.legacy_queue_pfn);
    try std.testing.expectEqual(@as(?u64, null), legacy.modern_desc);
    try std.testing.expectEqual(@as(u16, 12), legacy.queue_size);
    try std.testing.expect(!legacy.queue_ready);

    try std.testing.expectError(error.ModernQueueDescMustBeNonZero, window.planModernQueueAddress(0, 0x2000, 0x3000));
    try std.testing.expectError(error.ModernQueueAvailMustBeNonZero, window.planModernQueueAddress(0x1000, 0, 0x3000));
    try std.testing.expectError(error.ModernQueueUsedMustBeNonZero, window.planModernQueueAddress(0x1000, 0x2000, 0));

    const modern = try window.planModernQueueAddress(0x1000, 0x2000, 0x3000);
    try std.testing.expectEqual(virtio_mmio.QueueAddressKind.modern, modern.kind);
    try std.testing.expectEqual(@as(?u32, null), modern.legacy_guest_page_size);
    try std.testing.expectEqual(@as(?u32, null), modern.legacy_queue_align);
    try std.testing.expectEqual(@as(?u32, null), modern.legacy_queue_pfn);
    try std.testing.expectEqual(@as(?u64, 0x1000), modern.modern_desc);
    try std.testing.expectEqual(@as(?u64, 0x2000), modern.modern_avail);
    try std.testing.expectEqual(@as(?u64, 0x3000), modern.modern_used);
    try std.testing.expectEqual(@as(u16, 12), modern.queue_size);
    try std.testing.expect(!modern.queue_ready);

    _ = try window.writeSelectedQueueReady(true);
    try std.testing.expectError(error.QueueReadyBlocksAddressRewrite, window.planModernQueueAddress(0x4000, 0x5000, 0x6000));
}

test "phase10 virtio mmio keeps status writes separate from reset" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.initWithQueueMaximums(
        .{ 0, 0 },
        0,
        .{ 8, 16 },
    );

    _ = try window.selectQueue(1);
    _ = try window.writeSelectedQueueSize(16);
    _ = try window.planModernQueueAddress(0x1000, 0x2000, 0x3000);
    _ = try window.writeSelectedQueueReady(true);
    _ = try window.notifySelectedQueue();
    try std.testing.expectError(error.ResetRequiresDedicatedPath, window.setStatus(0));

    var status = try window.setStatus(0x07);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", status.anchor);
    try std.testing.expectEqual(@as(u8, 0x07), status.status);
    try std.testing.expectEqual(@as(usize, 0), status.reset_count);

    status = window.reset();
    try std.testing.expectEqual(@as(u8, 0), status.status);
    try std.testing.expectEqual(@as(usize, 1), status.reset_count);

    const queue = try window.queueRegisterSummary();
    try std.testing.expectEqual(@as(u32, 0), queue.selected_queue);
    try std.testing.expectEqual(@as(u16, 8), queue.selected_queue_size_max);
    try std.testing.expectEqual(@as(u16, 0), queue.selected_queue_size);
    try std.testing.expect(!queue.selected_queue_ready);
    try std.testing.expectError(error.QueueNotifyRequiresConfiguredSize, window.notifySelectedQueue());
    try std.testing.expectError(error.QueueAddressRequiresConfiguredSize, window.planModernQueueAddress(0x4000, 0x5000, 0x6000));
}

test "phase10 virtio mmio reset blocks stale queue, interrupt, and config-write state from leaking into reuse" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.initWithQueueMaximumsAndConfigWindow(
        .{ 0, 0 },
        4,
        .{ 8, 16 },
        .{ 0xaa, 0xbb, 0xcc, 0xdd, 0x10, 0x20, 0x30, 0x40, 0, 0, 0, 0, 0, 0, 0, 0 },
    );

    _ = try window.selectQueue(1);
    _ = try window.writeSelectedQueueSize(12);
    _ = try window.planModernQueueAddress(0x1000, 0x2000, 0x3000);
    _ = try window.writeSelectedQueueReady(true);
    _ = try window.notifySelectedQueue();
    _ = try window.planConfigWrite(0, .word, 0x11223344);
    try window.raiseInterrupt(virtio_mmio.supported_interrupt_bits);

    const original_config = try window.snapshotConfigWindow(0, .word);
    _ = window.reset();

    try std.testing.expectEqual(@as(?virtio_mmio.ConfigWritePlanSummary, null), window.pendingConfigWritePlan());
    try std.testing.expectEqual(@as(u32, 0), window.readInterruptStatus());

    var queue = try window.queueRegisterSummary();
    try std.testing.expectEqual(@as(u32, 0), queue.selected_queue);
    try std.testing.expectEqual(@as(u16, 8), queue.selected_queue_size_max);
    try std.testing.expectEqual(@as(u16, 0), queue.selected_queue_size);
    try std.testing.expect(!queue.selected_queue_ready);

    _ = try window.selectQueue(1);
    queue = try window.queueRegisterSummary();
    try std.testing.expectEqual(@as(u16, 16), queue.selected_queue_size_max);
    try std.testing.expectEqual(@as(u16, 0), queue.selected_queue_size);
    try std.testing.expect(!queue.selected_queue_ready);
    try std.testing.expectError(error.QueueNotifyRequiresConfiguredSize, window.notifySelectedQueue());
    try std.testing.expectError(error.QueueAddressRequiresConfiguredSize, window.planLegacyQueueAddress(4096, 4096, 0x80));

    const reset_config = try window.snapshotConfigWindow(0, .word);
    try std.testing.expectEqual(original_config.value, reset_config.value);
    try std.testing.expectEqual(original_config.generation, reset_config.generation);

    _ = try window.writeSelectedQueueSize(8);
    const legacy = try window.planLegacyQueueAddress(4096, 4096, 0x80);
    try std.testing.expectEqual(virtio_mmio.QueueAddressKind.legacy, legacy.kind);
    try std.testing.expectEqual(@as(?u32, 4096), legacy.legacy_guest_page_size);
    _ = try window.writeSelectedQueueReady(true);
    const notify = try window.notifySelectedQueue();
    try std.testing.expectEqual(@as(usize, 1), notify.notification_count);
}

test "phase10 virtio mmio tracks config generation changes without config-space IO" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.init(.{ 0, 0 }, 9);

    var generation = window.configGenerationSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", generation.anchor);
    try std.testing.expectEqual(@as(u32, 9), generation.generation);
    try std.testing.expect(!generation.changed);

    generation = window.bumpConfigGeneration();
    try std.testing.expectEqual(@as(u32, 10), generation.generation);
    try std.testing.expect(generation.changed);
}

test "phase10 virtio mmio snapshots a bounded config window without writes" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.initWithQueueMaximumsAndConfigWindow(
        .{ 0, 0 },
        11,
        .{ 8, 16 },
        .{ 0x34, 0x12, 0x78, 0x56, 0xbc, 0x9a, 0xf0, 0xde, 0x11, 0x22, 0x33, 0x44, 0, 0, 0, 0 },
    );

    var config = try window.snapshotConfigWindow(0, .half);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", config.anchor);
    try std.testing.expectEqual(@as(u32, 0), config.offset);
    try std.testing.expectEqual(virtio_mmio.ConfigWindowWidth.half, config.width);
    try std.testing.expectEqual(@as(u32, 11), config.generation);
    try std.testing.expectEqual(@as(u32, 0x1234), config.value);

    config = try window.snapshotConfigWindow(2, .word);
    try std.testing.expectEqual(@as(u32, 2), config.offset);
    try std.testing.expectEqual(virtio_mmio.ConfigWindowWidth.word, config.width);
    try std.testing.expectEqual(@as(u32, 0x9abc5678), config.value);

    _ = window.reset();
    config = try window.snapshotConfigWindow(8, .byte);
    try std.testing.expectEqual(@as(u32, 11), config.generation);
    try std.testing.expectEqual(@as(u32, 0x11), config.value);

    _ = window.bumpConfigGeneration();
    config = try window.snapshotConfigWindow(8, .half);
    try std.testing.expectEqual(@as(u32, 12), config.generation);
    try std.testing.expectEqual(@as(u32, 0x2211), config.value);

    try std.testing.expectError(error.ConfigWindowOutOfRange, window.snapshotConfigWindow(15, .half));
}

test "phase10 virtio mmio plans bounded config-window writes without side effects" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.initWithQueueMaximumsAndConfigWindow(
        .{ 0, 0 },
        11,
        .{ 8, 16 },
        .{ 0x34, 0x12, 0x78, 0x56, 0xbc, 0x9a, 0xf0, 0xde, 0x11, 0x22, 0x33, 0x44, 0, 0, 0, 0 },
    );

    const original = try window.snapshotConfigWindow(0, .half);
    var plan = try window.planConfigWrite(0, .half, 0xabcd);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", plan.anchor);
    try std.testing.expectEqual(@as(u32, 0), plan.offset);
    try std.testing.expectEqual(virtio_mmio.ConfigWindowWidth.half, plan.width);
    try std.testing.expectEqual(@as(u32, 11), plan.generation);
    try std.testing.expectEqual(@as(u32, 0x1234), plan.previous_value);
    try std.testing.expectEqual(@as(u32, 0xabcd), plan.planned_value);

    const pending_after_first_plan = window.pendingConfigWritePlan() orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(plan.offset, pending_after_first_plan.offset);
    try std.testing.expectEqual(plan.planned_value, pending_after_first_plan.planned_value);

    var config = try window.snapshotConfigWindow(0, .half);
    try std.testing.expectEqual(original.value, config.value);
    try std.testing.expectEqual(@as(u32, 11), config.generation);

    plan = try window.planConfigWrite(2, .word, 0x11223344);
    try std.testing.expectEqual(@as(u32, 0x9abc5678), plan.previous_value);
    try std.testing.expectEqual(@as(u32, 0x11223344), plan.planned_value);

    const pending_after_second_plan = window.pendingConfigWritePlan() orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(plan.offset, pending_after_second_plan.offset);
    try std.testing.expectEqual(plan.planned_value, pending_after_second_plan.planned_value);

    config = try window.snapshotConfigWindow(2, .word);
    try std.testing.expectEqual(@as(u32, 0x9abc5678), config.value);

    window.discardPendingConfigWritePlan();
    try std.testing.expectEqual(@as(?virtio_mmio.ConfigWritePlanSummary, null), window.pendingConfigWritePlan());

    _ = try window.planConfigWrite(8, .byte, 0x55);
    try std.testing.expect(window.pendingConfigWritePlan() != null);
    _ = window.reset();
    try std.testing.expectEqual(@as(?virtio_mmio.ConfigWritePlanSummary, null), window.pendingConfigWritePlan());
    config = try window.snapshotConfigWindow(8, .byte);
    try std.testing.expectEqual(@as(u32, 0x11), config.value);

    try std.testing.expectError(error.ConfigWriteValueTooWide, window.planConfigWrite(8, .byte, 0x100));
    try std.testing.expectError(error.ConfigWriteValueTooWide, window.planConfigWrite(8, .half, 0x1_0000));
    try std.testing.expectError(error.ConfigWindowOutOfRange, window.planConfigWrite(15, .half, 0xabcd));
}

test "phase10 virtio mmio summarizes bounded interrupt state and reset cleanup without claiming irq delivery" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.init(.{ 0, 0 }, 0);

    var summary = window.interruptSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 0), summary.pending_bits);
    try std.testing.expect(!summary.queue_interrupt_pending);
    try std.testing.expect(!summary.config_interrupt_pending);
    try std.testing.expect(!summary.line_asserted);

    try window.raiseInterrupt(virtio_mmio.queue_interrupt_bit);
    summary = window.interruptSummary();
    try std.testing.expectEqual(@as(u32, virtio_mmio.queue_interrupt_bit), summary.pending_bits);
    try std.testing.expect(summary.queue_interrupt_pending);
    try std.testing.expect(!summary.config_interrupt_pending);
    try std.testing.expect(summary.line_asserted);

    try window.raiseInterrupt(virtio_mmio.config_interrupt_bit);
    summary = window.interruptSummary();
    try std.testing.expectEqual(@as(u32, virtio_mmio.supported_interrupt_bits), summary.pending_bits);
    try std.testing.expect(summary.queue_interrupt_pending);
    try std.testing.expect(summary.config_interrupt_pending);
    try std.testing.expect(summary.line_asserted);

    _ = try window.acknowledgeInterrupt(virtio_mmio.queue_interrupt_bit);
    summary = window.interruptSummary();
    try std.testing.expectEqual(@as(u32, virtio_mmio.config_interrupt_bit), summary.pending_bits);
    try std.testing.expect(!summary.queue_interrupt_pending);
    try std.testing.expect(summary.config_interrupt_pending);
    try std.testing.expect(summary.line_asserted);

    _ = window.reset();
    summary = window.interruptSummary();
    try std.testing.expectEqual(@as(u32, 0), summary.pending_bits);
    try std.testing.expect(!summary.queue_interrupt_pending);
    try std.testing.expect(!summary.config_interrupt_pending);
    try std.testing.expect(!summary.line_asserted);
}

test "phase10 virtio mmio acknowledges only pending bounded interrupt bits" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.init(.{ 0, 0 }, 0);

    try std.testing.expectError(error.EmptyInterruptMask, window.raiseInterrupt(0));
    try std.testing.expectError(error.UnsupportedInterruptBits, window.raiseInterrupt(0x4));

    try window.raiseInterrupt(0x3);
    try std.testing.expectEqual(@as(u32, 0x3), window.readInterruptStatus());

    var ack = try window.acknowledgeInterrupt(0x1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", ack.anchor);
    try std.testing.expectEqual(@as(u32, 0x1), ack.acknowledged_bits);
    try std.testing.expectEqual(@as(u32, 0x3), ack.pending_bits_before_ack);
    try std.testing.expectEqual(@as(u32, 0x2), ack.pending_bits_after_ack);

    ack = try window.acknowledgeInterrupt(0x3);
    try std.testing.expectEqual(@as(u32, 0x2), ack.acknowledged_bits);
    try std.testing.expectEqual(@as(u32, 0x2), ack.pending_bits_before_ack);
    try std.testing.expectEqual(@as(u32, 0), ack.pending_bits_after_ack);

    try std.testing.expectError(error.EmptyInterruptMask, window.acknowledgeInterrupt(0));
    try std.testing.expectError(error.UnsupportedInterruptBits, window.acknowledgeInterrupt(0x8));
}
