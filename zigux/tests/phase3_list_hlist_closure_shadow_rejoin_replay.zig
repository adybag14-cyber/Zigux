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

test "phase3 list/hlist closure shadow rejoin replay keeps the live list closure visible while a detached shadow suffix stays off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&tail);
    second.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&second);

    shadow_bridge.next = @intFromPtr(&shadow_tail);
    shadow_bridge.prev = @intFromPtr(&second);
    shadow_tail.next = @intFromPtr(&head);
    shadow_tail.prev = @intFromPtr(&shadow_bridge);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &second, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist closure shadow rejoin replay reports the list closure break when a detached shadow suffix is adopted too early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&shadow_tail);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&tail);
    second.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&second);

    shadow_bridge.next = @intFromPtr(&shadow_tail);
    shadow_bridge.prev = @intFromPtr(&second);
    shadow_tail.next = @intFromPtr(&head);
    shadow_tail.prev = @intFromPtr(&shadow_bridge);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &second, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_tail)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist closure shadow rejoin replay keeps the live hlist closure visible while a detached shadow suffix stays off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&tail);
    second.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&second.next);

    shadow_bridge.next = @intFromPtr(&shadow_tail);
    shadow_bridge.pprev = @intFromPtr(&tail.next);
    shadow_tail.next = 0;
    shadow_tail.pprev = @intFromPtr(&shadow_bridge.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &second, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist closure shadow rejoin replay reports the first visible hlist closure break when a detached shadow suffix is adopted too early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&tail);
    second.pprev = @intFromPtr(&first.next);
    tail.next = @intFromPtr(&shadow_bridge);
    tail.pprev = @intFromPtr(&second.next);

    shadow_bridge.next = @intFromPtr(&shadow_tail);
    shadow_bridge.pprev = @intFromPtr(&second.next);
    shadow_tail.next = 0;
    shadow_tail.pprev = @intFromPtr(&shadow_bridge.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &second, &tail, &shadow_bridge, &shadow_tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&second.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
