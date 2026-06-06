const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;

fn listRoute(view: list_view.ListView, nodes: []const *const ListHead) [6]usize {
    var route: [6]usize = undefined;
    var count: usize = 0;
    var it = view.iterator();

    while (it.next()) |node| {
        route[count] = indexOf(ListHead, nodes, node);
        count += 1;
    }

    std.debug.assert(count == route.len);
    return route;
}

fn hlistRoute(view: hlist_view.HListView, nodes: []const *const HListNode) [6]usize {
    var route: [6]usize = undefined;
    var count: usize = 0;
    var it = view.iterator();

    while (it.next()) |node| {
        route[count] = indexOf(HListNode, nodes, node);
        count += 1;
    }

    std.debug.assert(count == route.len);
    return route;
}

fn indexOf(comptime T: type, nodes: []const *const T, needle: *const T) usize {
    for (nodes, 0..) |node, index| {
        if (node == needle) return index;
    }
    unreachable;
}

test "list double-pivot ladder exposes forward route before backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var one = ListHead{ .next = 0, .prev = 0 };
    var two = ListHead{ .next = 0, .prev = 0 };
    var three = ListHead{ .next = 0, .prev = 0 };
    var four = ListHead{ .next = 0, .prev = 0 };
    var five = ListHead{ .next = 0, .prev = 0 };
    var six = ListHead{ .next = 0, .prev = 0 };

    const nodes = [_]*const ListHead{ &one, &two, &three, &four, &five, &six };

    head.next = @intFromPtr(&three);
    head.prev = @intFromPtr(&two);
    one.next = @intFromPtr(&six);
    two.next = @intFromPtr(&head);
    three.next = @intFromPtr(&one);
    four.next = @intFromPtr(&five);
    five.next = @intFromPtr(&two);
    six.next = @intFromPtr(&four);

    one.prev = @intFromPtr(&head);
    two.prev = @intFromPtr(&one);
    three.prev = @intFromPtr(&two);
    four.prev = @intFromPtr(&three);
    five.prev = @intFromPtr(&four);
    six.prev = @intFromPtr(&five);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqualSlices(usize, &.{ 2, 0, 5, 3, 4, 1 }, &listRoute(view, &nodes));
    try std.testing.expectEqual(@as(usize, 6), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &three), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &two), view.last());
    try std.testing.expect(view.contains(&one));
    try std.testing.expect(view.contains(&six));
    try std.testing.expect(!view.hasConsistentBacklinks());

    var breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&two)), breakage.actual_prev);

    three.prev = @intFromPtr(&head);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&three)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);

    one.prev = @intFromPtr(&three);
    six.prev = @intFromPtr(&one);
    four.prev = @intFromPtr(&six);
    five.prev = @intFromPtr(&four);
    two.prev = @intFromPtr(&five);
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "hlist double-pivot ladder exposes forward route before pprev repair" {
    var head = HListHead{ .first = 0 };
    var one = HListNode{ .next = 0, .pprev = 0 };
    var two = HListNode{ .next = 0, .pprev = 0 };
    var three = HListNode{ .next = 0, .pprev = 0 };
    var four = HListNode{ .next = 0, .pprev = 0 };
    var five = HListNode{ .next = 0, .pprev = 0 };
    var six = HListNode{ .next = 0, .pprev = 0 };

    const nodes = [_]*const HListNode{ &one, &two, &three, &four, &five, &six };

    head.first = @intFromPtr(&three);
    one.next = @intFromPtr(&six);
    two.next = 0;
    three.next = @intFromPtr(&one);
    four.next = @intFromPtr(&five);
    five.next = @intFromPtr(&two);
    six.next = @intFromPtr(&four);

    one.pprev = @intFromPtr(&head.first);
    two.pprev = @intFromPtr(&one.next);
    three.pprev = @intFromPtr(&two.next);
    four.pprev = @intFromPtr(&three.next);
    five.pprev = @intFromPtr(&four.next);
    six.pprev = @intFromPtr(&five.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqualSlices(usize, &.{ 2, 0, 5, 3, 4, 1 }, &hlistRoute(view, &nodes));
    try std.testing.expectEqual(@as(usize, 6), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &three), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &two), view.last());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.contains(&one));
    try std.testing.expect(view.contains(&six));
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());

    var breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&two.next)), breakage.actual_pprev);

    three.pprev = @intFromPtr(&head.first);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&three.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);

    one.pprev = @intFromPtr(&three.next);
    six.pprev = @intFromPtr(&one.next);
    four.pprev = @intFromPtr(&six.next);
    five.pprev = @intFromPtr(&four.next);
    two.pprev = @intFromPtr(&five.next);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
}
