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

test "phase3 list/hlist segment rotation replay keeps the live list segment order visible while a rotated witness stays off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_left = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&middle);
    left.prev = @intFromPtr(&first);
    middle.next = @intFromPtr(&right);
    middle.prev = @intFromPtr(&left);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&middle);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    shadow_middle.next = @intFromPtr(&shadow_right);
    shadow_middle.prev = @intFromPtr(&first);
    shadow_right.next = @intFromPtr(&shadow_left);
    shadow_right.prev = @intFromPtr(&shadow_middle);
    shadow_left.next = @intFromPtr(&tail);
    shadow_left.prev = @intFromPtr(&shadow_right);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &left, &middle, &right, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist segment rotation replay reports the first visible list break when the middle segment rotates early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&right);
    middle.prev = @intFromPtr(&left);
    right.next = @intFromPtr(&left);
    right.prev = @intFromPtr(&middle);
    left.next = @intFromPtr(&tail);
    left.prev = @intFromPtr(&right);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&left);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &middle, &right, &left, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist segment rotation replay keeps the live hlist segment order visible while a rotated witness stays off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&middle);
    left.pprev = @intFromPtr(&first.next);
    middle.next = @intFromPtr(&right);
    middle.pprev = @intFromPtr(&left.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&middle.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    shadow_middle.next = @intFromPtr(&shadow_right);
    shadow_middle.pprev = @intFromPtr(&first.next);
    shadow_right.next = @intFromPtr(&shadow_left);
    shadow_right.pprev = @intFromPtr(&shadow_middle.next);
    shadow_left.next = @intFromPtr(&tail);
    shadow_left.pprev = @intFromPtr(&shadow_right.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &left, &middle, &right, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist segment rotation replay reports the first visible hlist break when the middle segment rotates early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&right);
    middle.pprev = @intFromPtr(&left.next);
    right.next = @intFromPtr(&left);
    right.pprev = @intFromPtr(&middle.next);
    left.next = @intFromPtr(&tail);
    left.pprev = @intFromPtr(&right.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&left.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &middle, &right, &left, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
