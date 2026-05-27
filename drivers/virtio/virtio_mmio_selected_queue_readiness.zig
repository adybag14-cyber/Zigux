const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

pub const SelectedQueueReadinessSummary = virtio_mmio.SelectedQueueReadinessSummary;

pub fn summarizeSelectedQueueReadiness(
    device: *const virtio_mmio.VirtioMmioLab,
) !SelectedQueueReadinessSummary {
    return device.selectedQueueReadinessSummary();
}

pub fn queueSizeProgrammed(summary: SelectedQueueReadinessSummary) bool {
    return summary.queue_size_programmed;
}

pub fn queueSizeMatchesAdvertised(summary: SelectedQueueReadinessSummary) bool {
    return summary.queue_size_matches_advertised;
}

pub fn queueReadyForHandoff(summary: SelectedQueueReadinessSummary) bool {
    return summary.queue_ready_for_handoff;
}

test "phase10 virtio mmio selected-queue-readiness wrapper keeps queue-size gating reviewable" {
    var device = try virtio_mmio.VirtioMmioLab.init(101, &[_]u16{ 8, 16 });

    _ = try device.writeRegister(.queue_sel, 1);
    var summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expectEqual(@as(u16, 1), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 16), summary.advertised_queue_size);
    try std.testing.expectEqual(@as(u16, 0), summary.programmed_queue_size);
    try std.testing.expect(!queueSizeProgrammed(summary));
    try std.testing.expect(!queueSizeMatchesAdvertised(summary));
    try std.testing.expect(!queueReadyForHandoff(summary));

    _ = try device.writeRegister(.queue_num, 8);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expect(queueSizeProgrammed(summary));
    try std.testing.expect(!queueSizeMatchesAdvertised(summary));
    try std.testing.expect(!queueReadyForHandoff(summary));

    _ = try device.writeRegister(.queue_num, 16);
    _ = try device.writeRegister(.queue_ready, 1);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expect(queueSizeProgrammed(summary));
    try std.testing.expect(queueSizeMatchesAdvertised(summary));
    try std.testing.expect(queueReadyForHandoff(summary));
}

test "phase10 virtio mmio selected-queue-readiness wrapper keeps selector-local state isolated" {
    var device = try virtio_mmio.VirtioMmioLab.init(102, &[_]u16{ 8, 16 });

    _ = try device.writeRegister(.queue_sel, 0);
    _ = try device.writeRegister(.queue_num, 8);
    _ = try device.writeRegister(.queue_ready, 1);

    _ = try device.writeRegister(.queue_sel, 1);
    var summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expectEqual(@as(u16, 1), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 16), summary.advertised_queue_size);
    try std.testing.expectEqual(@as(u16, 0), summary.programmed_queue_size);
    try std.testing.expect(!queueSizeProgrammed(summary));
    try std.testing.expect(!queueReadyForHandoff(summary));

    _ = try device.writeRegister(.queue_num, 16);
    _ = try device.writeRegister(.queue_ready, 1);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expect(queueSizeProgrammed(summary));
    try std.testing.expect(queueSizeMatchesAdvertised(summary));
    try std.testing.expect(queueReadyForHandoff(summary));

    _ = try device.writeRegister(.queue_sel, 0);
    summary = try summarizeSelectedQueueReadiness(&device);
    try std.testing.expectEqual(@as(u16, 0), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 8), summary.advertised_queue_size);
    try std.testing.expectEqual(@as(u16, 8), summary.programmed_queue_size);
    try std.testing.expect(queueSizeProgrammed(summary));
    try std.testing.expect(queueSizeMatchesAdvertised(summary));
    try std.testing.expect(queueReadyForHandoff(summary));
}
