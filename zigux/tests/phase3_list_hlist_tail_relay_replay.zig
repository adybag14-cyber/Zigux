const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list tail relay keeps the live penultimate node visible until adoption" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_mid = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_penultimate = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_penultimate = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_mid);
    first.prev = @intFromPtr(&head);
    live_mid.next = @intFromPtr(&live_penultimate);
    live_mid.prev = @intFromPtr(&first);
    live_penultimate.next = @intFromPtr(&tail);
    live_penultimate.prev = @intFromPtr(&live_mid);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_penultimate);

    alt_penultimate.next = @intFromPtr(&tail);
    alt_penultimate.prev = @intFromPtr(&live_mid);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try testing.expect(view.hasConsistentBacklinks());
}

test "list tail relay reports the reused live tail after adoption" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_mid = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_penultimate = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_penultimate = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_mid);
    first.prev = @intFromPtr(&head);
    live_mid.next = @intFromPtr(&alt_penultimate);
    live_mid.prev = @intFromPtr(&first);
    live_penultimate.next = @intFromPtr(&tail);
    live_penultimate.prev = @intFromPtr(&live_mid);
    alt_penultimate.next = @intFromPtr(&tail);
    alt_penultimate.prev = @intFromPtr(&live_mid);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_penultimate);

    const breakage = list_view.ListView.init(&head).firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&alt_penultimate)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_penultimate)), breakage.actual_prev);
    try testing.expect(!list_view.ListView.init(&head).hasConsistentBacklinks());
}

test "hlist tail relay keeps the live penultimate node visible until adoption" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_mid = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_penultimate = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_penultimate = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_mid);
    first.pprev = @intFromPtr(&head.first);
    live_mid.next = @intFromPtr(&live_penultimate);
    live_mid.pprev = @intFromPtr(&first.next);
    live_penultimate.next = @intFromPtr(&tail);
    live_penultimate.pprev = @intFromPtr(&live_mid.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_penultimate.next);

    alt_penultimate.next = @intFromPtr(&tail);
    alt_penultimate.pprev = @intFromPtr(&live_mid.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());
}

test "hlist tail relay reports the reused live tail after adoption" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_mid = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_penultimate = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_penultimate = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_mid);
    first.pprev = @intFromPtr(&head.first);
    live_mid.next = @intFromPtr(&alt_penultimate);
    live_mid.pprev = @intFromPtr(&first.next);
    live_penultimate.next = @intFromPtr(&tail);
    live_penultimate.pprev = @intFromPtr(&live_mid.next);
    alt_penultimate.next = @intFromPtr(&tail);
    alt_penultimate.pprev = @intFromPtr(&live_mid.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_penultimate.next);

    const breakage = hlist_view.HListView.init(&head).firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&alt_penultimate.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_penultimate.next)), breakage.actual_pprev);
    try testing.expect(!hlist_view.HListView.init(&head).hasConsistentPrevLinks());
}
