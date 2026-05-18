const std = @import("std");
const testing = std.testing;
const nvme_pci = @import("pci.zig");

test "nvme pci descriptor stays honest about the bounded starter packet" {
    const descriptor = nvme_pci.NvmePciQueueLab.descriptor();
    try testing.expectEqualStrings("nvme_pci_queue_lab", descriptor.name);
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", descriptor.anchor);
    try testing.expect(descriptor.provides_lab_queue_planner);
    try testing.expect(descriptor.provides_dropped_io_retirement_helper);
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

test "nvme pci dropped backlog retirement stays blocked until admin replay and queue rebuild catch up" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);

    _ = lab.beginReset();
    const frozen = lab.summarizeDroppedIoRetirement();
    try testing.expectEqual(nvme_pci.RecoveryState.reset_frozen, frozen.state);
    try testing.expect(frozen.admin_queue_must_be_replayed);
    try testing.expectEqual(@as(usize, 2), frozen.dropped_io_queue_count);
    try testing.expectEqual(@as(usize, 0), frozen.rebuilt_io_queue_count);
    try testing.expectEqual(@as(usize, 2), frozen.remaining_io_queue_count);
    try testing.expect(!frozen.can_retire_dropped_io_backlog);

    _ = lab.completeReset();
    const pending = lab.summarizeDroppedIoRetirement();
    try testing.expectEqual(nvme_pci.RecoveryState.running, pending.state);
    try testing.expect(pending.admin_queue_must_be_replayed);
    try testing.expect(pending.queue_numbering_restarted);
    try testing.expectEqual(@as(usize, 2), pending.remaining_io_queue_count);
    try testing.expect(!pending.can_retire_dropped_io_backlog);

    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    const partial = lab.summarizeDroppedIoRetirement();
    try testing.expect(partial.admin_queue_replayed_after_reset);
    try testing.expect(!partial.admin_queue_must_be_replayed);
    try testing.expectEqual(@as(usize, 1), partial.rebuilt_io_queue_count);
    try testing.expectEqual(@as(usize, 1), partial.remaining_io_queue_count);
    try testing.expect(!partial.can_retire_dropped_io_backlog);

    _ = try lab.planIoQueue(32, 64, true);
    const ready = lab.summarizeDroppedIoRetirement();
    try testing.expect(ready.admin_queue_replayed_after_reset);
    try testing.expectEqual(@as(usize, 2), ready.rebuilt_io_queue_count);
    try testing.expectEqual(@as(usize, 0), ready.remaining_io_queue_count);
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

test "nvme pci recovery rollback gate verifier keeps blocker transitions and DMA parity explicit" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(64, 64, false);
    _ = try lab.planIoQueue(128, 64, false);

    _ = lab.beginReset();
    const frozen = lab.recoveryRollbackGateSummary();
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", frozen.anchor);
    try testing.expectEqual(nvme_pci.RecoveryState.reset_frozen, frozen.state);
    try testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.reset_frozen, frozen.rollback_blocker);
    try testing.expectEqual(@as(usize, 2), frozen.dropped_io_queue_count);
    try testing.expectEqual(@as(u32, 5), frozen.dropped_io_host_dma_pages);
    try testing.expect(!frozen.queue_count_parity_recovered);
    try testing.expect(!frozen.host_dma_parity_recovered);
    try testing.expect(!frozen.can_clear_rollback_gate);

    _ = lab.completeReset();
    const replay_blocked = lab.recoveryRollbackGateSummary();
    try testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.admin_queue_replay, replay_blocked.rollback_blocker);
    try testing.expect(replay_blocked.queue_numbering_restarted);
    try testing.expectEqual(@as(usize, 2), replay_blocked.remaining_io_queue_count);
    try testing.expectEqual(@as(u32, 5), replay_blocked.remaining_io_host_dma_pages);
    try testing.expect(!replay_blocked.queue_count_parity_recovered);
    try testing.expect(!replay_blocked.host_dma_parity_recovered);
    try testing.expect(!replay_blocked.can_clear_rollback_gate);

    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, true);
    const queue_blocked = lab.recoveryRollbackGateSummary();
    try testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.queue_count_parity, queue_blocked.rollback_blocker);
    try testing.expect(queue_blocked.admin_queue_replayed_after_reset);
    try testing.expectEqual(@as(usize, 1), queue_blocked.rebuilt_io_queue_count);
    try testing.expectEqual(@as(usize, 1), queue_blocked.remaining_io_queue_count);
    try testing.expectEqual(@as(u32, 1), queue_blocked.rebuilt_io_host_dma_pages);
    try testing.expectEqual(@as(u32, 4), queue_blocked.remaining_io_host_dma_pages);
    try testing.expect(!queue_blocked.queue_count_parity_recovered);
    try testing.expect(!queue_blocked.host_dma_parity_recovered);
    try testing.expect(!queue_blocked.can_clear_rollback_gate);

    _ = try lab.planIoQueue(32, 64, true);
    const dma_blocked = lab.recoveryRollbackGateSummary();
    try testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.dma_page_parity, dma_blocked.rollback_blocker);
    try testing.expectEqual(@as(usize, 2), dma_blocked.rebuilt_io_queue_count);
    try testing.expectEqual(@as(usize, 0), dma_blocked.remaining_io_queue_count);
    try testing.expectEqual(@as(u32, 2), dma_blocked.rebuilt_io_host_dma_pages);
    try testing.expectEqual(@as(u32, 3), dma_blocked.remaining_io_host_dma_pages);
    try testing.expect(dma_blocked.queue_count_parity_recovered);
    try testing.expect(!dma_blocked.host_dma_parity_recovered);
    try testing.expect(!dma_blocked.can_clear_rollback_gate);

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
    try testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.none, ready.rollback_blocker);
    try testing.expect(ready.admin_queue_replayed_after_reset);
    try testing.expect(ready.queue_count_parity_recovered);
    try testing.expect(ready.host_dma_parity_recovered);
    try testing.expect(ready.queue_numbering_restarted);
    try testing.expect(ready.can_clear_rollback_gate);
}

