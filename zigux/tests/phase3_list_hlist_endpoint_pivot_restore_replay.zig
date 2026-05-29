const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

fn expectListOrder(view: ListView, expected: []const *const ListHead) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const ListHead, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

fn expectHListOrder(view: HListView, expected: []const *const HListNode) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const HListNode, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "list view reports stale endpoint pivot backlink before restore" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var stable = ListHead{ .next = 0, .prev = 0 };
    var old_tail = ListHead{ .next = 0, .prev = 0 };
    var pivot_tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&stable);
    head.prev = @intFromPtr(&pivot_tail);
    stable.next = @intFromPtr(&pivot_tail);
    stable.prev = @intFromPtr(&head);
    old_tail.next = @intFromPtr(&head);
    old_tail.prev = @intFromPtr(&stable);
    pivot_tail.next = @intFromPtr(&head);
    pivot_tail.prev = @intFromPtr(&old_tail);

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &stable, &pivot_tail });
    try std.testing.expectEqual(@as(?*const ListHead, &stable), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &pivot_tail), view.last());

    const tail_break = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), tail_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&stable)), tail_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_tail)), tail_break.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    pivot_tail.prev = @intFromPtr(&stable);

    try expectListOrder(view, &.{ &stable, &pivot_tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist view reports stale endpoint pivot prev-link before restore" {
    var head = HListHead{ .first = 0 };
    var stable = HListNode{ .next = 0, .pprev = 0 };
    var old_tail = HListNode{ .next = 0, .pprev = 0 };
    var pivot_tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&stable);
    stable.next = @intFromPtr(&pivot_tail);
    stable.pprev = @intFromPtr(&head.first);
    old_tail.next = 0;
    old_tail.pprev = @intFromPtr(&stable.next);
    pivot_tail.next = 0;
    pivot_tail.pprev = @intFromPtr(&old_tail.next);

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &stable, &pivot_tail });
    try std.testing.expectEqual(@as(?*const HListNode, &stable), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());

    const tail_break = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), tail_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&stable.next)), tail_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_tail.next)), tail_break.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    pivot_tail.pprev = @intFromPtr(&stable.next);

    try expectHListOrder(view, &.{ &stable, &pivot_tail });
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());
}
