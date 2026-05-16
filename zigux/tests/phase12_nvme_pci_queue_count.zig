const std = @import("std");
const pci_queue_count = @import("../../drivers/nvme/host/pci_queue_count.zig");

test "phase12 nvme pci queue count helper keeps requested counts when controller and planner allow them" {
    const summary = try pci_queue_count.planIoQueueCount(.{}, 4, 8);

    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 4), summary.selected_io_queue_count);
    try std.testing.expectEqual(@as(u16, 1), summary.first_io_queue_id);
    try std.testing.expectEqual(@as(u16, 4), summary.last_io_queue_id);
    try std.testing.expectEqual(@as(u16, 5), summary.total_queue_pair_count);
    try std.testing.expectEqual(pci_queue_count.IoQueueCountCapSource.requested, summary.cap_source);
}

test "phase12 nvme pci queue count helper keeps controller caps and planner caps reviewable" {
    const controller_capped = try pci_queue_count.planIoQueueCount(.{
        .next_io_queue_id = 2,
        .planned_io_queues = 1,
    }, 8, 3);
    try std.testing.expectEqual(@as(u16, 3), controller_capped.selected_io_queue_count);
    try std.testing.expectEqual(@as(u16, 2), controller_capped.first_io_queue_id);
    try std.testing.expectEqual(@as(u16, 4), controller_capped.last_io_queue_id);
    try std.testing.expectEqual(pci_queue_count.IoQueueCountCapSource.controller_cap, controller_capped.cap_source);

    const planner_capped = try pci_queue_count.planIoQueueCount(.{
        .next_io_queue_id = 63,
        .planned_io_queues = pci_queue_count.max_planned_io_queues - 2,
    }, 8, 8);
    try std.testing.expectEqual(@as(u16, 2), planner_capped.remaining_planner_slots);
    try std.testing.expectEqual(@as(u16, 2), planner_capped.selected_io_queue_count);
    try std.testing.expectEqual(@as(u16, 63), planner_capped.first_io_queue_id);
    try std.testing.expectEqual(@as(u16, 64), planner_capped.last_io_queue_id);
    try std.testing.expectEqual(@as(u16, 65), planner_capped.total_queue_pair_count);
    try std.testing.expectEqual(pci_queue_count.IoQueueCountCapSource.planner_capacity, planner_capped.cap_source);
}

test "phase12 nvme pci queue count helper rejects invalid negotiation and frozen resets" {
    try std.testing.expectError(error.InvalidIoQueueCount, pci_queue_count.planIoQueueCount(.{}, 0, 4));
    try std.testing.expectError(error.InvalidIoQueueCount, pci_queue_count.planIoQueueCount(.{}, 4, 0));
    try std.testing.expectError(error.NoPlannerQueueSlotsAvailable, pci_queue_count.planIoQueueCount(.{
        .planned_io_queues = pci_queue_count.max_planned_io_queues,
    }, 1, 1));
    try std.testing.expectError(error.QueuePlanningBlockedByReset, pci_queue_count.planIoQueueCount(.{
        .recovery_state = .reset_frozen,
    }, 1, 1));
}
