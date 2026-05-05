const std = @import("std");
const nvme_pci = @import("nvme_pci");

test "phase12 nvme pci descriptor and admin queue plan stay anchored to pci.c" {
    const descriptor = nvme_pci.NvmePciQueueLab.descriptor();
    try std.testing.expectEqualStrings("nvme_pci_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_queue_planner);
    try std.testing.expect(descriptor.provides_prp_metadata_helper);
    try std.testing.expect(descriptor.provides_recovery_replay_helper);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_pci_probe);
    try std.testing.expect(!descriptor.touches_irq_recovery);

    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    const admin = try lab.planAdminQueue(32, 64, false);
    try std.testing.expectEqual(nvme_pci.QueueRole.admin, admin.role);
    try std.testing.expectEqual(@as(u16, 0), admin.queue_id);
    try std.testing.expectEqual(@as(u32, 2048), admin.sq_bytes);
    try std.testing.expectEqual(@as(u32, 512), admin.cq_bytes);
    try std.testing.expectEqual(@as(u32, 2560), admin.queue_memory_bytes);
    try std.testing.expectEqual(@as(u32, 2560), admin.host_dma_bytes);
    try std.testing.expectEqual(@as(u16, 1), admin.required_host_dma_pages);
    try std.testing.expectEqual(@as(u32, 0), admin.sq_doorbell_offset);
    try std.testing.expectEqual(@as(u32, 8), admin.cq_doorbell_offset);

    const recovery = lab.recoverySummary();
    try std.testing.expectEqual(@as(u16, 32), recovery.last_admin_queue_depth);
    try std.testing.expectEqual(@as(usize, 0), recovery.planned_io_queues);
}

test "phase12 nvme pci ownership summary keeps starter and blocked transport work separate" {
    const ownership = nvme_pci.NvmePciQueueLab.ownershipSummary();
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", ownership.anchor);
    try std.testing.expectEqualStrings("P12-Y02", ownership.owner_lane);
    try std.testing.expectEqual(nvme_pci.OwnershipBoundary.starter_packet, ownership.queue_planning_owner);
    try std.testing.expectEqual(nvme_pci.OwnershipBoundary.starter_packet, ownership.prp_shape_owner);
    try std.testing.expectEqual(nvme_pci.OwnershipBoundary.dma_transport_substrate, ownership.live_dma_owner);
    try std.testing.expectEqual(nvme_pci.OwnershipBoundary.dma_transport_substrate, ownership.recovery_transport_owner);
}

test "phase12 nvme pci separates queue footprint from host DMA when CMB backs SQ" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 16);
    _ = try lab.planAdminQueue(64, 64, false);

    const first = try lab.planIoQueue(512, 64, true);
    try std.testing.expectEqual(nvme_pci.QueueRole.io, first.role);
    try std.testing.expectEqual(@as(u16, 1), first.queue_id);
    try std.testing.expectEqual(@as(u32, 32768), first.sq_bytes);
    try std.testing.expectEqual(@as(u32, 8192), first.cq_bytes);
    try std.testing.expectEqual(@as(u32, 40960), first.queue_memory_bytes);
    try std.testing.expectEqual(@as(u32, 8192), first.host_dma_bytes);
    try std.testing.expectEqual(@as(u16, 2), first.required_host_dma_pages);
    try std.testing.expectEqual(@as(u32, 32), first.sq_doorbell_offset);
    try std.testing.expectEqual(@as(u32, 48), first.cq_doorbell_offset);
    try std.testing.expect(first.uses_cmb);

    const second = try lab.planIoQueue(128, 32, false);
    try std.testing.expectEqual(@as(u16, 2), second.queue_id);
    try std.testing.expectEqual(@as(u32, 6144), second.host_dma_bytes);
    try std.testing.expectEqual(@as(u16, 2), second.required_host_dma_pages);
    try std.testing.expectEqual(@as(u32, 64), second.sq_doorbell_offset);
    try std.testing.expectEqual(@as(u32, 80), second.cq_doorbell_offset);

    const recovery = lab.recoverySummary();
    try std.testing.expectEqual(@as(usize, 2), recovery.planned_io_queues);
    try std.testing.expectEqual(@as(u32, 0), recovery.reset_generation);
}

test "phase12 nvme pci plans PRP buffer shapes without claiming live DMA setup" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);

    const single_page = try lab.planPrpBufferShape(512, 128);
    try std.testing.expectEqual(@as(u32, 512), single_page.total_transfer_bytes);
    try std.testing.expectEqual(@as(u32, 128), single_page.first_page_offset);
    try std.testing.expectEqual(@as(u32, 512), single_page.first_prp_bytes);
    try std.testing.expectEqual(@as(u32, 4096), single_page.rounded_span_bytes);
    try std.testing.expectEqual(@as(u16, 1), single_page.spanned_pages);
    try std.testing.expectEqual(@as(u16, 0), single_page.tail_page_count);
    try std.testing.expect(!single_page.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 0), single_page.prp_list_entries);
    try std.testing.expectEqual(@as(u16, 512), single_page.prp_list_capacity);

    const multi_page = try lab.planPrpBufferShape(9000, 128);
    try std.testing.expectEqual(@as(u32, 3968), multi_page.first_prp_bytes);
    try std.testing.expectEqual(@as(u32, 12288), multi_page.rounded_span_bytes);
    try std.testing.expectEqual(@as(u16, 3), multi_page.spanned_pages);
    try std.testing.expectEqual(@as(u16, 2), multi_page.tail_page_count);
    try std.testing.expect(multi_page.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 1), multi_page.prp_list_entries);
}

