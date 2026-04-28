const std = @import("std");
const nvme_pci = @import("nvme_pci");

test "phase12 nvme pci descriptor and admin queue plan stay anchored to pci.c" {
    const descriptor = nvme_pci.NvmePciQueueLab.descriptor();
    try std.testing.expectEqualStrings("nvme_pci_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_queue_planner);
    try std.testing.expect(descriptor.provides_prp_shape_helper);
    try std.testing.expect(descriptor.provides_pointer_selection_helper);
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

test "phase12 nvme pci prp shape helper records first-page offset and list bounds" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    const shape = try lab.shapePrpBuffer(0x1180, 8192);

    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", shape.anchor);
    try std.testing.expectEqual(@as(u64, 0x1180), shape.dma_address);
    try std.testing.expectEqual(@as(u32, 8192), shape.transfer_bytes);
    try std.testing.expectEqual(@as(u32, 0x180), shape.first_page_offset);
    try std.testing.expectEqual(@as(u32, 8576), shape.spanned_bytes);
    try std.testing.expectEqual(@as(u32, 12288), shape.rounded_span_bytes);
    try std.testing.expectEqual(@as(u16, 3), shape.spanned_pages);
    try std.testing.expect(shape.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 2), shape.prp_list_entries);
    try std.testing.expectEqual(@as(u16, 512), shape.prp_list_entries_per_page);
    try std.testing.expectEqual(@as(u16, 1), shape.prp_list_pages);
    try std.testing.expect(shape.fits_single_prp_list_page);
    try std.testing.expectEqual(@as(u32, 0), shape.reset_generation);
}

test "phase12 nvme pci prp shape helper handles single-page spans and resumes after reset" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    const shape = try lab.shapePrpBuffer(0x2000, 1024);
    try std.testing.expectEqual(@as(u32, 0), shape.first_page_offset);
    try std.testing.expectEqual(@as(u16, 1), shape.spanned_pages);
    try std.testing.expect(!shape.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 0), shape.prp_list_entries);
    try std.testing.expectEqual(@as(u16, 0), shape.prp_list_pages);
    try std.testing.expect(shape.fits_single_prp_list_page);

    _ = lab.beginReset();
    try std.testing.expectError(error.QueuePlanningBlockedByReset, lab.shapePrpBuffer(0x2000, 1024));
    _ = lab.completeReset();

    const shape_after_reset = try lab.shapePrpBuffer(0x3080, 4096);
    try std.testing.expectEqual(@as(u32, 0x80), shape_after_reset.first_page_offset);
    try std.testing.expectEqual(@as(u16, 2), shape_after_reset.spanned_pages);
    try std.testing.expectEqual(@as(u32, 1), shape_after_reset.reset_generation);

    try std.testing.expectError(error.InvalidTransferBytes, lab.shapePrpBuffer(0x2000, 0));
}

test "phase12 nvme pci data pointer strategy blocks forced sgl cases when the queue cannot use sgl" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);

    const admin_strategy = try lab.planDataPointerStrategy(0, 8192, 2, 0x180, true, false, 0, 32768);
    try std.testing.expectEqual(nvme_pci.SglSupport.unavailable, admin_strategy.sgl_support);
    try std.testing.expectEqual(nvme_pci.DataPointerPlan.blocked, admin_strategy.selected_pointer);
    try std.testing.expectEqual(@as(u32, 4096), admin_strategy.average_segment_bytes);
    try std.testing.expect(admin_strategy.forced_by_page_gap);
    try std.testing.expect(!admin_strategy.forced_by_user_command);
    try std.testing.expect(!admin_strategy.forced_by_integrity_segments);
    try std.testing.expect(admin_strategy.forced_sgl_unavailable);
    try std.testing.expect(!admin_strategy.threshold_prefers_sgl);

    const unsupported_io_strategy = try lab.planDataPointerStrategy(1, 32768, 4, 0, false, true, 0, 32768);
    try std.testing.expectEqual(nvme_pci.SglSupport.unavailable, unsupported_io_strategy.sgl_support);
    try std.testing.expectEqual(nvme_pci.DataPointerPlan.blocked, unsupported_io_strategy.selected_pointer);
    try std.testing.expect(unsupported_io_strategy.forced_by_user_command);
    try std.testing.expect(unsupported_io_strategy.forced_sgl_unavailable);
}

test "phase12 nvme pci data pointer strategy selects prp, threshold sgl, and forced sgl paths" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);

    const prp_strategy = try lab.planDataPointerStrategy(1, 16384, 8, 0, true, false, 0, 4096);
    try std.testing.expectEqual(nvme_pci.SglSupport.optional, prp_strategy.sgl_support);
    try std.testing.expectEqual(nvme_pci.DataPointerPlan.prp, prp_strategy.selected_pointer);
    try std.testing.expectEqual(@as(u32, 2048), prp_strategy.average_segment_bytes);
    try std.testing.expect(!prp_strategy.threshold_prefers_sgl);

    const threshold_strategy = try lab.planDataPointerStrategy(2, 65536, 2, 0, true, false, 0, 32768);
    try std.testing.expectEqual(nvme_pci.SglSupport.optional, threshold_strategy.sgl_support);
    try std.testing.expectEqual(nvme_pci.DataPointerPlan.sgl, threshold_strategy.selected_pointer);
    try std.testing.expectEqual(@as(u32, 32768), threshold_strategy.average_segment_bytes);
    try std.testing.expect(threshold_strategy.threshold_prefers_sgl);

    const forced_strategy = try lab.planDataPointerStrategy(3, 8192, 2, 0, true, false, 2, 32768);
    try std.testing.expectEqual(nvme_pci.SglSupport.forced, forced_strategy.sgl_support);
    try std.testing.expectEqual(nvme_pci.DataPointerPlan.sgl, forced_strategy.selected_pointer);
    try std.testing.expect(forced_strategy.forced_by_integrity_segments);
    try std.testing.expect(!forced_strategy.forced_sgl_unavailable);
}

