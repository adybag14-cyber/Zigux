const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list middle shadow stays off-path while the live middle route remains intact" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_mid = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_b = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_mid);
    first.prev = @intFromPtr(&head);
    live_mid.next = @intFromPtr(&tail);
    live_mid.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_mid);

    shadow_a.next = @intFromPtr(&shadow_b);
    shadow_a.prev = @intFromPtr(&first);
    shadow_b.next = @intFromPtr(&tail);
    shadow_b.prev = @intFromPtr(&shadow_a);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try testing.expect(view.hasConsistentBacklinks());
}

test "list middle shadow reports the stale tail backlink after adoption" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_mid = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_b = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&shadow_a);
    first.prev = @intFromPtr(&head);
    live_mid.next = @intFromPtr(&tail);
    live_mid.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_mid);

    shadow_a.next = @intFromPtr(&shadow_b);
    shadow_a.prev = @intFromPtr(&first);
    shadow_b.next = @intFromPtr(&tail);
    shadow_b.prev = @intFromPtr(&shadow_a);

    const breakage = list_view.ListView.init(&head).firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&shadow_b)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_mid)), breakage.actual_prev);
    try testing.expect(!list_view.ListView.init(&head).hasConsistentBacklinks());
}

test "hlist middle shadow stays off-path while the live middle route remains intact" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_mid = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_mid);
    first.pprev = @intFromPtr(&head.first);
    live_mid.next = @intFromPtr(&tail);
    live_mid.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_mid.next);

    shadow_a.next = @intFromPtr(&shadow_b);
    shadow_a.pprev = @intFromPtr(&first.next);
    shadow_b.next = @intFromPtr(&tail);
    shadow_b.pprev = @intFromPtr(&shadow_a.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());
}

test "hlist middle shadow reports the stale tail prev link after adoption" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_mid = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&shadow_a);
    first.pprev = @intFromPtr(&head.first);
    live_mid.next = @intFromPtr(&tail);
    live_mid.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_mid.next);

    shadow_a.next = @intFromPtr(&shadow_b);
    shadow_a.pprev = @intFromPtr(&first.next);
    shadow_b.next = @intFromPtr(&tail);
    shadow_b.pprev = @intFromPtr(&shadow_a.next);

    const breakage = hlist_view.HListView.init(&head).firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&shadow_b.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&live_mid.next)), breakage.actual_pprev);
    try testing.expect(!hlist_view.HListView.init(&head).hasConsistentPrevLinks());
}
