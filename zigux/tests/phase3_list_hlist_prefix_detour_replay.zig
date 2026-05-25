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

test "list view keeps the live route visible over a detached prefix detour" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var detour_entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var detour_left = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&middle);
    entry.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&tail);
    middle.prev = @intFromPtr(&entry);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&middle);

    detour_entry.next = @intFromPtr(&detour_left);
    detour_entry.prev = @intFromPtr(&detour_entry);
    detour_left.next = @intFromPtr(&middle);
    detour_left.prev = @intFromPtr(&detour_entry);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &entry), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &entry, &middle, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view reports the adopted prefix detour once the stale middle backlink is reached" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var detour_entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var detour_left = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&detour_entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&middle);
    entry.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&tail);
    middle.prev = @intFromPtr(&entry);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&middle);

    detour_entry.next = @intFromPtr(&detour_left);
    detour_entry.prev = @intFromPtr(&head);
    detour_left.next = @intFromPtr(&middle);
    detour_left.prev = @intFromPtr(&detour_entry);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &detour_entry, &detour_left, &middle, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detour_left)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entry)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "hlist view keeps the live route visible over a detached prefix detour" {
    var head = hlist_view.HListHead{ .first = 0 };
    var entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var detour_entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var detour_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&middle);
    entry.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&tail);
    middle.pprev = @intFromPtr(&entry.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&middle.next);

    detour_entry.next = @intFromPtr(&detour_left);
    detour_entry.pprev = @intFromPtr(&detour_entry.next);
    detour_left.next = @intFromPtr(&middle);
    detour_left.pprev = @intFromPtr(&detour_entry.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &entry), view.first());
    try expectHListSequence(view, &.{ &entry, &middle, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports the adopted prefix detour once the stale middle prev-link is reached" {
    var head = hlist_view.HListHead{ .first = 0 };
    var entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var detour_entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var detour_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&detour_entry);
    entry.next = @intFromPtr(&middle);
    entry.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&tail);
    middle.pprev = @intFromPtr(&entry.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&middle.next);

    detour_entry.next = @intFromPtr(&detour_left);
    detour_entry.pprev = @intFromPtr(&head.first);
    detour_left.next = @intFromPtr(&middle);
    detour_left.pprev = @intFromPtr(&detour_entry.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &detour_entry, &detour_left, &middle, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detour_left.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entry.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
