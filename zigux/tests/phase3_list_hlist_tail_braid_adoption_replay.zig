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

test "phase3 list/hlist tail braid adoption replay keeps the live tail route visible while the alternate braid stays off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&right);
    left.prev = @intFromPtr(&first);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    braid_left.next = @intFromPtr(&braid_right);
    braid_left.prev = @intFromPtr(&left);
    braid_right.next = @intFromPtr(&tail);
    braid_right.prev = @intFromPtr(&braid_left);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &left, &right, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist tail braid adoption replay reports the adopted list braid before the tail backlink follows" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&braid_left);
    left.prev = @intFromPtr(&first);
    braid_left.next = @intFromPtr(&braid_right);
    braid_left.prev = @intFromPtr(&left);
    braid_right.next = @intFromPtr(&tail);
    braid_right.prev = @intFromPtr(&braid_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&left);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &left, &braid_left, &braid_right, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&braid_right)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist tail braid adoption replay keeps the live tail route visible while the alternate hlist braid stays off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&right);
    left.pprev = @intFromPtr(&first.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    braid_left.next = @intFromPtr(&braid_right);
    braid_left.pprev = @intFromPtr(&left.next);
    braid_right.next = @intFromPtr(&tail);
    braid_right.pprev = @intFromPtr(&braid_left.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &left, &right, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist tail braid adoption replay reports the adopted hlist braid before the tail prev-link follows" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&braid_left);
    left.pprev = @intFromPtr(&first.next);
    braid_left.next = @intFromPtr(&braid_right);
    braid_left.pprev = @intFromPtr(&left.next);
    braid_right.next = @intFromPtr(&tail);
    braid_right.pprev = @intFromPtr(&braid_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&left.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try expectHListSequence(view, &.{ &first, &left, &braid_left, &braid_right, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&braid_right.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}