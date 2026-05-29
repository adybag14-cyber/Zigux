const std = @import("std");
const list = @import("list_view");
const hlist = @import("hlist_view");

test "list split-join braid exposes stale rejoin backlink before repair" {
    var head = list.ListHead{ .next = 0, .prev = 0 };
    var live_left = list.ListHead{ .next = 0, .prev = 0 };
    var braid_left = list.ListHead{ .next = 0, .prev = 0 };
    var braid_right = list.ListHead{ .next = 0, .prev = 0 };
    var rejoin = list.ListHead{ .next = 0, .prev = 0 };
    var tail = list.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_left);
    head.prev = @intFromPtr(&tail);
    live_left.next = @intFromPtr(&braid_left);
    live_left.prev = @intFromPtr(&head);
    braid_left.next = @intFromPtr(&braid_right);
    braid_left.prev = @intFromPtr(&live_left);
    braid_right.next = @intFromPtr(&rejoin);
    braid_right.prev = @intFromPtr(&braid_left);
    rejoin.next = @intFromPtr(&tail);
    rejoin.prev = @intFromPtr(&live_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&rejoin);

    const view = list.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const list.ListHead, &live_left), view.first());
    try std.testing.expectEqual(@as(?*const list.ListHead, &tail), view.last());

    const stale_rejoin = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), stale_rejoin.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&braid_right)), stale_rejoin.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_left)), stale_rejoin.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    rejoin.prev = @intFromPtr(&braid_right);
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist split-join braid mirrors stale rejoin prev-link before repair" {
    var head = hlist.HListHead{ .first = 0 };
    var live_left = hlist.HListNode{ .next = 0, .pprev = 0 };
    var braid_left = hlist.HListNode{ .next = 0, .pprev = 0 };
    var braid_right = hlist.HListNode{ .next = 0, .pprev = 0 };
    var rejoin = hlist.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_left);
    live_left.next = @intFromPtr(&braid_left);
    live_left.pprev = @intFromPtr(&head.first);
    braid_left.next = @intFromPtr(&braid_right);
    braid_left.pprev = @intFromPtr(&live_left.next);
    braid_right.next = @intFromPtr(&rejoin);
    braid_right.pprev = @intFromPtr(&braid_left.next);
    rejoin.next = @intFromPtr(&tail);
    rejoin.pprev = @intFromPtr(&live_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&rejoin.next);

    const view = hlist.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const hlist.HListNode, &live_left), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());

    const stale_rejoin = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), stale_rejoin.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&braid_right.next)), stale_rejoin.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_left.next)), stale_rejoin.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    rejoin.pprev = @intFromPtr(&braid_right.next);
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}
