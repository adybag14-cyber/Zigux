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

test "nvme pci recovery replay keeps legacy short-form request literals compatible" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(40, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    const metadata = try lab.planPrpMetadata(8192, 0x200);
    try testing.expect(metadata.requires_descriptor_rebuild_after_reset);

    _ = lab.beginReset();

    const legacy_shape = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = metadata.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
    });
    try testing.expect(legacy_shape.cached_prp_metadata_stale);
    try testing.expect(!legacy_shape.descriptor_rebuild_required);
    try testing.expectEqual(@as(u32, 0), legacy_shape.descriptor_rebuild_dma_bytes);
    try testing.expect(!legacy_shape.cached_queue_reservation_stale);
    try testing.expect(!legacy_shape.queue_reservation_replay_required);
    try testing.expectEqual(@as(usize, 0), legacy_shape.reserved_io_queues_to_renegotiate);
    try testing.expect(legacy_shape.admin_queue_must_be_replanned);
    try testing.expect(legacy_shape.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 1), legacy_shape.io_queues_dropped_by_reset);
}

test "nvme pci recovery replay renegotiates stale reservations against a reduced controller cap" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    const reservation = try lab.reserveIoQueues(8, 6);
    try testing.expectEqual(@as(usize, 6), reservation.reserved_io_queues);

    _ = lab.beginReset();
    _ = lab.completeReset();

    try testing.expectError(error.AdminQueueReplayRequired, lab.replayReservedIoQueues(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3));
    _ = try lab.planAdminQueue(32, 64, false);

    const replay = try lab.replayReservedIoQueues(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", replay.anchor);
    try testing.expectEqual(@as(usize, 6), replay.requested_io_queues);
    try testing.expectEqual(@as(usize, 3), replay.controller_io_queue_limit);
    try testing.expectEqual(@as(usize, 64), replay.planner_remaining_io_slots);
    try testing.expectEqual(@as(usize, 3), replay.reserved_io_queues);
    try testing.expectEqual(@as(u16, 1), replay.first_queue_id);
    try testing.expectEqual(@as(u16, 3), replay.last_queue_id);
    try testing.expectEqual(@as(usize, 3), replay.planned_io_queues_after_reserve);
    try testing.expect(replay.controller_limited);
    try testing.expect(!replay.planner_limited);
    try testing.expect(!replay.queues_frozen);
    try testing.expectEqual(@as(u32, 1), replay.reset_generation);

    const next = try lab.planIoQueue(8, 64, false);
    try testing.expectEqual(@as(u16, 4), next.queue_id);
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

test "nvme pci recovery reservation replay stays planner-limited after post-reset reservations consume queue IDs" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    const stale_reservation = try lab.reserveIoQueues(8, 8);
    try testing.expectEqual(@as(usize, 8), stale_reservation.reserved_io_queues);

    _ = lab.beginReset();
    _ = lab.completeReset();
    _ = try lab.planAdminQueue(32, 64, false);

    const interim = try lab.reserveIoQueues(62, 62);
    try testing.expectEqual(@as(usize, 62), interim.reserved_io_queues);
    try testing.expectEqual(@as(usize, 62), interim.planned_io_queues_after_reserve);

    const preflight = try lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = stale_reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = stale_reservation.reserved_io_queues,
    }, 8);
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", preflight.anchor);
    try testing.expectEqual(nvme_pci.RecoveryState.running, preflight.state);
    try testing.expectEqual(@as(u32, 1), preflight.reset_generation);
    try testing.expectEqual(@as(usize, 8), preflight.requested_reserved_io_queues);
    try testing.expectEqual(@as(usize, 8), preflight.controller_io_queue_limit);
    try testing.expectEqual(@as(usize, 2), preflight.planner_remaining_io_slots);
    try testing.expectEqual(@as(usize, 2), preflight.replayable_reserved_io_queues);
    try testing.expectEqual(@as(u16, 63), preflight.first_queue_id);
    try testing.expectEqual(@as(u16, 64), preflight.last_queue_id);
    try testing.expect(!preflight.controller_limited);
    try testing.expect(preflight.planner_limited);
    try testing.expect(!preflight.queue_planning_blocked);
    try testing.expect(!preflight.queues_frozen);
    try testing.expect(preflight.cached_queue_reservation_stale);
    try testing.expect(!preflight.admin_queue_must_be_replanned);

    const replay = try lab.replayReservedIoQueues(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = stale_reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = stale_reservation.reserved_io_queues,
    }, 8);
    try testing.expectEqual(@as(usize, 8), replay.requested_io_queues);
    try testing.expectEqual(@as(usize, 8), replay.controller_io_queue_limit);
    try testing.expectEqual(@as(usize, 2), replay.planner_remaining_io_slots);
    try testing.expectEqual(@as(usize, 2), replay.reserved_io_queues);
    try testing.expectEqual(@as(u16, 63), replay.first_queue_id);
    try testing.expectEqual(@as(u16, 64), replay.last_queue_id);
    try testing.expectEqual(@as(usize, 64), replay.planned_io_queues_after_reserve);
    try testing.expect(!replay.controller_limited);
    try testing.expect(replay.planner_limited);
    try testing.expectEqual(@as(u32, 1), replay.reset_generation);

    try testing.expectError(error.TooManyPlannedIoQueues, lab.planIoQueue(8, 64, false));
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

