const std = @import("std");
const testing = std.testing;
const nvme_pci = @import("pci.zig");

test "nvme pci queue-count throughput plan stays controller-capped and restarts after reset" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 16);
    _ = try lab.planAdminQueue(64, 64, false);
    _ = try lab.planIoQueue(128, 64, true);

    const throughput = try lab.planIoQueueCount(48, 31);
    try testing.expectEqual(@as(usize, 48), throughput.requested_io_queues);
    try testing.expectEqual(@as(usize, 31), throughput.controller_io_queue_limit);
    try testing.expectEqual(@as(usize, 63), throughput.planner_remaining_io_slots);
    try testing.expectEqual(@as(usize, 31), throughput.selected_io_queues);
    try testing.expectEqual(@as(u16, 2), throughput.first_queue_id);
    try testing.expectEqual(@as(u16, 32), throughput.last_queue_id);
    try testing.expectEqual(@as(usize, 33), throughput.queue_pairs_after_plan);
    try testing.expect(throughput.controller_limited);
    try testing.expect(!throughput.planner_limited);
    try testing.expect(!throughput.queues_frozen);
    try testing.expectEqual(@as(u32, 0), throughput.reset_generation);

    _ = lab.beginReset();
    try testing.expectError(error.QueuePlanningBlockedByReset, lab.planIoQueueCount(4, 8));

    _ = lab.completeReset();
    const resumed = try lab.planIoQueueCount(4, 8);
    try testing.expectEqual(@as(usize, 4), resumed.selected_io_queues);
    try testing.expectEqual(@as(u16, 1), resumed.first_queue_id);
    try testing.expectEqual(@as(u16, 4), resumed.last_queue_id);
    try testing.expectEqual(@as(usize, 5), resumed.queue_pairs_after_plan);
    try testing.expectEqual(@as(u32, 1), resumed.reset_generation);
}

test "nvme pci recovery replay clears stale admin and prp cues only after refresh while keeping queue rebuild pressure visible" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(32, 64, false);
    const metadata = try lab.planPrpMetadata(8192, 0x180);
    try testing.expect(metadata.requires_descriptor_rebuild_after_reset);

    _ = lab.beginReset();
    _ = lab.completeReset();

    const stale = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = metadata.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
        .cached_descriptor_dma_bytes = metadata.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = metadata.requires_descriptor_rebuild_after_reset,
    });
    try testing.expectEqual(nvme_pci.RecoveryState.running, stale.state);
    try testing.expect(!stale.queue_planning_blocked);
    try testing.expect(stale.cached_prp_metadata_stale);
    try testing.expect(stale.descriptor_rebuild_required);
    try testing.expectEqual(metadata.metadata_dma_bytes, stale.descriptor_rebuild_dma_bytes);
    try testing.expect(stale.admin_queue_must_be_replanned);
    try testing.expect(stale.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 1), stale.io_queues_dropped_by_reset);
    try testing.expectEqual(@as(u16, 1), stale.next_io_queue_id);
    try testing.expectEqual(@as(u16, 48), stale.last_admin_queue_depth);

    _ = try lab.planAdminQueue(48, 64, false);
    const refreshed_metadata = try lab.planPrpMetadata(8192, 0x180);
    const refreshed = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = refreshed_metadata.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = false,
        .cached_descriptor_dma_bytes = refreshed_metadata.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = refreshed_metadata.requires_descriptor_rebuild_after_reset,
    });
    try testing.expect(!refreshed.cached_prp_metadata_stale);
    try testing.expect(!refreshed.descriptor_rebuild_required);
    try testing.expectEqual(@as(u32, 0), refreshed.descriptor_rebuild_dma_bytes);
    try testing.expect(!refreshed.admin_queue_must_be_replanned);
    try testing.expect(refreshed.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 1), refreshed.io_queues_dropped_by_reset);
    try testing.expectEqual(@as(u16, 1), refreshed.next_io_queue_id);
    try testing.expectEqual(@as(u16, 48), refreshed.last_admin_queue_depth);
    try testing.expectEqual(@as(u32, 1), refreshed.reset_generation);
}

test "nvme pci recovery replay keeps stale inline-only metadata from overclaiming descriptor rebuild bytes" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    const inline_only = try lab.planPrpMetadata(4096, 0x80);
    try testing.expect(!inline_only.requires_descriptor_rebuild_after_reset);

    _ = lab.beginReset();
    const stale_inline_only = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = inline_only.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
        .cached_descriptor_dma_bytes = inline_only.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = inline_only.requires_descriptor_rebuild_after_reset,
    });
    try testing.expect(stale_inline_only.cached_prp_metadata_stale);
    try testing.expect(!stale_inline_only.descriptor_rebuild_required);
    try testing.expectEqual(@as(u32, 0), stale_inline_only.descriptor_rebuild_dma_bytes);
}
