const std = @import("std");
const abi = @import("abi_bindings");

pub const NOTIFIER_DONE: u32 = abi.NOTIFIER_DONE;
pub const NOTIFIER_OK: u32 = abi.NOTIFIER_OK;
pub const NOTIFIER_STOP: u32 = abi.NOTIFIER_STOP;

pub const NotifierResult = abi.NotifierResult;
pub const NotifierBlock = abi.NotifierBlock;
pub const PriorityIncrease = abi.ChainPriorityIncrease;
pub const ChainPriorityIncrease = abi.ChainPriorityIncrease;

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
    return abi.chainHasNonincreasingPriority(head);
}

pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease {
    return abi.firstChainPriorityIncrease(head);
}

test "notifier abi aliases stay aligned with the shared abi surface" {
    try std.testing.expectEqual(@as(u32, abi.NOTIFIER_DONE), NOTIFIER_DONE);
    try std.testing.expectEqual(@as(u32, abi.NOTIFIER_OK), NOTIFIER_OK);
    try std.testing.expectEqual(@as(u32, abi.NOTIFIER_STOP), NOTIFIER_STOP);
    try std.testing.expectEqual(@as(usize, @sizeOf(abi.NotifierBlock)), @sizeOf(NotifierBlock));
    try std.testing.expectEqual(
        @as(usize, @sizeOf(abi.ChainPriorityIncrease)),
        @sizeOf(ChainPriorityIncrease),
    );
}

test "notifier priority helper accepts empty chain" {
    try std.testing.expect(chainHasNonincreasingPriority(null));
    try std.testing.expect(firstChainPriorityIncrease(null) == null);
}

test "notifier priority helper accepts single node chain" {
    const node = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 4,
    };

    try std.testing.expect(chainHasNonincreasingPriority(&node));
    try std.testing.expect(firstChainPriorityIncrease(&node) == null);
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
    try std.testing.expect(firstChainPriorityIncrease(&first) == null);
}

test "notifier priority helper reports the first chain priority increase" {
    const fourth = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 1,
    };
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&fourth),
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

    const increase = firstChainPriorityIncrease(&first).?;
    const shared_increase = abi.firstChainPriorityIncrease(&first).?;
    try std.testing.expectEqual(@as(usize, 1), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 2), increase.current_index);
    try std.testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 6), increase.current_priority);
    try std.testing.expectEqual(shared_increase.previous_index, increase.previous_index);
    try std.testing.expectEqual(shared_increase.current_index, increase.current_index);
    try std.testing.expectEqual(shared_increase.previous_priority, increase.previous_priority);
    try std.testing.expectEqual(shared_increase.current_priority, increase.current_priority);
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
    const expected_chain_alignment = @alignOf(usize);
    const expected_chain_size = std.mem.alignForward(
        usize,
        (@sizeOf(usize) * 2) + (@sizeOf(i32) * 2),
        expected_chain_alignment,
    );

    try std.testing.expectEqual(@as(u32, 0), NOTIFIER_DONE);
    try std.testing.expectEqual(@as(u32, 1), NOTIFIER_OK);
    try std.testing.expectEqual(@as(u32, 2), NOTIFIER_STOP);
    try std.testing.expectEqual(@as(u32, NOTIFIER_DONE), @intFromEnum(NotifierResult.done));
    try std.testing.expectEqual(@as(u32, NOTIFIER_OK), @intFromEnum(NotifierResult.ok));
    try std.testing.expectEqual(@as(u32, NOTIFIER_STOP), @intFromEnum(NotifierResult.stop));

    try std.testing.expectEqual(@as(usize, 24), @sizeOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 8), @alignOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(NotifierBlock, "notifier_call"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(NotifierBlock, "next"));
    try std.testing.expectEqual(@as(usize, 16), @offsetOf(NotifierBlock, "priority"));

    try std.testing.expectEqual(expected_chain_size, @sizeOf(ChainPriorityIncrease));
    try std.testing.expectEqual(expected_chain_alignment, @alignOf(ChainPriorityIncrease));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ChainPriorityIncrease, "previous_index"));
    try std.testing.expectEqual(@sizeOf(usize), @offsetOf(ChainPriorityIncrease, "current_index"));
    try std.testing.expectEqual(@sizeOf(usize) * 2, @offsetOf(ChainPriorityIncrease, "previous_priority"));
    try std.testing.expectEqual((@sizeOf(usize) * 2) + @sizeOf(i32), @offsetOf(ChainPriorityIncrease, "current_priority"));
}
