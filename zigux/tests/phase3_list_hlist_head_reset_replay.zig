const std = @import("std");

const hlist_view = @import("hlist_view");
const list_view = @import("list_view");

const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;
const ListHead = list_view.ListHead;
const ListView = list_view.ListView;

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

test "list view reports stale head prev after visible tail handoff" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var detached = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&detached);
    first.next = @intFromPtr(&tail);
    first.prev = @intFromPtr(&head);
    detached.next = @intFromPtr(&head);
    detached.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&first);

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &first, &tail });
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &detached), view.last());

    const head_break = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), head_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail)), head_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached)), head_break.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    head.prev = @intFromPtr(&tail);

    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
    try expectListOrder(view, &.{ &first, &tail });
}

test "hlist view reports stale head first before reset to shorter chain" {
    var head = HListHead{ .first = 0 };
    var stale = HListNode{ .next = 0, .pprev = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&stale);
    stale.next = @intFromPtr(&tail);
    stale.pprev = @intFromPtr(&first.next);
    first.next = @intFromPtr(&tail);
    first.pprev = @intFromPtr(&head.first);
    tail.next = 0;
    tail.pprev = @intFromPtr(&first.next);

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &stale, &tail });
    try std.testing.expectEqual(@as(?*const HListNode, &stale), view.first());
    try std.testing.expect(!view.firstPprevMatchesHead());

    const stale_break = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), stale_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), stale_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), stale_break.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    head.first = @intFromPtr(&first);

    try expectHListOrder(view, &.{ &first, &tail });
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());
}
