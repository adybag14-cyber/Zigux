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

test "list parallel middle braid stays detached until the middle route adopts it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&right);
    middle.prev = @intFromPtr(&first);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&middle);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    braid_left.next = @intFromPtr(&right);
    braid_left.prev = @intFromPtr(&middle);
    braid_right.next = @intFromPtr(&tail);
    braid_right.prev = @intFromPtr(&right);

    const stable = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), stable.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), stable.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), stable.last());
    try expectListSequence(stable, &.{ &first, &middle, &right, &tail });
    try testing.expect(stable.hasConsistentBacklinks());

    middle.next = @intFromPtr(&braid_left);
    right.next = @intFromPtr(&braid_right);

    const broken = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 6), broken.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), broken.last());
    try expectListSequence(
        broken,
        &.{ &first, &middle, &braid_left, &right, &braid_right, &tail },
    );

    const breakage = broken.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_left)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&middle)), breakage.actual_prev);
    try testing.expect(!broken.hasConsistentBacklinks());
}

test "hlist parallel middle braid stays detached until the middle route adopts it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&right);
    middle.pprev = @intFromPtr(&first.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&middle.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    braid_left.next = @intFromPtr(&right);
    braid_left.pprev = @intFromPtr(&middle.next);
    braid_right.next = @intFromPtr(&tail);
    braid_right.pprev = @intFromPtr(&right.next);

    const stable = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), stable.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), stable.first());
    try expectHListSequence(stable, &.{ &first, &middle, &right, &tail });
    try testing.expect(stable.firstPprevMatchesHead());
    try testing.expect(stable.hasConsistentPrevLinks());
    try testing.expect(stable.tailNextIsNull());

    middle.next = @intFromPtr(&braid_left);
    right.next = @intFromPtr(&braid_right);

    const broken = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 6), broken.len());
    try expectHListSequence(
        broken,
        &.{ &first, &middle, &braid_left, &right, &braid_right, &tail },
    );
    try testing.expect(broken.tailNextIsNull());

    const breakage = broken.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_left.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), breakage.actual_pprev);
    try testing.expect(!broken.hasConsistentPrevLinks());
}
