const std = @import("std");
const nvme_pci = @import("nvme_pci");

test "phase12 nvme pci queue planner keeps host DMA budget smaller when IO queues use CMB" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);

    const admin = try lab.planAdminQueue(128, 64, false);
    const io = try lab.planIoQueue(128, 64, true);

    try std.testing.expectEqual(@as(u16, 3), admin.required_host_dma_pages);
    try std.testing.expectEqual(@as(u16, 1), io.required_host_dma_pages);
    try std.testing.expect(io.host_dma_bytes < io.queue_memory_bytes);
    try std.testing.expectEqual(@as(u32, 16), io.sq_doorbell_offset);
    try std.testing.expectEqual(@as(u32, 24), io.cq_doorbell_offset);
}

test "phase12 nvme pci prp shape reports multi-page throughput fanout" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 4);
    const shape = try lab.planPrpBufferShape(16384, 512);

    try std.testing.expectEqual(@as(u32, 3584), shape.first_prp_bytes);
    try std.testing.expectEqual(@as(u32, 20480), shape.rounded_span_bytes);
    try std.testing.expectEqual(@as(u16, 5), shape.spanned_pages);
    try std.testing.expectEqual(@as(u16, 4), shape.tail_page_count);
    try std.testing.expect(shape.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 3), shape.prp_list_entries);
}

test "phase12 nvme pci recovery restore summary keeps admin-first replay and DMA budget reviewable" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);

    const admin = try lab.planAdminQueue(64, 64, false);
    const first_io = try lab.planIoQueue(64, 64, true);
    const second_io = try lab.planIoQueue(32, 64, false);

    try std.testing.expectEqual(@as(u16, 2), admin.required_host_dma_pages);
    try std.testing.expectEqual(@as(u16, 1), first_io.required_host_dma_pages);
    try std.testing.expectEqual(@as(u16, 1), second_io.required_host_dma_pages);

    _ = lab.beginReset();
    const restore = try lab.recoveryQueueRestoreSummary();
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", restore.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryState.reset_frozen, restore.state);
    try std.testing.expectEqual(@as(u32, 1), restore.reset_generation);
    try std.testing.expectEqual(@as(u16, 64), restore.admin_queue_depth);
    try std.testing.expectEqual(@as(u16, 2), restore.admin_host_dma_pages);
    try std.testing.expectEqual(@as(usize, 2), restore.io_queue_count);
    try std.testing.expectEqual(@as(u32, 2), restore.io_host_dma_pages);
    try std.testing.expectEqual(@as(u32, 4), restore.total_host_dma_pages);
    try std.testing.expect(restore.restores_admin_first);
    try std.testing.expect(restore.restores_io_after_admin);

    _ = lab.completeReset();
    try std.testing.expectError(error.ResetNotFrozen, lab.recoveryQueueRestoreSummary());
}

test "phase12 nvme pci queue restart summary keeps post-reset numbering reviewable" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);

    const idle = lab.queueRestartSummary();
    try std.testing.expectEqual(nvme_pci.QueueRestartBlocker.no_recovery_window, idle.restart_blocker);
    try std.testing.expectEqual(@as(usize, 0), idle.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), idle.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), idle.remaining_io_queue_count);
    try std.testing.expectEqual(@as(u16, 3), idle.next_io_queue_id);
    try std.testing.expectEqual(@as(u16, 1), idle.expected_next_io_queue_id);
    try std.testing.expect(!idle.queue_numbering_restarted);

    _ = lab.beginReset();
    const frozen = lab.queueRestartSummary();
    try std.testing.expectEqual(nvme_pci.QueueRestartBlocker.reset_frozen, frozen.restart_blocker);
    try std.testing.expectEqual(@as(usize, 2), frozen.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), frozen.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 2), frozen.remaining_io_queue_count);
    try std.testing.expectEqual(@as(u16, 3), frozen.next_io_queue_id);
    try std.testing.expectEqual(@as(u16, 1), frozen.expected_next_io_queue_id);
    try std.testing.expect(!frozen.queue_numbering_restarted);

    _ = lab.completeReset();
    const restarted = lab.queueRestartSummary();
    try std.testing.expectEqual(nvme_pci.QueueRestartBlocker.none, restarted.restart_blocker);
    try std.testing.expectEqual(@as(usize, 2), restarted.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), restarted.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 2), restarted.remaining_io_queue_count);
    try std.testing.expectEqual(@as(u16, 1), restarted.next_io_queue_id);
    try std.testing.expectEqual(@as(u16, 1), restarted.expected_next_io_queue_id);
    try std.testing.expect(restarted.queue_numbering_restarted);

    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    const partial = lab.queueRestartSummary();
    try std.testing.expectEqual(nvme_pci.QueueRestartBlocker.none, partial.restart_blocker);
    try std.testing.expectEqual(@as(usize, 1), partial.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 1), partial.remaining_io_queue_count);
    try std.testing.expectEqual(@as(u16, 2), partial.next_io_queue_id);
    try std.testing.expectEqual(@as(u16, 2), partial.expected_next_io_queue_id);
    try std.testing.expect(partial.queue_numbering_restarted);
}

