const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

pub const ConfigWritePlanFreshnessSummary = virtio_mmio.ConfigWritePlanFreshnessSummary;
pub const ConfigWritePlanAvailability = virtio_mmio.ConfigWritePlanAvailability;

pub fn summarizeConfigWritePlanFreshness(
    device: *const virtio_mmio.VirtioMmioLab,
) ConfigWritePlanFreshnessSummary {
    return device.configWritePlanFreshnessSummary();
}

pub fn availabilityTag(availability: ConfigWritePlanAvailability) []const u8 {
    return @tagName(availability);
}

pub fn planPresent(summary: ConfigWritePlanFreshnessSummary) bool {
    return summary.plan_present;
}

pub fn planMatchesGeneration(summary: ConfigWritePlanFreshnessSummary) bool {
    return summary.plan_matches_generation;
}

pub fn availableForDisposition(summary: ConfigWritePlanFreshnessSummary) bool {
    return summary.available_for_disposition;
}

pub fn staleGeneration(summary: ConfigWritePlanFreshnessSummary) bool {
    return summary.availability == .stale_generation;
}

pub fn offsetMatches(
    summary: ConfigWritePlanFreshnessSummary,
    expected_relative_offset: u32,
    expected_absolute_offset: u32,
) bool {
    return summary.relative_offset == expected_relative_offset and
        summary.absolute_offset == expected_absolute_offset;
}

test "phase10 virtio mmio plan-freshness wrapper keeps unavailable and fresh plan states explicit" {
    var device = try virtio_mmio.VirtioMmioLab.init(96, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    var summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings(virtio_mmio.anchor_path, summary.anchor);
    try std.testing.expectEqualStrings("unavailable", availabilityTag(summary.availability));
    try std.testing.expect(!planPresent(summary));
    try std.testing.expect(!planMatchesGeneration(summary));
    try std.testing.expect(!availableForDisposition(summary));

    const plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);
    summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings("fresh", availabilityTag(summary.availability));
    try std.testing.expect(planPresent(summary));
    try std.testing.expect(planMatchesGeneration(summary));
    try std.testing.expect(offsetMatches(summary, plan.relative_offset, plan.absolute_offset));
    try std.testing.expectEqual(plan.planned_value, summary.planned_value);
    try std.testing.expectEqual(plan.config_generation, summary.planned_generation);
    try std.testing.expectEqual(@as(u32, 0), summary.current_generation);
    try std.testing.expect(availableForDisposition(summary));
}

test "phase10 virtio mmio plan-freshness wrapper keeps stale and restaged plan boundaries explicit" {
    var device = try virtio_mmio.VirtioMmioLab.init(97, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    const stale_plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0407);
    device.bumpConfigGeneration();

    var summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings("stale_generation", availabilityTag(summary.availability));
    try std.testing.expect(planPresent(summary));
    try std.testing.expect(!planMatchesGeneration(summary));
    try std.testing.expect(staleGeneration(summary));
    try std.testing.expect(offsetMatches(summary, stale_plan.relative_offset, stale_plan.absolute_offset));
    try std.testing.expectEqual(stale_plan.planned_value, summary.planned_value);
    try std.testing.expectEqual(@as(u32, 0), summary.planned_generation);
    try std.testing.expectEqual(@as(u32, 1), summary.current_generation);
    try std.testing.expect(!availableForDisposition(summary));

    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x08, 0x07, 0x06, 0x05 });
    summary = summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings("unavailable", availabilityTag(summary.availability));
    try std.testing.expect(!planPresent(summary));
    try std.testing.expect(!planMatchesGeneration(summary));
    try std.testing.expect(!staleGeneration(summary));
    try std.testing.expect(!availableForDisposition(summary));
}
