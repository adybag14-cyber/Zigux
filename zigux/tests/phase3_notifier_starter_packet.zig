const std = @import("std");
const testing = std.testing;

const notifier_abi = @import("notifier_abi");

test "notifier starter packet keeps result bytes explicit" {
    try testing.expectEqual(@as(u32, 0), @intFromEnum(notifier_abi.NotifierResult.done));
    try testing.expectEqual(@as(u32, 1), @intFromEnum(notifier_abi.NotifierResult.ok));
    try testing.expectEqual(@as(u32, 2), @intFromEnum(notifier_abi.NotifierResult.stop));
}

test "notifier starter packet keeps layout anchors explicit" {
    try testing.expectEqual(@as(usize, 0), @offsetOf(notifier_abi.NotifierBlock, "notifier_call"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(notifier_abi.NotifierBlock, "next"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(notifier_abi.NotifierBlock, "priority"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(notifier_abi.ListHead));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @sizeOf(notifier_abi.HListHead));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(notifier_abi.HListNode));
}

test "notifier starter packet keeps nonincreasing priority chains accepted" {
    const third = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 1,
    };
    const second = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 4,
    };
    const first = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 4,
    };

    try testing.expect(notifier_abi.chainHasNonincreasingPriority(&first));
    try testing.expect(notifier_abi.firstChainPriorityIncrease(&first) == null);
}

test "notifier starter packet reports the first priority increase" {
    const third = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    const second = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 2,
    };
    const first = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 5,
    };

    try testing.expect(!notifier_abi.chainHasNonincreasingPriority(&first));
    const increase = notifier_abi.firstChainPriorityIncrease(&first) orelse {
        return error.TestUnexpectedResult;
    };
    try testing.expectEqual(@as(usize, 1), increase.previous_index);
    try testing.expectEqual(@as(usize, 2), increase.current_index);
    try testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try testing.expectEqual(@as(i32, 7), increase.current_priority);
}

test "notifier starter packet keeps list backlink drift explicit" {
    var head = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var first = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var second = notifier_abi.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&head);

    const breakage = notifier_abi.firstBrokenBacklink(&head) orelse {
        return error.TestUnexpectedResult;
    };
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try testing.expect(!notifier_abi.listHasConsistentBacklinks(&head));
}

test "notifier starter packet keeps hlist prev-link drift explicit" {
    var head = notifier_abi.HListHead{ .first = 0 };
    var first = notifier_abi.HListNode{ .next = 0, .pprev = 0 };
    var second = notifier_abi.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&head.first);

    const breakage = notifier_abi.firstBrokenPrevLink(&head) orelse {
        return error.TestUnexpectedResult;
    };
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try testing.expect(!notifier_abi.hlistHasConsistentPrevLinks(&head));
}
