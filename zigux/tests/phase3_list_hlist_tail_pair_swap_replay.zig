const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListSequence(
    view: list_view.ListView,
    expected: []const *const list_view.ListHead,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const list_view.ListHead, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

fn expectHListSequence(
    view: hlist_view.HListView,
    expected: []const *const hlist_view.HListNode,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const hlist_view.HListNode, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "phase3 list/hlist tail pair swap replay keeps the live list tail order visible before the swap" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var left_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var right_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&right_tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&left_tail);
    middle.prev = @intFromPtr(&first);
    left_tail.next = @intFromPtr(&right_tail);
    left_tail.prev = @intFromPtr(&middle);
    right_tail.next = @intFromPtr(&head);
    right_tail.prev = @intFromPtr(&left_tail);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &right_tail), view.last());
    try expectListSequence(view, &.{ &first, &middle, &left_tail, &right_tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist tail pair swap replay reports the adopted list tail reorder before stale backlinks follow" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var left_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var right_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&left_tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&right_tail);
    middle.prev = @intFromPtr(&first);
    right_tail.next = @intFromPtr(&left_tail);
    right_tail.prev = @intFromPtr(&left_tail);
    left_tail.next = @intFromPtr(&head);
    left_tail.prev = @intFromPtr(&middle);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &middle, &right_tail, &left_tail });
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &left_tail), view.last());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left_tail)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist tail pair swap replay keeps the live hlist tail order visible before the swap" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&left_tail);
    middle.pprev = @intFromPtr(&first.next);
    left_tail.next = @intFromPtr(&right_tail);
    left_tail.pprev = @intFromPtr(&middle.next);
    right_tail.next = 0;
    right_tail.pprev = @intFromPtr(&left_tail.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &middle, &left_tail, &right_tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist tail pair swap replay reports the adopted hlist tail reorder before stale prev-links follow" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&right_tail);
    middle.pprev = @intFromPtr(&first.next);
    right_tail.next = @intFromPtr(&left_tail);
    right_tail.pprev = @intFromPtr(&left_tail.next);
    left_tail.next = 0;
    left_tail.pprev = @intFromPtr(&middle.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &middle, &right_tail, &left_tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left_tail.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