test "phase12 nvme pci rejects invalid PRP offsets and oversized list shapes" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    try std.testing.expectError(error.InvalidTransferSize, lab.planPrpBufferShape(0, 0));
    try std.testing.expectError(error.InvalidPrpOffset, lab.planPrpBufferShape(4096, 4096));
    try std.testing.expectError(error.PrpListTooLong, lab.planPrpBufferShape(4096 * 515, 0));
}

test "phase12 nvme pci prp metadata helper quantifies descriptor DMA footprint" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);

    const metadata = try lab.planPrpMetadata(8192, 0x180);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", metadata.anchor);
    try std.testing.expectEqual(@as(u16, 3), metadata.spanned_pages);
    try std.testing.expect(metadata.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 1), metadata.command_data_prp_entries);
    try std.testing.expectEqual(@as(u16, 2), metadata.prp_list_covered_pages);
    try std.testing.expectEqual(@as(u16, 1), metadata.prp_list_pages);
    try std.testing.expectEqual(@as(u32, 4096), metadata.metadata_dma_bytes);
    try std.testing.expectEqual(@as(u32, 16384), metadata.total_dma_bytes);
    try std.testing.expect(metadata.requires_descriptor_rebuild_after_reset);
    try std.testing.expectEqual(@as(u32, 0), metadata.reset_generation);

    const inline_only = try lab.planPrpMetadata(4096, 0x80);
    try std.testing.expectEqual(@as(u16, 2), inline_only.spanned_pages);
    try std.testing.expect(!inline_only.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 2), inline_only.command_data_prp_entries);
    try std.testing.expectEqual(@as(u16, 0), inline_only.prp_list_covered_pages);
    try std.testing.expectEqual(@as(u16, 0), inline_only.prp_list_pages);
    try std.testing.expectEqual(@as(u32, 0), inline_only.metadata_dma_bytes);
    try std.testing.expectEqual(@as(u32, 8192), inline_only.total_dma_bytes);
    try std.testing.expect(!inline_only.requires_descriptor_rebuild_after_reset);
}

test "phase12 nvme pci prp metadata helper respects reset freeze and resumes after reset" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = lab.beginReset();
    try std.testing.expectError(error.QueuePlanningBlockedByReset, lab.planPrpMetadata(8192, 0x180));

    _ = lab.completeReset();
    const metadata = try lab.planPrpMetadata(12288, 0x400);
    try std.testing.expectEqual(@as(u16, 4), metadata.spanned_pages);
    try std.testing.expect(metadata.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 3), metadata.prp_list_covered_pages);
    try std.testing.expectEqual(@as(u32, 4096), metadata.metadata_dma_bytes);
    try std.testing.expectEqual(@as(u32, 20480), metadata.total_dma_bytes);
    try std.testing.expect(metadata.requires_descriptor_rebuild_after_reset);
    try std.testing.expectEqual(@as(u32, 1), metadata.reset_generation);
}

test "phase12 nvme pci recovery replay summary marks cached metadata stale during and after reset" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);
    _ = try lab.planPrpMetadata(8192, 0x180);

    _ = lab.beginReset();
    const frozen_summary = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
    });
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", frozen_summary.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryState.reset_frozen, frozen_summary.state);
    try std.testing.expectEqual(@as(u32, 1), frozen_summary.reset_generation);
    try std.testing.expect(frozen_summary.queue_planning_blocked);
    try std.testing.expect(frozen_summary.cached_prp_metadata_stale);
    try std.testing.expect(frozen_summary.admin_queue_must_be_replanned);
    try std.testing.expect(frozen_summary.io_queues_must_be_rebuilt);
    try std.testing.expectEqual(@as(usize, 2), frozen_summary.io_queues_dropped_by_reset);
    try std.testing.expectEqual(@as(u16, 3), frozen_summary.next_io_queue_id);
    try std.testing.expectEqual(@as(u16, 48), frozen_summary.last_admin_queue_depth);

    _ = lab.completeReset();
    const replay_summary = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
    });
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, replay_summary.state);
    try std.testing.expect(!replay_summary.queue_planning_blocked);
    try std.testing.expect(replay_summary.cached_prp_metadata_stale);
    try std.testing.expect(replay_summary.admin_queue_must_be_replanned);
    try std.testing.expect(replay_summary.io_queues_must_be_rebuilt);
    try std.testing.expectEqual(@as(usize, 2), replay_summary.io_queues_dropped_by_reset);
    try std.testing.expectEqual(@as(u16, 1), replay_summary.next_io_queue_id);
    try std.testing.expectEqual(@as(u16, 48), replay_summary.last_admin_queue_depth);
}

