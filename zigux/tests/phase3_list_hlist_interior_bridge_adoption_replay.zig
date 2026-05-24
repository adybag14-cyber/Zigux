const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list interior bridge adoption keeps the live bridge visible until adoption" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_bridge_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_bridge_b = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_bridge_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_bridge_b = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_bridge_a);
    first.prev = @intFromPtr(&head);
    live_bridge_a.next = @intFromPtr(&live_bridge_b);
    live_bridge_a.prev = @intFromPtr(&first);
    live_bridge_b.next = @intFromPtr(&tail);
    live_bridge_b.prev = @intFromPtr(&live_bridge_a);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_bridge_b);

    alt_bridge_a.next = @intFromPtr(&alt_bridge_b);
    alt_bridge_a.prev = @intFromPtr(&first);
    alt_bridge_b.next = @intFromPtr(&live_bridge_b);
    alt_bridge_b.prev = @intFromPtr(&alt_bridge_a);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try testing.expect(view.hasConsistentBacklinks());
}

test "list interior bridge adoption reports the reused live bridge after adoption" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_bridge_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_bridge_b = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_bridge_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var alt_bridge_b = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&alt_bridge_a);
    first.prev = @intFromPtr(&head);
    live_bridge_a.next = @intFromPtr(&live_bridge_b);
    live_bridge_a.prev = @intFromPtr(&first);
    live_bridge_b.next = @intFromPtr(&tail);
    live_bridge_b.prev = @intFromPtr(&live_bridge_a);
    alt_bridge_a.next = @intFromPtr(&alt_bridge_b);
    alt_bridge_a.prev = @intFromPtr(&first);
    alt_bridge_b.next = @intFromPtr(&live_bridge_b);
    alt_bridge_b.prev = @intFromPtr(&alt_bridge_a);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_bridge_b);

    const breakage = list_view.ListView.init(&head).firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&alt_bridge_b)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_bridge_a)), breakage.actual_prev);
    try testing.expect(!list_view.ListView.init(&head).hasConsistentBacklinks());
}

test "hlist interior bridge adoption keeps the live bridge visible until adoption" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_bridge_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_bridge_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_bridge_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_bridge_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_bridge_a);
    first.pprev = @intFromPtr(&head.first);
    live_bridge_a.next = @intFromPtr(&live_bridge_b);
    live_bridge_a.pprev = @intFromPtr(&first.next);
    live_bridge_b.next = @intFromPtr(&tail);
    live_bridge_b.pprev = @intFromPtr(&live_bridge_a.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_bridge_b.next);

    alt_bridge_a.next = @intFromPtr(&alt_bridge_b);
    alt_bridge_a.pprev = @intFromPtr(&first.next);
    alt_bridge_b.next = @intFromPtr(&live_bridge_b);
    alt_bridge_b.pprev = @intFromPtr(&alt_bridge_a.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());
}

test "hlist interior bridge adoption reports the reused live bridge after adoption" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_bridge_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_bridge_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_bridge_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var alt_bridge_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&alt_bridge_a);
    first.pprev = @intFromPtr(&head.first);
    live_bridge_a.next = @intFromPtr(&live_bridge_b);
    live_bridge_a.pprev = @intFromPtr(&first.next);
    live_bridge_b.next = @intFromPtr(&tail);
    live_bridge_b.pprev = @intFromPtr(&live_bridge_a.next);
    alt_bridge_a.next = @intFromPtr(&alt_bridge_b);
    alt_bridge_a.pprev = @intFromPtr(&first.next);
    alt_bridge_b.next = @intFromPtr(&live_bridge_b);
    alt_bridge_b.pprev = @intFromPtr(&alt_bridge_a.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_bridge_b.next);

    const breakage = hlist_view.HListView.init(&head).firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&alt_bridge_b.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_bridge_a.next)), breakage.actual_pprev);
    try testing.expect(!hlist_view.HListView.init(&head).hasConsistentPrevLinks());
}
