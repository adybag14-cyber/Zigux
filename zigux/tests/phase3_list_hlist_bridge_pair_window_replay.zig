const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "bridge-pair window stays off the visible list route until adoption" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_one = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_two = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&tail);
    first.prev = @intFromPtr(&head);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&first);

    shadow_one.next = @intFromPtr(&shadow_two);
    shadow_one.prev = 0;
    shadow_two.next = 0;
    shadow_two.prev = @intFromPtr(&shadow_one);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try testing.expect(view.hasConsistentBacklinks());
}

test "bridge-pair window adoption fails closed at the stale list tail backlink" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_one = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_two = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&shadow_one);
    first.prev = @intFromPtr(&head);
    shadow_one.next = @intFromPtr(&shadow_two);
    shadow_one.prev = @intFromPtr(&first);
    shadow_two.next = @intFromPtr(&tail);
    shadow_two.prev = @intFromPtr(&shadow_one);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());

    const breakage = view.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&shadow_two)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.actual_prev);
    try testing.expect(!view.hasConsistentBacklinks());
}

test "bridge-pair window stays off the visible hlist route until adoption" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_one = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_two = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&tail);
    first.pprev = @intFromPtr(&head.first);
    tail.next = 0;
    tail.pprev = @intFromPtr(&first.next);

    shadow_one.next = @intFromPtr(&shadow_two);
    shadow_one.pprev = 0;
    shadow_two.next = 0;
    shadow_two.pprev = @intFromPtr(&shadow_one.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());
}

test "bridge-pair window adoption fails closed at the stale hlist tail prev-link" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_one = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_two = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&shadow_one);
    first.pprev = @intFromPtr(&head.first);
    shadow_one.next = @intFromPtr(&shadow_two);
    shadow_one.pprev = @intFromPtr(&first.next);
    shadow_two.next = @intFromPtr(&tail);
    shadow_two.pprev = @intFromPtr(&shadow_one.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 3), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&shadow_two.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.actual_pprev);
    try testing.expect(!view.hasConsistentPrevLinks());
}
