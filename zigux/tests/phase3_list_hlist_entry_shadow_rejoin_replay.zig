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

test "phase3 list/hlist entry shadow rejoin replay keeps the live entry route visible while a shadow prefix stays off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&bridge);
    second.prev = @intFromPtr(&first);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&second);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge);

    shadow_first.next = @intFromPtr(&shadow_second);
    shadow_first.prev = @intFromPtr(&head);
    shadow_second.next = @intFromPtr(&second);
    shadow_second.prev = @intFromPtr(&shadow_first);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &second, &bridge, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist entry shadow rejoin replay reports the first visible list break when the shadow prefix rejoins early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&shadow_first);
    head.prev = @intFromPtr(&tail);
    shadow_first.next = @intFromPtr(&shadow_second);
    shadow_first.prev = @intFromPtr(&head);
    shadow_second.next = @intFromPtr(&second);
    shadow_second.prev = @intFromPtr(&shadow_first);
    second.next = @intFromPtr(&bridge);
    second.prev = @intFromPtr(&first);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&second);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge);

    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &shadow_first, &shadow_second, &second, &bridge, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_second)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist entry shadow rejoin replay keeps the live hlist entry route visible while a shadow prefix stays off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&bridge);
    second.pprev = @intFromPtr(&first.next);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&second.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge.next);

    shadow_first.next = @intFromPtr(&shadow_second);
    shadow_first.pprev = @intFromPtr(&head.first);
    shadow_second.next = @intFromPtr(&second);
    shadow_second.pprev = @intFromPtr(&shadow_first.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &second, &bridge, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist entry shadow rejoin replay reports the first visible hlist break when the shadow prefix rejoins early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&shadow_first);
    shadow_first.next = @intFromPtr(&shadow_second);
    shadow_first.pprev = @intFromPtr(&head.first);
    shadow_second.next = @intFromPtr(&second);
    shadow_second.pprev = @intFromPtr(&shadow_first.next);
    second.next = @intFromPtr(&bridge);
    second.pprev = @intFromPtr(&first.next);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&second.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge.next);

    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &shadow_first, &shadow_second, &second, &bridge, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_second.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
