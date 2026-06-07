const std = @import("std");

const notifier_abi = @import("notifier_abi");

test "phase3 abi notifier list length treats null and sentinel-only lists distinctly" {
    var empty = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    empty.next = @intFromPtr(&empty);
    empty.prev = @intFromPtr(&empty);

    try std.testing.expect(!notifier_abi.listIsEmpty(null));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.listLength(null));

    try std.testing.expect(notifier_abi.listIsEmpty(&empty));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.listLength(&empty));

    empty.prev = 0;
    try std.testing.expect(!notifier_abi.listIsEmpty(&empty));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.listLength(&empty));
}

test "phase3 abi notifier list length follows the forward next chain to the sentinel" {
    var head = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var first = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var second = notifier_abi.ListHead{ .next = 0, .prev = 0 };
    var third = notifier_abi.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&third);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&head);
    third.prev = @intFromPtr(&second);

    try std.testing.expect(!notifier_abi.listIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 3), notifier_abi.listLength(&head));

    second.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&second);
    try std.testing.expectEqual(@as(usize, 2), notifier_abi.listLength(&head));
}

test "phase3 abi notifier hlist length and emptiness keep null head behavior explicit" {
    const empty = notifier_abi.HListHead{ .first = 0 };

    try std.testing.expect(!notifier_abi.hlistIsEmpty(null));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.hlistLength(null));
    try std.testing.expect(!notifier_abi.hlistTailNextIsNull(null));

    try std.testing.expect(notifier_abi.hlistIsEmpty(&empty));
    try std.testing.expectEqual(@as(usize, 0), notifier_abi.hlistLength(&empty));
    try std.testing.expect(notifier_abi.hlistTailNextIsNull(&empty));
}

test "phase3 abi notifier hlist length walks next links and confirms the tail" {
    var head = notifier_abi.HListHead{ .first = 0 };
    var first = notifier_abi.HListNode{ .next = 0, .pprev = 0 };
    var second = notifier_abi.HListNode{ .next = 0, .pprev = 0 };
    var third = notifier_abi.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = 0;
    third.pprev = @intFromPtr(&second.next);

    try std.testing.expect(!notifier_abi.hlistIsEmpty(&head));
    try std.testing.expectEqual(@as(usize, 3), notifier_abi.hlistLength(&head));
    try std.testing.expect(notifier_abi.hlistTailNextIsNull(&head));

    first.next = 0;
    try std.testing.expectEqual(@as(usize, 1), notifier_abi.hlistLength(&head));
    try std.testing.expect(notifier_abi.hlistTailNextIsNull(&head));
}
