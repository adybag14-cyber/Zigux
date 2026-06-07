const std = @import("std");

const notifier_abi = @import("notifier_abi");

fn initEmptyList(head: *notifier_abi.ListHead) void {
    head.next = @intFromPtr(head);
    head.prev = @intFromPtr(head);
}

test "phase3 notifier list metrics distinguish absent empty and populated heads" {
    try std.testing.expect(!notifier_abi.listIsEmpty(null));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.listLength(null));

    var head = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    initEmptyList(&head);

    try std.testing.expect(notifier_abi.listIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.listLength(&head));

    var first = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var second = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    try std.testing.expect(!notifier_abi.listIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 2), notifier_abi.listLength(&head));
}

test "phase3 notifier list metrics stop at the sentinel before stale tail links" {
    var head = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var first = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var stale_tail = notifier_abi.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&first);
    first.next = @intFromPtr(&head);
    first.prev = @intFromPtr(&head);
    stale_tail.next = @intFromPtr(&head);
    stale_tail.prev = @intFromPtr(&first);

    try std.testing.expect(!notifier_abi.listIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 1), notifier_abi.listLength(&head));
}

test "phase3 notifier hlist metrics distinguish absent empty and populated heads" {
    try std.testing.expect(!notifier_abi.hlistIsEmpty(null));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.hlistLength(null));
    try std.testing.expect(!notifier_abi.hlistTailNextIsNull(null));

    var head = notifier_abi.HListHead{ .first = 0 };
    try std.testing.expect(notifier_abi.hlistIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.hlistLength(&head));
    try std.testing.expect(notifier_abi.hlistTailNextIsNull(&head));

    var first = notifier_abi.HListNode{ .next = 0, .pprev = 0 };
    var second = notifier_abi.HListNode{ .next = 0, .pprev = 0 };
    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    try std.testing.expect(!notifier_abi.hlistIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 2), notifier_abi.hlistLength(&head));
    try std.testing.expect(notifier_abi.hlistTailNextIsNull(&head));
}

test "phase3 notifier hlist metrics count through prev-link drift without hiding termination" {
    var head = notifier_abi.HListHead{ .first = 0 };
    var first = notifier_abi.HListNode{ .next = 0, .pprev = 0 };
    var second = notifier_abi.HListNode{ .next = 0, .pprev = 0 };
    var leaked = notifier_abi.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&leaked);
    second.pprev = @intFromPtr(&first.next);
    leaked.next = 0;
    leaked.pprev = @intFromPtr(&head.first);

    try std.testing.expect(!notifier_abi.hlistIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 3), notifier_abi.hlistLength(&head));
    try std.testing.expect(notifier_abi.hlistTailNextIsNull(&head));
}
