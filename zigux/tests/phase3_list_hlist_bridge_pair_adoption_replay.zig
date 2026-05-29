const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list tail bridge claim is ignored until forward adoption" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_b = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&bridge_b);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);
    bridge_a.next = @intFromPtr(&bridge_b);
    bridge_a.prev = @intFromPtr(&second);
    bridge_b.next = @intFromPtr(&head);
    bridge_b.prev = @intFromPtr(&bridge_a);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &bridge_b), view.last());

    const breakage = view.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 2), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&second)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&bridge_b)), breakage.actual_prev);
    try testing.expect(!view.hasConsistentBacklinks());
}

test "list bridge pair adoption preserves the visible tail" {
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
    bridge_a.prev = @intFromPtr(&second);
    bridge_b.next = @intFromPtr(&head);
    bridge_b.prev = @intFromPtr(&bridge_a);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &bridge_b), view.last());
    try testing.expect(view.hasConsistentBacklinks());
}

test "hlist head bridge claim fails before forward adoption" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&bridge_a);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);
    bridge_a.next = @intFromPtr(&bridge_b);
    bridge_a.pprev = @intFromPtr(&second.next);
    bridge_b.next = 0;
    bridge_b.pprev = @intFromPtr(&bridge_a.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &bridge_a), view.first());
    try testing.expect(!view.firstPprevMatchesHead());
    try testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 0), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&second.next)), breakage.actual_pprev);
    try testing.expect(!view.hasConsistentPrevLinks());
}

test "hlist bridge pair adoption preserves the visible head route" {
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
    bridge_a.pprev = @intFromPtr(&second.next);
    bridge_b.next = 0;
    bridge_b.pprev = @intFromPtr(&bridge_a.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());
}
