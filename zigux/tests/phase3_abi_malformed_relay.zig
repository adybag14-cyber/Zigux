const std = @import("std");

const abi = @import("abi_bindings");

test "phase3 abi malformed relay reports the first notifier priority increase" {
    const rising_tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 8,
    };
    const rising_head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&rising_tail),
        .priority = 2,
    };
    const increase = abi.firstChainPriorityIncrease(&rising_head) orelse return error.TestUnexpectedResult;

    try std.testing.expect(!abi.chainHasNonincreasingPriority(&rising_head));
    try std.testing.expectEqual(@as(usize, 0), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 1), increase.current_index);
    try std.testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 8), increase.current_priority);
}

test "phase3 abi malformed relay reports the first broken list backlink" {
    var list_head = abi.ListHead{ .next = 0, .prev = 0 };
    var list_first = abi.ListHead{ .next = 0, .prev = 0 };
    var list_second = abi.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_second);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_head);
    list_second.prev = @intFromPtr(&list_head);

    const breakage = abi.firstBrokenBacklink(&list_head) orelse return error.TestUnexpectedResult;

    try std.testing.expect(!abi.listHasConsistentBacklinks(&list_head));
    try std.testing.expect(!abi.listHasConsistentBacklinks(null));
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), breakage.actual_prev);
}

test "phase3 abi malformed relay reports the first broken hlist prev-link" {
    var hlist_head = abi.HListHead{ .first = 0 };
    var hlist_first = abi.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = abi.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_head.first);

    const breakage = abi.firstBrokenPrevLink(&hlist_head) orelse return error.TestUnexpectedResult;

    try std.testing.expect(!abi.hlistHasConsistentPrevLinks(&hlist_head));
    try std.testing.expect(!abi.hlistHasConsistentPrevLinks(null));
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_head.first)), breakage.actual_pprev);
}
