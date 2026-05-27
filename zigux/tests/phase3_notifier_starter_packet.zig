const std = @import("std");
const testing = std.testing;

const notifier_abi = @import("notifier_abi");
const notifier_view = @import("notifier_view");

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

test "notifier starter packet keeps an empty chain reviewable" {
    const view = notifier_view.NotifierView.init(null);

    try testing.expect(view.isEmpty());
    try testing.expectEqual(@as(usize, 0), view.len());
    try testing.expectEqual(@as(?*const notifier_view.NotifierBlock, null), view.first());
    try testing.expectEqual(@as(?*const notifier_view.NotifierBlock, null), view.last());
    try testing.expect(view.hasNonincreasingPriority());
    try testing.expect(view.allCallbacksPresent());
}

test "notifier starter packet keeps nonincreasing priority chains accepted" {
    const tail = notifier_view.NotifierBlock{
        .notifier_call = 0x3000,
        .next = 0,
        .priority = 2,
    };
    const middle = notifier_view.NotifierBlock{
        .notifier_call = 0x2000,
        .next = @intFromPtr(&tail),
        .priority = 4,
    };
    const head = notifier_view.NotifierBlock{
        .notifier_call = 0x1000,
        .next = @intFromPtr(&middle),
        .priority = 4,
    };

    const view = notifier_view.NotifierView.init(&head);
    try testing.expect(!view.isEmpty());
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expectEqual(@as(?*const notifier_view.NotifierBlock, &head), view.first());
    try testing.expectEqual(@as(?*const notifier_view.NotifierBlock, &tail), view.last());
    try testing.expect(view.hasNonincreasingPriority());
    try testing.expect(view.allCallbacksPresent());
    try testing.expectEqual(@as(?usize, null), view.firstNullCallbackIndex());
    try testing.expectEqual(@as(?notifier_view.PriorityIncrease, null), view.firstPriorityIncrease());
}

test "notifier starter packet reports the first null callback witness" {
    const tail = notifier_view.NotifierBlock{
        .notifier_call = 0x3000,
        .next = 0,
        .priority = 1,
    };
    const middle = notifier_view.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 2,
    };
    const head = notifier_view.NotifierBlock{
        .notifier_call = 0x1000,
        .next = @intFromPtr(&middle),
        .priority = 3,
    };

    const view = notifier_view.NotifierView.init(&head);
    try testing.expect(!view.allCallbacksPresent());
    try testing.expectEqual(@as(?usize, 1), view.firstNullCallbackIndex());
}

test "notifier starter packet reports the first priority increase" {
    const tail = notifier_view.NotifierBlock{
        .notifier_call = 0x3000,
        .next = 0,
        .priority = 8,
    };
    const middle = notifier_view.NotifierBlock{
        .notifier_call = 0x2000,
        .next = @intFromPtr(&tail),
        .priority = 2,
    };
    const head = notifier_view.NotifierBlock{
        .notifier_call = 0x1000,
        .next = @intFromPtr(&middle),
        .priority = 4,
    };

    const increase = notifier_view.NotifierView.init(&head).firstPriorityIncrease().?;
    try testing.expect(!notifier_view.NotifierView.init(&head).hasNonincreasingPriority());
    try testing.expectEqual(@as(usize, 1), increase.previous_index);
    try testing.expectEqual(@as(usize, 2), increase.current_index);
    try testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try testing.expectEqual(@as(i32, 8), increase.current_priority);
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
