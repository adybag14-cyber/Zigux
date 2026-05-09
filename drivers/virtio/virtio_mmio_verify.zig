const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

test "virtio mmio wrapper-facing probe preflight keeps bounded blockers visible" {
    var device = try virtio_mmio.VirtioMmioLab.init(81, &[_]u16{ 8, 16 });
    device.seedTransportIdentity(
        virtio_mmio.mmio_magic_value,
        virtio_mmio.mmio_version_legacy,
        81,
        virtio_mmio.default_vendor_id,
    );

    var summary = device.probePreflightSummary();
    try std.testing.expect(summary.magic_matches);
    try std.testing.expect(summary.version_supported);
    try std.testing.expect(summary.requires_legacy_guest_page_size);
    try std.testing.expect(summary.device_present);
    try std.testing.expect(summary.vendor_id_present);
    try std.testing.expect(summary.ready_for_probe_handoff);

    device.vendor_id = 0;
    summary = device.probePreflightSummary();
    try std.testing.expect(summary.device_present);
    try std.testing.expect(!summary.vendor_id_present);
    try std.testing.expect(!summary.ready_for_probe_handoff);

    device.vendor_id = virtio_mmio.default_vendor_id;
    device.device_id = 0;
    summary = device.probePreflightSummary();
    try std.testing.expect(!summary.device_present);
    try std.testing.expect(summary.vendor_id_present);
    try std.testing.expect(!summary.ready_for_probe_handoff);
}

test "virtio mmio wrapper-facing config review stays scoped to the current generation" {
    var device = try virtio_mmio.VirtioMmioLab.init(82, &[_]u16{ 8, 16 });

    try device.stageConfigBytes(&[_]u8{
        0x78, 0x56, 0x34, 0x12,
        0xef, 0xcd, 0xab, 0x90,
    });
    device.bumpConfigGeneration();

    const plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x90ab_1200);
    try std.testing.expectEqual(@as(u32, 1), plan.config_generation);
    try std.testing.expectEqual(@as(u32, 0x90ab_cdef), plan.previous_value);

    const disposition = try device.configWriteDispositionSummary();
    try std.testing.expectEqual(@as(u32, 1), disposition.config_generation);
    try std.testing.expectEqual(@as(u8, 0b0011), disposition.changed_byte_mask);
    try std.testing.expectEqual(virtio_mmio.mmio_window_bytes + 8, disposition.end_offset);

    const config_summary = try device.readConfigOffset(virtio_mmio.mmio_window_bytes + 4);
    try std.testing.expectEqual(@as(u32, 0x90ab_cdef), config_summary.value);
    try std.testing.expectEqual(@as(u32, 1), config_summary.config_generation);

    device.bumpConfigGeneration();
    try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());
}

test "virtio mmio wrapper-facing feature negotiation stays word-local and preserves queue selection" {
    var device = try virtio_mmio.VirtioMmioLab.init(84, &[_]u16{ 8, 16 });

    try device.stageDeviceFeatureWord(0, 0xa5a5_0001);
    try device.stageDeviceFeatureWord(1, 0x5a5a_0002);
    _ = try device.writeRegister(.queue_sel, 1);

    var summary = device.featureNegotiationSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 0), summary.selected_device_feature_word);
    try std.testing.expectEqual(@as(u32, 0xa5a5_0001), summary.device_feature_word);
    try std.testing.expectEqual(@as(u32, 0), summary.driver_features);
    try std.testing.expect(summary.feature_word_selector_in_range);
    try std.testing.expect(summary.device_feature_window_ready);
    try std.testing.expect(summary.driver_feature_register_ready);
    try std.testing.expect(summary.ready_for_feature_handoff);

    _ = try device.writeRegister(.device_features_sel, 1);
    _ = try device.writeRegister(.driver_features, 0x1122_3344);
    summary = device.featureNegotiationSummary();
    try std.testing.expectEqual(@as(u32, 1), summary.selected_device_feature_word);
    try std.testing.expectEqual(@as(u32, 0x5a5a_0002), summary.device_feature_word);
    try std.testing.expectEqual(@as(u32, 0x1122_3344), summary.driver_features);
    try std.testing.expect(summary.ready_for_feature_handoff);

    const queue_summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 1), queue_summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 16), queue_summary.queue_num_max);
    try std.testing.expectEqual(@as(u16, 0), queue_summary.queue_num);
    try std.testing.expect(!queue_summary.queue_ready);
    try std.testing.expect(!queue_summary.queue_ready_for_handoff);

    device.selected_device_feature_word = virtio_mmio.feature_word_capacity;
    summary = device.featureNegotiationSummary();
    try std.testing.expect(!summary.feature_word_selector_in_range);
    try std.testing.expectEqual(@as(u32, 0), summary.device_feature_word);
    try std.testing.expect(!summary.ready_for_feature_handoff);
}

test "virtio mmio wrapper-facing queue handoff review stays selected-queue local" {
    var device = try virtio_mmio.VirtioMmioLab.init(83, &[_]u16{ 8, 16 });

    _ = try device.writeRegister(.queue_num, 8);
    _ = try device.writeRegister(.queue_ready, 1);

    _ = try device.writeRegister(.queue_sel, 1);
    var summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 1), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 16), summary.queue_num_max);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_num);
    try std.testing.expect(!summary.queue_ready);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 16);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_sel, 0);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 0), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 8), summary.queue_num);
    try std.testing.expect(summary.queue_ready);
    try std.testing.expect(summary.queue_ready_for_handoff);
}
