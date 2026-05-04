const std = @import("std");
const nvme_pci = @import("nvme_pci");

test "phase12 nvme pci descriptor and admin queue plan stay anchored to pci.c" {
    const descriptor = nvme_pci.NvmePciQueueLab.descriptor();
    try std.testing.expectEqualStrings("nvme_pci_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_queue_planner);
    try std.testing.expect(descriptor.provides_queue_count_helper);
    try std.testing.expect(descriptor.provides_prp_shape_helper);
    try std.testing.expect(descriptor.provides_prp_metadata_helper);
    try std.testing.expect(descriptor.provides_pointer_selection_helper);
    try std.testing.expect(descriptor.provides_recovery_replay_helper);
    try std.testing.expect(descriptor.provides_doorbell_window_helper);
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

test "phase12 nvme pci io queue count helper negotiates controller and planner caps" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    _ = try lab.planIoQueue(16, 64, false);

    const controller_capped = try lab.planIoQueueCount(8, 4);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", controller_capped.anchor);
    try std.testing.expectEqual(@as(usize, 8), controller_capped.requested_io_queues);
    try std.testing.expectEqual(@as(usize, 4), controller_capped.controller_io_queue_limit);
    try std.testing.expectEqual(@as(usize, 63), controller_capped.planner_remaining_io_slots);
    try std.testing.expectEqual(@as(usize, 4), controller_capped.selected_io_queues);
    try std.testing.expectEqual(@as(u16, 2), controller_capped.first_queue_id);
    try std.testing.expectEqual(@as(u16, 5), controller_capped.last_queue_id);
    try std.testing.expectEqual(@as(usize, 6), controller_capped.queue_pairs_after_plan);
    try std.testing.expect(controller_capped.controller_limited);
    try std.testing.expect(!controller_capped.planner_limited);
    try std.testing.expect(!controller_capped.queues_frozen);
    try std.testing.expectEqual(@as(u32, 0), controller_capped.reset_generation);

    var planner_capped_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try planner_capped_lab.planAdminQueue(32, 64, false);
    var counted: usize = 0;
    while (counted < 62) : (counted += 1) {
        _ = try planner_capped_lab.planIoQueue(8, 64, false);
    }

    const planner_capped = try planner_capped_lab.planIoQueueCount(8, 10);
    try std.testing.expectEqual(@as(usize, 2), planner_capped.planner_remaining_io_slots);
    try std.testing.expectEqual(@as(usize, 2), planner_capped.selected_io_queues);
    try std.testing.expectEqual(@as(u16, 63), planner_capped.first_queue_id);
    try std.testing.expectEqual(@as(u16, 64), planner_capped.last_queue_id);
    try std.testing.expectEqual(@as(usize, 65), planner_capped.queue_pairs_after_plan);
    try std.testing.expect(!planner_capped.controller_limited);
    try std.testing.expect(planner_capped.planner_limited);
}

test "phase12 nvme pci io queue count helper rejects empty negotiation and respects reset freeze" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    try std.testing.expectError(error.InvalidRequestedIoQueues, lab.planIoQueueCount(0, 4));
    try std.testing.expectError(error.InvalidControllerQueueCount, lab.planIoQueueCount(4, 0));

    _ = try lab.planAdminQueue(32, 64, false);
    var counted: usize = 0;
    while (counted < nvme_pci.max_planned_io_queues) : (counted += 1) {
        _ = try lab.planIoQueue(8, 64, false);
    }
    try std.testing.expectError(error.NoQueueIdsAvailable, lab.planIoQueueCount(1, 1));

    var reset_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = reset_lab.beginReset();
    try std.testing.expectError(error.QueuePlanningBlockedByReset, reset_lab.planIoQueueCount(1, 1));
    _ = reset_lab.completeReset();

    const after_reset = try reset_lab.planIoQueueCount(3, 5);
    try std.testing.expectEqual(@as(usize, 3), after_reset.selected_io_queues);
    try std.testing.expectEqual(@as(u16, 1), after_reset.first_queue_id);
    try std.testing.expectEqual(@as(u16, 3), after_reset.last_queue_id);
    try std.testing.expectEqual(@as(u32, 1), after_reset.reset_generation);
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

test "phase12 nvme pci prp metadata helper quantifies descriptor DMA footprint" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);

    const metadata = try lab.planPrpMetadata(0x1180, 8192);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", metadata.anchor);
    try std.testing.expectEqual(@as(u16, 3), metadata.spanned_pages);
    try std.testing.expect(metadata.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 2), metadata.command_data_prp_entries);
    try std.testing.expectEqual(@as(u16, 2), metadata.prp_list_covered_pages);
    try std.testing.expectEqual(@as(u16, 1), metadata.prp_list_pages);
    try std.testing.expectEqual(@as(u32, 4096), metadata.metadata_dma_bytes);
    try std.testing.expectEqual(@as(u32, 16384), metadata.total_dma_bytes);
    try std.testing.expect(metadata.requires_descriptor_rebuild_after_reset);
    try std.testing.expectEqual(@as(u32, 0), metadata.reset_generation);

    const inline_only = try lab.planPrpMetadata(0x3080, 4096);
    try std.testing.expectEqual(@as(u16, 2), inline_only.spanned_pages);
    try std.testing.expect(!inline_only.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 2), inline_only.command_data_prp_entries);
    try std.testing.expectEqual(@as(u16, 0), inline_only.prp_list_covered_pages);
    try std.testing.expectEqual(@as(u32, 0), inline_only.metadata_dma_bytes);
    try std.testing.expectEqual(@as(u32, 8192), inline_only.total_dma_bytes);
    try std.testing.expect(!inline_only.requires_descriptor_rebuild_after_reset);
}

