const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list segment skip keeps the live second interior segment visible until adoption" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_mid_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_mid_b = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_mid_b = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_mid_a);
    first.prev = @intFromPtr(&head);
    live_mid_a.next = @intFromPtr(&live_mid_b);
    live_mid_a.prev = @intFromPtr(&first);
    live_mid_b.next = @intFromPtr(&tail);
    live_mid_b.prev = @intFromPtr(&live_mid_a);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_mid_b);

    alt_mid_b.next = @intFromPtr(&tail);
    alt_mid_b.prev = @intFromPtr(&live_mid_a);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try testing.expect(view.hasConsistentBacklinks());
}

test "list segment skip reports the tail-side stale backlink after interior skip adoption" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_mid_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_mid_b = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_mid_b = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_mid_a);
    first.prev = @intFromPtr(&head);
    live_mid_a.next = @intFromPtr(&alt_mid_b);
    live_mid_a.prev = @intFromPtr(&first);
    live_mid_b.next = @intFromPtr(&tail);
    live_mid_b.prev = @intFromPtr(&live_mid_a);
    alt_mid_b.next = @intFromPtr(&tail);
    alt_mid_b.prev = @intFromPtr(&live_mid_a);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_mid_b);

    const breakage = list_view.ListView.init(&head).firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&alt_mid_b)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_mid_b)), breakage.actual_prev);
    try testing.expect(!list_view.ListView.init(&head).hasConsistentBacklinks());
}

test "hlist segment skip keeps the live second interior segment visible until adoption" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_mid_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_mid_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_mid_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_mid_a);
    first.pprev = @intFromPtr(&head.first);
    live_mid_a.next = @intFromPtr(&live_mid_b);
    live_mid_a.pprev = @intFromPtr(&first.next);
    live_mid_b.next = @intFromPtr(&tail);
    live_mid_b.pprev = @intFromPtr(&live_mid_a.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_mid_b.next);

    alt_mid_b.next = @intFromPtr(&tail);
    alt_mid_b.pprev = @intFromPtr(&live_mid_a.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());
}

test "hlist segment skip reports the tail-side stale prev link after interior skip adoption" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_mid_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_mid_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_mid_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_mid_a);
    first.pprev = @intFromPtr(&head.first);
    live_mid_a.next = @intFromPtr(&alt_mid_b);
    live_mid_a.pprev = @intFromPtr(&first.next);
    live_mid_b.next = @intFromPtr(&tail);
    live_mid_b.pprev = @intFromPtr(&live_mid_a.next);
    alt_mid_b.next = @intFromPtr(&tail);
    alt_mid_b.pprev = @intFromPtr(&live_mid_a.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_mid_b.next);

    const breakage = hlist_view.HListView.init(&head).firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&alt_mid_b.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_mid_b.next)), breakage.actual_pprev);
    try testing.expect(!hlist_view.HListView.init(&head).hasConsistentPrevLinks());
}
