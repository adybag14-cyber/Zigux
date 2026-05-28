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

test "list parallel closure braid stays detached until the closure route adopts it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_close_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_close_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&live_close_right);
    first.next = @intFromPtr(&live_left);
    first.prev = @intFromPtr(&head);
    live_left.next = @intFromPtr(&live_right);
    live_left.prev = @intFromPtr(&first);
    live_right.next = @intFromPtr(&live_close_left);
    live_right.prev = @intFromPtr(&live_left);
    live_close_left.next = @intFromPtr(&live_close_right);
    live_close_left.prev = @intFromPtr(&live_right);
    live_close_right.next = @intFromPtr(&head);
    live_close_right.prev = @intFromPtr(&live_close_left);

    braid_left.next = @intFromPtr(&braid_right);
    braid_left.prev = @intFromPtr(&live_right);
    braid_right.next = @intFromPtr(&head);
    braid_right.prev = @intFromPtr(&live_close_left);

    const stable = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 5), stable.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), stable.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &live_close_right), stable.last());
    try expectListSequence(
        stable,
        &.{ &first, &live_left, &live_right, &live_close_left, &live_close_right },
    );
    try testing.expect(stable.hasConsistentBacklinks());

    live_right.next = @intFromPtr(&braid_left);
    head.prev = @intFromPtr(&braid_right);

    const broken = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 5), broken.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &braid_right), broken.last());
    try expectListSequence(
        broken,
        &.{ &first, &live_left, &live_right, &braid_left, &braid_right },
    );

    const breakage = broken.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 4), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_left)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_close_left)), breakage.actual_prev);
    try testing.expect(!broken.hasConsistentBacklinks());
}

test "hlist parallel closure braid stays detached until the closure route adopts it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_close_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_close_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_left);
    first.pprev = @intFromPtr(&head.first);
    live_left.next = @intFromPtr(&live_right);
    live_left.pprev = @intFromPtr(&first.next);
    live_right.next = @intFromPtr(&live_close_left);
    live_right.pprev = @intFromPtr(&live_left.next);
    live_close_left.next = @intFromPtr(&live_close_right);
    live_close_left.pprev = @intFromPtr(&live_right.next);
    live_close_right.next = 0;
    live_close_right.pprev = @intFromPtr(&live_close_left.next);

    braid_left.next = @intFromPtr(&braid_right);
    braid_left.pprev = @intFromPtr(&live_right.next);
    braid_right.next = 0;
    braid_right.pprev = @intFromPtr(&live_close_left.next);

    const stable = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 5), stable.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), stable.first());
    try expectHListSequence(
        stable,
        &.{ &first, &live_left, &live_right, &live_close_left, &live_close_right },
    );
    try testing.expect(stable.firstPprevMatchesHead());
    try testing.expect(stable.hasConsistentPrevLinks());
    try testing.expect(stable.tailNextIsNull());

    live_right.next = @intFromPtr(&braid_left);

    const broken = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 5), broken.len());
    try expectHListSequence(
        broken,
        &.{ &first, &live_left, &live_right, &braid_left, &braid_right },
    );
    try testing.expect(broken.tailNextIsNull());

    const breakage = broken.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 4), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_left.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_close_left.next)), breakage.actual_pprev);
    try testing.expect(!broken.hasConsistentPrevLinks());
}
