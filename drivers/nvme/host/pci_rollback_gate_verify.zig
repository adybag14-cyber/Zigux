const std = @import("std");
const testing = std.testing;
const nvme_pci = @import("pci.zig");

test "nvme pci recovery rollback gate stays active until metadata reservation and backlog are all refreshed" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    const reservation = try lab.reserveIoQueues(8, 6);
    const metadata = try lab.planPrpMetadata(4096 * 515, 0);

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
    try testing.expect(stale.queue_reservation_replay_required);
    try testing.expect(stale.admin_queue_must_be_replanned);
    try testing.expect(stale.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 6), stale.io_queues_dropped_by_reset);

    _ = try lab.planAdminQueue(48, 64, false);
    const refreshed_metadata = try lab.planPrpMetadata(4096 * 515, 0);
    const replay = try lab.replayReservedIoQueues(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 6);
    try testing.expectEqual(@as(usize, 6), replay.reserved_io_queues);

    const after_metadata_and_reservation = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = refreshed_metadata.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = false,
        .cached_descriptor_dma_bytes = refreshed_metadata.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = refreshed_metadata.requires_descriptor_rebuild_after_reset,
        .cached_queue_reservation_generation = replay.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = replay.reserved_io_queues,
    });
    try testing.expect(!after_metadata_and_reservation.cached_prp_metadata_stale);
    try testing.expect(!after_metadata_and_reservation.descriptor_rebuild_required);
    try testing.expect(!after_metadata_and_reservation.queue_reservation_replay_required);
    try testing.expect(!after_metadata_and_reservation.admin_queue_must_be_replanned);
    try testing.expect(after_metadata_and_reservation.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 6), after_metadata_and_reservation.io_queues_dropped_by_reset);
    try testing.expectEqual(@as(u16, 7), after_metadata_and_reservation.next_io_queue_id);

    const partial_retirement = try lab.retireRecoveredIoQueues(2);
    try testing.expectEqual(@as(usize, 2), partial_retirement.dropped_io_queues_retired);
    try testing.expectEqual(@as(usize, 4), partial_retirement.dropped_io_queues_remaining);

    const after_partial_retirement = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = refreshed_metadata.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = false,
        .cached_descriptor_dma_bytes = refreshed_metadata.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = refreshed_metadata.requires_descriptor_rebuild_after_reset,
        .cached_queue_reservation_generation = replay.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = replay.reserved_io_queues,
    });
    try testing.expect(!after_partial_retirement.cached_prp_metadata_stale);
    try testing.expect(!after_partial_retirement.queue_reservation_replay_required);
    try testing.expect(!after_partial_retirement.admin_queue_must_be_replanned);
    try testing.expect(after_partial_retirement.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 4), after_partial_retirement.io_queues_dropped_by_reset);
    try testing.expectEqual(@as(u16, 7), after_partial_retirement.next_io_queue_id);

    const complete_retirement = try lab.retireRecoveredIoQueues(4);
    try testing.expectEqual(@as(usize, 6), complete_retirement.dropped_io_queues_retired);
    try testing.expectEqual(@as(usize, 0), complete_retirement.dropped_io_queues_remaining);

    const after_full_retirement = lab.summarizeRecoveryReplay(.{
        .cached_prp_metadata_generation = refreshed_metadata.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = false,
        .cached_descriptor_dma_bytes = refreshed_metadata.metadata_dma_bytes,
        .cached_requires_descriptor_rebuild = refreshed_metadata.requires_descriptor_rebuild_after_reset,
        .cached_queue_reservation_generation = replay.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = replay.reserved_io_queues,
    });
    try testing.expect(!after_full_retirement.cached_prp_metadata_stale);
    try testing.expect(!after_full_retirement.descriptor_rebuild_required);
    try testing.expectEqual(@as(u32, 0), after_full_retirement.descriptor_rebuild_dma_bytes);
    try testing.expect(!after_full_retirement.queue_reservation_replay_required);
    try testing.expectEqual(@as(usize, 0), after_full_retirement.reserved_io_queues_to_renegotiate);
    try testing.expect(!after_full_retirement.admin_queue_must_be_replanned);
    try testing.expect(!after_full_retirement.io_queues_must_be_rebuilt);
    try testing.expectEqual(@as(usize, 0), after_full_retirement.io_queues_dropped_by_reset);
    try testing.expectEqual(@as(u16, 7), after_full_retirement.next_io_queue_id);
}
