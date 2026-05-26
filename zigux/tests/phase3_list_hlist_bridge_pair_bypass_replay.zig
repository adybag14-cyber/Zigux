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

test "list view keeps the live bridge pair visible over a detached bypass pair" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var bypass_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var bypass_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&bridge_left);
    entry.prev = @intFromPtr(&head);
    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.prev = @intFromPtr(&entry);
    bridge_right.next = @intFromPtr(&tail);
    bridge_right.prev = @intFromPtr(&bridge_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge_right);

    bypass_left.next = @intFromPtr(&bypass_right);
    bypass_left.prev = @intFromPtr(&entry);
    bypass_right.next = @intFromPtr(&tail);
    bypass_right.prev = @intFromPtr(&bypass_left);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &entry), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &entry, &bridge_left, &bridge_right, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view reports the adopted bypass pair once the reused tail keeps the stale backlink" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var bypass_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var bypass_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&bypass_left);
    entry.prev = @intFromPtr(&head);
    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.prev = @intFromPtr(&entry);
    bridge_right.next = @intFromPtr(&tail);
    bridge_right.prev = @intFromPtr(&bridge_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge_right);

    bypass_left.next = @intFromPtr(&bypass_right);
    bypass_left.prev = @intFromPtr(&entry);
    bypass_right.next = @intFromPtr(&tail);
    bypass_right.prev = @intFromPtr(&bypass_left);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &entry, &bypass_left, &bypass_right, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bypass_right)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_right)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "hlist view keeps the live bridge pair visible over a detached bypass pair" {
    var head = hlist_view.HListHead{ .first = 0 };
    var entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bypass_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bypass_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&bridge_left);
    entry.pprev = @intFromPtr(&head.first);
    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.pprev = @intFromPtr(&entry.next);
    bridge_right.next = @intFromPtr(&tail);
    bridge_right.pprev = @intFromPtr(&bridge_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge_right.next);

    bypass_left.next = @intFromPtr(&bypass_right);
    bypass_left.pprev = @intFromPtr(&entry.next);
    bypass_right.next = @intFromPtr(&tail);
    bypass_right.pprev = @intFromPtr(&bypass_left.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &entry), view.first());
    try expectHListSequence(view, &.{ &entry, &bridge_left, &bridge_right, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports the adopted bypass pair once the reused tail keeps the stale prev-link" {
    var head = hlist_view.HListHead{ .first = 0 };
    var entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bypass_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bypass_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&bypass_left);
    entry.pprev = @intFromPtr(&head.first);
    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.pprev = @intFromPtr(&entry.next);
    bridge_right.next = @intFromPtr(&tail);
    bridge_right.pprev = @intFromPtr(&bridge_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge_right.next);

    bypass_left.next = @intFromPtr(&bypass_right);
    bypass_left.pprev = @intFromPtr(&entry.next);
    bypass_right.next = @intFromPtr(&tail);
    bypass_right.pprev = @intFromPtr(&bypass_left.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &entry, &bypass_left, &bypass_right, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bypass_right.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_right.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
