const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

test "phase10 virtio mmio keeps queue state isolated across queue selection changes" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.initWithQueueMaximums(
        .{ 0, 0 },
        0,
        .{ 8, 16 },
    );

    var queue = try window.selectQueue(0);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", queue.anchor);
    try std.testing.expectEqual(@as(u16, 8), queue.selected_queue_size_max);
    _ = try window.writeSelectedQueueSize(8);
    const legacy = try window.planLegacyQueueAddress(4096, 4096, 0x80);
    try std.testing.expectEqual(virtio_mmio.QueueAddressKind.legacy, legacy.kind);
    try std.testing.expectEqual(@as(?u32, 4096), legacy.legacy_guest_page_size);
    try std.testing.expectEqual(@as(?u32, 0x80), legacy.legacy_queue_pfn);
    _ = try window.writeSelectedQueueReady(true);

    queue = try window.selectQueue(1);
    try std.testing.expectEqual(@as(u32, 1), queue.selected_queue);
    try std.testing.expectEqual(@as(u16, 16), queue.selected_queue_size_max);
    try std.testing.expectEqual(@as(u16, 0), queue.selected_queue_size);
    try std.testing.expect(!queue.selected_queue_ready);
    _ = try window.writeSelectedQueueSize(12);
    const modern = try window.planModernQueueAddress(0x1000, 0x2000, 0x3000);
    try std.testing.expectEqual(virtio_mmio.QueueAddressKind.modern, modern.kind);
    try std.testing.expectEqual(@as(?u64, 0x1000), modern.modern_desc);
    try std.testing.expectEqual(@as(?u64, 0x3000), modern.modern_used);
    _ = try window.writeSelectedQueueReady(true);
    const first_notify = try window.notifySelectedQueue();
    try std.testing.expectEqual(@as(u32, 1), first_notify.notified_queue);
    try std.testing.expectEqual(@as(usize, 1), first_notify.notification_count);

    queue = try window.selectQueue(0);
    try std.testing.expectEqual(@as(u16, 8), queue.selected_queue_size);
    try std.testing.expect(queue.selected_queue_ready);
    const preserved_legacy = try window.queueAddressSummary(.legacy);
    try std.testing.expectEqual(@as(?u32, 4096), preserved_legacy.legacy_guest_page_size);
    try std.testing.expectEqual(@as(?u32, 4096), preserved_legacy.legacy_queue_align);
    try std.testing.expectEqual(@as(?u32, 0x80), preserved_legacy.legacy_queue_pfn);
    try std.testing.expectEqual(@as(?u64, null), preserved_legacy.modern_desc);
    try std.testing.expectError(error.QueueReadyBlocksAddressRewrite, window.planLegacyQueueAddress(4096, 4096, 0x81));

    queue = try window.selectQueue(1);
    try std.testing.expectEqual(@as(u16, 12), queue.selected_queue_size);
    try std.testing.expect(queue.selected_queue_ready);
    const preserved_modern = try window.queueAddressSummary(.modern);
    try std.testing.expectEqual(@as(?u32, null), preserved_modern.legacy_guest_page_size);
    try std.testing.expectEqual(@as(?u64, 0x1000), preserved_modern.modern_desc);
    try std.testing.expectEqual(@as(?u64, 0x2000), preserved_modern.modern_avail);
    try std.testing.expectEqual(@as(?u64, 0x3000), preserved_modern.modern_used);
    const second_notify = try window.notifySelectedQueue();
    try std.testing.expectEqual(@as(u32, 1), second_notify.notified_queue);
    try std.testing.expectEqual(@as(usize, 2), second_notify.notification_count);
}

test "phase10 virtio mmio reset clears legacy and modern queue address plans after queue selection changes" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.initWithQueueMaximums(
        .{ 0, 0 },
        0,
        .{ 8, 16 },
    );

    _ = try window.selectQueue(0);
    _ = try window.writeSelectedQueueSize(8);
    _ = try window.planLegacyQueueAddress(4096, 4096, 0x80);
    _ = try window.writeSelectedQueueReady(true);

    _ = try window.selectQueue(1);
    _ = try window.writeSelectedQueueSize(12);
    _ = try window.planModernQueueAddress(0x1000, 0x2000, 0x3000);
    _ = try window.writeSelectedQueueReady(true);

    const reset = window.reset();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", reset.anchor);
    try std.testing.expectEqual(@as(usize, 1), reset.reset_count);

    var queue = try window.queueRegisterSummary();
    try std.testing.expectEqual(@as(u32, 0), queue.selected_queue);
    try std.testing.expectEqual(@as(u16, 8), queue.selected_queue_size_max);
    try std.testing.expectEqual(@as(u16, 0), queue.selected_queue_size);
    try std.testing.expect(!queue.selected_queue_ready);

    const cleared_legacy = try window.queueAddressSummary(.legacy);
    try std.testing.expectEqual(@as(?u32, 0), cleared_legacy.legacy_guest_page_size);
    try std.testing.expectEqual(@as(?u32, 0), cleared_legacy.legacy_queue_align);
    try std.testing.expectEqual(@as(?u32, 0), cleared_legacy.legacy_queue_pfn);
    try std.testing.expectEqual(@as(?u64, null), cleared_legacy.modern_desc);

    queue = try window.selectQueue(1);
    try std.testing.expectEqual(@as(u16, 16), queue.selected_queue_size_max);
    try std.testing.expectEqual(@as(u16, 0), queue.selected_queue_size);
    try std.testing.expect(!queue.selected_queue_ready);

    const cleared_modern = try window.queueAddressSummary(.modern);
    try std.testing.expectEqual(@as(?u32, null), cleared_modern.legacy_guest_page_size);
    try std.testing.expectEqual(@as(?u64, 0), cleared_modern.modern_desc);
    try std.testing.expectEqual(@as(?u64, 0), cleared_modern.modern_avail);
    try std.testing.expectEqual(@as(?u64, 0), cleared_modern.modern_used);
    try std.testing.expectError(error.QueueAddressRequiresConfiguredSize, window.planModernQueueAddress(0x1110, 0x2220, 0x3330));
}
