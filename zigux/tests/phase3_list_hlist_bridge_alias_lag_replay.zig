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

test "phase3 list/hlist bridge alias lag replay keeps the live bridge visible while the detached alias stays off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var alias = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&bridge);
    middle.prev = @intFromPtr(&first);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&middle);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge);

    alias.next = @intFromPtr(&bridge);
    alias.prev = @intFromPtr(&middle);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &middle, &bridge, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist bridge alias lag replay reports the adopted list alias before the bridge backlink follows" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var alias = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&alias);
    middle.prev = @intFromPtr(&first);
    alias.next = @intFromPtr(&bridge);
    alias.prev = @intFromPtr(&middle);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&middle);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &middle, &alias, &bridge, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&alias)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist bridge alias lag replay keeps the live bridge visible while the detached hlist alias stays off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alias = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&bridge);
    middle.pprev = @intFromPtr(&first.next);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&middle.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge.next);

    alias.next = @intFromPtr(&bridge);
    alias.pprev = @intFromPtr(&middle.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &middle, &bridge, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist bridge alias lag replay reports the adopted hlist alias before the bridge prev-link follows" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alias = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&alias);
    middle.pprev = @intFromPtr(&first.next);
    alias.next = @intFromPtr(&bridge);
    alias.pprev = @intFromPtr(&middle.next);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&middle.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try expectHListSequence(view, &.{ &first, &middle, &alias, &bridge, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&alias.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}