test "nvme pci recovery replay keeps combined stale metadata and queue reservations visible until both are refreshed" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    const reservation = try lab.reserveIoQueues(8, 6);
    const metadata = try lab.planPrpMetadata(4096 * 515, 0);
    try testing.expect(metadata.requires_descriptor_rebuild_after_reset);
    try testing.expectEqual(@as(u32, 8192), metadata.metadata_dma_bytes);

    _ = lab.beginReset();
    _ = lab.completeReset();

    const stale = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = metadata.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
        .cached_descriptor_dma_bytes = metadata.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = metadata.requires_descriptor_rebuild_after_reset,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    });
    try testing.expect(stale.cached_prp_metadata_stale);
    try testing.expect(stale.descriptor_rebuild_required);
    try testing.expectEqual(@as(u32, 8192), stale.descriptor_rebuild_dma_bytes);
    try testing.expect(stale.cached_queue_reservation_stale);
    try testing.expect(stale.queue_reservation_replay_required);
    try testing.expectEqual(@as(usize, 6), stale.reserved_io_queues_to_renegotiate);
    try testing.expect(stale.admin_queue_must_be_replanned);
    try testing.expect(stale.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 6), stale.io_queues_dropped_by_reset);
    try testing.expectEqual(@as(u16, 1), stale.next_io_queue_id);
    try testing.expectEqual(@as(u16, 48), stale.last_admin_queue_depth);

    _ = try lab.planAdminQueue(48, 64, false);
    const refreshed_metadata = try lab.planPrpMetadata(4096 * 515, 0);
    const replay = try lab.replayReservedIoQueues(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try testing.expectEqual(@as(usize, 3), replay.reserved_io_queues);
    try testing.expectEqual(@as(u16, 1), replay.first_queue_id);
    try testing.expectEqual(@as(u16, 3), replay.last_queue_id);
    try testing.expectEqual(@as(u32, 1), replay.reset_generation);

    const refreshed = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = refreshed_metadata.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = false,
        .cached_descriptor_dma_bytes = refreshed_metadata.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = refreshed_metadata.requires_descriptor_rebuild_after_reset,
        .cached_queue_reservation_generation = replay.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = replay.reserved_io_queues,
    });
    try testing.expect(!refreshed.cached_prp_metadata_stale);
    try testing.expect(!refreshed.descriptor_rebuild_required);
    try testing.expectEqual(@as(u32, 0), refreshed.descriptor_rebuild_dma_bytes);
    try testing.expect(!refreshed.cached_queue_reservation_stale);
    try testing.expect(!refreshed.queue_reservation_replay_required);
    try testing.expectEqual(@as(usize, 0), refreshed.reserved_io_queues_to_renegotiate);
    try testing.expect(!refreshed.admin_queue_must_be_replanned);
    try testing.expect(refreshed.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 6), refreshed.io_queues_dropped_by_reset);
    try testing.expectEqual(@as(u16, 4), refreshed.next_io_queue_id);
    try testing.expectEqual(@as(u16, 48), refreshed.last_admin_queue_depth);
    try testing.expectEqual(@as(u32, 1), refreshed.reset_generation);
}

