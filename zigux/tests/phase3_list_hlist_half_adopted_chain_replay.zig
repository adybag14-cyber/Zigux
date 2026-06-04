const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list view reports a forward-adopted chain before tail metadata catches up" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&head);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    const half_adopted = list_view.ListView.init(&head);
    try testing.expect(!half_adopted.isEmpty());
    try testing.expect(!half_adopted.isSingular());
    try testing.expectEqual(@as(usize, 2), half_adopted.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), half_adopted.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, null), half_adopted.last());
    try testing.expect(!half_adopted.hasConsistentBacklinks());

    const breakage = half_adopted.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);

    head.prev = @intFromPtr(&second);
    const repaired = list_view.ListView.init(&head);
    try testing.expectEqual(@as(?*const list_view.ListHead, &second), repaired.last());
    try testing.expect(repaired.hasConsistentBacklinks());
    try testing.expect(repaired.firstBrokenBacklink() == null);
}

test "hlist view reports a head-adopted chain before first pprev catches up" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = 0;
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    const half_adopted = hlist_view.HListView.init(&head);
    try testing.expect(!half_adopted.isEmpty());
    try testing.expect(!half_adopted.isSingular());
    try testing.expectEqual(@as(usize, 2), half_adopted.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), half_adopted.first());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &second), half_adopted.last());
    try testing.expect(!half_adopted.firstPprevMatchesHead());
    try testing.expect(!half_adopted.hasConsistentPrevLinks());
    try testing.expect(half_adopted.tailNextIsNull());

    const breakage = half_adopted.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 0), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, 0), breakage.actual_pprev);

    first.pprev = @intFromPtr(&head.first);
    const repaired = hlist_view.HListView.init(&head);
    try testing.expect(repaired.firstPprevMatchesHead());
    try testing.expect(repaired.hasConsistentPrevLinks());
    try testing.expect(repaired.firstBrokenPrevLink() == null);
}
