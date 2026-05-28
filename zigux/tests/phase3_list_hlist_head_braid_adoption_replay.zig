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

test "phase3 list/hlist head braid adoption replay keeps the live head route visible while the alternate braid stays off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&tail);
    second.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&second);

    braid_first.next = @intFromPtr(&braid_second);
    braid_first.prev = @intFromPtr(&head);
    braid_second.next = @intFromPtr(&tail);
    braid_second.prev = @intFromPtr(&braid_first);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &second, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "phase3 list/hlist head braid adoption replay reports the adopted list braid before the head backlink follows" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&braid_first);
    head.prev = @intFromPtr(&tail);
    braid_first.next = @intFromPtr(&braid_second);
    braid_first.prev = @intFromPtr(&first);
    braid_second.next = @intFromPtr(&tail);
    braid_second.prev = @intFromPtr(&braid_first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&braid_second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&tail);
    second.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &braid_first), view.first());
    try expectListSequence(view, &.{ &braid_first, &braid_second, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist head braid adoption replay keeps the live hlist head route visible while the alternate braid stays off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&tail);
    second.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&second.next);

    braid_first.next = @intFromPtr(&braid_second);
    braid_first.pprev = @intFromPtr(&head.first);
    braid_second.next = @intFromPtr(&tail);
    braid_second.pprev = @intFromPtr(&braid_first.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &second, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist head braid adoption replay reports the adopted hlist braid before the head prev-link follows" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&braid_first);
    braid_first.next = @intFromPtr(&braid_second);
    braid_first.pprev = @intFromPtr(&first.next);
    braid_second.next = @intFromPtr(&tail);
    braid_second.pprev = @intFromPtr(&braid_first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&braid_second.next);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&tail);
    second.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &braid_first), view.first());
    try expectHListSequence(view, &.{ &braid_first, &braid_second, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
