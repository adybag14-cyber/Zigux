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

test "list parallel handoff braid stays detached until the live handoff route adopts it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_join = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_mid = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_left);
    first.prev = @intFromPtr(&head);
    live_left.next = @intFromPtr(&live_join);
    live_left.prev = @intFromPtr(&first);
    live_join.next = @intFromPtr(&live_right);
    live_join.prev = @intFromPtr(&live_left);
    live_right.next = @intFromPtr(&tail);
    live_right.prev = @intFromPtr(&live_join);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_right);

    braid_left.next = @intFromPtr(&braid_mid);
    braid_left.prev = @intFromPtr(&live_left);
    braid_mid.next = @intFromPtr(&braid_right);
    braid_mid.prev = @intFromPtr(&live_join);
    braid_right.next = @intFromPtr(&live_right);
    braid_right.prev = @intFromPtr(&braid_mid);

    const stable = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 5), stable.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), stable.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), stable.last());
    try expectListSequence(stable, &.{ &first, &live_left, &live_join, &live_right, &tail });
    try testing.expect(stable.hasConsistentBacklinks());

    live_left.next = @intFromPtr(&braid_left);

    const broken = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 7), broken.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), broken.last());
    try expectListSequence(
        broken,
        &.{ &first, &live_left, &braid_left, &braid_mid, &braid_right, &live_right, &tail },
    );

    const breakage = broken.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_left)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_join)), breakage.actual_prev);
    try testing.expect(!broken.hasConsistentBacklinks());
}

test "hlist parallel handoff braid stays detached until the live handoff route adopts it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_join = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_mid = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_left);
    first.pprev = @intFromPtr(&head.first);
    live_left.next = @intFromPtr(&live_join);
    live_left.pprev = @intFromPtr(&first.next);
    live_join.next = @intFromPtr(&live_right);
    live_join.pprev = @intFromPtr(&live_left.next);
    live_right.next = @intFromPtr(&tail);
    live_right.pprev = @intFromPtr(&live_join.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_right.next);

    braid_left.next = @intFromPtr(&braid_mid);
    braid_left.pprev = @intFromPtr(&live_left.next);
    braid_mid.next = @intFromPtr(&braid_right);
    braid_mid.pprev = @intFromPtr(&live_join.next);
    braid_right.next = @intFromPtr(&live_right);
    braid_right.pprev = @intFromPtr(&braid_mid.next);

    const stable = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 5), stable.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), stable.first());
    try expectHListSequence(stable, &.{ &first, &live_left, &live_join, &live_right, &tail });
    try testing.expect(stable.firstPprevMatchesHead());
    try testing.expect(stable.hasConsistentPrevLinks());
    try testing.expect(stable.tailNextIsNull());

    live_left.next = @intFromPtr(&braid_left);

    const broken = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 7), broken.len());
    try expectHListSequence(
        broken,
        &.{ &first, &live_left, &braid_left, &braid_mid, &braid_right, &live_right, &tail },
    );
    try testing.expect(broken.tailNextIsNull());

    const breakage = broken.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_left.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_join.next)), breakage.actual_pprev);
    try testing.expect(!broken.hasConsistentPrevLinks());
}
