const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListOrder(view: list_view.ListView, expected: []const *const list_view.ListHead) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const list_view.ListHead, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

fn expectHListOrder(view: hlist_view.HListView, expected: []const *const hlist_view.HListNode) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const hlist_view.HListNode, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

fn expectListBreak(view: list_view.ListView, index: usize, expected_prev: *const list_view.ListHead, actual_prev: *const list_view.ListHead) !void {
    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(index, breakage.current_index);
    try std.testing.expectEqual(@intFromPtr(expected_prev), breakage.expected_prev);
    try std.testing.expectEqual(@intFromPtr(actual_prev), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

fn expectHListBreak(view: hlist_view.HListView, index: usize, expected_pprev: *const usize, actual_pprev: *const usize) !void {
    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(index, breakage.current_index);
    try std.testing.expectEqual(@intFromPtr(expected_pprev), breakage.expected_pprev);
    try std.testing.expectEqual(@intFromPtr(actual_pprev), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}

test "list view follows alternating-drain reorder before staged backlinks are repaired" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var one = list_view.ListHead{ .next = 0, .prev = 0 };
    var two = list_view.ListHead{ .next = 0, .prev = 0 };
    var three = list_view.ListHead{ .next = 0, .prev = 0 };
    var four = list_view.ListHead{ .next = 0, .prev = 0 };
    var five = list_view.ListHead{ .next = 0, .prev = 0 };
    var six = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&one);
    head.prev = @intFromPtr(&six);
    one.next = @intFromPtr(&two);
    one.prev = @intFromPtr(&head);
    two.next = @intFromPtr(&three);
    two.prev = @intFromPtr(&one);
    three.next = @intFromPtr(&four);
    three.prev = @intFromPtr(&two);
    four.next = @intFromPtr(&five);
    four.prev = @intFromPtr(&three);
    five.next = @intFromPtr(&six);
    five.prev = @intFromPtr(&four);
    six.next = @intFromPtr(&head);
    six.prev = @intFromPtr(&five);

    head.next = @intFromPtr(&two);
    two.next = @intFromPtr(&four);
    four.next = @intFromPtr(&six);
    six.next = @intFromPtr(&one);
    one.next = @intFromPtr(&three);
    three.next = @intFromPtr(&five);
    five.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&five);

    const view = list_view.ListView.init(&head);
    const order = [_]*const list_view.ListHead{ &two, &four, &six, &one, &three, &five };

    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &two), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &five), view.last());
    try expectListOrder(view, &order);
    try std.testing.expect(!view.contains(&head));
    try expectListBreak(view, 0, &head, &one);

    two.prev = @intFromPtr(&head);
    try expectListBreak(view, 1, &two, &three);

    four.prev = @intFromPtr(&two);
    try expectListBreak(view, 2, &four, &five);

    six.prev = @intFromPtr(&four);
    try expectListBreak(view, 3, &six, &head);

    one.prev = @intFromPtr(&six);
    try expectListBreak(view, 4, &one, &two);

    three.prev = @intFromPtr(&one);
    try expectListBreak(view, 5, &three, &four);

    five.prev = @intFromPtr(&three);
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist view follows alternating-drain reorder before staged pprev links are repaired" {
    var head = hlist_view.HListHead{ .first = 0 };
    var one = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var two = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var three = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var four = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var five = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var six = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&one);
    one.next = @intFromPtr(&two);
    one.pprev = @intFromPtr(&head.first);
    two.next = @intFromPtr(&three);
    two.pprev = @intFromPtr(&one.next);
    three.next = @intFromPtr(&four);
    three.pprev = @intFromPtr(&two.next);
    four.next = @intFromPtr(&five);
    four.pprev = @intFromPtr(&three.next);
    five.next = @intFromPtr(&six);
    five.pprev = @intFromPtr(&four.next);
    six.next = 0;
    six.pprev = @intFromPtr(&five.next);

    head.first = @intFromPtr(&two);
    two.next = @intFromPtr(&four);
    four.next = @intFromPtr(&six);
    six.next = @intFromPtr(&one);
    one.next = @intFromPtr(&three);
    three.next = @intFromPtr(&five);
    five.next = 0;

    const view = hlist_view.HListView.init(&head);
    const order = [_]*const hlist_view.HListNode{ &two, &four, &six, &one, &three, &five };

    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &two), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &five), view.last());
    try std.testing.expect(view.tailNextIsNull());
    try expectHListOrder(view, &order);
    try expectHListBreak(view, 0, &head.first, &one.next);

    two.pprev = @intFromPtr(&head.first);
    try expectHListBreak(view, 1, &two.next, &three.next);

    four.pprev = @intFromPtr(&two.next);
    try expectHListBreak(view, 2, &four.next, &five.next);

    six.pprev = @intFromPtr(&four.next);
    try expectHListBreak(view, 3, &six.next, &head.first);

    one.pprev = @intFromPtr(&six.next);
    try expectHListBreak(view, 4, &one.next, &two.next);

    three.pprev = @intFromPtr(&one.next);
    try expectHListBreak(view, 5, &three.next, &four.next);

    five.pprev = @intFromPtr(&three.next);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}
