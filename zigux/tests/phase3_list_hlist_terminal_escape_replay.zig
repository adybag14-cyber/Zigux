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

test "list view reports terminal null escape before head sentinel is restored" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&tail);
    second.prev = @intFromPtr(&first);
    tail.next = 0;
    tail.prev = @intFromPtr(&second);

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &first, &second, &tail });
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());

    const terminal_break = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), terminal_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail)), terminal_break.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), terminal_break.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    tail.next = @intFromPtr(&head);

    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
    try expectListOrder(view, &.{ &first, &second, &tail });
}

test "hlist view reports escaped successor prev-link before detach" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var escaped = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&tail);
    second.pprev = @intFromPtr(&first.next);
    tail.next = @intFromPtr(&escaped);
    tail.pprev = @intFromPtr(&second.next);
    escaped.next = 0;
    escaped.pprev = @intFromPtr(&head.first);

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &first, &second, &tail, &escaped });
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());

    const escaped_break = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), escaped_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail.next)), escaped_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), escaped_break.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    escaped.pprev = @intFromPtr(&tail.next);

    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try expectHListOrder(view, &.{ &first, &second, &tail, &escaped });

    tail.next = 0;

    try expectHListOrder(view, &.{ &first, &second, &tail });
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());
}
