const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

pub const TransportIdentitySummary = virtio_mmio.TransportIdentitySummary;
pub const ProbePreflightSummary = virtio_mmio.ProbePreflightSummary;
pub const SelectedQueueReadinessSummary = virtio_mmio.SelectedQueueReadinessSummary;
pub const ConfigWriteDispositionSummary = virtio_mmio.ConfigWriteDispositionSummary;
pub const FeatureNegotiationSummary = virtio_mmio.FeatureNegotiationSummary;
pub const InterruptAckDispositionSummary = virtio_mmio.InterruptAckDispositionSummary;

pub fn summarizeTransportIdentity(device: *const virtio_mmio.VirtioMmioLab) TransportIdentitySummary {
    return device.transportIdentitySummary();
}

pub fn summarizeProbePreflight(device: *const virtio_mmio.VirtioMmioLab) ProbePreflightSummary {
    return device.probePreflightSummary();
}

pub fn summarizeSelectedQueueReadiness(device: *const virtio_mmio.VirtioMmioLab) !SelectedQueueReadinessSummary {
    return device.selectedQueueReadinessSummary();
}

pub fn summarizeFeatureNegotiation(device: *const virtio_mmio.VirtioMmioLab) FeatureNegotiationSummary {
    return device.featureNegotiationSummary();
}

pub fn summarizeConfigWriteDisposition(device: *const virtio_mmio.VirtioMmioLab) !ConfigWriteDispositionSummary {
    return device.configWriteDispositionSummary();
}

pub fn summarizeInterruptAckDisposition(
    device: *const virtio_mmio.VirtioMmioLab,
    requested_bits: u32,
) InterruptAckDispositionSummary {
    return device.interruptAckDispositionSummary(requested_bits);
}

pub fn changedByteCount(summary: ConfigWriteDispositionSummary) u3 {
    return @popCount(summary.changed_byte_mask);
}

pub fn negotiatedFeatureBitCount(summary: FeatureNegotiationSummary) u6 {
    return @popCount(summary.negotiated_feature_word);
}

pub fn acknowledgedInterruptCount(summary: InterruptAckDispositionSummary) u6 {
    return @popCount(summary.acknowledged_bits);
}

pub fn hasFeatureNegotiationDrift(summary: FeatureNegotiationSummary) bool {
    return !summary.selected_feature_words_in_range or
        !summary.device_features_known or
        !summary.driver_features_known;
}

pub fn requiresLegacyGuestPageSize(summary: ProbePreflightSummary) bool {
    return !summary.legacy_guest_page_size_ready;
}

test "phase10 virtio mmio verify keeps probe wrapper transitions explicit" {
    var device = try virtio_mmio.VirtioMmioLab.init(77, &[_]u16{ 8, 16 });
    device.version = virtio_mmio.mmio_version_legacy;

    const identity = summarizeTransportIdentity(&device);
    try std.testing.expect(identity.magic_matches);
    try std.testing.expect(identity.requires_legacy_guest_page_size);

    var summary = summarizeProbePreflight(&device);
    try std.testing.expect(requiresLegacyGuestPageSize(summary));
    try std.testing.expect(!summary.ready_for_probe_handoff);

    _ = try device.writeRegister(.guest_page_size, 4096);
    summary = summarizeProbePreflight(&device);
    try std.testing.expect(!requiresLegacyGuestPageSize(summary));
    try std.testing.expect(summary.ready_for_probe_handoff);
}

test "phase10 virtio mmio verify keeps queue readiness wrapper below transport claims" {
    var device = try virtio_mmio.VirtioMmioLab.init(78, &[_]u16{ 8, 16 });

    _ = try device.writeRegister(.queue_sel, 1);
    var summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expectEqual(@as(u16, 1), summary.selected_queue);
    try std.testing.expect(!summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 16);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_ready, 1);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_sel, 0);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expectEqual(@as(u16, 0), summary.selected_queue);
    try std.testing.expect(!summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_sel, 1);
    _ = try device.writeRegister(.queue_ready, 0);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);
}

test "phase10 virtio mmio verify keeps feature negotiation wrapper drift explicit" {
    var device = try virtio_mmio.VirtioMmioLab.init(81, &[_]u16{ 8, 16 });
    try device.stageDeviceFeatureWord(0, 0b1110);
    try device.stageDriverFeatureWord(0, 0b1011);

    var summary = summarizeFeatureNegotiation(&device);
    try std.testing.expect(!hasFeatureNegotiationDrift(summary));
    try std.testing.expect(summary.negotiation_possible);
    try std.testing.expect(!summary.feature_words_match);
    try std.testing.expectEqual(@as(u6, 2), negotiatedFeatureBitCount(summary));
    try std.testing.expectEqual(@as(u32, 0b0100), summary.device_only_feature_word);
    try std.testing.expectEqual(@as(u32, 0b0001), summary.driver_only_feature_word);

    _ = try device.writeRegister(.device_features_sel, 1);
    summary = summarizeFeatureNegotiation(&device);
    try std.testing.expect(hasFeatureNegotiationDrift(summary));
    try std.testing.expect(summary.selected_feature_words_in_range);
    try std.testing.expect(!summary.device_features_known);
    try std.testing.expect(summary.driver_features_known);
    try std.testing.expect(!summary.negotiation_possible);
    try std.testing.expectEqual(@as(u6, 0), negotiatedFeatureBitCount(summary));
}

test "phase10 virtio mmio verify counts changed config bytes without mutating staged data" {
    var device = try virtio_mmio.VirtioMmioLab.init(79, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });
    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0907);

    const summary = try summarizeConfigWriteDisposition(&device);
    try std.testing.expectEqual(@as(u4, 0b0011), summary.changed_byte_mask);
    try std.testing.expectEqual(@as(u3, 2), changedByteCount(summary));
    try std.testing.expect(summary.has_changes);
    try std.testing.expectEqual(@as(u32, 0x0203_0405), summary.previous_value);
}

test "phase10 virtio mmio verify keeps interrupt-ack disposition below IRQ-delivery claims" {
    var device = try virtio_mmio.VirtioMmioLab.init(82, &[_]u16{ 8, 16 });
    device.stageInterruptStatus(0b111);

    var summary = summarizeInterruptAckDisposition(&device, 0b111);
    try std.testing.expectEqual(@as(u32, 0b011), summary.acknowledged_bits);
    try std.testing.expectEqual(@as(u32, 0b100), summary.remaining_pending_bits);
    try std.testing.expectEqual(@as(u6, 2), acknowledgedInterruptCount(summary));
    try std.testing.expect(summary.has_acknowledgements);

    _ = try device.writeRegister(.interrupt_ack, 0b001);
    summary = summarizeInterruptAckDisposition(&device, 0b011);
    try std.testing.expectEqual(@as(u32, 0b001), summary.acknowledged_bits);
    try std.testing.expectEqual(@as(u32, 0b010), summary.ignored_bits);
    try std.testing.expectEqual(@as(u6, 1), acknowledgedInterruptCount(summary));
}