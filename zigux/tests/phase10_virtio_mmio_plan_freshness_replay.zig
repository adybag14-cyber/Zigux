const std = @import("std");
const virtio_mmio = @import("virtio_mmio");
const plan_freshness = @import("virtio_mmio_plan_freshness");

test "phase10 virtio mmio plan-freshness replay keeps fresh, stale, replacement, and restaged plan states reviewable" {
    var device = try virtio_mmio.VirtioMmioLab.init(101, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });

    var summary = plan_freshness.summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings("unavailable", plan_freshness.availabilityTag(summary.availability));
    try std.testing.expect(!plan_freshness.planPresent(summary));
    try std.testing.expect(!plan_freshness.availableForDisposition(summary));

    const plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_0409);
    summary = plan_freshness.summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings("fresh", plan_freshness.availabilityTag(summary.availability));
    try std.testing.expect(plan_freshness.planPresent(summary));
    try std.testing.expect(plan_freshness.planMatchesGeneration(summary));
    try std.testing.expect(plan_freshness.offsetMatches(summary, plan.relative_offset, plan.absolute_offset));
    try std.testing.expectEqual(plan.planned_value, summary.planned_value);
    try std.testing.expect(plan_freshness.availableForDisposition(summary));

    device.bumpConfigGeneration();
    summary = plan_freshness.summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings("stale_generation", plan_freshness.availabilityTag(summary.availability));
    try std.testing.expect(plan_freshness.planPresent(summary));
    try std.testing.expect(!plan_freshness.planMatchesGeneration(summary));
    try std.testing.expect(plan_freshness.staleGeneration(summary));
    try std.testing.expect(!plan_freshness.availableForDisposition(summary));

    const replacement_plan = try device.planConfigWriteOffset(virtio_mmio.mmio_window_bytes + 4, 0x0203_040b);
    summary = plan_freshness.summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings("fresh", plan_freshness.availabilityTag(summary.availability));
    try std.testing.expect(plan_freshness.planPresent(summary));
    try std.testing.expect(plan_freshness.planMatchesGeneration(summary));
    try std.testing.expect(!plan_freshness.staleGeneration(summary));
    try std.testing.expect(plan_freshness.offsetMatches(summary, replacement_plan.relative_offset, replacement_plan.absolute_offset));
    try std.testing.expectEqual(replacement_plan.planned_value, summary.planned_value);
    try std.testing.expectEqual(device.config_generation, summary.planned_generation);
    try std.testing.expectEqual(device.config_generation, summary.current_generation);
    try std.testing.expect(plan_freshness.availableForDisposition(summary));

    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x09, 0x08, 0x07, 0x06 });
    summary = plan_freshness.summarizeConfigWritePlanFreshness(&device);
    try std.testing.expectEqualStrings("unavailable", plan_freshness.availabilityTag(summary.availability));
    try std.testing.expect(!plan_freshness.planPresent(summary));
    try std.testing.expect(!plan_freshness.planMatchesGeneration(summary));
    try std.testing.expect(!plan_freshness.staleGeneration(summary));
    try std.testing.expect(!plan_freshness.availableForDisposition(summary));
}
