const std = @import("std");
const nvme_pci = @import("nvme_pci");

test "phase12 nvme pci direct replay keeps queue reservation reviewable without shared build wiring" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);

    const reservation = try lab.reserveIoQueues(6, 4);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", reservation.anchor);
    try std.testing.expectEqual(@as(usize, 6), reservation.requested_io_queues);
    try std.testing.expectEqual(@as(usize, 4), reservation.reserved_io_queues);
    try std.testing.expect(reservation.controller_limited);
    try std.testing.expect(!reservation.planner_limited);
    try std.testing.expectEqual(@as(u16, 1), reservation.first_queue_id);
    try std.testing.expectEqual(@as(u16, 4), reservation.last_queue_id);
}

test "phase12 nvme pci direct replay keeps recovery budgeting and PRP metadata pressure explicit" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(64, 64, false);
    _ = try lab.planIoQueue(64, 64, true);
    _ = try lab.planIoQueue(32, 64, false);

    const metadata = try lab.planPrpMetadataBudget(4096 * 5, 0);
    try std.testing.expect(metadata.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 3), metadata.prp_list_entries);
    try std.testing.expectEqual(@as(u16, 1), metadata.metadata_host_dma_pages);

    _ = lab.beginReset();
    const restore = try lab.recoveryQueueRestoreSummary();
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", restore.anchor);
    try std.testing.expectEqual(@as(u16, 64), restore.admin_queue_depth);
    try std.testing.expectEqual(@as(usize, 2), restore.io_queue_count);
    try std.testing.expectEqual(@as(u32, 4), restore.total_host_dma_pages);
    try std.testing.expect(restore.restores_admin_first);
    try std.testing.expect(restore.restores_io_after_admin);
}

test "phase12 nvme pci direct replay keeps stale recovery reservation debt explicit" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    const reservation = try lab.reserveIoQueues(6, 6);
    _ = try lab.planPrpMetadataBudget(4096 * 5, 0);

    _ = lab.beginReset();
    _ = lab.completeReset();
    _ = try lab.planAdminQueue(32, 64, false);

    const preflight = try lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = reservation.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", preflight.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, preflight.state);
    try std.testing.expectEqual(@as(u32, 1), preflight.reset_generation);
    try std.testing.expectEqual(@as(usize, 6), preflight.requested_reserved_io_queues);
    try std.testing.expectEqual(@as(usize, 3), preflight.replayable_reserved_io_queues);
    try std.testing.expectEqual(@as(u16, 1), preflight.first_queue_id);
    try std.testing.expectEqual(@as(u16, 3), preflight.last_queue_id);
    try std.testing.expectEqual(@as(usize, 3), preflight.planned_io_queues_after_replay);
    try std.testing.expectEqual(@as(u16, 4), preflight.next_io_queue_id_after_replay);
    try std.testing.expect(preflight.queue_numbering_restarted);
    try std.testing.expect(preflight.controller_limited);
    try std.testing.expect(!preflight.planner_limited);
    try std.testing.expect(preflight.cached_queue_reservation_stale);
    try std.testing.expect(preflight.cached_prp_metadata_stale);
    try std.testing.expect(preflight.descriptor_rebuild_required);
    try std.testing.expect(!preflight.admin_queue_must_be_replanned);

    const recovery = lab.recoverySummary();
    try std.testing.expectEqual(@as(usize, 0), recovery.planned_io_queues);

    const replay = try lab.replayReservedIoQueues(.{
        .cached_prp_metadata_generation = reservation.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try std.testing.expectEqual(preflight.replayable_reserved_io_queues, replay.reserved_io_queues);
    try std.testing.expectEqual(preflight.first_queue_id, replay.first_queue_id);
    try std.testing.expectEqual(preflight.last_queue_id, replay.last_queue_id);

    const next = try lab.planIoQueue(8, 64, false);
    try std.testing.expectEqual(@as(u16, 4), next.queue_id);
}

test "phase12 nvme pci direct replay keeps rollback-gate parity explicit through recovery" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);

    _ = lab.beginReset();
    _ = lab.completeReset();
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);

    const queue_blocked = lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.queue_count_parity, queue_blocked.rollback_blocker);
    try std.testing.expect(queue_blocked.admin_queue_replayed_after_reset);
    try std.testing.expect(queue_blocked.queue_numbering_restarted);
    try std.testing.expectEqual(@as(usize, 2), queue_blocked.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 1), queue_blocked.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 1), queue_blocked.remaining_io_queue_count);
    try std.testing.expectEqual(@as(u32, 2), queue_blocked.dropped_io_host_dma_pages);
    try std.testing.expectEqual(@as(u32, 1), queue_blocked.rebuilt_io_host_dma_pages);
    try std.testing.expectEqual(@as(u32, 1), queue_blocked.remaining_io_host_dma_pages);
    try std.testing.expect(!queue_blocked.queue_count_parity_recovered);
    try std.testing.expect(!queue_blocked.host_dma_parity_recovered);
    try std.testing.expect(!queue_blocked.can_clear_rollback_gate);

    _ = try lab.planIoQueue(32, 64, true);
    const ready = lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.none, ready.rollback_blocker);
    try std.testing.expect(ready.admin_queue_replayed_after_reset);
    try std.testing.expect(ready.queue_numbering_restarted);
    try std.testing.expectEqual(@as(usize, 2), ready.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 2), ready.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), ready.remaining_io_queue_count);
    try std.testing.expectEqual(@as(u32, 2), ready.dropped_io_host_dma_pages);
    try std.testing.expectEqual(@as(u32, 2), ready.rebuilt_io_host_dma_pages);
    try std.testing.expectEqual(@as(u32, 0), ready.remaining_io_host_dma_pages);
    try std.testing.expect(ready.queue_count_parity_recovered);
    try std.testing.expect(ready.host_dma_parity_recovered);
    try std.testing.expect(ready.can_clear_rollback_gate);
}
