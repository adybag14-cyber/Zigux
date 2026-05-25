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

    const applied = try lab.applyRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = reservation.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", applied.anchor);
    try std.testing.expectEqual(preflight.requested_reserved_io_queues, applied.requested_reserved_io_queues);
    try std.testing.expectEqual(preflight.controller_io_queue_limit, applied.controller_io_queue_limit);
    try std.testing.expectEqual(preflight.planner_remaining_io_slots, applied.planner_remaining_io_slots);
    try std.testing.expectEqual(preflight.replayable_reserved_io_queues, applied.replayed_reserved_io_queues);
    try std.testing.expectEqual(preflight.first_queue_id, applied.first_queue_id);
    try std.testing.expectEqual(preflight.last_queue_id, applied.last_queue_id);
    try std.testing.expectEqual(preflight.planned_io_queues_after_replay, applied.planned_io_queues_after_replay);
    try std.testing.expectEqual(preflight.next_io_queue_id_after_replay, applied.next_io_queue_id_after_replay);
    try std.testing.expectEqual(preflight.queue_numbering_restarted, applied.queue_numbering_restarted);
    try std.testing.expectEqual(preflight.controller_limited, applied.controller_limited);
    try std.testing.expectEqual(preflight.planner_limited, applied.planner_limited);
    try std.testing.expectEqual(preflight.cached_queue_reservation_stale, applied.cached_queue_reservation_stale);
    try std.testing.expectEqual(preflight.cached_prp_metadata_stale, applied.cached_prp_metadata_stale);
    try std.testing.expectEqual(preflight.descriptor_rebuild_required, applied.descriptor_rebuild_required);
    try std.testing.expectEqual(preflight.admin_queue_must_be_replanned, applied.admin_queue_must_be_replanned);

    const applied_recovery = lab.recoverySummary();
    try std.testing.expectEqual(@as(usize, 3), applied_recovery.planned_io_queues);

    const next = try lab.planIoQueue(8, 64, false);
    try std.testing.expectEqual(@as(u16, 4), next.queue_id);
}

test "phase12 nvme pci direct replay keeps recovery debt blockers and caps reviewable before preflight succeeds" {
    var frozen_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try frozen_lab.planAdminQueue(32, 64, false);
    const frozen = try frozen_lab.reserveIoQueues(4, 4);
    _ = frozen_lab.beginReset();

    const frozen_debt = try frozen_lab.recoveryReservationReplayDebtSummary(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = frozen.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = frozen.reserved_io_queues,
    }, 4);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", frozen_debt.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryReservationReplayBlocker.reset_frozen, frozen_debt.replay_blocker);
    try std.testing.expect(frozen_debt.queue_planning_blocked);
    try std.testing.expect(frozen_debt.queues_frozen);
    try std.testing.expect(frozen_debt.has_queue_reservation_to_replay);
    try std.testing.expect(frozen_debt.cached_queue_reservation_stale);
    try std.testing.expect(!frozen_debt.replay_preflight_ready);
    try std.testing.expectEqual(@as(?u16, null), frozen_debt.first_queue_id);
    try std.testing.expectEqual(@as(?u16, null), frozen_debt.next_io_queue_id_after_replay);

    var current_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try current_lab.planAdminQueue(32, 64, false);
    const current = try current_lab.reserveIoQueues(4, 4);
    const current_debt = try current_lab.recoveryReservationReplayDebtSummary(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = current.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = current.reserved_io_queues,
    }, 4);
    try std.testing.expectEqual(nvme_pci.RecoveryReservationReplayBlocker.queue_reservation_current, current_debt.replay_blocker);
    try std.testing.expect(current_debt.has_queue_reservation_to_replay);
    try std.testing.expect(current_debt.queue_reservation_already_current);
    try std.testing.expect(!current_debt.cached_queue_reservation_stale);
    try std.testing.expect(!current_debt.replay_preflight_ready);

    var capped_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try capped_lab.planAdminQueue(32, 64, false);
    const reservation = try capped_lab.reserveIoQueues(4, 4);
    _ = capped_lab.beginReset();
    _ = capped_lab.completeReset();
    _ = try capped_lab.planAdminQueue(32, 64, false);

    const no_controller = try capped_lab.recoveryReservationReplayDebtSummary(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 0);
    try std.testing.expectEqual(nvme_pci.RecoveryReservationReplayBlocker.no_controller_io_queues, no_controller.replay_blocker);
    try std.testing.expect(no_controller.cached_queue_reservation_stale);
    try std.testing.expect(!no_controller.replay_preflight_ready);
    try std.testing.expectEqual(@as(usize, 64), no_controller.planner_remaining_io_slots);
    try std.testing.expectEqual(@as(usize, 0), no_controller.replayable_reserved_io_queues);

    const rebuilt = try capped_lab.reserveIoQueues(64, 64);
    try std.testing.expectEqual(@as(usize, 64), rebuilt.reserved_io_queues);
    const planner_full = try capped_lab.recoveryReservationReplayDebtSummary(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 4);
    try std.testing.expectEqual(nvme_pci.RecoveryReservationReplayBlocker.planner_queue_slots, planner_full.replay_blocker);
    try std.testing.expect(!planner_full.replay_preflight_ready);
    try std.testing.expectEqual(@as(usize, 0), planner_full.planner_remaining_io_slots);
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

