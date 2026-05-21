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

test "list view follows a reordered live middle segment instead of a stale older route" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_order = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&right);
    first.prev = @intFromPtr(&head);
    right.next = @intFromPtr(&left);
    right.prev = @intFromPtr(&first);
    left.next = @intFromPtr(&tail);
    left.prev = @intFromPtr(&right);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&left);

    // Detached witness for the older first->left->right->tail ordering.
    stale_order.next = @intFromPtr(&right);
    stale_order.prev = @intFromPtr(&left);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &right, &left, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view reports a stale older middle ordering once the visible route is rewired through it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_order = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&stale_order);
    first.prev = @intFromPtr(&head);
    right.next = @intFromPtr(&left);
    right.prev = @intFromPtr(&first);
    left.next = @intFromPtr(&tail);
    left.prev = @intFromPtr(&right);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&left);

    stale_order.next = @intFromPtr(&tail);
    stale_order.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &stale_order, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&stale_order)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "hlist view follows a reordered live middle segment instead of a stale older route" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_order = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&right);
    first.pprev = @intFromPtr(&head.first);
    right.next = @intFromPtr(&left);
    right.pprev = @intFromPtr(&first.next);
    left.next = @intFromPtr(&tail);
    left.pprev = @intFromPtr(&right.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&left.next);

    stale_order.next = @intFromPtr(&right);
    stale_order.pprev = @intFromPtr(&left.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &right, &left, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports a stale older middle ordering once the visible route is rewired through it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_order = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&stale_order);
    first.pprev = @intFromPtr(&head.first);
    right.next = @intFromPtr(&left);
    right.pprev = @intFromPtr(&first.next);
    left.next = @intFromPtr(&tail);
    left.pprev = @intFromPtr(&right.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&left.next);

    stale_order.next = @intFromPtr(&tail);
    stale_order.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &stale_order, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&stale_order.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
