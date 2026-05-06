const std = @import("std");
const nvme_pci = @import("pci.zig");

test "phase12 nvme pci verify keeps descriptor rebuild DMA bytes tied to stale PRP list metadata" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    _ = try lab.planIoQueue(32, 64, false);
    const metadata = try lab.planPrpMetadata(8192, 0x180);

    _ = lab.beginReset();
    const frozen = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
        .cached_descriptor_dma_bytes = metadata.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = metadata.requires_descriptor_rebuild_after_reset,
    });
    try std.testing.expectEqual(nvme_pci.RecoveryState.reset_frozen, frozen.state);
    try std.testing.expect(frozen.cached_prp_metadata_stale);
    try std.testing.expect(frozen.descriptor_rebuild_required);
    try std.testing.expectEqual(metadata.metadata_dma_bytes, frozen.descriptor_rebuild_dma_bytes);
    try std.testing.expect(frozen.admin_queue_must_be_replanned);
    try std.testing.expect(frozen.io_queues_must_be_rebuilt);
    try std.testing.expectEqual(@as(usize, 1), frozen.io_queues_dropped_by_reset);
}

test "phase12 nvme pci verify keeps DMA rebuild bytes at zero when stale metadata was inline only" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(16, 64, false);
    const metadata = try lab.planPrpMetadata(4096, 0x80);

    _ = lab.beginReset();
    const frozen = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
        .cached_descriptor_dma_bytes = metadata.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = metadata.requires_descriptor_rebuild_after_reset,
    });
    try std.testing.expect(frozen.cached_prp_metadata_stale);
    try std.testing.expect(!frozen.descriptor_rebuild_required);
    try std.testing.expectEqual(@as(u32, 0), frozen.descriptor_rebuild_dma_bytes);
}

test "phase12 nvme pci verify preserves fresh cached metadata without forcing descriptor rebuild" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(24, 64, false);
    const metadata = try lab.planPrpMetadata(12288, 0x400);

    _ = lab.beginReset();
    _ = lab.completeReset();
    const current_generation = lab.recoverySummary().reset_generation;

    const replay = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = current_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = false,
        .cached_descriptor_dma_bytes = metadata.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = metadata.requires_descriptor_rebuild_after_reset,
    });
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, replay.state);
    try std.testing.expect(!replay.cached_prp_metadata_stale);
    try std.testing.expect(!replay.descriptor_rebuild_required);
    try std.testing.expectEqual(@as(u32, 0), replay.descriptor_rebuild_dma_bytes);
    try std.testing.expect(!replay.admin_queue_must_be_replanned);
}
