const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

pub const TransportIdentitySummary = virtio_mmio.TransportIdentitySummary;
pub const ProbePreflightSummary = virtio_mmio.ProbePreflightSummary;
pub const SelectedQueueReadinessSummary = virtio_mmio.SelectedQueueReadinessSummary;
pub const ConfigWritePlanSummary = virtio_mmio.ConfigWritePlanSummary;
pub const ConfigWriteDispositionSummary = virtio_mmio.ConfigWriteDispositionSummary;
pub const ConfigWriteApplyObservationSummary = virtio_mmio.ConfigWriteApplyObservationSummary;
pub const ConfigWritePlanFreshnessSummary = virtio_mmio.ConfigWritePlanFreshnessSummary;
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

pub fn summarizeConfigWritePlan(
    device: *virtio_mmio.VirtioMmioLab,
    offset: u32,
    planned_value: u32,
) !ConfigWritePlanSummary {
    return device.planConfigWriteOffset(offset, planned_value);
}

pub fn summarizeConfigWriteDisposition(device: *const virtio_mmio.VirtioMmioLab) !ConfigWriteDispositionSummary {
    return device.configWriteDispositionSummary();
}

pub fn summarizeConfigWriteApplyObservation(device: *const virtio_mmio.VirtioMmioLab) !ConfigWriteApplyObservationSummary {
    return device.configWriteApplyObservationSummary();
}

pub fn summarizeConfigWritePlanFreshness(device: *const virtio_mmio.VirtioMmioLab) ConfigWritePlanFreshnessSummary {
    return device.configWritePlanFreshnessSummary();
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

pub fn applyObservationChangedByteCount(summary: ConfigWriteApplyObservationSummary) u3 {
    return summary.changed_byte_count;
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

pub fn configWritePlanWithinWindow(summary: ConfigWritePlanSummary) bool {
    return summary.within_config_window;
}

pub fn hasFreshConfigWritePlan(summary: ConfigWritePlanFreshnessSummary) bool {
    return summary.available_for_disposition;
}

pub fn configWriteObservationTouchesFullWord(summary: ConfigWriteApplyObservationSummary) bool {
    return summary.touched_byte_mask == 0b1111;
}

pub fn configWriteWouldApply(summary: ConfigWriteApplyObservationSummary) bool {
    return summary.applies_changes;
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

    _ = try device.writeRegister(.queue_num, 8);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_ready, 1);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_size_matches_advertised);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 16);
    _ = try device.writeRegister(.queue_ready, 1);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(summary.queue_size_matches_advertised);
    try std.testing.expect(summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 8);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_size_matches_advertised);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 16);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(summary.queue_size_matches_advertised);
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

