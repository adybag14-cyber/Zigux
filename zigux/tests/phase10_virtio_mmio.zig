const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

test "phase10 virtio mmio plans a bounded config-word write without mutating config space" {
    var device = try virtio_mmio.VirtioMmioLab.init(80, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 1, 2, 3, 4, 5, 6, 7, 8 });
    const before = device.config_bytes;
    const plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x1122_3344);
    try std.testing.expectEqual(@as(u32, 4), plan.relative_offset);
    try std.testing.expectEqual(before[4], device.config_bytes[4]);
}

test "phase10 virtio mmio summarizes a planned config-word write disposition without mutating config space" {
    var device = try virtio_mmio.VirtioMmioLab.init(81, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0, 1, 2, 3, 4, 5, 6, 7 });
    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes, 0xaabb_ccdd);
    const disposition = try device.configWriteDispositionSummary();
    try std.testing.expect(disposition.has_changes);
    try std.testing.expectEqual(@as(u32, 0), disposition.relative_offset);
}

test "phase10 virtio mmio summarizes bounded feature negotiation before lifecycle work" {
    var device = try virtio_mmio.VirtioMmioLab.init(82, &[_]u16{ 8, 16 });
    try device.stageDeviceFeatureWord(0, 0xf0);
    try device.stageDriverFeatureWord(0, 0x30);
    const summary = device.featureNegotiationSummary();
    try std.testing.expect(summary.device_features_known);
    try std.testing.expect(summary.driver_features_known);
    try std.testing.expect(summary.negotiation_possible);
}

test "phase10 virtio mmio summarizes transport identity before lifecycle work" {
    const device = try virtio_mmio.VirtioMmioLab.init(83, &[_]u16{ 8, 16 });
    const summary = device.transportIdentitySummary();
    try std.testing.expect(summary.magic_matches);
    try std.testing.expect(summary.version_supported);
    try std.testing.expect(summary.device_present);
    try std.testing.expect(summary.vendor_id_present);
}

test "phase10 virtio mmio summarizes bounded probe preflight readiness before lifecycle work" {
    const device = try virtio_mmio.VirtioMmioLab.init(84, &[_]u16{ 8, 16 });
    const summary = device.probePreflightSummary();
    try std.testing.expect(summary.bounded_queue_register_window_ready);
    try std.testing.expect(summary.interrupt_ack_ready);
    try std.testing.expect(summary.ready_for_probe_handoff);
}

test "phase10 virtio mmio keeps the legacy probe preflight path ready when transport identity stays aligned" {
    var device = try virtio_mmio.VirtioMmioLab.init(85, &[_]u16{ 8, 16 });
    device.version = virtio_mmio.mmio_version_legacy;
    _ = try device.writeRegister(.guest_page_size, 4096);
    const summary = device.probePreflightSummary();
    try std.testing.expect(summary.ready_for_probe_handoff);
    try std.testing.expect(summary.version_supported);
}

test "phase10 virtio mmio marks probe preflight incomplete when identity presence falls away" {
    var device = try virtio_mmio.VirtioMmioLab.init(86, &[_]u16{ 8, 16 });
    device.vendor_id = 0;
    const summary = device.probePreflightSummary();
    try std.testing.expect(!summary.vendor_id_present);
    try std.testing.expect(!summary.ready_for_probe_handoff);
}

test "phase10 virtio mmio marks probe preflight incomplete when transport identity drifts" {
    var device = try virtio_mmio.VirtioMmioLab.init(87, &[_]u16{ 8, 16 });
    device.magic_value = 0;
    const summary = device.probePreflightSummary();
    try std.testing.expect(summary.device_present);
    try std.testing.expect(!summary.ready_for_probe_handoff);
}

test "phase10 virtio mmio summarizes selected-queue readiness before queue handoff" {
    var device = try virtio_mmio.VirtioMmioLab.init(88, &[_]u16{ 8, 16 });
    _ = try device.writeRegister(.queue_sel, 1);
    _ = try device.writeRegister(.queue_num, 16);
    _ = try device.writeRegister(.queue_ready, 1);
    const summary = try device.selectedQueueReadinessSummary();
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(summary.queue_ready_for_handoff);
}