test "phase12 nvme pci dropped backlog retirement stays blocked until recovery plans are rebuilt" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    const descriptor = nvme_pci.NvmePciQueueLab.descriptor();
    try std.testing.expect(descriptor.provides_dropped_io_retirement_helper);

    _ = try lab.planAdminQueue(64, 64, false);
    _ = try lab.planIoQueue(32, 64, false);
    _ = try lab.planIoQueue(16, 64, true);

    _ = lab.beginReset();
    _ = lab.completeReset();

    const pending = lab.summarizeDroppedIoRetirement();
    try std.testing.expect(pending.admin_queue_must_be_replayed);
    try std.testing.expectEqual(@as(usize, 2), pending.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), pending.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 2), pending.remaining_io_queue_count);
    try std.testing.expect(!pending.can_retire_dropped_io_backlog);

    _ = try lab.planAdminQueue(64, 64, false);
    _ = try lab.planIoQueue(32, 64, false);
    _ = try lab.planIoQueue(16, 64, true);

    const ready = lab.summarizeDroppedIoRetirement();
    try std.testing.expect(ready.admin_queue_replayed_after_reset);
    try std.testing.expectEqual(@as(usize, 2), ready.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), ready.remaining_io_queue_count);
    try std.testing.expect(ready.queue_numbering_restarted);
    try std.testing.expect(ready.can_retire_dropped_io_backlog);
}

test "phase12 nvme pci rollback gate keeps rollback closure blocked until recovery parity returns" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    const descriptor = nvme_pci.NvmePciQueueLab.descriptor();
    try std.testing.expect(descriptor.provides_recovery_rollback_gate_helper);

    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(64, 64, false);
    _ = try lab.planIoQueue(128, 64, false);

    _ = lab.beginReset();
    const frozen = lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.reset_frozen, frozen.rollback_blocker);
    try std.testing.expect(!frozen.can_clear_rollback_gate);

    _ = lab.completeReset();
    const replay_blocked = lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.admin_queue_replay, replay_blocked.rollback_blocker);
    try std.testing.expect(!replay_blocked.can_clear_rollback_gate);

    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, true);
    const queue_blocked = lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.queue_count_parity, queue_blocked.rollback_blocker);
    try std.testing.expectEqual(@as(usize, 1), queue_blocked.remaining_io_queue_count);
    try std.testing.expect(!queue_blocked.can_clear_rollback_gate);

    _ = try lab.planIoQueue(32, 64, true);
    const dma_blocked = lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.dma_page_parity, dma_blocked.rollback_blocker);
    try std.testing.expectEqual(@as(u32, 3), dma_blocked.remaining_io_host_dma_pages);
    try std.testing.expect(!dma_blocked.can_clear_rollback_gate);

    var parity_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try parity_lab.planAdminQueue(48, 64, false);
    _ = try parity_lab.planIoQueue(16, 64, false);
    _ = try parity_lab.planIoQueue(32, 64, true);

    _ = parity_lab.beginReset();
    _ = parity_lab.completeReset();

    _ = try parity_lab.planAdminQueue(48, 64, false);
    _ = try parity_lab.planIoQueue(16, 64, false);
    _ = try parity_lab.planIoQueue(32, 64, true);

    const ready = parity_lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.none, ready.rollback_blocker);
    try std.testing.expect(ready.queue_count_parity_recovered);
    try std.testing.expect(ready.host_dma_parity_recovered);
    try std.testing.expect(ready.queue_numbering_restarted);
    try std.testing.expect(ready.can_clear_rollback_gate);
}
