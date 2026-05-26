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

test "list view keeps the live bridge route over a detached adopter pair" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left_bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var right_bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var adopter_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var adopter_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left_bridge);
    first.prev = @intFromPtr(&head);
    left_bridge.next = @intFromPtr(&right_bridge);
    left_bridge.prev = @intFromPtr(&first);
    right_bridge.next = @intFromPtr(&tail);
    right_bridge.prev = @intFromPtr(&left_bridge);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right_bridge);

    adopter_left.next = @intFromPtr(&adopter_right);
    adopter_left.prev = @intFromPtr(&first);
    adopter_right.next = @intFromPtr(&tail);
    adopter_right.prev = @intFromPtr(&adopter_left);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &left_bridge, &right_bridge, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view reports the reused tail when bridge adoption keeps a stale backlink" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left_bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var right_bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var adopter_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var adopter_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&adopter_left);
    first.prev = @intFromPtr(&head);
    left_bridge.next = @intFromPtr(&right_bridge);
    left_bridge.prev = @intFromPtr(&first);
    right_bridge.next = @intFromPtr(&tail);
    right_bridge.prev = @intFromPtr(&left_bridge);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right_bridge);

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
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right_bridge)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "hlist view keeps the live bridge route over a detached adopter pair" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left_bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right_bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var adopter_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var adopter_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left_bridge);
    first.pprev = @intFromPtr(&head.first);
    left_bridge.next = @intFromPtr(&right_bridge);
    left_bridge.pprev = @intFromPtr(&first.next);
    right_bridge.next = @intFromPtr(&tail);
    right_bridge.pprev = @intFromPtr(&left_bridge.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right_bridge.next);

    adopter_left.next = @intFromPtr(&adopter_right);
    adopter_left.pprev = @intFromPtr(&first.next);
    adopter_right.next = @intFromPtr(&tail);
    adopter_right.pprev = @intFromPtr(&adopter_left.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &left_bridge, &right_bridge, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports the reused tail when bridge adoption keeps a stale prev-link" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left_bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right_bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var adopter_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var adopter_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&adopter_left);
    first.pprev = @intFromPtr(&head.first);
    left_bridge.next = @intFromPtr(&right_bridge);
    left_bridge.pprev = @intFromPtr(&first.next);
    right_bridge.next = @intFromPtr(&tail);
    right_bridge.pprev = @intFromPtr(&left_bridge.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right_bridge.next);

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
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right_bridge.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}