test "phase12 nvme pci prp metadata helper respects reset freeze and resumes after reset" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    const stale_metadata = try lab.planPrpMetadata(0x1180, 8192);
    try std.testing.expectEqual(@as(u32, 0), stale_metadata.reset_generation);
    try std.testing.expect(stale_metadata.requires_descriptor_rebuild_after_reset);

    _ = lab.beginReset();
    try std.testing.expectError(error.QueuePlanningBlockedByReset, lab.planPrpMetadata(0x1180, 8192));

    _ = lab.completeReset();
    const metadata = try lab.planPrpMetadata(0x1400, 12288);
    try std.testing.expect(stale_metadata.reset_generation < metadata.reset_generation);
    try std.testing.expectEqual(@as(u16, 4), metadata.spanned_pages);
    try std.testing.expect(metadata.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 3), metadata.prp_list_covered_pages);
    try std.testing.expectEqual(@as(u32, 4096), metadata.metadata_dma_bytes);
    try std.testing.expectEqual(@as(u32, 20480), metadata.total_dma_bytes);
    try std.testing.expect(metadata.requires_descriptor_rebuild_after_reset);
    try std.testing.expectEqual(@as(u32, 1), metadata.reset_generation);
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

test "phase12 nvme pci doorbell window helper summarizes planned admin and io register aperture" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 16);
    _ = try lab.planAdminQueue(64, 64, false);
    _ = try lab.planIoQueue(128, 64, false);
    _ = try lab.planIoQueue(64, 64, true);

    const window = try lab.planDoorbellWindow();
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", window.anchor);
    try std.testing.expectEqual(@as(usize, 2), window.planned_io_queues);
    try std.testing.expectEqual(@as(usize, 3), window.queue_pair_count);
    try std.testing.expectEqual(@as(u32, 16), window.doorbell_stride_bytes);
    try std.testing.expectEqual(@as(u32, 0), window.admin_sq_doorbell_offset);
    try std.testing.expectEqual(@as(u32, 16), window.admin_cq_doorbell_offset);
    try std.testing.expect(window.has_io_queues);
    try std.testing.expectEqual(@as(u32, 32), window.first_io_sq_doorbell_offset);
    try std.testing.expectEqual(@as(u32, 80), window.last_cq_doorbell_offset);
    try std.testing.expectEqual(@as(u32, 96), window.total_doorbell_window_bytes);
    try std.testing.expect(!window.queues_frozen);
    try std.testing.expectEqual(@as(u32, 0), window.reset_generation);
}

test "phase12 nvme pci doorbell window helper tracks reset state without claiming live irq routing" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    _ = try lab.planIoQueue(16, 64, false);

    var window = try lab.planDoorbellWindow();
    try std.testing.expectEqual(@as(usize, 2), window.queue_pair_count);
    try std.testing.expectEqual(@as(u32, 24), window.last_cq_doorbell_offset);
    try std.testing.expectEqual(@as(u32, 32), window.total_doorbell_window_bytes);
    try std.testing.expect(!window.queues_frozen);

    _ = lab.beginReset();
    window = try lab.planDoorbellWindow();
    try std.testing.expect(window.queues_frozen);
    try std.testing.expectEqual(@as(usize, 1), window.planned_io_queues);
    try std.testing.expectEqual(@as(u32, 1), window.reset_generation);

    _ = lab.completeReset();
    window = try lab.planDoorbellWindow();
    try std.testing.expectEqual(@as(usize, 0), window.planned_io_queues);
    try std.testing.expectEqual(@as(usize, 1), window.queue_pair_count);
    try std.testing.expect(!window.has_io_queues);
    try std.testing.expectEqual(@as(u32, 0), window.first_io_sq_doorbell_offset);
    try std.testing.expectEqual(@as(u32, 8), window.last_cq_doorbell_offset);
    try std.testing.expectEqual(@as(u32, 16), window.total_doorbell_window_bytes);
    try std.testing.expect(!window.queues_frozen);
    try std.testing.expectEqual(@as(u32, 1), window.reset_generation);
}

