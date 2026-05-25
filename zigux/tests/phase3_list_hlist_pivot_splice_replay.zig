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

test "list view keeps the live pivot route over a detached splice" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var splice_entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var splice_exit = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&pivot);
    left.prev = @intFromPtr(&first);
    pivot.next = @intFromPtr(&right);
    pivot.prev = @intFromPtr(&left);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&pivot);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    splice_entry.next = @intFromPtr(&splice_exit);
    splice_entry.prev = @intFromPtr(&pivot);
    splice_exit.next = @intFromPtr(&right);
    splice_exit.prev = @intFromPtr(&splice_entry);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &left, &pivot, &right, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view reports the adopted splice when the reused right link keeps a stale backlink" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var splice_entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var splice_exit = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&pivot);
    left.prev = @intFromPtr(&first);
    pivot.next = @intFromPtr(&splice_entry);
    pivot.prev = @intFromPtr(&left);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&pivot);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    splice_entry.next = @intFromPtr(&splice_exit);
    splice_entry.prev = @intFromPtr(&pivot);
    splice_exit.next = @intFromPtr(&right);
    splice_exit.prev = @intFromPtr(&splice_entry);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &left, &pivot, &splice_entry, &splice_exit, &right, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 5), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&splice_exit)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&pivot)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "hlist view keeps the live pivot route over a detached splice" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var splice_entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var splice_exit = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&pivot);
    left.pprev = @intFromPtr(&first.next);
    pivot.next = @intFromPtr(&right);
    pivot.pprev = @intFromPtr(&left.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&pivot.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    splice_entry.next = @intFromPtr(&splice_exit);
    splice_entry.pprev = @intFromPtr(&pivot.next);
    splice_exit.next = @intFromPtr(&right);
    splice_exit.pprev = @intFromPtr(&splice_entry.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &left, &pivot, &right, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports the adopted splice when the reused right link keeps a stale prev-link" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var splice_entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var splice_exit = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&pivot);
    left.pprev = @intFromPtr(&first.next);
    pivot.next = @intFromPtr(&splice_entry);
    pivot.pprev = @intFromPtr(&left.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&pivot.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    splice_entry.next = @intFromPtr(&splice_exit);
    splice_entry.pprev = @intFromPtr(&pivot.next);
    splice_exit.next = @intFromPtr(&right);
    splice_exit.pprev = @intFromPtr(&splice_entry.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &left, &pivot, &splice_entry, &splice_exit, &right, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 5), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&splice_exit.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&pivot.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
