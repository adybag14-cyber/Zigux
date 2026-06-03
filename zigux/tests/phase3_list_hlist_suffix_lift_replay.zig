const testing = @import("std").testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list suffix lift keeps forward route while stale prefix backlink is detected" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var detached_prefix = list_view.ListHead{ .next = 0, .prev = 0 };
    var lifted_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var lifted_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&lifted_first);
    head.prev = @intFromPtr(&lifted_tail);
    detached_prefix.next = @intFromPtr(&lifted_first);
    detached_prefix.prev = @intFromPtr(&head);
    lifted_first.next = @intFromPtr(&lifted_tail);
    lifted_first.prev = @intFromPtr(&detached_prefix);
    lifted_tail.next = @intFromPtr(&head);
    lifted_tail.prev = @intFromPtr(&lifted_first);

    var view = list_view.ListView.init(&head);
    try testing.expect(!view.isEmpty());
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &lifted_first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &lifted_tail), view.last());

    const stale_prefix = view.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 0), stale_prefix.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&head)), stale_prefix.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&detached_prefix)), stale_prefix.actual_prev);
    try testing.expect(!view.hasConsistentBacklinks());

    lifted_first.prev = @intFromPtr(&head);
    view = list_view.ListView.init(&head);
    try testing.expect(view.hasConsistentBacklinks());
    try testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist suffix lift keeps tail null while stale prefix pprev is detected" {
    var head = hlist_view.HListHead{ .first = 0 };
    var detached_prefix = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var lifted_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var lifted_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&lifted_first);
    detached_prefix.next = @intFromPtr(&lifted_first);
    detached_prefix.pprev = @intFromPtr(&head.first);
    lifted_first.next = @intFromPtr(&lifted_tail);
    lifted_first.pprev = @intFromPtr(&detached_prefix.next);
    lifted_tail.next = 0;
    lifted_tail.pprev = @intFromPtr(&lifted_first.next);

    var view = hlist_view.HListView.init(&head);
    try testing.expect(!view.isEmpty());
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &lifted_first), view.first());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &lifted_tail), view.last());
    try testing.expect(view.tailNextIsNull());

    const stale_prefix = view.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 0), stale_prefix.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&head.first)), stale_prefix.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&detached_prefix.next)), stale_prefix.actual_pprev);
    try testing.expect(!view.firstPprevMatchesHead());
    try testing.expect(!view.hasConsistentPrevLinks());

    lifted_first.pprev = @intFromPtr(&head.first);
    view = hlist_view.HListView.init(&head);
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.firstBrokenPrevLink() == null);
}
