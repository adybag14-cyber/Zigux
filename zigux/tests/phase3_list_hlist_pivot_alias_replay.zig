const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListSequence(
    view: list_view.ListView,
    expected: []const *const list_view.ListHead,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const list_view.ListHead, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

fn expectHListSequence(
    view: hlist_view.HListView,
    expected: []const *const hlist_view.HListNode,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const hlist_view.HListNode, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "list view keeps the live pivot visible over a detached pivot alias" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var alias = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&pivot);
    entry.prev = @intFromPtr(&head);
    pivot.next = @intFromPtr(&tail);
    pivot.prev = @intFromPtr(&entry);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&pivot);

    alias.next = @intFromPtr(&tail);
    alias.prev = @intFromPtr(&alias);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &entry), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &entry, &pivot, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view reports the adopted pivot alias once the reused tail keeps the stale backlink" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var alias = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&alias);
    entry.prev = @intFromPtr(&head);
    pivot.next = @intFromPtr(&tail);
    pivot.prev = @intFromPtr(&entry);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&pivot);

    alias.next = @intFromPtr(&tail);
    alias.prev = @intFromPtr(&entry);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &entry, &alias, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&alias)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&pivot)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "hlist view keeps the live pivot visible over a detached pivot alias" {
    var head = hlist_view.HListHead{ .first = 0 };
    var entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alias = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&pivot);
    entry.pprev = @intFromPtr(&head.first);
    pivot.next = @intFromPtr(&tail);
    pivot.pprev = @intFromPtr(&entry.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&pivot.next);

    alias.next = @intFromPtr(&tail);
    alias.pprev = @intFromPtr(&alias.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &entry), view.first());
    try expectHListSequence(view, &.{ &entry, &pivot, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports the adopted pivot alias once the reused tail keeps the stale prev-link" {
    var head = hlist_view.HListHead{ .first = 0 };
    var entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alias = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&alias);
    entry.pprev = @intFromPtr(&head.first);
    pivot.next = @intFromPtr(&tail);
    pivot.pprev = @intFromPtr(&entry.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&pivot.next);

    alias.next = @intFromPtr(&tail);
    alias.pprev = @intFromPtr(&entry.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &entry, &alias, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&alias.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&pivot.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
