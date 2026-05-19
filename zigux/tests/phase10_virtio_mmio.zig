const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

test "phase10 virtio mmio keeps probe gating anchored below transport-backed claims" {
    var device = try virtio_mmio.VirtioMmioLab.init(91, &[_]u16{ 8, 16 });
    device.version = virtio_mmio.mmio_version_legacy;

    const identity = device.transportIdentitySummary();
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, identity.anchor);
    try std.testing.expect(identity.magic_matches);
    try std.testing.expect(identity.version_supported);
    try std.testing.expect(identity.device_present);
    try std.testing.expect(identity.vendor_id_present);
    try std.testing.expect(identity.requires_legacy_guest_page_size);

    var probe = device.probePreflightSummary();
    try std.testing.expect(!probe.legacy_guest_page_size_ready);
    try std.testing.expect(!probe.ready_for_probe_handoff);

    _ = try device.writeRegister(.guest_page_size, 4096);
    probe = device.probePreflightSummary();
    try std.testing.expect(probe.legacy_guest_page_size_ready);
    try std.testing.expect(probe.ready_for_probe_handoff);
}

test "phase10 virtio mmio keeps selected queue readiness bounded to in-memory register state" {
    var device = try virtio_mmio.VirtioMmioLab.init(92, &[_]u16{ 8, 16 });

    _ = try device.writeRegister(.queue_sel, 1);
    var summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expectEqual(@as(u16, 1), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 16), summary.advertised_queue_size);
    try std.testing.expectEqual(@as(u16, 0), summary.programmed_queue_size);
    try std.testing.expect(!summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_size_matches_advertised);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 8);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 16), summary.advertised_queue_size);
    try std.testing.expectEqual(@as(u16, 8), summary.programmed_queue_size);
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_size_matches_advertised);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 16);
    _ = try device.writeRegister(.queue_ready, 1);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(summary.queue_size_matches_advertised);
    try std.testing.expect(summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_sel, 0);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 0), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 8), summary.advertised_queue_size);
    try std.testing.expectEqual(@as(u16, 0), summary.programmed_queue_size);
    try std.testing.expect(!summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_size_matches_advertised);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    try std.testing.expectError(error.QueueSelectionOutOfRange, device.writeRegister(.queue_sel, 2));
    try std.testing.expectError(error.QueueSizeExceedsAdvertised, device.writeRegister(.queue_num, 32));
}

test "phase10 virtio mmio records feature mismatches without claiming live negotiation" {
    var device = try virtio_mmio.VirtioMmioLab.init(93, &[_]u16{ 8, 16 });
    try device.stageDeviceFeatureWord(0, 0b1110);
    try device.stageDriverFeatureWord(0, 0b1011);

    var summary = device.featureNegotiationSummary();
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expect(summary.selected_feature_words_in_range);
    try std.testing.expect(summary.negotiation_possible);
    try std.testing.expect(!summary.feature_words_match);
    try std.testing.expectEqual(@as(u32, 0b1010), summary.negotiated_feature_word);
    try std.testing.expectEqual(@as(u32, 0b0100), summary.device_only_feature_word);
    try std.testing.expectEqual(@as(u32, 0b0001), summary.driver_only_feature_word);

    _ = try device.writeRegister(.device_features_sel, 1);
    summary = device.featureNegotiationSummary();
    try std.testing.expect(summary.device_feature_selector_in_range);
    try std.testing.expect(summary.driver_feature_selector_in_range);
    try std.testing.expect(!summary.device_features_known);
    try std.testing.expect(summary.driver_features_known);
    try std.testing.expect(!summary.negotiation_possible);
}

test "phase10 virtio mmio keeps interrupt-ack disposition bounded to reviewable queue and config bits" {
    var device = try virtio_mmio.VirtioMmioLab.init(95, &[_]u16{ 8, 16 });
    device.stageInterruptStatus(0b111);

    const summary = device.interruptAckDispositionSummary(0b111);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expectEqual(@as(u32, 0b111), summary.requested_bits);
    try std.testing.expectEqual(@as(u32, 0b111), summary.pending_bits);
    try std.testing.expectEqual(@as(u32, 0b011), summary.acknowledged_bits);
    try std.testing.expectEqual(@as(u32, 0b100), summary.ignored_bits);
    try std.testing.expectEqual(@as(u32, 0b100), summary.remaining_pending_bits);
    try std.testing.expect(summary.has_acknowledgements);

    _ = try device.writeRegister(.interrupt_ack, 0b001);
    const queue_only = device.interruptAckDispositionSummary(0b011);
    try std.testing.expectEqual(@as(u32, 0b001), queue_only.acknowledged_bits);
    try std.testing.expectEqual(@as(u32, 0b010), queue_only.ignored_bits);
}

test "phase10 virtio mmio keeps config-write disposition planning-only across restaging" {
    var device = try virtio_mmio.VirtioMmioLab.init(94, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });
    const before = device.config_bytes;

    const plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, plan.anchor);
    try std.testing.expect(plan.within_config_window);
    try std.testing.expectEqual(@as(u32, 4), plan.relative_offset);

    const disposition = try device.configWriteDispositionSummary();
    try std.testing.expectEqual(@as(u32, 0x0203_0405), disposition.previous_value);
    try std.testing.expectEqual(@as(u32, 0x0203_0407), disposition.planned_value);
    try std.testing.expectEqual(@as(u4, 0b0001), disposition.changed_byte_mask);
    try std.testing.expect(disposition.has_changes);
    try std.testing.expectEqualSlices(u8, before[0..8], device.config_bytes[0..8]);

    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x08, 0x07, 0x06, 0x05 });
    try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0506_0709);
    const refreshed = try device.configWriteDispositionSummary();
    try std.testing.expectEqual(@as(u32, 0x0506_0708), refreshed.previous_value);
    try std.testing.expectEqual(@as(u32, 0x0506_0709), refreshed.planned_value);
    try std.testing.expectEqual(@as(u4, 0b0001), refreshed.changed_byte_mask);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x08, 0x07, 0x06, 0x05 }, device.config_bytes[0..8]);
}
