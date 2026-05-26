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

test "phase3 list/hlist bridge pair splice replay keeps the live list bridge pair visible while a detached splice pair stays off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var splice_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var splice_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&bridge_left);
    left.prev = @intFromPtr(&first);
    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.prev = @intFromPtr(&left);
    bridge_right.next = @intFromPtr(&tail);
    bridge_right.prev = @intFromPtr(&bridge_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge_right);

    splice_left.next = @intFromPtr(&splice_right);
    splice_left.prev = @intFromPtr(&bridge_left);
    splice_right.next = @intFromPtr(&tail);
    splice_right.prev = @intFromPtr(&splice_left);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &left, &bridge_left, &bridge_right, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist bridge pair splice replay reports the reused tail list node when the splice pair replaces the right bridge early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var splice_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var splice_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&bridge_left);
    left.prev = @intFromPtr(&first);
    bridge_left.next = @intFromPtr(&splice_left);
    bridge_left.prev = @intFromPtr(&left);
    bridge_right.next = @intFromPtr(&tail);
    bridge_right.prev = @intFromPtr(&bridge_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge_right);

    splice_left.next = @intFromPtr(&splice_right);
    splice_left.prev = @intFromPtr(&bridge_left);
    splice_right.next = @intFromPtr(&tail);
    splice_right.prev = @intFromPtr(&splice_left);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &left, &bridge_left, &splice_left, &splice_right, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 5), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&splice_right)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_right)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist bridge pair splice replay keeps the live hlist bridge pair visible while a detached splice pair stays off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var splice_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var splice_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&bridge_left);
    left.pprev = @intFromPtr(&first.next);
    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.pprev = @intFromPtr(&left.next);
    bridge_right.next = @intFromPtr(&tail);
    bridge_right.pprev = @intFromPtr(&bridge_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge_right.next);

    splice_left.next = @intFromPtr(&splice_right);
    splice_left.pprev = @intFromPtr(&bridge_left.next);
    splice_right.next = @intFromPtr(&tail);
    splice_right.pprev = @intFromPtr(&splice_left.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &left, &bridge_left, &bridge_right, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist bridge pair splice replay reports the reused tail hlist node when the splice pair replaces the right bridge early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var splice_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var splice_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&bridge_left);
    left.pprev = @intFromPtr(&first.next);
    bridge_left.next = @intFromPtr(&splice_left);
    bridge_left.pprev = @intFromPtr(&left.next);
    bridge_right.next = @intFromPtr(&tail);
    bridge_right.pprev = @intFromPtr(&bridge_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge_right.next);

    splice_left.next = @intFromPtr(&splice_right);
    splice_left.pprev = @intFromPtr(&bridge_left.next);
    splice_right.next = @intFromPtr(&tail);
    splice_right.pprev = @intFromPtr(&splice_left.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &left, &bridge_left, &splice_left, &splice_right, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 5), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&splice_right.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_right.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
