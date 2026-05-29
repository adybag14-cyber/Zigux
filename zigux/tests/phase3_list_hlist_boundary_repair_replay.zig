const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list boundary replay repairs first and sentinel backlinks without hiding traversal" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = 0;
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    const broken_first = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 2), broken_first.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), broken_first.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &second), broken_first.last());

    const first_breakage = broken_first.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 0), first_breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&head)), first_breakage.expected_prev);
    try testing.expectEqual(@as(usize, 0), first_breakage.actual_prev);

    first.prev = @intFromPtr(&head);
    head.prev = @intFromPtr(&first);

    const broken_tail = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 2), broken_tail.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), broken_tail.last());

    const tail_breakage = broken_tail.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 2), tail_breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&second)), tail_breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&first)), tail_breakage.actual_prev);

    head.prev = @intFromPtr(&second);
    try testing.expect(list_view.ListView.init(&head).hasConsistentBacklinks());
}

test "hlist boundary replay repairs head and tail prev-link slots" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&second.next);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    const broken_head = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 2), broken_head.len());
    try testing.expect(!broken_head.firstPprevMatchesHead());
    try testing.expect(broken_head.tailNextIsNull());

    const head_breakage = broken_head.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 0), head_breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&head.first)), head_breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&second.next)), head_breakage.actual_pprev);

    first.pprev = @intFromPtr(&head.first);
    second.pprev = @intFromPtr(&head.first);
    const broken_tail = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 2), broken_tail.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), broken_tail.first());
    try testing.expect(broken_tail.firstPprevMatchesHead());

    const tail_breakage = broken_tail.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 1), tail_breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&first.next)), tail_breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head.first)), tail_breakage.actual_pprev);

    second.pprev = @intFromPtr(&first.next);
    const repaired = hlist_view.HListView.init(&head);
    try testing.expect(repaired.tailNextIsNull());
    try testing.expect(repaired.hasConsistentPrevLinks());
}
