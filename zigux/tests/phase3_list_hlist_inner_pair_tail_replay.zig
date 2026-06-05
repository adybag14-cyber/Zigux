const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

fn expectListOrder(view: ListView, expected: []const *const ListHead) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const ListHead, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

fn expectHListOrder(view: HListView, expected: []const *const HListNode) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const HListNode, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "list view sees an inner pair moved to the tail before backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };
    var third = ListHead{ .next = 0, .prev = 0 };
    var fourth = ListHead{ .next = 0, .prev = 0 };
    var fifth = ListHead{ .next = 0, .prev = 0 };

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

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &first, &second, &third, &fourth, &fifth });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &fifth), view.last());

    first.next = @intFromPtr(&fourth);
    fourth.next = @intFromPtr(&fifth);
    fifth.next = @intFromPtr(&second);
    second.next = @intFromPtr(&third);
    third.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&third);

    try expectListOrder(view, &.{ &first, &fourth, &fifth, &second, &third });
    try std.testing.expect(view.contains(&second));
    try std.testing.expect(view.contains(&third));
    try std.testing.expectEqual(@as(?*const ListHead, &third), view.last());

    var breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@intFromPtr(&first), breakage.expected_prev);
    try std.testing.expectEqual(@intFromPtr(&third), breakage.actual_prev);

    fourth.prev = @intFromPtr(&first);
    fifth.prev = @intFromPtr(&fourth);

    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@intFromPtr(&fifth), breakage.expected_prev);
    try std.testing.expectEqual(@intFromPtr(&first), breakage.actual_prev);

    second.prev = @intFromPtr(&fifth);
    third.prev = @intFromPtr(&second);

    try std.testing.expect(view.hasConsistentBacklinks());
    try expectListOrder(view, &.{ &first, &fourth, &fifth, &second, &third });
}

test "hlist view sees an inner pair moved to the tail before prev-link repair" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };
    var third = HListNode{ .next = 0, .pprev = 0 };
    var fourth = HListNode{ .next = 0, .pprev = 0 };
    var fifth = HListNode{ .next = 0, .pprev = 0 };

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

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &first, &second, &third, &fourth, &fifth });
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());

    first.next = @intFromPtr(&fourth);
    fourth.next = @intFromPtr(&fifth);
    fifth.next = @intFromPtr(&second);
    second.next = @intFromPtr(&third);
    third.next = 0;

    try expectHListOrder(view, &.{ &first, &fourth, &fifth, &second, &third });
    try std.testing.expect(view.contains(&second));
    try std.testing.expect(view.contains(&third));
    try std.testing.expectEqual(@as(?*const HListNode, &third), view.last());
    try std.testing.expect(view.tailNextIsNull());

    var breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@intFromPtr(&first.next), breakage.expected_pprev);
    try std.testing.expectEqual(@intFromPtr(&third.next), breakage.actual_pprev);

    fourth.pprev = @intFromPtr(&first.next);
    fifth.pprev = @intFromPtr(&fourth.next);

    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@intFromPtr(&fifth.next), breakage.expected_pprev);
    try std.testing.expectEqual(@intFromPtr(&first.next), breakage.actual_pprev);

    second.pprev = @intFromPtr(&fifth.next);
    third.pprev = @intFromPtr(&second.next);

    try std.testing.expect(view.hasConsistentPrevLinks());
    try expectHListOrder(view, &.{ &first, &fourth, &fifth, &second, &third });
}
