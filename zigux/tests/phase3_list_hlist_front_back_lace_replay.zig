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

test "list front-back lace exposes forward route before backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var one = ListHead{ .next = 0, .prev = 0 };
    var two = ListHead{ .next = 0, .prev = 0 };
    var three = ListHead{ .next = 0, .prev = 0 };
    var four = ListHead{ .next = 0, .prev = 0 };
    var five = ListHead{ .next = 0, .prev = 0 };
    var six = ListHead{ .next = 0, .prev = 0 };

    const nodes = [_]*const ListHead{ &one, &two, &three, &four, &five, &six };

    head.next = @intFromPtr(&six);
    head.prev = @intFromPtr(&three);
    one.next = @intFromPtr(&five);
    two.next = @intFromPtr(&four);
    three.next = @intFromPtr(&head);
    four.next = @intFromPtr(&three);
    five.next = @intFromPtr(&two);
    six.next = @intFromPtr(&one);

    one.prev = @intFromPtr(&head);
    two.prev = @intFromPtr(&one);
    three.prev = @intFromPtr(&two);
    four.prev = @intFromPtr(&three);
    five.prev = @intFromPtr(&four);
    six.prev = @intFromPtr(&five);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqualSlices(usize, &.{ 5, 0, 4, 1, 3, 2 }, &listRoute(view, &nodes));
    try std.testing.expectEqual(@as(usize, 6), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &six), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &three), view.last());
    try std.testing.expect(view.contains(&one));
    try std.testing.expect(view.contains(&four));
    try std.testing.expect(!view.hasConsistentBacklinks());

    var breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five)), breakage.actual_prev);

    six.prev = @intFromPtr(&head);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&six)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);

    one.prev = @intFromPtr(&six);
    breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&one)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&four)), breakage.actual_prev);

    five.prev = @intFromPtr(&one);
    two.prev = @intFromPtr(&five);
    four.prev = @intFromPtr(&two);
    three.prev = @intFromPtr(&four);
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "hlist front-back lace exposes forward route before pprev repair" {
    var head = HListHead{ .first = 0 };
    var one = HListNode{ .next = 0, .pprev = 0 };
    var two = HListNode{ .next = 0, .pprev = 0 };
    var three = HListNode{ .next = 0, .pprev = 0 };
    var four = HListNode{ .next = 0, .pprev = 0 };
    var five = HListNode{ .next = 0, .pprev = 0 };
    var six = HListNode{ .next = 0, .pprev = 0 };

    const nodes = [_]*const HListNode{ &one, &two, &three, &four, &five, &six };

    head.first = @intFromPtr(&six);
    one.next = @intFromPtr(&five);
    two.next = @intFromPtr(&four);
    three.next = 0;
    four.next = @intFromPtr(&three);
    five.next = @intFromPtr(&two);
    six.next = @intFromPtr(&one);

    one.pprev = @intFromPtr(&head.first);
    two.pprev = @intFromPtr(&one.next);
    three.pprev = @intFromPtr(&two.next);
    four.pprev = @intFromPtr(&three.next);
    five.pprev = @intFromPtr(&four.next);
    six.pprev = @intFromPtr(&five.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqualSlices(usize, &.{ 5, 0, 4, 1, 3, 2 }, &hlistRoute(view, &nodes));
    try std.testing.expectEqual(@as(usize, 6), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &six), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &three), view.last());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.contains(&one));
    try std.testing.expect(view.contains(&four));
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());

    var breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five.next)), breakage.actual_pprev);

    six.pprev = @intFromPtr(&head.first);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&six.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);

    one.pprev = @intFromPtr(&six.next);
    breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&one.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&four.next)), breakage.actual_pprev);

    five.pprev = @intFromPtr(&one.next);
    two.pprev = @intFromPtr(&five.next);
    four.pprev = @intFromPtr(&two.next);
    three.pprev = @intFromPtr(&four.next);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
}
