const std = @import("std");
const testing = std.testing;
const nvme_pci = @import("pci.zig");

test "nvme pci replayReservedIoQueues keeps controller-limited stale reservations reviewable" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    const reservation = try lab.reserveIoQueues(6, 6);

    _ = lab.beginReset();
    _ = lab.completeReset();
    _ = try lab.planAdminQueue(32, 64, false);

    const replayed = try lab.replayReservedIoQueues(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", replayed.anchor);
    try testing.expectEqual(@as(usize, 6), replayed.requested_io_queues);
    try testing.expectEqual(@as(usize, 3), replayed.controller_io_queue_limit);
    try testing.expectEqual(@as(usize, 64), replayed.planner_remaining_io_slots);
    try testing.expectEqual(@as(usize, 3), replayed.reserved_io_queues);
    try testing.expectEqual(@as(u16, 1), replayed.first_queue_id);
    try testing.expectEqual(@as(u16, 3), replayed.last_queue_id);
    try testing.expectEqual(@as(usize, 3), replayed.planned_io_queues_after_reserve);
    try testing.expect(replayed.controller_limited);
    try testing.expect(!replayed.planner_limited);
    try testing.expect(!replayed.queues_frozen);
    try testing.expectEqual(@as(u32, 1), replayed.reset_generation);

    const recovery = lab.recoverySummary();
    try testing.expectEqual(@as(usize, 3), recovery.planned_io_queues);

    const next = try lab.planIoQueue(8, 64, false);
    try testing.expectEqual(@as(u16, 4), next.queue_id);
}

test "nvme pci replayReservedIoQueues stays planner-limited after rebuilt queues consume the remaining slots" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(64, 64, false);
    const reservation = try lab.reserveIoQueues(4, 8);

    _ = lab.beginReset();
    _ = lab.completeReset();
    _ = try lab.planAdminQueue(64, 64, false);
    const rebuilt = try lab.reserveIoQueues(62, 64);
    try testing.expectEqual(@as(usize, 62), rebuilt.reserved_io_queues);
    try testing.expectEqual(@as(u16, 1), rebuilt.first_queue_id);
    try testing.expectEqual(@as(u16, 62), rebuilt.last_queue_id);

    const replayed = try lab.replayReservedIoQueues(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 8);
    try testing.expectEqualStrings("drivers/nvme/host/pci.c", replayed.anchor);
    try testing.expectEqual(@as(usize, 4), replayed.requested_io_queues);
    try testing.expectEqual(@as(usize, 8), replayed.controller_io_queue_limit);
    try testing.expectEqual(@as(usize, 2), replayed.planner_remaining_io_slots);
    try testing.expectEqual(@as(usize, 2), replayed.reserved_io_queues);
    try testing.expectEqual(@as(u16, 63), replayed.first_queue_id);
    try testing.expectEqual(@as(u16, 64), replayed.last_queue_id);
    try testing.expectEqual(@as(usize, 64), replayed.planned_io_queues_after_reserve);
    try testing.expect(!replayed.controller_limited);
    try testing.expect(replayed.planner_limited);
    try testing.expect(!replayed.queues_frozen);
    try testing.expectEqual(@as(u32, 1), replayed.reset_generation);

    const recovery = lab.recoverySummary();
    try testing.expectEqual(@as(usize, 64), recovery.planned_io_queues);
    try testing.expectError(error.TooManyPlannedIoQueues, lab.planIoQueue(8, 64, false));
}
