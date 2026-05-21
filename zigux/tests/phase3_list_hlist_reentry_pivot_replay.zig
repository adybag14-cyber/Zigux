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

test "phase3 list/hlist reentry pivot replay keeps the live list pivot visible while a detached lead-in rejoins off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&pivot);
    first.prev = @intFromPtr(&head);
    pivot.next = @intFromPtr(&tail);
    pivot.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&pivot);

    shadow_left.next = @intFromPtr(&shadow_right);
    shadow_left.prev = @intFromPtr(&first);
    shadow_right.next = @intFromPtr(&pivot);
    shadow_right.prev = @intFromPtr(&shadow_left);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &pivot, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist reentry pivot replay reports the first visible list break when the pivot adopts the detached lead-in early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var pivot = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&pivot);
    first.prev = @intFromPtr(&head);
    pivot.next = @intFromPtr(&tail);
    pivot.prev = @intFromPtr(&shadow_right);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&pivot);

    shadow_left.next = @intFromPtr(&shadow_right);
    shadow_left.prev = @intFromPtr(&first);
    shadow_right.next = @intFromPtr(&pivot);
    shadow_right.prev = @intFromPtr(&shadow_left);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &pivot, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_right)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist reentry pivot replay keeps the live hlist pivot visible while a detached lead-in rejoins off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&pivot);
    first.pprev = @intFromPtr(&head.first);
    pivot.next = @intFromPtr(&tail);
    pivot.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&pivot.next);

    shadow_left.next = @intFromPtr(&shadow_right);
    shadow_left.pprev = @intFromPtr(&first.next);
    shadow_right.next = @intFromPtr(&pivot);
    shadow_right.pprev = @intFromPtr(&shadow_left.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &pivot, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist reentry pivot replay reports the first visible hlist break when the pivot adopts the detached lead-in early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var pivot = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&pivot);
    first.pprev = @intFromPtr(&head.first);
    pivot.next = @intFromPtr(&tail);
    pivot.pprev = @intFromPtr(&shadow_right.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&pivot.next);

    shadow_left.next = @intFromPtr(&shadow_right);
    shadow_left.pprev = @intFromPtr(&first.next);
    shadow_right.next = @intFromPtr(&pivot);
    shadow_right.pprev = @intFromPtr(&shadow_left.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &pivot, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_right.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