test "nvme pci recovery replay carries multi-page PRP descriptor DMA through reset" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    const descriptor = nvme_pci.NvmePciQueueLab.descriptor();
    try testing.expect(descriptor.provides_prp_shape_helper);
    try testing.expect(descriptor.provides_prp_metadata_helper);
    _ = try lab.planAdminQueue(32, 64, false);
    const metadata = try lab.planPrpMetadata(4096 * 515, 0);
    try testing.expectEqual(@as(u16, 2), metadata.prp_list_pages);
    try testing.expectEqual(@as(u16, 1), metadata.prp_list_link_entries);
    try testing.expectEqual(@as(u16, 2), metadata.last_prp_list_page_entries);
    try testing.expectEqual(@as(u32, 8192), metadata.metadata_dma_bytes);

    _ = lab.beginReset();
    _ = lab.completeReset();

    const stale = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = metadata.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
        .cached_descriptor_dma_bytes = metadata.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = metadata.requires_descriptor_rebuild_after_reset,
    });
    try testing.expect(stale.cached_prp_metadata_stale);
    try testing.expect(stale.descriptor_rebuild_required);
    try testing.expectEqual(@as(u32, 8192), stale.descriptor_rebuild_dma_bytes);
    try testing.expect(stale.admin_queue_must_be_replanned);
}

test "nvme pci recovery rebuild progress tracks partial and complete backlog retirement after admin replay" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, false);

    _ = lab.beginReset();
    _ = lab.completeReset();

    const stale = lab.summarizeRecoveryRebuildProgress();
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", stale.anchor);
    try testing.expectEqual(nvme_pci.RecoveryState.running, stale.state);
    try testing.expectEqual(@as(u32, 1), stale.reset_generation);
    try testing.expectEqual(@as(usize, 0), stale.planned_io_queues);
    try testing.expectEqual(@as(usize, 2), stale.dropped_io_queues_initial);
    try testing.expectEqual(@as(usize, 0), stale.dropped_io_queues_retired);
    try testing.expectEqual(@as(usize, 2), stale.dropped_io_queues_remaining);
    try testing.expect(!stale.queue_planning_blocked);
    try testing.expect(stale.admin_queue_must_be_replanned);

    try testing.expectError(error.AdminQueueReplayRequired, lab.retireRecoveredIoQueues(1));

    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.reserveIoQueues(2, 2);

    const partial = try lab.retireRecoveredIoQueues(1);
    try testing.expectEqual(@as(usize, 2), partial.planned_io_queues);
    try testing.expectEqual(@as(usize, 2), partial.dropped_io_queues_initial);
    try testing.expectEqual(@as(usize, 1), partial.dropped_io_queues_retired);
    try testing.expectEqual(@as(usize, 1), partial.dropped_io_queues_remaining);
    try testing.expect(!partial.queue_planning_blocked);
    try testing.expect(!partial.admin_queue_must_be_replanned);

    const complete = try lab.retireRecoveredIoQueues(1);
    try testing.expectEqual(@as(usize, 2), complete.planned_io_queues);
    try testing.expectEqual(@as(usize, 2), complete.dropped_io_queues_initial);
    try testing.expectEqual(@as(usize, 2), complete.dropped_io_queues_retired);
    try testing.expectEqual(@as(usize, 0), complete.dropped_io_queues_remaining);
    try testing.expect(!complete.queue_planning_blocked);
    try testing.expect(!complete.admin_queue_must_be_replanned);
}

