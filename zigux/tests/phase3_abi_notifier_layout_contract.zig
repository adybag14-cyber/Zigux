const std = @import("std");

const abi = @import("abi_bindings");

test "phase3 abi notifier results stay aligned across relays" {
    try std.testing.expectEqual(@as(?abi.NotifierResult, .done), abi.notifierResultFromInt(abi.NOTIFIER_DONE));
    try std.testing.expectEqual(@as(?abi.NotifierResult, .ok), abi.notifierResultFromInt(abi.NOTIFIER_OK));
    try std.testing.expectEqual(@as(?abi.NotifierResult, .stop), abi.notifierResultFromInt(abi.NOTIFIER_STOP));
    try std.testing.expectEqual(@as(?abi.NotifierResult, null), abi.notifierResultFromInt(99));
}

test "phase3 abi notifier stop semantics reject unknown values" {
    try std.testing.expect(!abi.notifierResultStopsChainValue(abi.NOTIFIER_DONE));
    try std.testing.expect(!abi.notifierResultStopsChainValue(abi.NOTIFIER_OK));
    try std.testing.expect(abi.notifierResultStopsChainValue(abi.NOTIFIER_STOP));
    try std.testing.expect(!abi.notifierResultStopsChainValue(99));
}

test "phase3 abi notifier block layout constants mirror the public struct" {
    const raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_size = std.mem.alignForward(usize, raw_size, @alignOf(usize));

    try std.testing.expectEqual(expected_size, abi.notifier_block_size);
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), abi.notifier_block_align);
    try std.testing.expectEqual(@as(usize, 0), abi.notifier_block_notifier_call_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), abi.notifier_block_next_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), abi.notifier_block_priority_offset);

    try std.testing.expectEqual(abi.notifier_block_size, @sizeOf(abi.NotifierBlock));
    try std.testing.expectEqual(abi.notifier_block_align, @alignOf(abi.NotifierBlock));
}

test "phase3 abi notifier priority increase layout remains reviewable" {
    const raw_size = (@sizeOf(usize) * 2) + (@sizeOf(i32) * 2);
    const expected_size = std.mem.alignForward(usize, raw_size, @alignOf(usize));

    try std.testing.expectEqual(expected_size, @sizeOf(abi.NotifierChainPriorityIncrease));
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(abi.NotifierChainPriorityIncrease));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.NotifierChainPriorityIncrease, "previous_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.NotifierChainPriorityIncrease, "current_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(abi.NotifierChainPriorityIncrease, "previous_priority"));
    try std.testing.expectEqual(
        @as(usize, (@sizeOf(usize) * 2) + @sizeOf(i32)),
        @offsetOf(abi.NotifierChainPriorityIncrease, "current_priority"),
    );
}

test "phase3 abi notifier priority relay reports first increase" {
    const fourth = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    const third = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&fourth),
        .priority = 2,
    };
    const second = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 4,
    };
    const first = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 6,
    };

    try std.testing.expect(!abi.chainHasNonincreasingPriority(&first));

    const increase = abi.firstChainPriorityIncrease(&first) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(usize, 2), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 3), increase.current_index);
    try std.testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 7), increase.current_priority);
}
