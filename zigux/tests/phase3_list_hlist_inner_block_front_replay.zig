const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListOrder(
    view: list_view.ListView,
    expected: []const *const list_view.ListHead,
) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const list_view.ListHead, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

fn expectHListOrder(
    view: hlist_view.HListView,
    expected: []const *const hlist_view.HListNode,
) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const hlist_view.HListNode, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "list view reports staged backlinks when an inner block is promoted to front" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var fourth = list_view.ListHead{ .next = 0, .prev = 0 };
    var fifth = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&fifth);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&fourth);
    third.prev = @intFromPtr(&second);
    fourth.next = @intFromPtr(&fifth);
    fourth.prev = @intFromPtr(&third);
    fifth.next = @intFromPtr(&head);
    fifth.prev = @intFromPtr(&fourth);

    head.next = @intFromPtr(&second);
    second.next = @intFromPtr(&third);
    third.next = @intFromPtr(&first);
    first.next = @intFromPtr(&fourth);
    fourth.next = @intFromPtr(&fifth);

    const view = list_view.ListView.init(&head);
    const reordered = [_]*const list_view.ListHead{ &second, &third, &first, &fourth, &fifth };
    try expectListOrder(view, &reordered);
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &second), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &fifth), view.last());
    try std.testing.expect(!view.contains(&head));
    try std.testing.expect(!view.hasConsistentBacklinks());

    var breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.actual_prev);

    second.prev = @intFromPtr(&head);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&third)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);

    first.prev = @intFromPtr(&third);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&third)), breakage.actual_prev);

    fourth.prev = @intFromPtr(&first);
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist view reports staged prev-links when an inner block is promoted to front" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var fourth = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var fifth = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = @intFromPtr(&fourth);
    third.pprev = @intFromPtr(&second.next);
    fourth.next = @intFromPtr(&fifth);
    fourth.pprev = @intFromPtr(&third.next);
    fifth.next = 0;
    fifth.pprev = @intFromPtr(&fourth.next);

    head.first = @intFromPtr(&second);
    second.next = @intFromPtr(&third);
    third.next = @intFromPtr(&first);
    first.next = @intFromPtr(&fourth);
    fourth.next = @intFromPtr(&fifth);

    const view = hlist_view.HListView.init(&head);
    const reordered = [_]*const hlist_view.HListNode{ &second, &third, &first, &fourth, &fifth };
    try expectHListOrder(view, &reordered);
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &second), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &fifth), view.last());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());

    var breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.actual_pprev);

    second.pprev = @intFromPtr(&head.first);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&third.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);

    first.pprev = @intFromPtr(&third.next);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&third.next)), breakage.actual_pprev);

    fourth.pprev = @intFromPtr(&first.next);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}
