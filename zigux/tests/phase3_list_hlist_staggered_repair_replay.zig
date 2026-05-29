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

test "list view reports staggered backlink repairs in traversal order" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var middle = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&tail);
    middle.prev = @intFromPtr(&head);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&first);

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &first, &middle, &tail });
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());

    const first_break = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), first_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), first_break.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    middle.prev = @intFromPtr(&first);

    const second_break = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), second_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle)), second_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), second_break.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    tail.prev = @intFromPtr(&middle);
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
    try expectListOrder(view, &.{ &first, &middle, &tail });
}

test "hlist view reports staggered prev-link repairs in traversal order" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var middle = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&tail);
    middle.pprev = @intFromPtr(&head.first);
    tail.next = 0;
    tail.pprev = @intFromPtr(&first.next);

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &first, &middle, &tail });
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());

    const first_break = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), first_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), first_break.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    middle.pprev = @intFromPtr(&first.next);

    const second_break = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), second_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), second_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), second_break.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    tail.pprev = @intFromPtr(&middle.next);
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try expectHListOrder(view, &.{ &first, &middle, &tail });
}
