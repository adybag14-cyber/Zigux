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

test "list view detects and clears head-handoff backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var new_first = ListHead{ .next = 0, .prev = 0 };
    var old_first = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&new_first);
    head.prev = @intFromPtr(&tail);
    new_first.next = @intFromPtr(&old_first);
    new_first.prev = @intFromPtr(&head);
    old_first.next = @intFromPtr(&tail);
    old_first.prev = @intFromPtr(&head);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&old_first);

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &new_first, &old_first, &tail });
    try std.testing.expectEqual(@as(?*const ListHead, &new_first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&new_first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    old_first.prev = @intFromPtr(&new_first);
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
    try expectListOrder(view, &.{ &new_first, &old_first, &tail });
}

test "hlist view detects and clears head-handoff prev-link repair" {
    var head = HListHead{ .first = 0 };
    var new_first = HListNode{ .next = 0, .pprev = 0 };
    var old_first = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&new_first);
    new_first.next = @intFromPtr(&old_first);
    new_first.pprev = @intFromPtr(&head.first);
    old_first.next = @intFromPtr(&tail);
    old_first.pprev = @intFromPtr(&head.first);
    tail.next = 0;
    tail.pprev = @intFromPtr(&old_first.next);

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &new_first, &old_first, &tail });
    try std.testing.expectEqual(@as(?*const HListNode, &new_first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&new_first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    old_first.pprev = @intFromPtr(&new_first.next);
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try expectHListOrder(view, &.{ &new_first, &old_first, &tail });
}
