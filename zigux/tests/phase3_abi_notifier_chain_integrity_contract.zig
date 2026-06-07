const std = @import("std");

const abi = @import("abi_bindings");

fn ptrToInt(ptr: anytype) usize {
    return @intFromPtr(ptr);
}

test "notifier chain priority relays report the first increasing edge" {
    var third = abi.NotifierBlock{
        .notifier_call = 0x30,
        .next = 0,
        .priority = 20,
    };
    var second = abi.NotifierBlock{
        .notifier_call = 0x20,
        .next = ptrToInt(&third),
        .priority = 10,
    };
    var first = abi.NotifierBlock{
        .notifier_call = 0x10,
        .next = ptrToInt(&second),
        .priority = 30,
    };

    try std.testing.expect(!abi.chainHasNonincreasingPriority(&first));

    const increase = abi.firstChainPriorityIncrease(&first) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 2), increase.current_index);
    try std.testing.expectEqual(@as(i32, 10), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 20), increase.current_priority);
}

test "notifier chain priority relays accept empty singleton and descending chains" {
    var third = abi.NotifierBlock{
        .notifier_call = 0x33,
        .next = 0,
        .priority = -10,
    };
    var second = abi.NotifierBlock{
        .notifier_call = 0x22,
        .next = ptrToInt(&third),
        .priority = 0,
    };
    var first = abi.NotifierBlock{
        .notifier_call = 0x11,
        .next = ptrToInt(&second),
        .priority = 5,
    };
    var singleton = abi.NotifierBlock{
        .notifier_call = 0x44,
        .next = 0,
        .priority = 99,
    };

    try std.testing.expect(abi.chainHasNonincreasingPriority(null));
    try std.testing.expect(abi.chainHasNonincreasingPriority(&singleton));
    try std.testing.expect(abi.chainHasNonincreasingPriority(&first));
    try std.testing.expectEqual(@as(?abi.ChainPriorityIncrease, null), abi.firstChainPriorityIncrease(null));
    try std.testing.expectEqual(@as(?abi.ChainPriorityIncrease, null), abi.firstChainPriorityIncrease(&singleton));
    try std.testing.expectEqual(@as(?abi.ChainPriorityIncrease, null), abi.firstChainPriorityIncrease(&first));
}

test "list backlink relay reports the first broken prev pointer" {
    var sentinel = abi.ListHead{ .next = 0, .prev = 0 };
    var first = abi.ListHead{ .next = 0, .prev = 0 };
    var second = abi.ListHead{ .next = 0, .prev = 0 };
    sentinel.next = ptrToInt(&first);
    sentinel.prev = ptrToInt(&second);
    first.next = ptrToInt(&second);
    first.prev = ptrToInt(&sentinel);
    second.next = ptrToInt(&sentinel);
    second.prev = ptrToInt(&sentinel);

    try std.testing.expect(!abi.listHasConsistentBacklinks(&sentinel));

    const broken = abi.firstBrokenBacklink(&sentinel) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), broken.current_index);
    try std.testing.expectEqual(ptrToInt(&first), broken.expected_prev);
    try std.testing.expectEqual(ptrToInt(&sentinel), broken.actual_prev);

    second.prev = ptrToInt(&first);
    try std.testing.expect(abi.listHasConsistentBacklinks(&sentinel));
    try std.testing.expectEqual(@as(?abi.ListBackLinkBreak, null), abi.firstBrokenBacklink(&sentinel));
}

test "hlist previous-link relays distinguish head and interior breaks" {
    var head = abi.HListHead{ .first = 0 };
    var first = abi.HListNode{ .next = 0, .pprev = 0 };
    var second = abi.HListNode{ .next = 0, .pprev = 0 };
    head.first = ptrToInt(&first);
    first.next = ptrToInt(&second);
    first.pprev = ptrToInt(&head.first);
    second.pprev = ptrToInt(&head.first);

    try std.testing.expect(abi.hlistFirstPprevMatchesHead(&head));
    try std.testing.expect(!abi.hlistHasConsistentPrevLinks(&head));

    const broken = abi.firstBrokenPrevLink(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), broken.current_index);
    try std.testing.expectEqual(ptrToInt(&first.next), broken.expected_pprev);
    try std.testing.expectEqual(ptrToInt(&head.first), broken.actual_pprev);

    second.pprev = ptrToInt(&first.next);
    try std.testing.expect(abi.hlistHasConsistentPrevLinks(&head));
    try std.testing.expectEqual(@as(?abi.HListPrevLinkBreak, null), abi.firstBrokenPrevLink(&head));

    first.pprev = 0;
    try std.testing.expect(!abi.hlistFirstPprevMatchesHead(&head));
    try std.testing.expect(!abi.hlistHasConsistentPrevLinks(&head));
}
