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

test "phase3 list/hlist middle hinge replay keeps the live list hinge visible while an alternate hinge stays off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_hinge = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_hinge = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_hinge);
    first.prev = @intFromPtr(&head);
    live_hinge.next = @intFromPtr(&third);
    live_hinge.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&tail);
    third.prev = @intFromPtr(&live_hinge);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&third);

    alt_hinge.next = @intFromPtr(&third);
    alt_hinge.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &live_hinge, &third, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist middle hinge replay reports the first list middle mismatch when the alternate hinge is adopted too early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_hinge = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_hinge = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&alt_hinge);
    first.prev = @intFromPtr(&head);
    live_hinge.next = @intFromPtr(&third);
    live_hinge.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&tail);
    third.prev = @intFromPtr(&live_hinge);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&third);

    alt_hinge.next = @intFromPtr(&third);
    alt_hinge.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &alt_hinge, &third, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&alt_hinge)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_hinge)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist middle hinge replay keeps the live hlist hinge visible while an alternate hinge stays off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_hinge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_hinge = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_hinge);
    first.pprev = @intFromPtr(&head.first);
    live_hinge.next = @intFromPtr(&third);
    live_hinge.pprev = @intFromPtr(&first.next);
    third.next = @intFromPtr(&tail);
    third.pprev = @intFromPtr(&live_hinge.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&third.next);

    alt_hinge.next = @intFromPtr(&third);
    alt_hinge.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &live_hinge, &third, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist middle hinge replay reports the first hlist middle mismatch when the alternate hinge is adopted too early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_hinge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_hinge = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&alt_hinge);
    first.pprev = @intFromPtr(&head.first);
    live_hinge.next = @intFromPtr(&third);
    live_hinge.pprev = @intFromPtr(&first.next);
    third.next = @intFromPtr(&tail);
    third.pprev = @intFromPtr(&live_hinge.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&third.next);

    alt_hinge.next = @intFromPtr(&third);
    alt_hinge.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &alt_hinge, &third, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&alt_hinge.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_hinge.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
