const std = @import("std");
const abi = @import("abi.zig");
const notifier_abi = @import("notifier_abi.zig");

pub const NotifierBlock = abi.NotifierBlock;
pub const NotifierChainPriorityIncrease = abi.NotifierChainPriorityIncrease;
pub const ListHead = abi.ListHead;
pub const HListHead = abi.HListHead;
pub const HListNode = abi.HListNode;
pub const ListBackLinkBreak = abi.ListBackLinkBreak;
pub const HListPrevLinkBreak = abi.HListPrevLinkBreak;

pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {
    return notifier_abi.chainHasNonincreasingPriority(head);
}

pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?NotifierChainPriorityIncrease {
    return notifier_abi.firstChainPriorityIncrease(head);
}

pub fn listIsEmpty(head: ?*const ListHead) bool {
    return notifier_abi.listIsEmpty(head);
}

pub fn listLength(head: ?*const ListHead) usize {
    return notifier_abi.listLength(head);
}

pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {
    return notifier_abi.listHasConsistentBacklinks(head);
}

pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {
    return notifier_abi.firstBrokenBacklink(head);
}

pub fn hlistFirstPprevMatchesHead(head: ?*const HListHead) bool {
    return notifier_abi.firstPprevMatchesHead(head);
}

pub fn hlistLength(head: ?*const HListHead) usize {
    return notifier_abi.hlistLength(head);
}

pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {
    return notifier_abi.hlistHasConsistentPrevLinks(head);
}

pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {
    return notifier_abi.firstBrokenPrevLink(head);
}

pub fn hlistTailNextIsNull(head: ?*const HListHead) bool {
    return notifier_abi.tailNextIsNull(head);
}

test "notifier/list shape relay keeps empty list and hlist witnesses explicit" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_head);
    list_head.prev = @intFromPtr(&list_head);

    try std.testing.expect(listIsEmpty(&list_head));
    try std.testing.expectEqual(@as(usize, 0), listLength(&list_head));
    try std.testing.expectEqual(@as(bool, false), listIsEmpty(null));
    try std.testing.expectEqual(@as(usize, 0), listLength(null));
    try std.testing.expectEqual(@as(?ListBackLinkBreak, null), firstBrokenBacklink(&list_head));
    try std.testing.expect(listHasConsistentBacklinks(&list_head));

    const hlist_head = HListHead{ .first = 0 };
    try std.testing.expect(hlistFirstPprevMatchesHead(&hlist_head));
    try std.testing.expectEqual(@as(usize, 0), hlistLength(&hlist_head));
    try std.testing.expectEqual(@as(usize, 0), hlistLength(null));
    try std.testing.expect(hlistTailNextIsNull(&hlist_head));
    try std.testing.expectEqual(@as(?HListPrevLinkBreak, null), firstBrokenPrevLink(&hlist_head));
    try std.testing.expect(hlistHasConsistentPrevLinks(&hlist_head));
}

test "notifier/list shape relay keeps bounded list and hlist witnesses explicit" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_first = ListHead{ .next = 0, .prev = 0 };
    var list_second = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_second);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_head);
    list_second.prev = @intFromPtr(&list_first);

    try std.testing.expect(!listIsEmpty(&list_head));
    try std.testing.expectEqual(@as(usize, 2), listLength(&list_head));
    try std.testing.expect(listHasConsistentBacklinks(&list_head));
    try std.testing.expectEqual(@as(?ListBackLinkBreak, null), firstBrokenBacklink(&list_head));

    var hlist_head = HListHead{ .first = 0 };
    var hlist_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_first.next);

    try std.testing.expect(hlistFirstPprevMatchesHead(&hlist_head));
    try std.testing.expectEqual(@as(usize, 2), hlistLength(&hlist_head));
    try std.testing.expect(hlistHasConsistentPrevLinks(&hlist_head));
    try std.testing.expectEqual(@as(?HListPrevLinkBreak, null), firstBrokenPrevLink(&hlist_head));
    try std.testing.expect(hlistTailNextIsNull(&hlist_head));
}

test "notifier/list shape relay reports malformed notifier, list, and hlist witnesses" {
    const rising_tail = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 8,
    };
    const rising_head = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&rising_tail),
        .priority = 2,
    };
    const increase = firstChainPriorityIncrease(&rising_head) orelse return error.TestUnexpectedResult;

    try std.testing.expect(!chainHasNonincreasingPriority(&rising_head));
    try std.testing.expectEqual(@as(usize, 0), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 1), increase.current_index);
    try std.testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 8), increase.current_priority);

    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_first = ListHead{ .next = 0, .prev = 0 };
    var list_second = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_second);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_head);
    list_second.prev = @intFromPtr(&list_head);

    const list_break = firstBrokenBacklink(&list_head) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!listHasConsistentBacklinks(&list_head));
    try std.testing.expectEqual(@as(usize, 1), list_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_first)), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_break.actual_prev);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_head.first);

    const hlist_break = firstBrokenPrevLink(&hlist_head) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!hlistHasConsistentPrevLinks(&hlist_head));
    try std.testing.expectEqual(@as(usize, 1), hlist_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_first.next)), hlist_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_head.first)), hlist_break.actual_pprev);
}
