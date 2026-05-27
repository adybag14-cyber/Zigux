const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

pub const ConfigWriteApplyObservationSummary = virtio_mmio.ConfigWriteApplyObservationSummary;

pub fn summarizeConfigWriteApplyObservation(
    device: *const virtio_mmio.VirtioMmioLab,
) !ConfigWriteApplyObservationSummary {
    return device.configWriteApplyObservationSummary();
}

pub fn touchedByteCount(summary: ConfigWriteApplyObservationSummary) u3 {
    return @as(u3, @popCount(summary.touched_byte_mask));
}

pub fn changedByteCount(summary: ConfigWriteApplyObservationSummary) u3 {
    return summary.changed_byte_count;
}

pub fn changedBytesStayWithinTouchedMask(summary: ConfigWriteApplyObservationSummary) bool {
    return (summary.changed_byte_mask & ~summary.touched_byte_mask) == 0;
}

pub fn appliesByteChanges(summary: ConfigWriteApplyObservationSummary) bool {
    return summary.applies_changes;
}

test "phase10 virtio mmio apply-observation wrapper keeps touched and changed bytes reviewable" {
    var device = try virtio_mmio.VirtioMmioLab.init(99, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0907);
    const summary = try summarizeConfigWriteApplyObservation(&device);

    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expectEqual(@as(u32, 4), summary.relative_offset);
    try std.testing.expectEqual(@as(u32, virtio_mmio.mmio_window_bytes + 4), summary.absolute_offset);
    try std.testing.expectEqual(@as(u32, 7), summary.relative_end_offset);
    try std.testing.expectEqual(@as(u32, virtio_mmio.mmio_window_bytes + 7), summary.absolute_end_offset);
    try std.testing.expectEqual(@as(u32, 0x0203_0405), summary.previous_value);
    try std.testing.expectEqual(@as(u32, 0x0203_0907), summary.planned_value);
    try std.testing.expectEqual(@as(u4, 0b1111), summary.touched_byte_mask);
    try std.testing.expectEqual(@as(u4, 0b0011), summary.changed_byte_mask);
    try std.testing.expectEqual(@as(u3, 4), touchedByteCount(summary));
    try std.testing.expectEqual(@as(u3, 2), changedByteCount(summary));
    try std.testing.expect(changedBytesStayWithinTouchedMask(summary));
    try std.testing.expect(appliesByteChanges(summary));
}

test "phase10 virtio mmio apply-observation wrapper keeps no-op and stale plans explicit" {
    var device = try virtio_mmio.VirtioMmioLab.init(100, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0405);
    const no_op = try summarizeConfigWriteApplyObservation(&device);
    try std.testing.expectEqual(@as(u4, 0b1111), no_op.touched_byte_mask);
    try std.testing.expectEqual(@as(u4, 0), no_op.changed_byte_mask);
    try std.testing.expectEqual(@as(u3, 4), touchedByteCount(no_op));
    try std.testing.expectEqual(@as(u3, 0), changedByteCount(no_op));
    try std.testing.expect(changedBytesStayWithinTouchedMask(no_op));
    try std.testing.expect(!appliesByteChanges(no_op));

    device.bumpConfigGeneration();
    try std.testing.expectError(
        error.ConfigWritePlanUnavailable,
        summarizeConfigWriteApplyObservation(&device),
    );
}

test "phase10 virtio mmio apply-observation wrapper refreshes after stale generation instead of reusing an unavailable plan" {
    var device = try virtio_mmio.VirtioMmioLab.init(101, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);
    device.bumpConfigGeneration();
    try std.testing.expectError(
        error.ConfigWritePlanUnavailable,
        summarizeConfigWriteApplyObservation(&device),
    );

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0907);
    const refreshed = try summarizeConfigWriteApplyObservation(&device);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, refreshed.anchor);
    try std.testing.expectEqual(@as(u32, 4), refreshed.relative_offset);
    try std.testing.expectEqual(@as(u32, virtio_mmio.mmio_window_bytes + 4), refreshed.absolute_offset);
    try std.testing.expectEqual(@as(u32, 7), refreshed.relative_end_offset);
    try std.testing.expectEqual(@as(u32, virtio_mmio.mmio_window_bytes + 7), refreshed.absolute_end_offset);
    try std.testing.expectEqual(@as(u32, 0x0203_0405), refreshed.previous_value);
    try std.testing.expectEqual(@as(u32, 0x0203_0907), refreshed.planned_value);
    try std.testing.expectEqual(@as(u32, 1), refreshed.config_generation);
    try std.testing.expectEqual(@as(u4, 0b1111), refreshed.touched_byte_mask);
    try std.testing.expectEqual(@as(u4, 0b0011), refreshed.changed_byte_mask);
    try std.testing.expectEqual(@as(u3, 4), touchedByteCount(refreshed));
    try std.testing.expectEqual(@as(u3, 2), changedByteCount(refreshed));
    try std.testing.expect(changedBytesStayWithinTouchedMask(refreshed));
    try std.testing.expect(appliesByteChanges(refreshed));
}
