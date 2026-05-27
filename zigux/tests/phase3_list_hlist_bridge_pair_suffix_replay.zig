const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListSequence(
    view: list_view.ListView,
    expected: []const *const list_view.ListHead,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try testing.expectEqual(@as(?*const list_view.ListHead, node), it.next());
    }
    try testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

fn expectHListSequence(
    view: hlist_view.HListView,
    expected: []const *const hlist_view.HListNode,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try testing.expectEqual(@as(?*const hlist_view.HListNode, node), it.next());
    }
    try testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "list bridge-pair suffix stays off-route until the visible route adopts it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var live = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var suffix_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var suffix_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&live);
    entry.prev = @intFromPtr(&head);
    live.next = @intFromPtr(&tail);
    live.prev = @intFromPtr(&entry);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live);

    suffix_left.next = @intFromPtr(&suffix_right);
    suffix_left.prev = @intFromPtr(&entry);
    suffix_right.next = @intFromPtr(&tail);
    suffix_right.prev = @intFromPtr(&suffix_left);

    const stable = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 3), stable.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &entry), stable.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), stable.last());
    try expectListSequence(stable, &.{ &entry, &live, &tail });
    try testing.expect(stable.hasConsistentBacklinks());

    live.next = @intFromPtr(&suffix_left);
    tail.prev = @intFromPtr(&suffix_right);

    const broken = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 5), broken.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), broken.last());
    try expectListSequence(broken, &.{ &entry, &live, &suffix_left, &suffix_right, &tail });

    const breakage = broken.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&live)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&entry)), breakage.actual_prev);
    try testing.expect(!broken.hasConsistentBacklinks());
}

test "hlist bridge-pair suffix stays off-route until the visible route adopts it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var suffix_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var suffix_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&live);
    entry.pprev = @intFromPtr(&head.first);
    live.next = @intFromPtr(&tail);
    live.pprev = @intFromPtr(&entry.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live.next);

    suffix_left.next = @intFromPtr(&suffix_right);
    suffix_left.pprev = @intFromPtr(&entry.next);
    suffix_right.next = @intFromPtr(&tail);
    suffix_right.pprev = @intFromPtr(&suffix_left.next);

    const stable = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 3), stable.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &entry), stable.first());
    try expectHListSequence(stable, &.{ &entry, &live, &tail });
    try testing.expect(stable.firstPprevMatchesHead());
    try testing.expect(stable.hasConsistentPrevLinks());
    try testing.expect(stable.tailNextIsNull());

    live.next = @intFromPtr(&suffix_left);
    tail.pprev = @intFromPtr(&suffix_right.next);

    const broken = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 5), broken.len());
    try expectHListSequence(broken, &.{ &entry, &live, &suffix_left, &suffix_right, &tail });
    try testing.expect(broken.tailNextIsNull());

    const breakage = broken.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&live.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&entry.next)), breakage.actual_pprev);
    try testing.expect(!broken.hasConsistentPrevLinks());
}
