const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "detached middle braid stays off the visible list route until the bridge adopts it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var fourth = list_view.ListHead{ .next = 0, .prev = 0 };
    var fifth = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&fifth);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&fourth);
    third.prev = @intFromPtr(&second);
    fourth.next = @intFromPtr(&fifth);
    fourth.prev = @intFromPtr(&third);
    fifth.next = @intFromPtr(&head);
    fifth.prev = @intFromPtr(&fourth);

    braid_first.next = @intFromPtr(&braid_second);
    braid_first.prev = @intFromPtr(&second);
    braid_second.next = @intFromPtr(&fourth);
    braid_second.prev = @intFromPtr(&braid_first);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &fifth), view.last());
    try testing.expectEqual(@as(usize, 5), view.len());
    try testing.expect(view.hasConsistentBacklinks());
    try testing.expect(view.firstBrokenBacklink() == null);
}

test "list middle braid adoption fails closed at the stale rejoin backlink" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var third = list_view.ListHead{ .next = 0, .prev = 0 };
    var fourth = list_view.ListHead{ .next = 0, .prev = 0 };
    var fifth = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var braid_second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&fifth);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&braid_first);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&fourth);
    third.prev = @intFromPtr(&second);
    fourth.next = @intFromPtr(&fifth);
    fourth.prev = @intFromPtr(&third);
    fifth.next = @intFromPtr(&head);
    fifth.prev = @intFromPtr(&fourth);

    braid_first.next = @intFromPtr(&braid_second);
    braid_first.prev = @intFromPtr(&second);
    braid_second.next = @intFromPtr(&fourth);
    braid_second.prev = @intFromPtr(&braid_first);

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &fifth), view.last());
    try testing.expectEqual(@as(usize, 6), view.len());

    const breakage = view.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 4), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_second)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&third)), breakage.actual_prev);
    try testing.expect(!view.hasConsistentBacklinks());
}

test "detached middle braid stays off the visible hlist route until the bridge adopts it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var fourth = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var fifth = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = @intFromPtr(&fourth);
    third.pprev = @intFromPtr(&second.next);
    fourth.next = @intFromPtr(&fifth);
    fourth.pprev = @intFromPtr(&third.next);
    fifth.next = 0;
    fifth.pprev = @intFromPtr(&fourth.next);

    braid_first.next = @intFromPtr(&braid_second);
    braid_first.pprev = @intFromPtr(&second.next);
    braid_second.next = @intFromPtr(&fourth);
    braid_second.pprev = @intFromPtr(&braid_first.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expectEqual(@as(usize, 5), view.len());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.tailNextIsNull());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.firstBrokenPrevLink() == null);
}

test "hlist middle braid adoption fails closed at the stale rejoin prev-link" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var fourth = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var fifth = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var braid_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&braid_first);
    second.pprev = @intFromPtr(&first.next);
    third.next = @intFromPtr(&fourth);
    third.pprev = @intFromPtr(&second.next);
    fourth.next = @intFromPtr(&fifth);
    fourth.pprev = @intFromPtr(&third.next);
    fifth.next = 0;
    fifth.pprev = @intFromPtr(&fourth.next);

    braid_first.next = @intFromPtr(&braid_second);
    braid_first.pprev = @intFromPtr(&second.next);
    braid_second.next = @intFromPtr(&fourth);
    braid_second.pprev = @intFromPtr(&braid_first.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expectEqual(@as(usize, 6), view.len());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 4), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&braid_second.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&third.next)), breakage.actual_pprev);
    try testing.expect(!view.hasConsistentPrevLinks());
}
