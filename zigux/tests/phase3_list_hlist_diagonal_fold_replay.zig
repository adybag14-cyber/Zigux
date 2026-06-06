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

test "list view observes diagonal-fold route before staged backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var one = ListHead{ .next = 0, .prev = 0 };
    var two = ListHead{ .next = 0, .prev = 0 };
    var three = ListHead{ .next = 0, .prev = 0 };
    var four = ListHead{ .next = 0, .prev = 0 };
    var five = ListHead{ .next = 0, .prev = 0 };
    var six = ListHead{ .next = 0, .prev = 0 };
    var detached = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&four);
    head.prev = @intFromPtr(&six);
    four.next = @intFromPtr(&two);
    two.next = @intFromPtr(&six);
    six.next = @intFromPtr(&one);
    one.next = @intFromPtr(&five);
    five.next = @intFromPtr(&three);
    three.next = @intFromPtr(&head);

    one.prev = @intFromPtr(&head);
    two.prev = @intFromPtr(&one);
    three.prev = @intFromPtr(&two);
    four.prev = @intFromPtr(&three);
    five.prev = @intFromPtr(&four);
    six.prev = @intFromPtr(&five);
    detached.next = @intFromPtr(&detached);
    detached.prev = @intFromPtr(&detached);

    const view = ListView.init(&head);
    const route = [_]*const ListHead{ &four, &two, &six, &one, &five, &three };
    try expectListOrder(view, &route);
    try std.testing.expectEqual(@as(?*const ListHead, &four), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &six), view.last());
    try std.testing.expect(!view.contains(&head));
    try std.testing.expect(!view.contains(&detached));

    var breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&three)), breakage.actual_prev);

    four.prev = @intFromPtr(&head);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&four)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&one)), breakage.actual_prev);

    two.prev = @intFromPtr(&four);
    six.prev = @intFromPtr(&two);
    one.prev = @intFromPtr(&six);
    five.prev = @intFromPtr(&one);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 5), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&two)), breakage.actual_prev);

    three.prev = @intFromPtr(&five);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 6), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&three)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&six)), breakage.actual_prev);

    head.prev = @intFromPtr(&three);
    try std.testing.expectEqual(@as(?*const ListHead, &three), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "hlist view observes diagonal-fold route before staged prev-link repair" {
    var head = HListHead{ .first = 0 };
    var one = HListNode{ .next = 0, .pprev = 0 };
    var two = HListNode{ .next = 0, .pprev = 0 };
    var three = HListNode{ .next = 0, .pprev = 0 };
    var four = HListNode{ .next = 0, .pprev = 0 };
    var five = HListNode{ .next = 0, .pprev = 0 };
    var six = HListNode{ .next = 0, .pprev = 0 };
    var detached = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&four);
    four.next = @intFromPtr(&two);
    two.next = @intFromPtr(&six);
    six.next = @intFromPtr(&one);
    one.next = @intFromPtr(&five);
    five.next = @intFromPtr(&three);
    three.next = 0;

    one.pprev = @intFromPtr(&head.first);
    two.pprev = @intFromPtr(&one.next);
    three.pprev = @intFromPtr(&two.next);
    four.pprev = @intFromPtr(&three.next);
    five.pprev = @intFromPtr(&four.next);
    six.pprev = @intFromPtr(&five.next);

    const view = HListView.init(&head);
    const route = [_]*const HListNode{ &four, &two, &six, &one, &five, &three };
    try expectHListOrder(view, &route);
    try std.testing.expectEqual(@as(?*const HListNode, &four), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &three), view.last());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(!view.contains(&detached));

    var breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&three.next)), breakage.actual_pprev);

    four.pprev = @intFromPtr(&head.first);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&four.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&one.next)), breakage.actual_pprev);

    two.pprev = @intFromPtr(&four.next);
    six.pprev = @intFromPtr(&two.next);
    one.pprev = @intFromPtr(&six.next);
    five.pprev = @intFromPtr(&one.next);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 5), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&two.next)), breakage.actual_pprev);

    three.pprev = @intFromPtr(&five.next);

    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
}
