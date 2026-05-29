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

test "list view reports stale interior shortcut backlink before restore" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var left = ListHead{ .next = 0, .prev = 0 };
    var skipped = ListHead{ .next = 0, .prev = 0 };
    var right = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&left);
    head.prev = @intFromPtr(&tail);
    left.next = @intFromPtr(&right);
    left.prev = @intFromPtr(&head);
    skipped.next = @intFromPtr(&right);
    skipped.prev = @intFromPtr(&left);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&skipped);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &left, &right, &tail });
    try std.testing.expectEqual(@as(?*const ListHead, &left), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&skipped)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    right.prev = @intFromPtr(&left);

    try expectListOrder(view, &.{ &left, &right, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist view reports stale interior shortcut prev-link before restore" {
    var head = HListHead{ .first = 0 };
    var left = HListNode{ .next = 0, .pprev = 0 };
    var skipped = HListNode{ .next = 0, .pprev = 0 };
    var right = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&left);
    left.next = @intFromPtr(&right);
    left.pprev = @intFromPtr(&head.first);
    skipped.next = @intFromPtr(&right);
    skipped.pprev = @intFromPtr(&left.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&skipped.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &left, &right, &tail });
    try std.testing.expectEqual(@as(?*const HListNode, &left), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&skipped.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    right.pprev = @intFromPtr(&left.next);

    try expectHListOrder(view, &.{ &left, &right, &tail });
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());
}
