const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

pub const ConfigWritePlanAvailability = virtio_mmio.ConfigWritePlanAvailability;
pub const ConfigWritePlanFreshnessSummary = virtio_mmio.ConfigWritePlanFreshnessSummary;

pub fn summarizeConfigWritePlanFreshness(
    device: *const virtio_mmio.VirtioMmioLab,
) ConfigWritePlanFreshnessSummary {
    return device.configWritePlanFreshnessSummary();
}

pub fn planIsFresh(summary: ConfigWritePlanFreshnessSummary) bool {
    return summary.availability == .fresh;
}

pub fn planNeedsRefresh(summary: ConfigWritePlanFreshnessSummary) bool {
    return summary.plan_present and !summary.plan_matches_generation;
}

pub fn planHasReviewableOffsets(summary: ConfigWritePlanFreshnessSummary) bool {
    return summary.plan_present and summary.within_config_window;
}

test "phase10 virtio mmio plan-freshness wrapper keeps missing plans explicit" {
    var device = try virtio_mmio.VirtioMmioLab.init(93, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    const summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expectEqual(ConfigWritePlanAvailability.unavailable, summary.availability);
    try std.testing.expect(!summary.plan_present);
    try std.testing.expect(!summary.plan_matches_generation);
    try std.testing.expectEqual(@as(u32, 0), summary.current_generation);
    try std.testing.expect(!planIsFresh(summary));
    try std.testing.expect(!planNeedsRefresh(summary));
    try std.testing.expect(!planHasReviewableOffsets(summary));
}

test "phase10 virtio mmio plan-freshness wrapper keeps fresh plans reviewable" {
    var device = try virtio_mmio.VirtioMmioLab.init(94, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    const plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);
    const summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expectEqual(ConfigWritePlanAvailability.fresh, summary.availability);
    try std.testing.expect(summary.plan_present);
    try std.testing.expect(summary.plan_matches_generation);
    try std.testing.expectEqual(plan.relative_offset, summary.relative_offset);
    try std.testing.expectEqual(plan.absolute_offset, summary.absolute_offset);
    try std.testing.expectEqual(plan.planned_value, summary.planned_value);
    try std.testing.expectEqual(plan.config_generation, summary.planned_generation);
    try std.testing.expectEqual(device.config_generation, summary.current_generation);
    try std.testing.expect(planIsFresh(summary));
    try std.testing.expect(!planNeedsRefresh(summary));
    try std.testing.expect(planHasReviewableOffsets(summary));
}

test "phase10 virtio mmio plan-freshness wrapper keeps the newest same-generation plan reviewable" {
    var device = try virtio_mmio.VirtioMmioLab.init(98, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02, 0x09, 0x08, 0x07, 0x06 });

    const first_plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes, 0xddcc_bbaa);
    const second_plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);

    const summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqual(ConfigWritePlanAvailability.fresh, summary.availability);
    try std.testing.expect(summary.plan_present);
    try std.testing.expect(summary.plan_matches_generation);
    try std.testing.expectEqual(@as(u32, 0), summary.current_generation);
    try std.testing.expectEqual(first_plan.config_generation, second_plan.config_generation);
    try std.testing.expect(first_plan.absolute_offset != second_plan.absolute_offset);
    try std.testing.expect(first_plan.planned_value != second_plan.planned_value);
    try std.testing.expectEqual(second_plan.relative_offset, summary.relative_offset);
    try std.testing.expectEqual(second_plan.absolute_offset, summary.absolute_offset);
    try std.testing.expectEqual(second_plan.planned_value, summary.planned_value);
    try std.testing.expectEqual(second_plan.config_generation, summary.planned_generation);
    try std.testing.expect(planIsFresh(summary));
    try std.testing.expect(!planNeedsRefresh(summary));
    try std.testing.expect(planHasReviewableOffsets(summary));
}

test "phase10 virtio mmio plan-freshness wrapper keeps generation drift visible but unavailable" {
    var device = try virtio_mmio.VirtioMmioLab.init(95, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    const plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);
    device.bumpConfigGeneration();

    const summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqual(ConfigWritePlanAvailability.stale_generation, summary.availability);
    try std.testing.expect(summary.plan_present);
    try std.testing.expect(!summary.plan_matches_generation);
    try std.testing.expectEqual(plan.relative_offset, summary.relative_offset);
    try std.testing.expectEqual(plan.absolute_offset, summary.absolute_offset);
    try std.testing.expectEqual(plan.planned_value, summary.planned_value);
    try std.testing.expectEqual(plan.config_generation, summary.planned_generation);
    try std.testing.expectEqual(@as(u32, 1), summary.current_generation);
    try std.testing.expect(!planIsFresh(summary));
    try std.testing.expect(planNeedsRefresh(summary));
    try std.testing.expect(planHasReviewableOffsets(summary));
}

test "phase10 virtio mmio plan-freshness wrapper recovers fresh review state after generation drift" {
    var device = try virtio_mmio.VirtioMmioLab.init(97, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    const stale_plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);
    device.bumpConfigGeneration();

    var summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqual(ConfigWritePlanAvailability.stale_generation, summary.availability);
    try std.testing.expect(summary.plan_present);
    try std.testing.expect(!summary.plan_matches_generation);
    try std.testing.expectEqual(stale_plan.relative_offset, summary.relative_offset);
    try std.testing.expectEqual(stale_plan.absolute_offset, summary.absolute_offset);
    try std.testing.expectEqual(stale_plan.planned_value, summary.planned_value);
    try std.testing.expectEqual(@as(u32, 0), summary.planned_generation);
    try std.testing.expectEqual(@as(u32, 1), summary.current_generation);
    try std.testing.expect(!planIsFresh(summary));
    try std.testing.expect(planNeedsRefresh(summary));
    try std.testing.expect(planHasReviewableOffsets(summary));

    const refreshed_plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0409);
    summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqual(ConfigWritePlanAvailability.fresh, summary.availability);
    try std.testing.expect(summary.plan_present);
    try std.testing.expect(summary.plan_matches_generation);
    try std.testing.expectEqual(refreshed_plan.relative_offset, summary.relative_offset);
    try std.testing.expectEqual(refreshed_plan.absolute_offset, summary.absolute_offset);
    try std.testing.expectEqual(refreshed_plan.planned_value, summary.planned_value);
    try std.testing.expectEqual(@as(u32, 1), summary.planned_generation);
    try std.testing.expectEqual(@as(u32, 1), summary.current_generation);
    try std.testing.expect(planIsFresh(summary));
    try std.testing.expect(!planNeedsRefresh(summary));
    try std.testing.expect(planHasReviewableOffsets(summary));
}

test "phase10 virtio mmio plan-freshness wrapper clears restaged plans instead of reusing stale offsets" {
    var device = try virtio_mmio.VirtioMmioLab.init(96, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    _ = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x08, 0x07, 0x06, 0x05 });

    const summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqual(ConfigWritePlanAvailability.unavailable, summary.availability);
    try std.testing.expect(!summary.plan_present);
    try std.testing.expect(!summary.plan_matches_generation);
    try std.testing.expectEqual(@as(u32, 0), summary.relative_offset);
    try std.testing.expectEqual(@as(u32, 0), summary.absolute_offset);
    try std.testing.expectEqual(@as(u32, 0), summary.planned_value);
    try std.testing.expectEqual(@as(u32, 0), summary.planned_generation);
    try std.testing.expectEqual(device.config_generation, summary.current_generation);
    try std.testing.expect(!planIsFresh(summary));
    try std.testing.expect(!planNeedsRefresh(summary));
    try std.testing.expect(!planHasReviewableOffsets(summary));
}
