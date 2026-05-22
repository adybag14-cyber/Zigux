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

test "phase3 list/hlist bridge pair swap replay keeps the live list bridge order visible while a swapped witness stays off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&bridge);
    left.prev = @intFromPtr(&first);
    bridge.next = @intFromPtr(&right);
    bridge.prev = @intFromPtr(&left);
    right.next = @intFromPtr(&tail);
    right.prev = @intFromPtr(&bridge);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&right);

    shadow_bridge.next = @intFromPtr(&shadow_right);
    shadow_bridge.prev = @intFromPtr(&left);
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.prev = @intFromPtr(&shadow_bridge);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &left, &bridge, &right, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist bridge pair swap replay reports the first visible list break when the bridge pair adopts the swapped order early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&right);
    left.prev = @intFromPtr(&first);
    right.next = @intFromPtr(&bridge);
    right.prev = @intFromPtr(&bridge);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &left, &right, &bridge, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist bridge pair swap replay keeps the live hlist bridge order visible while a swapped witness stays off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&bridge);
    left.pprev = @intFromPtr(&first.next);
    bridge.next = @intFromPtr(&right);
    bridge.pprev = @intFromPtr(&left.next);
    right.next = @intFromPtr(&tail);
    right.pprev = @intFromPtr(&bridge.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&right.next);

    shadow_bridge.next = @intFromPtr(&shadow_right);
    shadow_bridge.pprev = 0;
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.pprev = @intFromPtr(&shadow_bridge.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &left, &bridge, &right, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist bridge pair swap replay reports the first visible hlist break when the bridge pair adopts the swapped order early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&right);
    left.pprev = @intFromPtr(&first.next);
    right.next = @intFromPtr(&bridge);
    right.pprev = @intFromPtr(&bridge.next);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &left, &right, &bridge, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
