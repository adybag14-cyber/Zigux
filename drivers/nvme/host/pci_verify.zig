const std = @import("std");
const testing = std.testing;
const nvme_pci = @import("pci.zig");

test "nvme pci descriptor stays honest about the bounded starter packet" {
    const descriptor = nvme_pci.NvmePciQueueLab.descriptor();
    try testing.expectEqualStrings("nvme_pci_queue_lab", descriptor.name);
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", descriptor.anchor);
    try testing.expect(descriptor.provides_lab_queue_planner);
    try testing.expect(descriptor.provides_dropped_io_retirement_helper);
    try testing.expect(descriptor.provides_recovery_rollback_gate_helper);
    try testing.expect(!descriptor.touches_live_dma);
    try testing.expect(!descriptor.touches_pci_probe);
    try testing.expect(!descriptor.touches_irq_recovery);
}

test "nvme pci admin and io queue planning keeps CMB host DMA accounting bounded" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 16);

    const admin = try lab.planAdminQueue(64, 64, false);
    try testing.expectEqual(nvme_pci.QueueRole.admin, admin.role);
    try testing.expectEqual(@as(u16, 0), admin.queue_id);
    try testing.expectEqual(@as(u32, 4096), admin.sq_bytes);
    try testing.expectEqual(@as(u32, 1024), admin.cq_bytes);
    try testing.expectEqual(admin.queue_memory_bytes, admin.host_dma_bytes);
    try testing.expectEqual(@as(u16, 2), admin.required_host_dma_pages);
    try testing.expectEqual(@as(u32, 0), admin.reset_generation);
}

test "nvme pci io queue planning uses CQ-only host DMA when CMB backs the submission queue" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 16);
    _ = try lab.planAdminQueue(64, 64, false);

    const io = try lab.planIoQueue(128, 64, true);
    try testing.expectEqual(nvme_pci.QueueRole.io, io.role);
    try testing.expectEqual(@as(u16, 1), io.queue_id);
    try testing.expectEqual(@as(u32, 8192), io.sq_bytes);
    try testing.expectEqual(@as(u32, 2048), io.cq_bytes);
    try testing.expectEqual(@as(u32, 10240), io.queue_memory_bytes);
    try testing.expectEqual(@as(u32, 2048), io.host_dma_bytes);
    try testing.expectEqual(@as(u16, 1), io.required_host_dma_pages);
    try testing.expectEqual(@as(u32, 32), io.sq_doorbell_offset);
    try testing.expectEqual(@as(u32, 48), io.cq_doorbell_offset);
    try testing.expect(io.uses_cmb);
    try testing.expectEqual(@as(u32, 0), io.reset_generation);
}

test "nvme pci prp shape planning records multi-page list pressure without live DMA claims" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);

    const prp = try lab.planPrpBufferShape(4096 * 514, 0);
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", prp.anchor);
    try testing.expectEqual(@as(u32, 4096), prp.first_prp_bytes);
    try testing.expectEqual(@as(u32, 4096 * 514), prp.rounded_span_bytes);
    try testing.expectEqual(@as(u16, 514), prp.spanned_pages);
    try testing.expectEqual(@as(u16, 513), prp.tail_page_count);
    try testing.expect(prp.uses_prp_list);
    try testing.expectEqual(@as(u16, 512), prp.prp_list_entries);
    try testing.expectEqual(@as(u16, 512), prp.prp_list_capacity);
    try testing.expectError(error.PrpListTooLong, lab.planPrpBufferShape(4096 * 515, 0));
}

test "nvme pci reset summary freezes queue planning then clears io backlog while keeping admin depth" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, false);

    const frozen = lab.beginReset();
    try testing.expectEqual(nvme_pci.RecoveryState.reset_frozen, frozen.state);
    try testing.expect(frozen.queues_frozen);
    try testing.expectEqual(@as(usize, 2), frozen.planned_io_queues);
    try testing.expectEqual(@as(u32, 1), frozen.reset_generation);
    try testing.expectEqual(@as(u16, 48), frozen.last_admin_queue_depth);
    try testing.expectError(error.QueuePlanningBlockedByReset, lab.planIoQueue(8, 64, false));

    const resumed = lab.completeReset();
    try testing.expectEqual(nvme_pci.RecoveryState.running, resumed.state);
    try testing.expect(!resumed.queues_frozen);
    try testing.expectEqual(@as(usize, 0), resumed.planned_io_queues);
    try testing.expectEqual(@as(u32, 1), resumed.reset_generation);
    try testing.expectEqual(@as(u16, 48), resumed.last_admin_queue_depth);

    const next = try lab.planIoQueue(8, 64, false);
    try testing.expectEqual(@as(u16, 1), next.queue_id);
    try testing.expectEqual(@as(u32, 1), next.reset_generation);
}

