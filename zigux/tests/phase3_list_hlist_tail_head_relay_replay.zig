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

fn listRoute(view: list_view.ListView, nodes: []const *const ListHead) [7]usize {
    var route: [7]usize = undefined;
    var count: usize = 0;
    var it = view.iterator();

    while (it.next()) |node| {
        route[count] = indexOf(ListHead, nodes, node);
        count += 1;
    }

    std.debug.assert(count == route.len);
    return route;
}

fn hlistRoute(view: hlist_view.HListView, nodes: []const *const HListNode) [7]usize {
    var route: [7]usize = undefined;
    var count: usize = 0;
    var it = view.iterator();

    while (it.next()) |node| {
        route[count] = indexOf(HListNode, nodes, node);
        count += 1;
    }

    std.debug.assert(count == route.len);
    return route;
}

test "list tail-head relay repairs backlinks from the outside inward" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var one = ListHead{ .next = 0, .prev = 0 };
    var two = ListHead{ .next = 0, .prev = 0 };
    var three = ListHead{ .next = 0, .prev = 0 };
    var four = ListHead{ .next = 0, .prev = 0 };
    var five = ListHead{ .next = 0, .prev = 0 };
    var six = ListHead{ .next = 0, .prev = 0 };
    var seven = ListHead{ .next = 0, .prev = 0 };
    var detached = ListHead{ .next = 0, .prev = 0 };

    const nodes = [_]*const ListHead{ &one, &two, &three, &four, &five, &six, &seven };

    head.next = @intFromPtr(&seven);
    head.prev = @intFromPtr(&four);
    one.next = @intFromPtr(&six);
    two.next = @intFromPtr(&five);
    three.next = @intFromPtr(&four);
    four.next = @intFromPtr(&head);
    five.next = @intFromPtr(&three);
    six.next = @intFromPtr(&two);
    seven.next = @intFromPtr(&one);
    detached.next = @intFromPtr(&detached);
    detached.prev = @intFromPtr(&detached);

    one.prev = @intFromPtr(&head);
    two.prev = @intFromPtr(&one);
    three.prev = @intFromPtr(&two);
    four.prev = @intFromPtr(&three);
    five.prev = @intFromPtr(&four);
    six.prev = @intFromPtr(&five);
    seven.prev = @intFromPtr(&six);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqualSlices(usize, &.{ 6, 0, 5, 1, 4, 2, 3 }, &listRoute(view, &nodes));
    try std.testing.expectEqual(@as(usize, 7), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &seven), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &four), view.last());
    try std.testing.expect(view.contains(&two));
    try std.testing.expect(view.contains(&five));
    try std.testing.expect(!view.contains(&detached));
    try std.testing.expect(!view.hasConsistentBacklinks());

    var breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&six)), breakage.actual_prev);

    seven.prev = @intFromPtr(&head);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&seven)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);

    one.prev = @intFromPtr(&seven);
    six.prev = @intFromPtr(&one);
    two.prev = @intFromPtr(&six);
    five.prev = @intFromPtr(&two);
    three.prev = @intFromPtr(&five);
    four.prev = @intFromPtr(&three);
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "hlist tail-head relay repairs pprev links from the outside inward" {
    var head = HListHead{ .first = 0 };
    var one = HListNode{ .next = 0, .pprev = 0 };
    var two = HListNode{ .next = 0, .pprev = 0 };
    var three = HListNode{ .next = 0, .pprev = 0 };
    var four = HListNode{ .next = 0, .pprev = 0 };
    var five = HListNode{ .next = 0, .pprev = 0 };
    var six = HListNode{ .next = 0, .pprev = 0 };
    var seven = HListNode{ .next = 0, .pprev = 0 };
    var detached = HListNode{ .next = 0, .pprev = 0 };

    const nodes = [_]*const HListNode{ &one, &two, &three, &four, &five, &six, &seven };

    head.first = @intFromPtr(&seven);
    one.next = @intFromPtr(&six);
    two.next = @intFromPtr(&five);
    three.next = @intFromPtr(&four);
    four.next = 0;
    five.next = @intFromPtr(&three);
    six.next = @intFromPtr(&two);
    seven.next = @intFromPtr(&one);
    detached.next = 0;
    detached.pprev = 0;

    one.pprev = @intFromPtr(&head.first);
    two.pprev = @intFromPtr(&one.next);
    three.pprev = @intFromPtr(&two.next);
    four.pprev = @intFromPtr(&three.next);
    five.pprev = @intFromPtr(&four.next);
    six.pprev = @intFromPtr(&five.next);
    seven.pprev = @intFromPtr(&six.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqualSlices(usize, &.{ 6, 0, 5, 1, 4, 2, 3 }, &hlistRoute(view, &nodes));
    try std.testing.expectEqual(@as(usize, 7), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &seven), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &four), view.last());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.contains(&two));
    try std.testing.expect(view.contains(&five));
    try std.testing.expect(!view.contains(&detached));
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());

    var breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&six.next)), breakage.actual_pprev);

    seven.pprev = @intFromPtr(&head.first);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&seven.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);

    one.pprev = @intFromPtr(&seven.next);
    six.pprev = @intFromPtr(&one.next);
    two.pprev = @intFromPtr(&six.next);
    five.pprev = @intFromPtr(&two.next);
    three.pprev = @intFromPtr(&five.next);
    four.pprev = @intFromPtr(&three.next);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
}
