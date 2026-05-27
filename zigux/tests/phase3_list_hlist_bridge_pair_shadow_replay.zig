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

test "list bridge-pair shadow stays off-route until the visible route adopts it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&live_left);
    entry.prev = @intFromPtr(&head);
    live_left.next = @intFromPtr(&live_right);
    live_left.prev = @intFromPtr(&entry);
    live_right.next = @intFromPtr(&tail);
    live_right.prev = @intFromPtr(&live_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_right);

    shadow_left.next = @intFromPtr(&shadow_right);
    shadow_left.prev = @intFromPtr(&live_left);
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.prev = @intFromPtr(&shadow_left);

    const stable = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), stable.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &entry), stable.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), stable.last());
    try expectListSequence(stable, &.{ &entry, &live_left, &live_right, &tail });
    try testing.expect(stable.hasConsistentBacklinks());

    entry.next = @intFromPtr(&shadow_left);
    tail.prev = @intFromPtr(&shadow_right);

    const broken = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), broken.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), broken.last());
    try expectListSequence(broken, &.{ &entry, &shadow_left, &shadow_right, &tail });

    const breakage = broken.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&entry)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_left)), breakage.actual_prev);
    try testing.expect(!broken.hasConsistentBacklinks());
}

test "hlist bridge-pair shadow stays off-route until the visible route adopts it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&live_left);
    entry.pprev = @intFromPtr(&head.first);
    live_left.next = @intFromPtr(&live_right);
    live_left.pprev = @intFromPtr(&entry.next);
    live_right.next = @intFromPtr(&tail);
    live_right.pprev = @intFromPtr(&live_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_right.next);

    shadow_left.next = @intFromPtr(&shadow_right);
    shadow_left.pprev = @intFromPtr(&live_left.next);
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.pprev = @intFromPtr(&shadow_left.next);

    const stable = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), stable.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &entry), stable.first());
    try expectHListSequence(stable, &.{ &entry, &live_left, &live_right, &tail });
    try testing.expect(stable.firstPprevMatchesHead());
    try testing.expect(stable.hasConsistentPrevLinks());
    try testing.expect(stable.tailNextIsNull());

    entry.next = @intFromPtr(&shadow_left);
    tail.pprev = @intFromPtr(&shadow_right.next);

    const broken = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), broken.len());
    try expectHListSequence(broken, &.{ &entry, &shadow_left, &shadow_right, &tail });
    try testing.expect(broken.tailNextIsNull());

    const breakage = broken.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&entry.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_left.next)), breakage.actual_pprev);
    try testing.expect(!broken.hasConsistentPrevLinks());
}
