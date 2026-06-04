const std = @import("std");

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;

fn expectListOrder(view: list_view.ListView, expected: []const *const ListHead) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const ListHead, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

fn expectHListOrder(view: hlist_view.HListView, expected: []const *const HListNode) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const HListNode, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "list view exposes and repairs middle excision backlink drift" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var middle = ListHead{ .next = 0, .prev = 0 };
    var last = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&last);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&last);
    middle.prev = @intFromPtr(&first);
    last.next = @intFromPtr(&head);
    last.prev = @intFromPtr(&middle);

    var view = list_view.ListView.init(&head);
    try expectListOrder(view, &.{ &first, &middle, &last });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &last), view.last());

    first.next = @intFromPtr(&last);
    middle.next = 0;
    middle.prev = 0;

    view = list_view.ListView.init(&head);
    try expectListOrder(view, &.{ &first, &last });
    const stale = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), stale.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), stale.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle)), stale.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &last), view.last());

    last.prev = @intFromPtr(&first);

    view = list_view.ListView.init(&head);
    try expectListOrder(view, &.{ &first, &last });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &last), view.last());
}

test "hlist view exposes and repairs middle excision prev-link drift" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var middle = HListNode{ .next = 0, .pprev = 0 };
    var last = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&last);
    middle.pprev = @intFromPtr(&first.next);
    last.next = 0;
    last.pprev = @intFromPtr(&middle.next);

    var view = hlist_view.HListView.init(&head);
    try expectHListOrder(view, &.{ &first, &middle, &last });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &last), view.last());

    first.next = @intFromPtr(&last);
    middle.next = 0;
    middle.pprev = 0;

    view = hlist_view.HListView.init(&head);
    try expectHListOrder(view, &.{ &first, &last });
    const stale = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), stale.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), stale.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), stale.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &last), view.last());

    last.pprev = @intFromPtr(&first.next);

    view = hlist_view.HListView.init(&head);
    try expectHListOrder(view, &.{ &first, &last });
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &last), view.last());
}
