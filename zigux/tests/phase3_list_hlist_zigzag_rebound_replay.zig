const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

fn expectListRoute(view: ListView, expected: []const *const ListHead) !void {
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(expected.len, view.len());
    try std.testing.expectEqual(@as(?*const ListHead, expected[0]), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, expected[expected.len - 1]), view.last());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const ListHead, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

fn expectHListRoute(view: HListView, expected: []const *const HListNode) !void {
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(expected.len, view.len());
    try std.testing.expectEqual(@as(?*const HListNode, expected[0]), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, expected[expected.len - 1]), view.last());
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const HListNode, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "list view witnesses zigzag rebound before backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var one = ListHead{ .next = 0, .prev = 0 };
    var two = ListHead{ .next = 0, .prev = 0 };
    var three = ListHead{ .next = 0, .prev = 0 };
    var four = ListHead{ .next = 0, .prev = 0 };
    var five = ListHead{ .next = 0, .prev = 0 };
    var six = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&two);
    head.prev = @intFromPtr(&four);
    two.next = @intFromPtr(&five);
    five.next = @intFromPtr(&one);
    one.next = @intFromPtr(&six);
    six.next = @intFromPtr(&three);
    three.next = @intFromPtr(&four);
    four.next = @intFromPtr(&head);

    one.prev = @intFromPtr(&head);
    two.prev = @intFromPtr(&one);
    three.prev = @intFromPtr(&two);
    four.prev = @intFromPtr(&three);
    five.prev = @intFromPtr(&four);
    six.prev = @intFromPtr(&five);

    const view = ListView.init(&head);
    try expectListRoute(view, &.{ &two, &five, &one, &six, &three, &four });

    var breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&one)), breakage.actual_prev);

    two.prev = @intFromPtr(&head);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&two)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&four)), breakage.actual_prev);

    five.prev = @intFromPtr(&two);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);

    one.prev = @intFromPtr(&five);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&one)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five)), breakage.actual_prev);

    six.prev = @intFromPtr(&one);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&six)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&two)), breakage.actual_prev);

    three.prev = @intFromPtr(&six);
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist view witnesses zigzag rebound before prev-link repair" {
    var head = HListHead{ .first = 0 };
    var one = HListNode{ .next = 0, .pprev = 0 };
    var two = HListNode{ .next = 0, .pprev = 0 };
    var three = HListNode{ .next = 0, .pprev = 0 };
    var four = HListNode{ .next = 0, .pprev = 0 };
    var five = HListNode{ .next = 0, .pprev = 0 };
    var six = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&two);
    two.next = @intFromPtr(&five);
    five.next = @intFromPtr(&one);
    one.next = @intFromPtr(&six);
    six.next = @intFromPtr(&three);
    three.next = @intFromPtr(&four);
    four.next = 0;

    one.pprev = @intFromPtr(&head.first);
    two.pprev = @intFromPtr(&one.next);
    three.pprev = @intFromPtr(&two.next);
    four.pprev = @intFromPtr(&three.next);
    five.pprev = @intFromPtr(&four.next);
    six.pprev = @intFromPtr(&five.next);

    const view = HListView.init(&head);
    try expectHListRoute(view, &.{ &two, &five, &one, &six, &three, &four });
    try std.testing.expect(!view.firstPprevMatchesHead());

    var breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&one.next)), breakage.actual_pprev);

    two.pprev = @intFromPtr(&head.first);
    try std.testing.expect(view.firstPprevMatchesHead());
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&two.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&four.next)), breakage.actual_pprev);

    five.pprev = @intFromPtr(&two.next);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);

    one.pprev = @intFromPtr(&five.next);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&one.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five.next)), breakage.actual_pprev);

    six.pprev = @intFromPtr(&one.next);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&six.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&two.next)), breakage.actual_pprev);

    three.pprev = @intFromPtr(&six.next);
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}
