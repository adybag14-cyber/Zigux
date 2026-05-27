const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "detached exit bridge pair stays off the visible list route" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_b = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&third);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&head);
    third.prev = @intFromPtr(&second);

    bridge_a.next = @intFromPtr(&bridge_b);
    bridge_a.prev = @intFromPtr(&bridge_b);
    bridge_b.next = @intFromPtr(&head);
    bridge_b.prev = @intFromPtr(&bridge_a);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &third), view.last());
    try testing.expect(view.hasConsistentBacklinks());
}

test "list exit claim fails closed at the first adopted bridge node" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_b = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&bridge_b);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&bridge_a);
    second.prev = @intFromPtr(&first);
    bridge_a.next = @intFromPtr(&bridge_b);
    bridge_a.prev = @intFromPtr(&head);
    bridge_b.next = @intFromPtr(&head);
    bridge_b.prev = @intFromPtr(&bridge_a);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &bridge_b), view.last());

    const breakage = view.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
    try testing.expect(!view.hasConsistentBacklinks());
}

test "detached exit bridge pair stays off the visible hlist route" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = 0;
    third.pprev = @intFromPtr(&second.next);

    bridge_a.next = @intFromPtr(&bridge_b);
    bridge_a.pprev = @intFromPtr(&bridge_b.next);
    bridge_b.next = 0;
    bridge_b.pprev = @intFromPtr(&bridge_a.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());
}

test "hlist exit claim fails closed at the first adopted bridge node" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&bridge_a);
    second.pprev = @intFromPtr(&first.next);
    bridge_a.next = @intFromPtr(&bridge_b);
    bridge_a.pprev = @intFromPtr(&head.first);
    bridge_b.next = 0;
    bridge_b.pprev = @intFromPtr(&bridge_a.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&second.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try testing.expect(!view.hasConsistentPrevLinks());
}