test "nvme pci recovery reservation replay preflight stays non-mutating and controller-capped" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    const reservation = try lab.reserveIoQueues(8, 6);
    try testing.expectEqual(@as(usize, 6), reservation.reserved_io_queues);

    _ = lab.beginReset();
    _ = lab.completeReset();

    try testing.expectError(error.AdminQueueReplayRequired, lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3));

    _ = try lab.planAdminQueue(32, 64, false);
    const preflight = try lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", preflight.anchor);
    try testing.expectEqual(nvme_pci.RecoveryState.running, preflight.state);
    try testing.expectEqual(@as(u32, 1), preflight.reset_generation);
    try testing.expectEqual(@as(usize, 6), preflight.requested_reserved_io_queues);
    try testing.expectEqual(@as(usize, 3), preflight.controller_io_queue_limit);
    try testing.expectEqual(@as(usize, 64), preflight.planner_remaining_io_slots);
    try testing.expectEqual(@as(usize, 3), preflight.replayable_reserved_io_queues);
    try testing.expectEqual(@as(u16, 1), preflight.first_queue_id);
    try testing.expectEqual(@as(u16, 3), preflight.last_queue_id);
    try testing.expect(preflight.controller_limited);
    try testing.expect(!preflight.planner_limited);
    try testing.expect(!preflight.queue_planning_blocked);
    try testing.expect(!preflight.queues_frozen);
    try testing.expect(preflight.cached_queue_reservation_stale);
    try testing.expect(!preflight.admin_queue_must_be_replanned);

    const recovery = lab.recoverySummary();
    try testing.expectEqual(@as(usize, 0), recovery.planned_io_queues);

    const replay = try lab.replayReservedIoQueues(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try testing.expectEqual(preflight.replayable_reserved_io_queues, replay.reserved_io_queues);
    try testing.expectEqual(preflight.first_queue_id, replay.first_queue_id);
    try testing.expectEqual(preflight.last_queue_id, replay.last_queue_id);

    const next = try lab.planIoQueue(8, 64, false);
    try testing.expectEqual(@as(u16, 4), next.queue_id);
}

test "nvme pci recovery reservation replay preflight rejects frozen, missing, and current reservations" {
    var frozen_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try frozen_lab.planAdminQueue(32, 64, false);
    const frozen = try frozen_lab.reserveIoQueues(4, 4);
    _ = frozen_lab.beginReset();
    try testing.expectError(error.QueuePlanningBlockedByReset, frozen_lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = frozen.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = frozen.reserved_io_queues,
    }, 4));

    var missing_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try missing_lab.planAdminQueue(32, 64, false);
    try testing.expectError(error.NoQueueReservationToReplay, missing_lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
    }, 4));

    var current_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try current_lab.planAdminQueue(32, 64, false);
    const current = try current_lab.reserveIoQueues(4, 4);
    try testing.expectError(error.QueueReservationAlreadyCurrent, current_lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = current.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = current.reserved_io_queues,
    }, 4));
}

test "nvme pci rollback gate keeps admin replay blocked even after queue and DMA parity recover" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);

    _ = lab.beginReset();
    _ = lab.completeReset();

    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);

    const rollback = lab.recoveryRollbackGateSummary();
    try testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.admin_queue_replay, rollback.rollback_blocker);
    try testing.expect(!rollback.admin_queue_replayed_after_reset);
    try testing.expect(!rollback.queue_count_parity_recovered);
    try testing.expect(!rollback.host_dma_parity_recovered);
    try testing.expect(rollback.queue_numbering_restarted);
    try testing.expectEqual(@as(usize, 2), rollback.dropped_io_queue_count);
    try testing.expectEqual(@as(usize, 2), rollback.rebuilt_io_queue_count);
    try testing.expectEqual(@as(usize, 0), rollback.remaining_io_queue_count);
    try testing.expectEqual(@as(u32, 0), rollback.remaining_io_host_dma_pages);
    try testing.expect(!rollback.can_clear_rollback_gate);

    const retirement = lab.summarizeDroppedIoRetirement();
    try testing.expect(retirement.admin_queue_must_be_replayed);
    try testing.expectEqual(@as(usize, 0), retirement.remaining_io_queue_count);
    try testing.expect(!retirement.can_retire_dropped_io_backlog);
}
