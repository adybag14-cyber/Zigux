const std = @import("std");
const virtio_mmio = @import("virtio_mmio");
const apply_observation = @import("virtio_mmio_apply_observation");

test "phase10 virtio mmio apply-observation replay keeps changed bytes explicit" {
    var device = try virtio_mmio.VirtioMmioLab.init(99, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0907);
    const summary = try apply_observation.summarizeConfigWriteApplyObservation(&device);

    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expectEqual(@as(u32, 4), summary.relative_offset);
    try std.testing.expectEqual(@as(u32, virtio_mmio.mmio_window_bytes + 4), summary.absolute_offset);
    try std.testing.expectEqual(@as(u32, 7), summary.relative_end_offset);
    try std.testing.expectEqual(@as(u32, virtio_mmio.mmio_window_bytes + 7), summary.absolute_end_offset);
    try std.testing.expectEqual(@as(u32, 0x0203_0405), summary.previous_value);
    try std.testing.expectEqual(@as(u32, 0x0203_0907), summary.planned_value);
    try std.testing.expectEqual(@as(u4, 0b1111), summary.touched_byte_mask);
    try std.testing.expectEqual(@as(u4, 0b0011), summary.changed_byte_mask);
    try std.testing.expectEqual(@as(u3, 4), apply_observation.touchedByteCount(summary));
    try std.testing.expectEqual(@as(u3, 2), apply_observation.changedByteCount(summary));
    try std.testing.expect(apply_observation.changedBytesStayWithinTouchedMask(summary));
    try std.testing.expect(apply_observation.appliesByteChanges(summary));
}

test "phase10 virtio mmio apply-observation replay keeps no-op and stale plans distinct" {
    var device = try virtio_mmio.VirtioMmioLab.init(100, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0405);
    const no_op = try apply_observation.summarizeConfigWriteApplyObservation(&device);
    try std.testing.expectEqual(@as(u4, 0b1111), no_op.touched_byte_mask);
    try std.testing.expectEqual(@as(u4, 0), no_op.changed_byte_mask);
    try std.testing.expectEqual(@as(u3, 4), apply_observation.touchedByteCount(no_op));
    try std.testing.expectEqual(@as(u3, 0), apply_observation.changedByteCount(no_op));
    try std.testing.expect(apply_observation.changedBytesStayWithinTouchedMask(no_op));
    try std.testing.expect(!apply_observation.appliesByteChanges(no_op));

    device.bumpConfigGeneration();
    try std.testing.expectError(
        error.ConfigWritePlanUnavailable,
        apply_observation.summarizeConfigWriteApplyObservation(&device),
    );
}

test "phase10 virtio mmio apply-observation replay clears stale plans across config restaging" {
    var device = try virtio_mmio.VirtioMmioLab.init(101, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0907);
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x08, 0x07, 0x06, 0x05 });
    try std.testing.expectError(
        error.ConfigWritePlanUnavailable,
        apply_observation.summarizeConfigWriteApplyObservation(&device),
    );

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0506_0709);
    const refreshed = try apply_observation.summarizeConfigWriteApplyObservation(&device);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, refreshed.anchor);
    try std.testing.expectEqual(@as(u32, 0x0506_0708), refreshed.previous_value);
    try std.testing.expectEqual(@as(u32, 0x0506_0709), refreshed.planned_value);
    try std.testing.expectEqual(@as(u4, 0b1111), refreshed.touched_byte_mask);
    try std.testing.expectEqual(@as(u4, 0b0001), refreshed.changed_byte_mask);
    try std.testing.expectEqual(@as(u3, 4), apply_observation.touchedByteCount(refreshed));
    try std.testing.expectEqual(@as(u3, 1), apply_observation.changedByteCount(refreshed));
    try std.testing.expect(apply_observation.changedBytesStayWithinTouchedMask(refreshed));
    try std.testing.expect(apply_observation.appliesByteChanges(refreshed));
}
