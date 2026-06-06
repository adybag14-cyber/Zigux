const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;

fn indexOf(comptime T: type, nodes: []const *const T, needle: *const T) usize {
    for (nodes, 0..) |node, index| {
        if (node == needle) return index;
    }
    unreachable;
}

fn listRoute(view: list_view.ListView, nodes: []const *const ListHead) [8]usize {
    var route: [8]usize = undefined;
    var count: usize = 0;
    var it = view.iterator();

    while (it.next()) |node| {
        route[count] = indexOf(ListHead, nodes, node);
        count += 1;
    }

    std.debug.assert(count == route.len);
    return route;
}

fn hlistRoute(view: hlist_view.HListView, nodes: []const *const HListNode) [8]usize {
    var route: [8]usize = undefined;
    var count: usize = 0;
    var it = view.iterator();

    while (it.next()) |node| {
        route[count] = indexOf(HListNode, nodes, node);
        count += 1;
    }

    std.debug.assert(count == route.len);
    return route;
}

test "list octant spoke relay repairs backlinks across four spokes" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var one = ListHead{ .next = 0, .prev = 0 };
    var two = ListHead{ .next = 0, .prev = 0 };
    var three = ListHead{ .next = 0, .prev = 0 };
    var four = ListHead{ .next = 0, .prev = 0 };
    var five = ListHead{ .next = 0, .prev = 0 };
    var six = ListHead{ .next = 0, .prev = 0 };
    var seven = ListHead{ .next = 0, .prev = 0 };
    var eight = ListHead{ .next = 0, .prev = 0 };
    var detached = ListHead{ .next = 0, .prev = 0 };

    const nodes = [_]*const ListHead{ &one, &two, &three, &four, &five, &six, &seven, &eight };

    head.next = @intFromPtr(&eight);
    head.prev = @intFromPtr(&five);
    one.next = @intFromPtr(&seven);
    two.next = @intFromPtr(&five);
    three.next = @intFromPtr(&six);
    four.next = @intFromPtr(&one);
    five.next = @intFromPtr(&head);
    six.next = @intFromPtr(&two);
    seven.next = @intFromPtr(&three);
    eight.next = @intFromPtr(&four);
    detached.next = @intFromPtr(&detached);
    detached.prev = @intFromPtr(&detached);

    one.prev = @intFromPtr(&head);
    two.prev = @intFromPtr(&one);
    three.prev = @intFromPtr(&two);
    four.prev = @intFromPtr(&three);
    five.prev = @intFromPtr(&four);
    six.prev = @intFromPtr(&five);
    seven.prev = @intFromPtr(&six);
    eight.prev = @intFromPtr(&seven);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqualSlices(usize, &.{ 7, 3, 0, 6, 2, 5, 1, 4 }, &listRoute(view, &nodes));
    try std.testing.expectEqual(@as(usize, 8), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &eight), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &five), view.last());
    try std.testing.expect(view.contains(&one));
    try std.testing.expect(view.contains(&six));
    try std.testing.expect(!view.contains(&detached));
    try std.testing.expect(!view.hasConsistentBacklinks());

    var breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&seven)), breakage.actual_prev);

    eight.prev = @intFromPtr(&head);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&eight)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&three)), breakage.actual_prev);

    four.prev = @intFromPtr(&eight);
    one.prev = @intFromPtr(&four);
    seven.prev = @intFromPtr(&one);
    three.prev = @intFromPtr(&seven);
    six.prev = @intFromPtr(&three);
    two.prev = @intFromPtr(&six);
    five.prev = @intFromPtr(&two);
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "hlist octant spoke relay repairs pprev links across four spokes" {
    var head = HListHead{ .first = 0 };
    var one = HListNode{ .next = 0, .pprev = 0 };
    var two = HListNode{ .next = 0, .pprev = 0 };
    var three = HListNode{ .next = 0, .pprev = 0 };
    var four = HListNode{ .next = 0, .pprev = 0 };
    var five = HListNode{ .next = 0, .pprev = 0 };
    var six = HListNode{ .next = 0, .pprev = 0 };
    var seven = HListNode{ .next = 0, .pprev = 0 };
    var eight = HListNode{ .next = 0, .pprev = 0 };
    var detached = HListNode{ .next = 0, .pprev = 0 };

    const nodes = [_]*const HListNode{ &one, &two, &three, &four, &five, &six, &seven, &eight };

    head.first = @intFromPtr(&eight);
    one.next = @intFromPtr(&seven);
    two.next = @intFromPtr(&five);
    three.next = @intFromPtr(&six);
    four.next = @intFromPtr(&one);
    five.next = 0;
    six.next = @intFromPtr(&two);
    seven.next = @intFromPtr(&three);
    eight.next = @intFromPtr(&four);
    detached.next = 0;
    detached.pprev = 0;

    one.pprev = @intFromPtr(&head.first);
    two.pprev = @intFromPtr(&one.next);
    three.pprev = @intFromPtr(&two.next);
    four.pprev = @intFromPtr(&three.next);
    five.pprev = @intFromPtr(&four.next);
    six.pprev = @intFromPtr(&five.next);
    seven.pprev = @intFromPtr(&six.next);
    eight.pprev = @intFromPtr(&seven.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqualSlices(usize, &.{ 7, 3, 0, 6, 2, 5, 1, 4 }, &hlistRoute(view, &nodes));
    try std.testing.expectEqual(@as(usize, 8), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &eight), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &five), view.last());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.contains(&one));
    try std.testing.expect(view.contains(&six));
    try std.testing.expect(!view.contains(&detached));
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());

    var breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&seven.next)), breakage.actual_pprev);

    eight.pprev = @intFromPtr(&head.first);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&eight.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&three.next)), breakage.actual_pprev);

    four.pprev = @intFromPtr(&eight.next);
    one.pprev = @intFromPtr(&four.next);
    seven.pprev = @intFromPtr(&one.next);
    three.pprev = @intFromPtr(&seven.next);
    six.pprev = @intFromPtr(&three.next);
    two.pprev = @intFromPtr(&six.next);
    five.pprev = @intFromPtr(&two.next);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
}
