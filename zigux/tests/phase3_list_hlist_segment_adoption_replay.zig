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

test "list view keeps the live middle segment over a detached adopter segment" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var adopter_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var adopter_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&right);
    left.prev = @intFromPtr(&first);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    adopter_left.next = @intFromPtr(&adopter_right);
    adopter_left.prev = @intFromPtr(&first);
    adopter_right.next = @intFromPtr(&tail);
    adopter_right.prev = @intFromPtr(&adopter_left);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &left, &right, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view reports the stale tail backlink when a middle adopter segment takes the forward route first" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var adopter_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var adopter_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&adopter_left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&right);
    left.prev = @intFromPtr(&first);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    adopter_left.next = @intFromPtr(&adopter_right);
    adopter_left.prev = @intFromPtr(&first);
    adopter_right.next = @intFromPtr(&tail);
    adopter_right.prev = @intFromPtr(&adopter_left);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &adopter_left, &adopter_right, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&adopter_right)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "hlist view keeps the live middle segment over a detached adopter segment" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var adopter_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var adopter_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&right);
    left.pprev = @intFromPtr(&first.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    adopter_left.next = @intFromPtr(&adopter_right);
    adopter_left.pprev = @intFromPtr(&first.next);
    adopter_right.next = @intFromPtr(&tail);
    adopter_right.pprev = @intFromPtr(&adopter_left.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &left, &right, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports the stale tail prev-link when a middle adopter segment takes the forward route first" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var adopter_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var adopter_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&adopter_left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&right);
    left.pprev = @intFromPtr(&first.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    adopter_left.next = @intFromPtr(&adopter_right);
    adopter_left.pprev = @intFromPtr(&first.next);
    adopter_right.next = @intFromPtr(&tail);
    adopter_right.pprev = @intFromPtr(&adopter_left.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &adopter_left, &adopter_right, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&adopter_right.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
