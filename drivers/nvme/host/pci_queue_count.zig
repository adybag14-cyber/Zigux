const std = @import("std");

pub const default_anchor = "drivers/nvme/host/pci.c";
pub const max_planned_io_queues: usize = 64;

pub const RecoveryState = enum {
    running,
    reset_frozen,
};

pub const IoQueueCountCapSource = enum {
    requested,
    controller_cap,
    planner_capacity,
};

pub const IoQueueCountPlanSummary = struct {
    anchor: []const u8,
    requested_io_queue_count: u16,
    controller_io_queue_cap: u16,
    remaining_planner_slots: u16,
    selected_io_queue_count: u16,
    first_io_queue_id: u16,
    last_io_queue_id: u16,
    total_queue_pair_count: u16,
    cap_source: IoQueueCountCapSource,
    reset_generation: u32,
};

pub const IoQueueCountPlannerState = struct {
    recovery_state: RecoveryState = .running,
    next_io_queue_id: u16 = 1,
    planned_io_queues: usize = 0,
    reset_generation: u32 = 0,
};

pub fn planIoQueueCount(
    state: IoQueueCountPlannerState,
    requested_io_queue_count: u16,
    controller_io_queue_cap: u16,
) !IoQueueCountPlanSummary {
    if (state.recovery_state != .running) return error.QueuePlanningBlockedByReset;
    if (requested_io_queue_count == 0 or controller_io_queue_cap == 0) {
        return error.InvalidIoQueueCount;
    }

    const remaining_planner_slots = std.math.cast(
        u16,
        max_planned_io_queues - state.planned_io_queues,
    ) orelse return error.QueueCountOverflow;
    if (remaining_planner_slots == 0) return error.NoPlannerQueueSlotsAvailable;

    const selected_io_queue_count = @min(
        requested_io_queue_count,
        @min(controller_io_queue_cap, remaining_planner_slots),
    );
    const cap_source: IoQueueCountCapSource = if (selected_io_queue_count == requested_io_queue_count)
        .requested
    else if (selected_io_queue_count == controller_io_queue_cap)
        .controller_cap
    else
        .planner_capacity;
    const last_io_queue_id = state.next_io_queue_id + selected_io_queue_count - 1;
    const total_queue_pair_count = 1 + @as(u16, @intCast(state.planned_io_queues)) + selected_io_queue_count;

    return .{
        .anchor = default_anchor,
        .requested_io_queue_count = requested_io_queue_count,
        .controller_io_queue_cap = controller_io_queue_cap,
        .remaining_planner_slots = remaining_planner_slots,
        .selected_io_queue_count = selected_io_queue_count,
        .first_io_queue_id = state.next_io_queue_id,
        .last_io_queue_id = last_io_queue_id,
        .total_queue_pair_count = total_queue_pair_count,
        .cap_source = cap_source,
        .reset_generation = state.reset_generation,
    };
}

test "requested count wins when controller and planner both have room" {
    const summary = try planIoQueueCount(.{}, 4, 8);

    try std.testing.expectEqualStrings(default_anchor, summary.anchor);
    try std.testing.expectEqual(@as(u16, 4), summary.requested_io_queue_count);
    try std.testing.expectEqual(@as(u16, 8), summary.controller_io_queue_cap);
    try std.testing.expectEqual(@as(u16, 64), summary.remaining_planner_slots);
    try std.testing.expectEqual(@as(u16, 4), summary.selected_io_queue_count);
    try std.testing.expectEqual(@as(u16, 1), summary.first_io_queue_id);
    try std.testing.expectEqual(@as(u16, 4), summary.last_io_queue_id);
    try std.testing.expectEqual(@as(u16, 5), summary.total_queue_pair_count);
    try std.testing.expectEqual(IoQueueCountCapSource.requested, summary.cap_source);
    try std.testing.expectEqual(@as(u32, 0), summary.reset_generation);
}

test "controller cap wins when planner still has room" {
    const summary = try planIoQueueCount(.{
        .next_io_queue_id = 2,
        .planned_io_queues = 1,
    }, 8, 3);

    try std.testing.expectEqual(@as(u16, 63), summary.remaining_planner_slots);
    try std.testing.expectEqual(@as(u16, 3), summary.selected_io_queue_count);
    try std.testing.expectEqual(@as(u16, 2), summary.first_io_queue_id);
    try std.testing.expectEqual(@as(u16, 4), summary.last_io_queue_id);
    try std.testing.expectEqual(@as(u16, 5), summary.total_queue_pair_count);
    try std.testing.expectEqual(IoQueueCountCapSource.controller_cap, summary.cap_source);
}

test "planner capacity wins when the starter is almost full" {
    const summary = try planIoQueueCount(.{
        .next_io_queue_id = 63,
        .planned_io_queues = max_planned_io_queues - 2,
        .reset_generation = 7,
    }, 8, 8);

    try std.testing.expectEqual(@as(u16, 2), summary.remaining_planner_slots);
    try std.testing.expectEqual(@as(u16, 2), summary.selected_io_queue_count);
    try std.testing.expectEqual(@as(u16, 63), summary.first_io_queue_id);
    try std.testing.expectEqual(@as(u16, 64), summary.last_io_queue_id);
    try std.testing.expectEqual(@as(u16, 65), summary.total_queue_pair_count);
    try std.testing.expectEqual(IoQueueCountCapSource.planner_capacity, summary.cap_source);
    try std.testing.expectEqual(@as(u32, 7), summary.reset_generation);
}

test "invalid inputs, exhausted slots, and frozen resets are rejected" {
    try std.testing.expectError(error.InvalidIoQueueCount, planIoQueueCount(.{}, 0, 4));
    try std.testing.expectError(error.InvalidIoQueueCount, planIoQueueCount(.{}, 4, 0));
    try std.testing.expectError(error.NoPlannerQueueSlotsAvailable, planIoQueueCount(.{
        .planned_io_queues = max_planned_io_queues,
    }, 1, 1));
    try std.testing.expectError(error.QueuePlanningBlockedByReset, planIoQueueCount(.{
        .recovery_state = .reset_frozen,
    }, 1, 1));
}
