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

test "list view exposes alternating stale backlinks after partial repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };
    var third = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&tail);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&tail);
    third.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&third);

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &first, &second, &third, &tail });
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());

    const first_break = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), first_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail)), first_break.actual_prev);

    first.prev = @intFromPtr(&head);

    const later_break = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), later_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second)), later_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), later_break.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    third.prev = @intFromPtr(&second);
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
    try expectListOrder(view, &.{ &first, &second, &third, &tail });
}

test "hlist view exposes alternating stale prev-links after partial repair" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };
    var third = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&tail.next);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = @intFromPtr(&tail);
    third.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&third.next);

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &first, &second, &third, &tail });
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());

    const first_break = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), first_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail.next)), first_break.actual_pprev);

    first.pprev = @intFromPtr(&head.first);
    try std.testing.expect(view.firstPprevMatchesHead());

    const later_break = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), later_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second.next)), later_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), later_break.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    third.pprev = @intFromPtr(&second.next);
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try expectHListOrder(view, &.{ &first, &second, &third, &tail });
}
