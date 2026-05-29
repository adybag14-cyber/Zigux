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

test "list view reports stale pivot backlink before restore" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var stable = ListHead{ .next = 0, .prev = 0 };
    var old_mid = ListHead{ .next = 0, .prev = 0 };
    var pivot = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&stable);
    head.prev = @intFromPtr(&tail);
    stable.next = @intFromPtr(&pivot);
    stable.prev = @intFromPtr(&head);
    old_mid.next = @intFromPtr(&tail);
    old_mid.prev = @intFromPtr(&stable);
    pivot.next = @intFromPtr(&tail);
    pivot.prev = @intFromPtr(&old_mid);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&pivot);

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &stable, &pivot, &tail });
    try std.testing.expectEqual(@as(?*const ListHead, &stable), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());

    const pivot_break = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), pivot_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&stable)), pivot_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_mid)), pivot_break.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    pivot.prev = @intFromPtr(&stable);

    try expectListOrder(view, &.{ &stable, &pivot, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist view reports stale pivot prev-link before restore" {
    var head = HListHead{ .first = 0 };
    var stable = HListNode{ .next = 0, .pprev = 0 };
    var old_mid = HListNode{ .next = 0, .pprev = 0 };
    var pivot = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&stable);
    stable.next = @intFromPtr(&pivot);
    stable.pprev = @intFromPtr(&head.first);
    old_mid.next = @intFromPtr(&tail);
    old_mid.pprev = @intFromPtr(&stable.next);
    pivot.next = @intFromPtr(&tail);
    pivot.pprev = @intFromPtr(&old_mid.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&pivot.next);

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &stable, &pivot, &tail });
    try std.testing.expectEqual(@as(?*const HListNode, &stable), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());

    const pivot_break = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), pivot_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&stable.next)), pivot_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_mid.next)), pivot_break.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    pivot.pprev = @intFromPtr(&stable.next);

    try expectHListOrder(view, &.{ &stable, &pivot, &tail });
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());
}
