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

test "list parallel segment braid stays detached until the segment route adopts it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_left);
    first.prev = @intFromPtr(&head);
    live_left.next = @intFromPtr(&live_middle);
    live_left.prev = @intFromPtr(&first);
    live_middle.next = @intFromPtr(&live_right);
    live_middle.prev = @intFromPtr(&live_left);
    live_right.next = @intFromPtr(&tail);
    live_right.prev = @intFromPtr(&live_middle);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_right);

    braid_left.next = @intFromPtr(&braid_middle);
    braid_left.prev = @intFromPtr(&live_left);
    braid_middle.next = @intFromPtr(&braid_right);
    braid_middle.prev = @intFromPtr(&braid_left);
    braid_right.next = @intFromPtr(&tail);
    braid_right.prev = @intFromPtr(&braid_middle);

    const stable = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 5), stable.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), stable.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), stable.last());
    try expectListSequence(stable, &.{ &first, &live_left, &live_middle, &live_right, &tail });
    try testing.expect(stable.hasConsistentBacklinks());

    live_left.next = @intFromPtr(&braid_left);

    const broken = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 6), broken.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), broken.last());
    try expectListSequence(
        broken,
        &.{ &first, &live_left, &braid_left, &braid_middle, &braid_right, &tail },
    );

    const breakage = broken.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 5), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_right)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_right)), breakage.actual_prev);
    try testing.expect(!broken.hasConsistentBacklinks());
}

test "hlist parallel segment braid stays detached until the segment route adopts it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_left);
    first.pprev = @intFromPtr(&head.first);
    live_left.next = @intFromPtr(&live_middle);
    live_left.pprev = @intFromPtr(&first.next);
    live_middle.next = @intFromPtr(&live_right);
    live_middle.pprev = @intFromPtr(&live_left.next);
    live_right.next = @intFromPtr(&tail);
    live_right.pprev = @intFromPtr(&live_middle.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_right.next);

    braid_left.next = @intFromPtr(&braid_middle);
    braid_left.pprev = @intFromPtr(&live_left.next);
    braid_middle.next = @intFromPtr(&braid_right);
    braid_middle.pprev = @intFromPtr(&braid_left.next);
    braid_right.next = @intFromPtr(&tail);
    braid_right.pprev = @intFromPtr(&braid_middle.next);

    const stable = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 5), stable.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), stable.first());
    try expectHListSequence(stable, &.{ &first, &live_left, &live_middle, &live_right, &tail });
    try testing.expect(stable.firstPprevMatchesHead());
    try testing.expect(stable.hasConsistentPrevLinks());
    try testing.expect(stable.tailNextIsNull());

    live_left.next = @intFromPtr(&braid_left);

    const broken = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 6), broken.len());
    try expectHListSequence(
        broken,
        &.{ &first, &live_left, &braid_left, &braid_middle, &braid_right, &tail },
    );
    try testing.expect(broken.tailNextIsNull());

    const breakage = broken.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 5), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_right.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_right.next)), breakage.actual_pprev);
    try testing.expect(!broken.hasConsistentPrevLinks());
}
