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

test "list view detects and clears stale sentinel-tail backlink" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var old_tail = ListHead{ .next = 0, .prev = 0 };
    var new_tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&new_tail);
    first.next = @intFromPtr(&old_tail);
    first.prev = @intFromPtr(&head);
    old_tail.next = @intFromPtr(&new_tail);
    old_tail.prev = @intFromPtr(&first);
    new_tail.next = @intFromPtr(&head);
    new_tail.prev = @intFromPtr(&head);

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &first, &old_tail, &new_tail });
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &new_tail), view.last());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_tail)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    new_tail.prev = @intFromPtr(&old_tail);
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
    try expectListOrder(view, &.{ &first, &old_tail, &new_tail });
}

test "hlist view detects and clears stale sentinel-tail prev-link" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var old_tail = HListNode{ .next = 0, .pprev = 0 };
    var new_tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&old_tail);
    first.pprev = @intFromPtr(&head.first);
    old_tail.next = @intFromPtr(&new_tail);
    old_tail.pprev = @intFromPtr(&first.next);
    new_tail.next = 0;
    new_tail.pprev = @intFromPtr(&head.first);

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &first, &old_tail, &new_tail });
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_tail.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    new_tail.pprev = @intFromPtr(&old_tail.next);
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try expectHListOrder(view, &.{ &first, &old_tail, &new_tail });
}