test "phase12 nvme pci direct replay keeps admin replay blocker explicit even after IO counts recover" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);

    _ = lab.beginReset();
    _ = lab.completeReset();

    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);

    const blocked = lab.recoveryRollbackGateSummary();
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", blocked.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, blocked.state);
    try std.testing.expectEqual(@as(u32, 1), blocked.reset_generation);
    try std.testing.expect(!blocked.admin_queue_replayed_after_reset);
    try std.testing.expect(blocked.queue_numbering_restarted);
    try std.testing.expectEqual(@as(usize, 2), blocked.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 2), blocked.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), blocked.remaining_io_queue_count);
    try std.testing.expectEqual(@as(u32, 2), blocked.dropped_io_host_dma_pages);
    try std.testing.expectEqual(@as(u32, 2), blocked.rebuilt_io_host_dma_pages);
    try std.testing.expectEqual(@as(u32, 0), blocked.remaining_io_host_dma_pages);
    try std.testing.expectEqual(nvme_pci.RecoveryRollbackBlocker.admin_queue_replay, blocked.rollback_blocker);
    try std.testing.expect(!blocked.queue_count_parity_recovered);
    try std.testing.expect(!blocked.host_dma_parity_recovered);
    try std.testing.expect(!blocked.can_clear_rollback_gate);
}

test "phase12 nvme pci direct replay keeps dropped backlog retirement blocked until admin replay completes even after IO parity recovers" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);

    _ = lab.beginReset();
    _ = lab.completeReset();

    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);

    const blocked = lab.summarizeDroppedIoRetirement();
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", blocked.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, blocked.state);
    try std.testing.expectEqual(@as(u32, 1), blocked.reset_generation);
    try std.testing.expect(!blocked.admin_queue_replayed_after_reset);
    try std.testing.expect(blocked.admin_queue_must_be_replayed);
    try std.testing.expect(blocked.queue_numbering_restarted);
    try std.testing.expectEqual(@as(usize, 2), blocked.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 2), blocked.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), blocked.remaining_io_queue_count);
    try std.testing.expect(!blocked.can_retire_dropped_io_backlog);
}

test "phase12 nvme pci dropped backlog retirement stays idle before any reset backlog exists" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(24, 64, false);
    _ = try lab.planIoQueue(8, 64, false);

    const summary = lab.summarizeDroppedIoRetirement();
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, summary.state);
    try std.testing.expectEqual(@as(u32, 0), summary.reset_generation);
    try std.testing.expect(summary.admin_queue_replayed_after_reset);
    try std.testing.expect(!summary.admin_queue_must_be_replayed);
    try std.testing.expectEqual(@as(usize, 0), summary.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 1), summary.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), summary.remaining_io_queue_count);
    try std.testing.expect(!summary.queue_numbering_restarted);
    try std.testing.expect(!summary.can_retire_dropped_io_backlog);
}

test "phase12 nvme pci direct replay keeps stale reservation replay blocked until admin queue is replanned" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    const reservation = try lab.reserveIoQueues(4, 4);

    _ = lab.beginReset();
    _ = lab.completeReset();

    const debt = try lab.recoveryReservationReplayDebtSummary(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 4);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", debt.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryReservationReplayBlocker.admin_queue_replay, debt.replay_blocker);
    try std.testing.expect(debt.cached_queue_reservation_stale);
    try std.testing.expect(debt.admin_queue_must_be_replanned);
    try std.testing.expect(!debt.replay_preflight_ready);

    try std.testing.expectError(error.AdminQueueReplayRequired, lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 4));

    _ = try lab.planAdminQueue(32, 64, false);
    const ready = try lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 4);
    try std.testing.expectEqual(@as(usize, 4), ready.replayable_reserved_io_queues);
    try std.testing.expectEqual(@as(u16, 1), ready.first_queue_id);
    try std.testing.expectEqual(@as(u16, 4), ready.last_queue_id);
    try std.testing.expect(ready.queue_numbering_restarted);
    try std.testing.expect(!ready.admin_queue_must_be_replanned);
}

