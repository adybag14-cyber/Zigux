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

test "list view follows the live head route instead of a detached reflected copy" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var reflected_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var reflected_first = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&tail);
    third.prev = @intFromPtr(&second);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&third);

    reflected_second.next = @intFromPtr(&reflected_first);
    reflected_second.prev = @intFromPtr(&head);
    reflected_first.next = @intFromPtr(&third);
    reflected_first.prev = @intFromPtr(&reflected_second);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &second, &third, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view reports the rejoined middle node after a reflected head copy is adopted" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var reflected_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var reflected_first = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&reflected_second);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&tail);
    third.prev = @intFromPtr(&second);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&third);

    reflected_second.next = @intFromPtr(&reflected_first);
    reflected_second.prev = @intFromPtr(&head);
    reflected_first.next = @intFromPtr(&third);
    reflected_first.prev = @intFromPtr(&reflected_second);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &reflected_second), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &reflected_second, &reflected_first, &third, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&reflected_first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "hlist view follows the live head route instead of a detached reflected copy" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var reflected_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var reflected_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = @intFromPtr(&tail);
    third.pprev = @intFromPtr(&second.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&third.next);

    reflected_second.next = @intFromPtr(&reflected_first);
    reflected_second.pprev = @intFromPtr(&head.first);
    reflected_first.next = @intFromPtr(&third);
    reflected_first.pprev = @intFromPtr(&reflected_second.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &second, &third, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports the rejoined middle node after a reflected head copy is adopted" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var reflected_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var reflected_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&reflected_second);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = @intFromPtr(&tail);
    third.pprev = @intFromPtr(&second.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&third.next);

    reflected_second.next = @intFromPtr(&reflected_first);
    reflected_second.pprev = @intFromPtr(&head.first);
    reflected_first.next = @intFromPtr(&third);
    reflected_first.pprev = @intFromPtr(&reflected_second.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &reflected_second), view.first());
    try expectHListSequence(view, &.{ &reflected_second, &reflected_first, &third, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&reflected_first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
