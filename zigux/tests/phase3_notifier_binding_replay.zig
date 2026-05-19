const std = @import("std");
const testing = std.testing;

const notifier_abi = @import("notifier_abi");

test "phase3 notifier binding replay keeps result values and layout explicit" {
    try testing.expectEqual(@as(u32, 0), @intFromEnum(notifier_abi.NotifierResult.done));
    try testing.expectEqual(@as(u32, 1), @intFromEnum(notifier_abi.NotifierResult.ok));
    try testing.expectEqual(@as(u32, 2), @intFromEnum(notifier_abi.NotifierResult.stop));

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(notifier_abi.NotifierBlock));
    try testing.expectEqual(@as(usize, 0), @offsetOf(notifier_abi.NotifierBlock, "notifier_call"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(notifier_abi.NotifierBlock, "next"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(notifier_abi.NotifierBlock, "priority"));

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(notifier_abi.ListHead));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(notifier_abi.ListHead));
    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(notifier_abi.HListNode));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(notifier_abi.HListNode));
}

test "phase3 notifier binding replay keeps priority helpers aligned on public chains" {
    const tail = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 3,
    };
    const middle = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 5,
    };
    const head = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&middle),
        .priority = 5,
    };

    try testing.expect(notifier_abi.chainHasNonincreasingPriority(&head));
    try testing.expectEqual(
        @as(?notifier_abi.NotifierChainPriorityIncrease, null),
        notifier_abi.firstChainPriorityIncrease(&head),
    );

    const rising_tail = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    const rising_middle = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&rising_tail),
        .priority = 2,
    };
    const rising_head = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&rising_middle),
        .priority = 4,
    };

    try testing.expect(!notifier_abi.chainHasNonincreasingPriority(&rising_head));

    const increase = notifier_abi.firstChainPriorityIncrease(&rising_head) orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 1), increase.previous_index);
    try testing.expectEqual(@as(usize, 2), increase.current_index);
    try testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try testing.expectEqual(@as(i32, 7), increase.current_priority);
}

test "phase3 notifier binding replay keeps list and hlist link checks explicit" {
    var sentinel = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var first = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var second = notifier_abi.ListHead{ .next = 0, .prev = 0 };

    sentinel.next = @intFromPtr(&first);
    sentinel.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&sentinel);
    second.next = @intFromPtr(&sentinel);
    second.prev = @intFromPtr(&first);

    try testing.expect(notifier_abi.listHasConsistentBacklinks(&sentinel));

    second.prev = @intFromPtr(&sentinel);
    try testing.expect(!notifier_abi.listHasConsistentBacklinks(&sentinel));

    var hlist = notifier_abi.HListHead{ .first = 0 };
    var h_first = notifier_abi.HListNode{ .next = 0, .pprev = 0 };
    var h_second = notifier_abi.HListNode{ .next = 0, .pprev = 0 };

    hlist.first = @intFromPtr(&h_first);
    h_first.next = @intFromPtr(&h_second);
    h_first.pprev = @intFromPtr(&hlist.first);
    h_second.next = 0;
    h_second.pprev = @intFromPtr(&h_first.next);

    try testing.expect(notifier_abi.hlistHasConsistentPrevLinks(&hlist));

    h_second.pprev = @intFromPtr(&hlist.first);
    try testing.expect(!notifier_abi.hlistHasConsistentPrevLinks(&hlist));
}