test "phase12 nvme pci direct replay keeps planner-capped reservation debt explicit before replay" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    const reservation = try lab.reserveIoQueues(8, 8);

    _ = lab.beginReset();
    _ = lab.completeReset();
    _ = try lab.planAdminQueue(32, 64, false);
    const prefill = try lab.reserveIoQueues(62, 62);
    try std.testing.expectEqual(@as(usize, 62), prefill.reserved_io_queues);

    const debt = try lab.recoveryReservationReplayDebtSummary(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 8);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", debt.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, debt.state);
    try std.testing.expectEqual(@as(u32, 1), debt.reset_generation);
    try std.testing.expectEqual(@as(usize, 8), debt.requested_reserved_io_queues);
    try std.testing.expectEqual(@as(usize, 8), debt.controller_io_queue_limit);
    try std.testing.expectEqual(@as(usize, 2), debt.planner_remaining_io_slots);
    try std.testing.expectEqual(@as(usize, 2), debt.replayable_reserved_io_queues);
    try std.testing.expectEqual(@as(?u16, 63), debt.first_queue_id);
    try std.testing.expectEqual(@as(?u16, 64), debt.last_queue_id);
    try std.testing.expectEqual(@as(?u16, 65), debt.next_io_queue_id_after_replay);
    try std.testing.expect(!debt.queue_numbering_would_restart);
    try std.testing.expect(!debt.controller_limited);
    try std.testing.expect(debt.planner_limited);
    try std.testing.expect(!debt.queue_planning_blocked);
    try std.testing.expect(!debt.queues_frozen);
    try std.testing.expect(debt.has_queue_reservation_to_replay);
    try std.testing.expect(!debt.queue_reservation_already_current);
    try std.testing.expect(debt.cached_queue_reservation_stale);
    try std.testing.expect(!debt.cached_prp_metadata_stale);
    try std.testing.expect(!debt.descriptor_rebuild_required);
    try std.testing.expect(!debt.admin_queue_must_be_replanned);
    try std.testing.expectEqual(nvme_pci.RecoveryReservationReplayBlocker.none, debt.replay_blocker);
    try std.testing.expect(debt.replay_preflight_ready);
}

test "phase12 nvme pci direct replay applies planner-limited stale reservations without renumbering rebuilt queues" {
    var applied_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try applied_lab.planAdminQueue(32, 64, false);
    const reservation = try applied_lab.reserveIoQueues(8, 8);

    _ = applied_lab.beginReset();
    _ = applied_lab.completeReset();
    _ = try applied_lab.planAdminQueue(32, 64, false);
    _ = try applied_lab.reserveIoQueues(62, 62);

    const applied = try applied_lab.applyRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 8);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", applied.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, applied.state);
    try std.testing.expectEqual(@as(u32, 1), applied.reset_generation);
    try std.testing.expectEqual(@as(usize, 8), applied.requested_reserved_io_queues);
    try std.testing.expectEqual(@as(usize, 8), applied.controller_io_queue_limit);
    try std.testing.expectEqual(@as(usize, 2), applied.planner_remaining_io_slots);
    try std.testing.expectEqual(@as(usize, 2), applied.replayed_reserved_io_queues);
    try std.testing.expectEqual(@as(u16, 63), applied.first_queue_id);
    try std.testing.expectEqual(@as(u16, 64), applied.last_queue_id);
    try std.testing.expectEqual(@as(usize, 64), applied.planned_io_queues_after_replay);
    try std.testing.expectEqual(@as(u16, 65), applied.next_io_queue_id_after_replay);
    try std.testing.expect(!applied.queue_numbering_restarted);
    try std.testing.expect(!applied.controller_limited);
    try std.testing.expect(applied.planner_limited);
    try std.testing.expect(!applied.queue_planning_blocked);
    try std.testing.expect(!applied.queues_frozen);
    try std.testing.expect(applied.cached_queue_reservation_stale);
    try std.testing.expect(!applied.cached_prp_metadata_stale);
    try std.testing.expect(!applied.descriptor_rebuild_required);
    try std.testing.expect(!applied.admin_queue_must_be_replanned);

    const applied_summary = applied_lab.recoverySummary();
    try std.testing.expectEqual(@as(usize, 64), applied_summary.planned_io_queues);
    try std.testing.expectEqual(@as(u16, 65), applied_lab.next_io_queue_id);
    try std.testing.expectError(error.TooManyPlannedIoQueues, applied_lab.planIoQueue(8, 64, false));

    var replay_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try replay_lab.planAdminQueue(32, 64, false);
    _ = try replay_lab.reserveIoQueues(8, 8);
    _ = replay_lab.beginReset();
    _ = replay_lab.completeReset();
    _ = try replay_lab.planAdminQueue(32, 64, false);
    _ = try replay_lab.reserveIoQueues(62, 62);

    const replayed = try replay_lab.replayReservedIoQueues(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 8);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", replayed.anchor);
    try std.testing.expectEqual(@as(usize, 2), replayed.reserved_io_queues);
    try std.testing.expectEqual(@as(u16, 63), replayed.first_queue_id);
    try std.testing.expectEqual(@as(u16, 64), replayed.last_queue_id);
    try std.testing.expectEqual(@as(usize, 64), replayed.planned_io_queues_after_reserve);
    try std.testing.expect(!replayed.controller_limited);
    try std.testing.expect(replayed.planner_limited);
    try std.testing.expectEqual(@as(u32, 1), replayed.reset_generation);
}