test "nvme pci dropped backlog retirement keeps blocker ordering and parity surfaces explicit" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    const descriptor = nvme_pci.NvmePciQueueLab.descriptor();
    try std.testing.expect(descriptor.provides_dropped_io_retirement_helper);

    _ = try lab.planAdminQueue(64, 64, false);
    _ = try lab.planIoQueue(32, 64, false);
    _ = try lab.planIoQueue(16, 64, true);

    _ = lab.beginReset();
    _ = lab.completeReset();

    const replay_blocked = lab.summarizeDroppedIoRetirement();
    try testing.expectEqual(nvme_pci.DroppedIoRetirementBlocker.admin_queue_replay, replay_blocked.retirement_blocker);
    try testing.expect(!replay_blocked.queue_count_parity_recovered);
    try testing.expect(!replay_blocked.host_dma_parity_recovered);
    try testing.expect(!replay_blocked.can_retire_dropped_io_backlog);

    _ = try lab.planAdminQueue(64, 64, false);
    _ = try lab.planIoQueue(32, 64, false);
    const queue_blocked = lab.summarizeDroppedIoRetirement();
    try testing.expectEqual(nvme_pci.DroppedIoRetirementBlocker.queue_count_parity, queue_blocked.retirement_blocker);
    try testing.expect(!queue_blocked.queue_count_parity_recovered);
    try testing.expect(!queue_blocked.host_dma_parity_recovered);
    try testing.expect(!queue_blocked.can_retire_dropped_io_backlog);

    _ = try lab.planIoQueue(16, 64, true);
    const ready = lab.summarizeDroppedIoRetirement();
    try testing.expectEqual(nvme_pci.DroppedIoRetirementBlocker.none, ready.retirement_blocker);
    try testing.expect(ready.queue_count_parity_recovered);
    try testing.expect(ready.host_dma_parity_recovered);
    try testing.expect(ready.can_retire_dropped_io_backlog);
}

test "nvme pci recovery restore verifier keeps admin-first replay and mixed DMA budget explicit" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);

    const admin = try lab.planAdminQueue(64, 64, false);
    const first_io = try lab.planIoQueue(64, 64, true);
    const second_io = try lab.planIoQueue(32, 64, false);

    try testing.expectEqual(@as(u16, 2), admin.required_host_dma_pages);
    try testing.expectEqual(@as(u16, 1), first_io.required_host_dma_pages);
    try testing.expectEqual(@as(u16, 1), second_io.required_host_dma_pages);

    const frozen = lab.beginReset();
    try testing.expectEqual(nvme_pci.RecoveryState.reset_frozen, frozen.state);

    const restore = try lab.recoveryQueueRestoreSummary();
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", restore.anchor);
    try testing.expectEqual(nvme_pci.RecoveryState.reset_frozen, restore.state);
    try testing.expectEqual(@as(u32, 1), restore.reset_generation);
    try testing.expectEqual(@as(u16, 64), restore.admin_queue_depth);
    try testing.expectEqual(@as(u16, 2), restore.admin_host_dma_pages);
    try testing.expectEqual(@as(usize, 2), restore.io_queue_count);
    try testing.expectEqual(@as(u32, 2), restore.io_host_dma_pages);
    try testing.expectEqual(@as(u32, 4), restore.total_host_dma_pages);
    try testing.expect(restore.restores_admin_first);
    try testing.expect(restore.restores_io_after_admin);
}

test "nvme pci rollback gate verifier keeps rollback blockers ordered" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);

    const idle = lab.recoveryRollbackGateSummary();
    try testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.no_recovery_window, idle.rollback_blocker);
    try testing.expect(!idle.can_clear_rollback_gate);

    _ = lab.beginReset();
    const frozen = lab.recoveryRollbackGateSummary();
    try testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.reset_frozen, frozen.rollback_blocker);
    try testing.expect(!frozen.can_clear_rollback_gate);

    _ = lab.completeReset();
    const replay_blocked = lab.recoveryRollbackGateSummary();
    try testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.admin_queue_replay, replay_blocked.rollback_blocker);
    try testing.expectEqual(@as(usize, 2), replay_blocked.dropped_io_queue_count);
    try testing.expect(!replay_blocked.can_clear_rollback_gate);

    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    const queue_blocked = lab.recoveryRollbackGateSummary();
    try testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.queue_count_parity, queue_blocked.rollback_blocker);
    try testing.expectEqual(@as(usize, 1), queue_blocked.remaining_io_queue_count);
    try testing.expect(!queue_blocked.can_clear_rollback_gate);

    _ = try lab.planIoQueue(32, 64, true);
    const ready = lab.recoveryRollbackGateSummary();
    try testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.none, ready.rollback_blocker);
    try testing.expect(ready.host_dma_parity_recovered);
    try testing.expect(ready.queue_numbering_restarted);
    try testing.expect(ready.can_clear_rollback_gate);
}