test "nvme pci recovery replay keeps dropped-queue retirement gated until admin replay and full rebuild coverage" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, false);

    _ = lab.beginReset();
    _ = lab.completeReset();

    const stale = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
    });
    try testing.expect(stale.admin_queue_must_be_replanned);
    try testing.expect(stale.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 2), stale.io_queues_dropped_by_reset);

    try testing.expectError(error.AdminQueueReplayRequired, lab.retireRecoveredIoQueues(1));

    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.reserveIoQueues(1, 1);
    const partial = try lab.retireRecoveredIoQueues(1);
    try testing.expectEqual(@as(usize, 1), partial.dropped_io_queues_retired);
    try testing.expectEqual(@as(usize, 1), partial.dropped_io_queues_remaining);

    const after_partial = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = false,
    });
    try testing.expect(!after_partial.admin_queue_must_be_replanned);
    try testing.expect(after_partial.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 1), after_partial.io_queues_dropped_by_reset);

    _ = try lab.reserveIoQueues(1, 1);
    const complete = try lab.retireRecoveredIoQueues(1);
    try testing.expectEqual(@as(usize, 2), complete.dropped_io_queues_retired);
    try testing.expectEqual(@as(usize, 0), complete.dropped_io_queues_remaining);

    const after_complete = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = false,
    });
    try testing.expect(!after_complete.admin_queue_must_be_replanned);
    try testing.expect(!after_complete.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 0), after_complete.io_queues_dropped_by_reset);
    try testing.expectEqual(@as(u16, 3), after_complete.next_io_queue_id);
}

test "nvme pci recovery transport preflight tracks partial backlog retirement without mutating state" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, false);

    _ = lab.beginReset();
    _ = lab.completeReset();
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.reserveIoQueues(1, 1);

    const after_retire = try lab.retireRecoveredIoQueues(1);
    try testing.expectEqual(@as(usize, 1), after_retire.dropped_io_queues_retired);
    try testing.expectEqual(@as(usize, 1), after_retire.dropped_io_queues_remaining);

    const before = lab.summarizeRecoveryRebuildProgress();
    const preflight = try lab.planRecoveryTransportPreflight(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = false,
    });
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", preflight.anchor);
    try testing.expectEqual(nvme_pci.RecoveryState.running, preflight.state);
    try testing.expectEqual(@as(u32, 1), preflight.reset_generation);
    try testing.expect(!preflight.descriptor_rebuild_required);
    try testing.expectEqual(@as(u32, 0), preflight.descriptor_rebuild_dma_bytes);
    try testing.expectEqual(@as(u16, 0), preflight.descriptor_rebuild_pages);
    try testing.expect(!preflight.queue_reservation_replay_required);
    try testing.expectEqual(@as(usize, 0), preflight.reserved_io_queues_to_renegotiate);
    try testing.expect(preflight.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 1), preflight.io_queues_dropped_by_reset);
    try testing.expectEqual(@as(u16, 2), preflight.next_io_queue_id);
    try testing.expectEqual(@as(u16, 48), preflight.last_admin_queue_depth);

    const after = lab.summarizeRecoveryRebuildProgress();
    try testing.expectEqual(before.dropped_io_queues_retired, after.dropped_io_queues_retired);
    try testing.expectEqual(before.dropped_io_queues_remaining, after.dropped_io_queues_remaining);
    try testing.expectEqual(before.planned_io_queues, after.planned_io_queues);
}

test "nvme pci recovery transport preflight clears once backlog retirement is complete" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = lab.beginReset();
    _ = lab.completeReset();
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.reserveIoQueues(1, 1);
    _ = try lab.retireRecoveredIoQueues(1);

    try testing.expectError(error.NoRecoveryTransportPreflightNeeded, lab.planRecoveryTransportPreflight(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = false,
    }));
}

test "nvme pci recovery rebuild progress rejects empty, missing, and oversized retirement requests" {
    var missing = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try missing.planAdminQueue(32, 64, false);
    try testing.expectError(error.NoRecoveryBacklog, missing.retireRecoveredIoQueues(1));

    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    _ = try lab.planIoQueue(8, 64, false);
    _ = lab.beginReset();
    _ = lab.completeReset();
    _ = try lab.planAdminQueue(32, 64, false);
    _ = try lab.reserveIoQueues(1, 1);

    try testing.expectError(error.InvalidRecoveredIoQueueCount, lab.retireRecoveredIoQueues(0));
    try testing.expectError(error.RebuiltIoQueuesExceedBacklog, lab.retireRecoveredIoQueues(2));

    const retired = try lab.retireRecoveredIoQueues(1);
    try testing.expectEqual(@as(usize, 1), retired.dropped_io_queues_initial);
    try testing.expectEqual(@as(usize, 1), retired.dropped_io_queues_retired);
    try testing.expectEqual(@as(usize, 0), retired.dropped_io_queues_remaining);

    try testing.expectError(error.RebuiltIoQueuesExceedBacklog, lab.retireRecoveredIoQueues(1));
}
