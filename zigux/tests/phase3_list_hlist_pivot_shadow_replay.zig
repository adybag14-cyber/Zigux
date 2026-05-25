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

test "list view follows a live pivot route instead of a detached shadow pair" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&pivot);
    first.prev = @intFromPtr(&head);
    pivot.next = @intFromPtr(&right);
    pivot.prev = @intFromPtr(&first);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&pivot);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    shadow_pivot.next = @intFromPtr(&shadow_right);
    shadow_pivot.prev = @intFromPtr(&first);
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.prev = @intFromPtr(&shadow_pivot);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &pivot, &right, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view reports a pivot shadow once the visible route adopts it early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&shadow_pivot);
    first.prev = @intFromPtr(&head);
    pivot.next = @intFromPtr(&right);
    pivot.prev = @intFromPtr(&first);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&pivot);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    shadow_pivot.next = @intFromPtr(&shadow_right);
    shadow_pivot.prev = @intFromPtr(&first);
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.prev = @intFromPtr(&shadow_pivot);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &shadow_pivot, &shadow_right, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_right)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "hlist view follows a live pivot route instead of a detached shadow pair" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&pivot);
    first.pprev = @intFromPtr(&head.first);
    pivot.next = @intFromPtr(&right);
    pivot.pprev = @intFromPtr(&first.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&pivot.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    shadow_pivot.next = @intFromPtr(&shadow_right);
    shadow_pivot.pprev = @intFromPtr(&first.next);
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.pprev = @intFromPtr(&shadow_pivot.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &pivot, &right, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports a pivot shadow once the visible route adopts it early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&shadow_pivot);
    first.pprev = @intFromPtr(&head.first);
    pivot.next = @intFromPtr(&right);
    pivot.pprev = @intFromPtr(&first.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&pivot.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    shadow_pivot.next = @intFromPtr(&shadow_right);
    shadow_pivot.pprev = @intFromPtr(&first.next);
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.pprev = @intFromPtr(&shadow_pivot.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &shadow_pivot, &shadow_right, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_right.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
