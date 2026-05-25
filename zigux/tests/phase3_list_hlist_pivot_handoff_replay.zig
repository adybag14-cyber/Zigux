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

test "list view keeps the live pivot visible over a detached pivot handoff" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var handoff = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&pivot);
    entry.prev = @intFromPtr(&head);
    pivot.next = @intFromPtr(&bridge);
    pivot.prev = @intFromPtr(&entry);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&pivot);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge);

    handoff.next = @intFromPtr(&bridge);
    handoff.prev = @intFromPtr(&handoff);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &entry), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &entry, &pivot, &bridge, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view reports the adopted pivot handoff once the reused bridge keeps the stale backlink" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var handoff = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&pivot);
    entry.prev = @intFromPtr(&head);
    pivot.next = @intFromPtr(&handoff);
    pivot.prev = @intFromPtr(&entry);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&pivot);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge);

    handoff.next = @intFromPtr(&bridge);
    handoff.prev = @intFromPtr(&pivot);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &entry, &pivot, &handoff, &bridge, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&handoff)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&pivot)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "hlist view keeps the live pivot visible over a detached pivot handoff" {
    var head = hlist_view.HListHead{ .first = 0 };
    var entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var handoff = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&pivot);
    entry.pprev = @intFromPtr(&head.first);
    pivot.next = @intFromPtr(&bridge);
    pivot.pprev = @intFromPtr(&entry.next);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&pivot.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge.next);

    handoff.next = @intFromPtr(&bridge);
    handoff.pprev = @intFromPtr(&handoff.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &entry), view.first());
    try expectHListSequence(view, &.{ &entry, &pivot, &bridge, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports the adopted pivot handoff once the reused bridge keeps the stale prev-link" {
    var head = hlist_view.HListHead{ .first = 0 };
    var entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var handoff = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&pivot);
    entry.pprev = @intFromPtr(&head.first);
    pivot.next = @intFromPtr(&handoff);
    pivot.pprev = @intFromPtr(&entry.next);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&pivot.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge.next);

    handoff.next = @intFromPtr(&bridge);
    handoff.pprev = @intFromPtr(&pivot.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &entry, &pivot, &handoff, &bridge, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&handoff.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&pivot.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
