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

test "phase3 list/hlist middle shadow rejoin replay keeps the live list middle route visible while a shadow rejoin stays off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var exit = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_exit = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&middle);
    left.prev = @intFromPtr(&first);
    middle.next = @intFromPtr(&right);
    middle.prev = @intFromPtr(&left);
    right.next = @intFromPtr(&exit);
    right.prev = @intFromPtr(&middle);
    exit.next = @intFromPtr(&tail);
    exit.prev = @intFromPtr(&right);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&exit);

    shadow_middle.next = @intFromPtr(&shadow_exit);
    shadow_middle.prev = @intFromPtr(&left);
    shadow_exit.next = @intFromPtr(&exit);
    shadow_exit.prev = @intFromPtr(&shadow_middle);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 6), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &left, &middle, &right, &exit, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist middle shadow rejoin replay reports the first visible list break when the shadow middle rejoins early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var right = list_view.ListHead{ .next = 0, .prev = 0 };
    var exit = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_exit = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&left);
    first.prev = @intFromPtr(&head);
    left.next = @intFromPtr(&shadow_middle);
    left.prev = @intFromPtr(&first);
    shadow_middle.next = @intFromPtr(&shadow_exit);
    shadow_middle.prev = @intFromPtr(&left);
    shadow_exit.next = @intFromPtr(&exit);
    shadow_exit.prev = @intFromPtr(&shadow_middle);
    exit.next = @intFromPtr(&tail);
    exit.prev = @intFromPtr(&right);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&exit);

    middle.next = @intFromPtr(&right);
    middle.prev = @intFromPtr(&left);
    right.next = @intFromPtr(&exit);
    right.prev = @intFromPtr(&middle);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &left, &shadow_middle, &shadow_exit, &exit, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_exit)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist middle shadow rejoin replay keeps the live hlist middle route visible while a shadow rejoin stays off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var exit = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_exit = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&middle);
    left.pprev = @intFromPtr(&first.next);
    middle.next = @intFromPtr(&right);
    middle.pprev = @intFromPtr(&left.next);
    right.next = @intFromPtr(&exit);
    right.pprev = @intFromPtr(&middle.next);
    exit.next = @intFromPtr(&tail);
    exit.pprev = @intFromPtr(&right.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&exit.next);

    shadow_middle.next = @intFromPtr(&shadow_exit);
    shadow_middle.pprev = 0;
    shadow_exit.next = @intFromPtr(&exit);
    shadow_exit.pprev = @intFromPtr(&shadow_middle.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 6), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &left, &middle, &right, &exit, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist middle shadow rejoin replay reports the first visible hlist break when the shadow middle rejoins early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var exit = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_exit = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&left);
    first.pprev = @intFromPtr(&head.first);
    left.next = @intFromPtr(&shadow_middle);
    left.pprev = @intFromPtr(&first.next);
    shadow_middle.next = @intFromPtr(&shadow_exit);
    shadow_middle.pprev = @intFromPtr(&left.next);
    shadow_exit.next = @intFromPtr(&exit);
    shadow_exit.pprev = @intFromPtr(&shadow_middle.next);
    exit.next = @intFromPtr(&tail);
    exit.pprev = @intFromPtr(&right.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&exit.next);

    middle.next = @intFromPtr(&right);
    middle.pprev = @intFromPtr(&left.next);
    right.next = @intFromPtr(&exit);
    right.pprev = @intFromPtr(&middle.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &left, &shadow_middle, &shadow_exit, &exit, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_exit.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
