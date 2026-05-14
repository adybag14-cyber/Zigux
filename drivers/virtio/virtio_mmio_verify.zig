const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

test "virtio mmio wrapper-facing probe preflight keeps bounded blockers visible" {
    var device = try virtio_mmio.VirtioMmioLab.init(73, &[_]u16{ 8, 16 });

    device.device_id = 0;
    var summary = device.probePreflightSummary();
    try std.testing.expect(!summary.ready_for_probe_handoff);
    try std.testing.expect(!summary.device_present);
    try std.testing.expect(summary.vendor_id_present);

    device.device_id = 73;
    device.vendor_id = virtio_mmio.default_vendor_id;
    summary = device.probePreflightSummary();
    try std.testing.expect(summary.ready_for_probe_handoff);
    try std.testing.expect(summary.bounded_queue_register_window_ready);
    try std.testing.expect(summary.interrupt_ack_ready);
}

test "virtio mmio wrapper-facing config review stays scoped to the current generation" {
    var device = try virtio_mmio.VirtioMmioLab.init(74, &[_]u16{ 8, 16 });

    try device.stageConfigBytes(&[_]u8{ 0x78, 0x56, 0x34, 0x12, 0xef, 0xcd, 0xab, 0x90 });
    device.bumpConfigGeneration();
    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x1122_3344);

    const disposition = try device.configWriteDispositionSummary();
    try std.testing.expectEqual(@as(u32, 1), disposition.config_generation);
    try std.testing.expect(disposition.has_changes);

    device.bumpConfigGeneration();
    try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());
}

test "virtio mmio wrapper-facing queue handoff review stays selected-queue local" {
    var device = try virtio_mmio.VirtioMmioLab.init(75, &[_]u16{ 8, 16 });

    _ = try device.writeRegister(.queue_sel, 1);
    var summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 1), summary.selected_queue);
    try std.testing.expect(!summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 16);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_ready, 1);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expect(summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_sel, 0);
    const first_queue = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 0), first_queue.selected_queue);
    try std.testing.expect(!first_queue.queue_ready_for_handoff);
}
