const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list segment handoff keeps the live middle segment until the route changes" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_mid = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_mid = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_mid);
    first.prev = @intFromPtr(&head);
    live_mid.next = @intFromPtr(&tail);
    live_mid.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_mid);

    alt_mid.next = @intFromPtr(&tail);
    alt_mid.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try testing.expect(view.hasConsistentBacklinks());
}

test "list segment handoff reports the tail-side stale backlink after forward adoption" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_mid = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_mid = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&alt_mid);
    first.prev = @intFromPtr(&head);
    live_mid.next = @intFromPtr(&tail);
    live_mid.prev = @intFromPtr(&first);
    alt_mid.next = @intFromPtr(&tail);
    alt_mid.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_mid);

    const breakage = list_view.ListView.init(&head).firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&alt_mid)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_mid)), breakage.actual_prev);
    try testing.expect(!list_view.ListView.init(&head).hasConsistentBacklinks());
}

test "hlist segment handoff keeps the live middle segment until the route changes" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_mid = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_mid = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_mid);
    first.pprev = @intFromPtr(&head.first);
    live_mid.next = @intFromPtr(&tail);
    live_mid.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_mid.next);

    alt_mid.next = @intFromPtr(&tail);
    alt_mid.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());
}

test "hlist segment handoff reports the tail-side stale prev link after forward adoption" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_mid = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_mid = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&alt_mid);
    first.pprev = @intFromPtr(&head.first);
    live_mid.next = @intFromPtr(&tail);
    live_mid.pprev = @intFromPtr(&first.next);
    alt_mid.next = @intFromPtr(&tail);
    alt_mid.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_mid.next);

    const breakage = hlist_view.HListView.init(&head).firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&alt_mid.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_mid.next)), breakage.actual_pprev);
    try testing.expect(!hlist_view.HListView.init(&head).hasConsistentPrevLinks());
}