test "phase12 nvme pci recovery replay summary clears rollback gate after helper refresh" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);

    const before_reset = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
    });
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, before_reset.state);
    try std.testing.expect(!before_reset.queue_planning_blocked);
    try std.testing.expect(!before_reset.cached_prp_metadata_stale);
    try std.testing.expect(!before_reset.admin_queue_must_be_replanned);
    try std.testing.expect(!before_reset.io_queues_must_be_rebuilt);
    try std.testing.expectEqual(@as(usize, 0), before_reset.io_queues_dropped_by_reset);
    try std.testing.expectEqual(@as(u16, 1), before_reset.next_io_queue_id);
    try std.testing.expectEqual(@as(u16, 32), before_reset.last_admin_queue_depth);

    _ = lab.beginReset();
    _ = lab.completeReset();
    const current_generation = lab.recoverySummary().reset_generation;
    const after_refresh = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = current_generation,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = false,
    });
    try std.testing.expectEqual(@as(u32, 1), after_refresh.reset_generation);
    try std.testing.expect(!after_refresh.cached_prp_metadata_stale);
    try std.testing.expect(!after_refresh.admin_queue_must_be_replanned);
    try std.testing.expect(!after_refresh.io_queues_must_be_rebuilt);
    try std.testing.expectEqual(@as(usize, 0), after_refresh.io_queues_dropped_by_reset);
    try std.testing.expectEqual(@as(u16, 1), after_refresh.next_io_queue_id);
}

test "phase12 nvme pci recovery replay does not overclaim stale metadata when none was cached" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(16, 64, false);
    _ = try lab.planIoQueue(8, 64, false);

    _ = lab.beginReset();
    const frozen_summary = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
    });
    try std.testing.expect(!frozen_summary.cached_prp_metadata_stale);
    try std.testing.expect(frozen_summary.admin_queue_must_be_replanned);
    try std.testing.expect(frozen_summary.io_queues_must_be_rebuilt);

    _ = lab.completeReset();
    const replay_summary = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
    });
    try std.testing.expect(!replay_summary.cached_prp_metadata_stale);
    try std.testing.expect(replay_summary.admin_queue_must_be_replanned);
    try std.testing.expect(replay_summary.io_queues_must_be_rebuilt);
    try std.testing.expectEqual(@as(usize, 1), replay_summary.io_queues_dropped_by_reset);
}

test "phase12 nvme pci rejects invalid queue geometry and excessive io queue plans" {
    try std.testing.expectError(error.InvalidPageSize, nvme_pci.NvmePciQueueLab.init(2048, 8));
    try std.testing.expectError(error.InvalidDoorbellStride, nvme_pci.NvmePciQueueLab.init(4096, 6));

    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    try std.testing.expectError(error.QueueDepthOutOfRange, lab.planAdminQueue(1, 64, false));
    try std.testing.expectError(error.QueueDepthOutOfRange, lab.planAdminQueue(4096, 64, false));
    try std.testing.expectError(error.InvalidSqEntryBytes, lab.planAdminQueue(64, 24, false));

    var counted: usize = 0;
    while (counted < nvme_pci.max_planned_io_queues) : (counted += 1) {
        _ = try lab.planIoQueue(8, 64, false);
    }
    try std.testing.expectError(error.TooManyPlannedIoQueues, lab.planIoQueue(8, 64, false));
}

test "phase12 nvme pci freezes queue planning across reset and restarts io numbering afterward" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    _ = try lab.planIoQueue(16, 64, false);

    var recovery = lab.beginReset();
    try std.testing.expectEqual(nvme_pci.RecoveryState.reset_frozen, recovery.state);
    try std.testing.expect(recovery.queues_frozen);
    try std.testing.expectEqual(@as(u32, 1), recovery.reset_generation);
    try std.testing.expectError(error.QueuePlanningBlockedByReset, lab.planAdminQueue(16, 64, false));
    try std.testing.expectError(error.QueuePlanningBlockedByReset, lab.planIoQueue(16, 64, false));

    recovery = lab.completeReset();
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, recovery.state);
    try std.testing.expect(!recovery.queues_frozen);
    try std.testing.expectEqual(@as(usize, 0), recovery.planned_io_queues);
    try std.testing.expectEqual(@as(u16, 32), recovery.last_admin_queue_depth);

    const admin_after_reset = try lab.planAdminQueue(24, 64, false);
    try std.testing.expectEqual(@as(u16, 0), admin_after_reset.queue_id);
    try std.testing.expectEqual(@as(u32, 1), admin_after_reset.reset_generation);

    const io_after_reset = try lab.planIoQueue(16, 64, false);
    try std.testing.expectEqual(@as(u16, 1), io_after_reset.queue_id);
    try std.testing.expectEqual(@as(u32, 1), io_after_reset.reset_generation);

    recovery = lab.recoverySummary();
    try std.testing.expectEqual(@as(u16, 24), recovery.last_admin_queue_depth);
}