test "phase12 nvme pci queue recovery replay helper summarizes capped io queues and host DMA" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 16);
    _ = try lab.planAdminQueue(32, 64, false);
    _ = try lab.planIoQueue(512, 64, true);
    _ = try lab.planIoQueue(128, 32, false);
    _ = try lab.planIoQueue(64, 64, false);

    const replay = try lab.planQueueRecoveryReplay(2);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", replay.anchor);
    try std.testing.expectEqual(@as(usize, 3), replay.planned_io_queues);
    try std.testing.expectEqual(@as(usize, 2), replay.replay_io_queues);
    try std.testing.expectEqual(@as(usize, 1), replay.dropped_io_queues);
    try std.testing.expectEqual(@as(usize, 3), replay.total_queue_pairs);
    try std.testing.expectEqual(@as(u16, 1), replay.first_io_queue_id);
    try std.testing.expectEqual(@as(u16, 2), replay.last_io_queue_id);
    try std.testing.expectEqual(@as(u16, 32), replay.admin_queue_depth);
    try std.testing.expectEqual(@as(u16, 64), replay.admin_sq_entry_bytes);
    try std.testing.expectEqual(@as(u32, 2560), replay.admin_host_dma_bytes);
    try std.testing.expectEqual(@as(u32, 14336), replay.replay_io_host_dma_bytes);
    try std.testing.expectEqual(@as(u32, 16896), replay.total_host_dma_bytes);
    try std.testing.expect(replay.replay_uses_cmb_io_queue);
    try std.testing.expect(replay.controller_limited);
    try std.testing.expect(!replay.queues_frozen);
    try std.testing.expectEqual(@as(u32, 0), replay.reset_generation);
}

test "phase12 nvme pci queue recovery replay helper requires admin state and survives reset freeze" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    try std.testing.expectError(error.AdminQueueNotPlanned, lab.planQueueRecoveryReplay(4));

    _ = try lab.planAdminQueue(64, 64, false);
    _ = try lab.planIoQueue(32, 64, false);
    _ = try lab.planIoQueue(16, 64, true);
    _ = lab.beginReset();

    const replay = try lab.planQueueRecoveryReplay(8);
    try std.testing.expectEqual(@as(usize, 2), replay.replay_io_queues);
    try std.testing.expectEqual(@as(usize, 0), replay.dropped_io_queues);
    try std.testing.expectEqual(@as(usize, 3), replay.total_queue_pairs);
    try std.testing.expectEqual(@as(u32, 5120), replay.admin_host_dma_bytes);
    try std.testing.expectEqual(@as(u32, 2816), replay.replay_io_host_dma_bytes);
    try std.testing.expectEqual(@as(u32, 7936), replay.total_host_dma_bytes);
    try std.testing.expect(replay.replay_uses_cmb_io_queue);
    try std.testing.expect(!replay.controller_limited);
    try std.testing.expect(replay.queues_frozen);
    try std.testing.expectEqual(@as(u32, 1), replay.reset_generation);

    _ = lab.completeReset();
    const cleared = try lab.planQueueRecoveryReplay(8);
    try std.testing.expectEqual(@as(usize, 0), cleared.replay_io_queues);
    try std.testing.expectEqual(@as(usize, 1), cleared.total_queue_pairs);
    try std.testing.expectEqual(@as(u16, 0), cleared.first_io_queue_id);
    try std.testing.expectEqual(@as(u16, 0), cleared.last_io_queue_id);
    try std.testing.expectEqual(@as(u32, 5120), cleared.total_host_dma_bytes);
    try std.testing.expect(!cleared.replay_uses_cmb_io_queue);
    try std.testing.expect(!cleared.queues_frozen);
    try std.testing.expectEqual(@as(u32, 1), cleared.reset_generation);
}