test "phase12 nvme pci data pointer strategy respects reset freeze and resumes after reset" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    try std.testing.expectError(error.InvalidSegmentCount, lab.planDataPointerStrategy(1, 4096, 0, 0, true, false, 0, 32768));

    _ = lab.beginReset();
    try std.testing.expectError(error.QueuePlanningBlockedByReset, lab.planDataPointerStrategy(1, 4096, 1, 0, true, false, 0, 32768));

    _ = lab.completeReset();
    const strategy_after_reset = try lab.planDataPointerStrategy(1, 16384, 4, 0, true, false, 0, 4096);
    try std.testing.expectEqual(nvme_pci.SglSupport.optional, strategy_after_reset.sgl_support);
    try std.testing.expectEqual(nvme_pci.DataPointerPlan.sgl, strategy_after_reset.selected_pointer);
    try std.testing.expect(strategy_after_reset.threshold_prefers_sgl);
    try std.testing.expectEqual(@as(u32, 1), strategy_after_reset.reset_generation);
}

test "phase12 nvme pci recovery replay summary marks cached planning stale during and after reset" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);
    _ = try lab.shapePrpBuffer(0x1180, 8192);
    _ = try lab.planDataPointerStrategy(2, 32768, 4, 0, true, false, 0, 4096);

    _ = lab.beginReset();
    const frozen_summary = lab.summarizeRecoveryReplay(.{
        .cached_prp_shape_generation = 0,
        .cached_pointer_plan_generation = 0,
        .had_admin_queue_plan = true,
    });
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", frozen_summary.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryState.reset_frozen, frozen_summary.state);
    try std.testing.expectEqual(@as(u32, 1), frozen_summary.reset_generation);
    try std.testing.expect(frozen_summary.queue_planning_blocked);
    try std.testing.expect(frozen_summary.cached_prp_shape_stale);
    try std.testing.expect(frozen_summary.cached_pointer_plan_stale);
    try std.testing.expect(frozen_summary.admin_queue_must_be_replanned);
    try std.testing.expect(frozen_summary.io_queues_must_be_rebuilt);
    try std.testing.expectEqual(@as(usize, 2), frozen_summary.io_queues_dropped_by_reset);
    try std.testing.expectEqual(@as(u16, 3), frozen_summary.next_io_queue_id);
    try std.testing.expectEqual(@as(u16, 48), frozen_summary.last_admin_queue_depth);

    _ = lab.completeReset();
    const replay_summary = lab.summarizeRecoveryReplay(.{
        .cached_prp_shape_generation = 0,
        .cached_pointer_plan_generation = 0,
        .had_admin_queue_plan = true,
    });
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, replay_summary.state);
    try std.testing.expect(!replay_summary.queue_planning_blocked);
    try std.testing.expect(replay_summary.cached_prp_shape_stale);
    try std.testing.expect(replay_summary.cached_pointer_plan_stale);
    try std.testing.expect(replay_summary.admin_queue_must_be_replanned);
    try std.testing.expect(replay_summary.io_queues_must_be_rebuilt);
    try std.testing.expectEqual(@as(usize, 2), replay_summary.io_queues_dropped_by_reset);
    try std.testing.expectEqual(@as(u16, 1), replay_summary.next_io_queue_id);
    try std.testing.expectEqual(@as(u16, 48), replay_summary.last_admin_queue_depth);
}

test "phase12 nvme pci recovery replay summary stays current when cached helpers match the running generation" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);

    const before_reset = lab.summarizeRecoveryReplay(.{
        .cached_prp_shape_generation = 0,
        .cached_pointer_plan_generation = 0,
        .had_admin_queue_plan = true,
    });
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, before_reset.state);
    try std.testing.expect(!before_reset.queue_planning_blocked);
    try std.testing.expect(!before_reset.cached_prp_shape_stale);
    try std.testing.expect(!before_reset.cached_pointer_plan_stale);
    try std.testing.expect(!before_reset.admin_queue_must_be_replanned);
    try std.testing.expect(!before_reset.io_queues_must_be_rebuilt);
    try std.testing.expectEqual(@as(usize, 0), before_reset.io_queues_dropped_by_reset);
    try std.testing.expectEqual(@as(u16, 1), before_reset.next_io_queue_id);
    try std.testing.expectEqual(@as(u16, 32), before_reset.last_admin_queue_depth);

    _ = lab.beginReset();
    _ = lab.completeReset();
    const current_generation = lab.recoverySummary().reset_generation;
    const after_refresh = lab.summarizeRecoveryReplay(.{
        .cached_prp_shape_generation = current_generation,
        .cached_pointer_plan_generation = current_generation,
        .had_admin_queue_plan = false,
    });
    try std.testing.expectEqual(@as(u32, 1), after_refresh.reset_generation);
    try std.testing.expect(!after_refresh.cached_prp_shape_stale);
    try std.testing.expect(!after_refresh.cached_pointer_plan_stale);
    try std.testing.expect(!after_refresh.admin_queue_must_be_replanned);
    try std.testing.expect(!after_refresh.io_queues_must_be_rebuilt);
    try std.testing.expectEqual(@as(usize, 0), after_refresh.io_queues_dropped_by_reset);
    try std.testing.expectEqual(@as(u16, 1), after_refresh.next_io_queue_id);
}