test "phase10 virtio mmio verify keeps config-write plan wrapper below config application" {
    var device = try virtio_mmio.VirtioMmioLab.init(89, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    const plan = try summarizeConfigWritePlan(&device, virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, plan.anchor);
    try std.testing.expectEqual(@as(u32, 4), plan.relative_offset);
    try std.testing.expectEqual(@as(u32, virtio_mmio.mmio_window_bytes + 4), plan.absolute_offset);
    try std.testing.expectEqual(@as(u32, 0x0203_0407), plan.planned_value);
    try std.testing.expectEqual(@as(u32, 0), plan.config_generation);
    try std.testing.expect(configWritePlanWithinWindow(plan));

    var freshness = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expect(freshness.plan_present);
    try std.testing.expect(freshness.plan_matches_generation);
    try std.testing.expectEqual(plan.relative_offset, freshness.relative_offset);
    try std.testing.expectEqual(plan.absolute_offset, freshness.absolute_offset);
    try std.testing.expectEqual(plan.planned_value, freshness.planned_value);
    try std.testing.expectEqual(plan.config_generation, freshness.planned_generation);
    try std.testing.expect(hasFreshConfigWritePlan(freshness));

    device.bumpConfigGeneration();
    freshness = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expect(freshness.plan_present);
    try std.testing.expect(!freshness.plan_matches_generation);
    try std.testing.expect(!hasFreshConfigWritePlan(freshness));
    try std.testing.expectError(error.ConfigWritePlanUnavailable, summarizeConfigWriteDisposition(&device));
}

test "phase10 virtio mmio verify keeps config-write plan freshness below config application" {
    var device = try virtio_mmio.VirtioMmioLab.init(83, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    var summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expect(!summary.plan_present);
    try std.testing.expect(!hasFreshConfigWritePlan(summary));

    const plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);
    summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expect(summary.plan_present);
    try std.testing.expect(summary.plan_matches_generation);
    try std.testing.expectEqual(plan.relative_offset, summary.relative_offset);
    try std.testing.expectEqual(plan.absolute_offset, summary.absolute_offset);
    try std.testing.expect(hasFreshConfigWritePlan(summary));

    device.bumpConfigGeneration();
    summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expect(summary.plan_present);
    try std.testing.expect(!summary.plan_matches_generation);
    try std.testing.expectEqual(virtio_mmio.ConfigWritePlanAvailability.stale_generation, summary.availability);
    try std.testing.expectEqual(plan.config_generation, summary.planned_generation);
    try std.testing.expectEqual(@as(u32, 1), summary.current_generation);
    try std.testing.expect(!hasFreshConfigWritePlan(summary));
}

test "phase10 virtio mmio verify keeps stale config-write freshness visible but unavailable" {
    var device = try virtio_mmio.VirtioMmioLab.init(87, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });
    const plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);
    device.bumpConfigGeneration();

    const summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expect(summary.plan_present);
    try std.testing.expect(!summary.plan_matches_generation);
    try std.testing.expectEqual(virtio_mmio.ConfigWritePlanAvailability.stale_generation, summary.availability);
    try std.testing.expectEqual(plan.relative_offset, summary.relative_offset);
    try std.testing.expectEqual(plan.absolute_offset, summary.absolute_offset);
    try std.testing.expectEqual(plan.planned_value, summary.planned_value);
    try std.testing.expectEqual(@as(u32, 0), summary.planned_generation);
    try std.testing.expectEqual(@as(u32, 1), summary.current_generation);
    try std.testing.expect(!hasFreshConfigWritePlan(summary));
    try std.testing.expectError(error.ConfigWritePlanUnavailable, summarizeConfigWriteDisposition(&device));
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

test "phase10 virtio mmio verify keeps config-write apply observation wrapper planning-only and explicit" {
    var device = try virtio_mmio.VirtioMmioLab.init(90, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0907);
    var summary = try summarizeConfigWriteApplyObservation(&device);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expect(configWriteObservationTouchesFullWord(summary));
    try std.testing.expectEqual(@as(u4, 0b1111), summary.touched_byte_mask);
    try std.testing.expectEqual(@as(u4, 0b0011), summary.changed_byte_mask);
    try std.testing.expectEqual(@as(u3, 2), applyObservationChangedByteCount(summary));
    try std.testing.expect(configWriteWouldApply(summary));
    try std.testing.expectEqual(@as(u32, 0x0203_0405), summary.previous_value);
    try std.testing.expectEqual(@as(u32, 0x0203_0907), summary.planned_value);

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0405);
    summary = try summarizeConfigWriteApplyObservation(&device);
    try std.testing.expect(configWriteObservationTouchesFullWord(summary));
    try std.testing.expectEqual(@as(u4, 0b1111), summary.touched_byte_mask);
    try std.testing.expectEqual(@as(u4, 0), summary.changed_byte_mask);
    try std.testing.expectEqual(@as(u3, 0), applyObservationChangedByteCount(summary));
    try std.testing.expect(!configWriteWouldApply(summary));

    device.bumpConfigGeneration();
    try std.testing.expectError(error.ConfigWritePlanUnavailable, summarizeConfigWriteApplyObservation(&device));
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
