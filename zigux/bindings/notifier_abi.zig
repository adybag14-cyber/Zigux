const std = @import("std");

pub const NotifierResult = enum(u32) {
    done = 0,
    ok = 1,
    stop = 2,
};

pub const NotifierBlock = extern struct {
    notifier_call: usize,
    next: usize,
    priority: i32,
};

pub const PriorityIncrease = struct {
    previous_index: usize,
    current_index: usize,
    previous_priority: i32,
    current_priority: i32,
};

pub fn prioritiesNonincreasing(blocks: []const NotifierBlock) bool {
    return firstPriorityIncrease(blocks) == null;
}

pub fn firstPriorityIncrease(blocks: []const NotifierBlock) ?PriorityIncrease {
    if (blocks.len < 2) return null;

    var previous_priority = blocks[0].priority;
    for (blocks[1..], 1..) |block, index| {
        if (block.priority > previous_priority) {
            return .{
                .previous_index = index - 1,
                .current_index = index,
                .previous_priority = previous_priority,
                .current_priority = block.priority,
            };
        }
        previous_priority = block.priority;
    }

    return null;
}

pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {
    var current = head orelse return true;
    var previous_priority = current.priority;

    while (current.next != 0) {
        const next: *const NotifierBlock = @ptrFromInt(current.next);
        if (next.priority > previous_priority) return false;
        previous_priority = next.priority;
        current = next;
    }

    return true;
}

test "notifier priority helper accepts empty chain" {
    try std.testing.expect(chainHasNonincreasingPriority(null));
}

test "notifier priority helper accepts single node chain" {
    const node = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 4,
    };

    try std.testing.expect(chainHasNonincreasingPriority(&node));
}

test "notifier priority helper accepts equal and descending priorities" {
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 3,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 5,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 5,
    };

    try std.testing.expect(chainHasNonincreasingPriority(&first));
}

test "notifier priority helper rejects increasing priority" {
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 6,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 2,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 4,
    };

    try std.testing.expect(!chainHasNonincreasingPriority(&first));
}

test "notifier abi reports the first priority increase" {
    const sample = [_]NotifierBlock{
        .{ .notifier_call = 1, .next = 0, .priority = 9 },
        .{ .notifier_call = 2, .next = 0, .priority = 7 },
        .{ .notifier_call = 3, .next = 0, .priority = 8 },
        .{ .notifier_call = 4, .next = 0, .priority = 1 },
    };

    const increase = firstPriorityIncrease(&sample).?;
    try std.testing.expectEqual(@as(usize, 1), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 2), increase.current_index);
    try std.testing.expectEqual(@as(i32, 7), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 8), increase.current_priority);
}

test "notifier abi keeps nonincreasing priority order reviewable" {
    const ordered = [_]NotifierBlock{
        .{ .notifier_call = 1, .next = 2, .priority = 8 },
        .{ .notifier_call = 2, .next = 3, .priority = 8 },
        .{ .notifier_call = 3, .next = 0, .priority = -4 },
    };
    const rising = [_]NotifierBlock{
        .{ .notifier_call = 1, .next = 2, .priority = 3 },
        .{ .notifier_call = 2, .next = 0, .priority = 5 },
    };

    try std.testing.expect(prioritiesNonincreasing(&ordered));
    try std.testing.expect(firstPriorityIncrease(&ordered) == null);

    const increase = firstPriorityIncrease(&rising).?;
    try std.testing.expectEqual(@as(usize, 0), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 1), increase.current_index);
    try std.testing.expectEqual(@as(i32, 3), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 5), increase.current_priority);
    try std.testing.expect(!prioritiesNonincreasing(&rising));
}

test "notifier abi accepts empty and singleton priority samples" {
    const single = [_]NotifierBlock{
        .{ .notifier_call = 1, .next = 0, .priority = 7 },
    };

    try std.testing.expect(firstPriorityIncrease(&.{}) == null);
    try std.testing.expect(prioritiesNonincreasing(&.{}));
    try std.testing.expect(firstPriorityIncrease(&single) == null);
    try std.testing.expect(prioritiesNonincreasing(&single));
}

test "notifier abi keeps result codes and block layout explicit" {
    try std.testing.expectEqual(@as(u32, 0), @intFromEnum(NotifierResult.done));
    try std.testing.expectEqual(@as(u32, 1), @intFromEnum(NotifierResult.ok));
    try std.testing.expectEqual(@as(u32, 2), @intFromEnum(NotifierResult.stop));

    try std.testing.expectEqual(@as(usize, 24), @sizeOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 8), @alignOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(NotifierBlock, "notifier_call"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(NotifierBlock, "next"));
    try std.testing.expectEqual(@as(usize, 16), @offsetOf(NotifierBlock, "priority"));
}