test "phase12 nvme pci direct replay applies controller-limited stale reservations with restart still explicit" {
    var applied_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try applied_lab.planAdminQueue(32, 64, false);
    const reservation = try applied_lab.reserveIoQueues(8, 8);

    _ = applied_lab.beginReset();
    _ = applied_lab.completeReset();
    _ = try applied_lab.planAdminQueue(32, 64, false);

    const preflight = try applied_lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try std.testing.expect(preflight.controller_limited);
    try std.testing.expect(!preflight.planner_limited);
    try std.testing.expect(preflight.queue_numbering_restarted);
    try std.testing.expectEqual(@as(usize, 3), preflight.replayable_reserved_io_queues);
    try std.testing.expectEqual(@as(u16, 1), preflight.first_queue_id);
    try std.testing.expectEqual(@as(u16, 3), preflight.last_queue_id);
    try std.testing.expectEqual(@as(u16, 4), preflight.next_io_queue_id_after_replay);

    const applied = try applied_lab.applyRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", applied.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, applied.state);
    try std.testing.expectEqual(@as(u32, 1), applied.reset_generation);
    try std.testing.expectEqual(@as(usize, 8), applied.requested_reserved_io_queues);
    try std.testing.expectEqual(@as(usize, 3), applied.controller_io_queue_limit);
    try std.testing.expectEqual(@as(usize, 64), applied.planner_remaining_io_slots);
    try std.testing.expectEqual(@as(usize, 3), applied.replayed_reserved_io_queues);
    try std.testing.expectEqual(@as(u16, 1), applied.first_queue_id);
    try std.testing.expectEqual(@as(u16, 3), applied.last_queue_id);
    try std.testing.expectEqual(@as(usize, 3), applied.planned_io_queues_after_replay);
    try std.testing.expectEqual(@as(u16, 4), applied.next_io_queue_id_after_replay);
    try std.testing.expect(applied.queue_numbering_restarted);
    try std.testing.expect(applied.controller_limited);
    try std.testing.expect(!applied.planner_limited);
    try std.testing.expect(!applied.queue_planning_blocked);
    try std.testing.expect(!applied.queues_frozen);
    try std.testing.expect(applied.cached_queue_reservation_stale);
    try std.testing.expect(!applied.cached_prp_metadata_stale);
    try std.testing.expect(!applied.descriptor_rebuild_required);
    try std.testing.expect(!applied.admin_queue_must_be_replanned);

    const applied_summary = applied_lab.recoverySummary();
    try std.testing.expectEqual(@as(usize, 3), applied_summary.planned_io_queues);
    const next = try applied_lab.planIoQueue(8, 64, false);
    try std.testing.expectEqual(@as(u16, 4), next.queue_id);

    var replay_lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try replay_lab.planAdminQueue(32, 64, false);
    _ = try replay_lab.reserveIoQueues(8, 8);
    _ = replay_lab.beginReset();
    _ = replay_lab.completeReset();
    _ = try replay_lab.planAdminQueue(32, 64, false);

    const replayed = try replay_lab.replayReservedIoQueues(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", replayed.anchor);
    try std.testing.expectEqual(@as(usize, 8), replayed.requested_io_queues);
    try std.testing.expectEqual(@as(usize, 3), replayed.controller_io_queue_limit);
    try std.testing.expectEqual(@as(usize, 64), replayed.planner_remaining_io_slots);
    try std.testing.expectEqual(@as(usize, 3), replayed.reserved_io_queues);
    try std.testing.expectEqual(@as(u16, 1), replayed.first_queue_id);
    try std.testing.expectEqual(@as(u16, 3), replayed.last_queue_id);
    try std.testing.expectEqual(@as(usize, 3), replayed.planned_io_queues_after_reserve);
    try std.testing.expect(replayed.controller_limited);
    try std.testing.expect(!replayed.planner_limited);
    try std.testing.expectEqual(@as(u32, 1), replayed.reset_generation);
}
