const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list view reports stale prefix graft backlinks before repair" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var old_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var old_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var prefix = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&old_first);
    head.prev = @intFromPtr(&old_tail);
    old_first.next = @intFromPtr(&old_tail);
    old_first.prev = @intFromPtr(&head);
    old_tail.next = @intFromPtr(&head);
    old_tail.prev = @intFromPtr(&old_first);

    head.next = @intFromPtr(&prefix);
    prefix.next = @intFromPtr(&old_first);
    prefix.prev = @intFromPtr(&head);

    const stale = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 3), stale.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &prefix), stale.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &old_tail), stale.last());

    const breakage = stale.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&prefix)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try testing.expect(!stale.hasConsistentBacklinks());

    old_first.prev = @intFromPtr(&prefix);

    const repaired = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 3), repaired.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &prefix), repaired.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &old_tail), repaired.last());
    try testing.expect(repaired.hasConsistentBacklinks());
    try testing.expect(repaired.firstBrokenBacklink() == null);

    var it = repaired.iterator();
    try testing.expectEqual(@as(?*const list_view.ListHead, &prefix), it.next());
    try testing.expectEqual(@as(?*const list_view.ListHead, &old_first), it.next());
    try testing.expectEqual(@as(?*const list_view.ListHead, &old_tail), it.next());
    try testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

test "hlist view reports stale prefix graft prev-link before repair" {
    var head = hlist_view.HListHead{ .first = 0 };
    var old_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var old_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var prefix = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&old_first);
    old_first.next = @intFromPtr(&old_tail);
    old_first.pprev = @intFromPtr(&head.first);
    old_tail.next = 0;
    old_tail.pprev = @intFromPtr(&old_first.next);

    head.first = @intFromPtr(&prefix);
    prefix.next = @intFromPtr(&old_first);
    prefix.pprev = @intFromPtr(&head.first);

    const stale = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 3), stale.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &prefix), stale.first());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &old_tail), stale.last());
    try testing.expect(stale.firstPprevMatchesHead());
    try testing.expect(stale.tailNextIsNull());

    const breakage = stale.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&prefix.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try testing.expect(!stale.hasConsistentPrevLinks());

    old_first.pprev = @intFromPtr(&prefix.next);

    const repaired = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 3), repaired.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &prefix), repaired.first());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &old_tail), repaired.last());
    try testing.expect(repaired.firstPprevMatchesHead());
    try testing.expect(repaired.hasConsistentPrevLinks());
    try testing.expect(repaired.firstBrokenPrevLink() == null);
    try testing.expect(repaired.tailNextIsNull());

    var it = repaired.iterator();
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &prefix), it.next());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &old_first), it.next());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &old_tail), it.next());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}
