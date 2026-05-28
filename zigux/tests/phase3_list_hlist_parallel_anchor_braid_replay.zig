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

test "list parallel anchor braid stays detached while the live anchor route remains visible" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var anchor = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&anchor);
    first.prev = @intFromPtr(&head);
    anchor.next = @intFromPtr(&live_left);
    anchor.prev = @intFromPtr(&first);
    live_left.next = @intFromPtr(&live_right);
    live_left.prev = @intFromPtr(&anchor);
    live_right.next = @intFromPtr(&tail);
    live_right.prev = @intFromPtr(&live_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_right);

    braid_left.next = @intFromPtr(&braid_right);
    braid_left.prev = @intFromPtr(&anchor);
    braid_right.next = @intFromPtr(&tail);
    braid_right.prev = @intFromPtr(&braid_left);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 5), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &anchor, &live_left, &live_right, &tail });
    try testing.expect(view.hasConsistentBacklinks());
    try testing.expect(view.firstBrokenBacklink() == null);
}

test "list parallel anchor braid reports the first visible break when the anchor adopts a detached braid early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var anchor = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&anchor);
    first.prev = @intFromPtr(&head);
    anchor.next = @intFromPtr(&braid_left);
    anchor.prev = @intFromPtr(&first);
    live_left.next = @intFromPtr(&live_right);
    live_left.prev = @intFromPtr(&anchor);
    live_right.next = @intFromPtr(&tail);
    live_right.prev = @intFromPtr(&live_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_right);

    braid_left.next = @intFromPtr(&braid_right);
    braid_left.prev = @intFromPtr(&anchor);
    braid_right.next = @intFromPtr(&tail);
    braid_right.prev = @intFromPtr(&braid_left);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 5), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &anchor, &braid_left, &braid_right, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 4), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_right)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_right)), breakage.actual_prev);
    try testing.expect(!view.hasConsistentBacklinks());
}

test "hlist parallel anchor braid stays detached while the live anchor route remains visible" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var anchor = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&anchor);
    first.pprev = @intFromPtr(&head.first);
    anchor.next = @intFromPtr(&live_left);
    anchor.pprev = @intFromPtr(&first.next);
    live_left.next = @intFromPtr(&live_right);
    live_left.pprev = @intFromPtr(&anchor.next);
    live_right.next = @intFromPtr(&tail);
    live_right.pprev = @intFromPtr(&live_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_right.next);

    braid_left.next = @intFromPtr(&braid_right);
    braid_left.pprev = @intFromPtr(&anchor.next);
    braid_right.next = @intFromPtr(&tail);
    braid_right.pprev = @intFromPtr(&braid_left.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 5), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &anchor, &live_left, &live_right, &tail });
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());
}

test "hlist parallel anchor braid reports the first visible break when the anchor adopts a detached braid early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var anchor = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&anchor);
    first.pprev = @intFromPtr(&head.first);
    anchor.next = @intFromPtr(&braid_left);
    anchor.pprev = @intFromPtr(&first.next);
    live_left.next = @intFromPtr(&live_right);
    live_left.pprev = @intFromPtr(&anchor.next);
    live_right.next = @intFromPtr(&tail);
    live_right.pprev = @intFromPtr(&live_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_right.next);

    braid_left.next = @intFromPtr(&braid_right);
    braid_left.pprev = @intFromPtr(&anchor.next);
    braid_right.next = @intFromPtr(&tail);
    braid_right.pprev = @intFromPtr(&braid_left.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 5), view.len());
    try expectHListSequence(view, &.{ &first, &anchor, &braid_left, &braid_right, &tail });
    try testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 4), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_right.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_right.next)), breakage.actual_pprev);
    try testing.expect(!view.hasConsistentPrevLinks());
}
