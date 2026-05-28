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

test "list parallel head braid stays detached until the head route adopts it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_left);
    first.prev = @intFromPtr(&head);
    live_left.next = @intFromPtr(&live_right);
    live_left.prev = @intFromPtr(&first);
    live_right.next = @intFromPtr(&tail);
    live_right.prev = @intFromPtr(&live_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_right);

    braid_left.next = @intFromPtr(&braid_right);
    braid_left.prev = @intFromPtr(&head);
    braid_right.next = @intFromPtr(&first);
    braid_right.prev = @intFromPtr(&braid_left);

    const stable = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), stable.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), stable.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), stable.last());
    try expectListSequence(stable, &.{ &first, &live_left, &live_right, &tail });
    try testing.expect(stable.hasConsistentBacklinks());

    head.next = @intFromPtr(&braid_left);

    const broken = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 6), broken.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &braid_left), broken.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), broken.last());
    try expectListSequence(
        broken,
        &.{ &braid_left, &braid_right, &first, &live_left, &live_right, &tail },
    );

    const breakage = broken.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_right)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try testing.expect(!broken.hasConsistentBacklinks());
}

test "hlist parallel head braid stays detached until the head route adopts it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_left);
    first.pprev = @intFromPtr(&head.first);
    live_left.next = @intFromPtr(&live_right);
    live_left.pprev = @intFromPtr(&first.next);
    live_right.next = @intFromPtr(&tail);
    live_right.pprev = @intFromPtr(&live_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_right.next);

    braid_left.next = @intFromPtr(&braid_right);
    braid_left.pprev = @intFromPtr(&head.first);
    braid_right.next = @intFromPtr(&first);
    braid_right.pprev = @intFromPtr(&braid_left.next);

    const stable = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), stable.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), stable.first());
    try expectHListSequence(stable, &.{ &first, &live_left, &live_right, &tail });
    try testing.expect(stable.firstPprevMatchesHead());
    try testing.expect(stable.hasConsistentPrevLinks());
    try testing.expect(stable.tailNextIsNull());

    head.first = @intFromPtr(&braid_left);

    const broken = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 6), broken.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &braid_left), broken.first());
    try expectHListSequence(
        broken,
        &.{ &braid_left, &braid_right, &first, &live_left, &live_right, &tail },
    );
    try testing.expect(broken.tailNextIsNull());

    const breakage = broken.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_right.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try testing.expect(!broken.hasConsistentPrevLinks());
}
