const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 replacement tails become the only visible list and hlist tails" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_list_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var replacement_list_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&replacement_list_tail);
    list_first.next = @intFromPtr(&replacement_list_tail);
    list_first.prev = @intFromPtr(&list_head);
    stale_list_tail.next = @intFromPtr(&list_head);
    stale_list_tail.prev = @intFromPtr(&list_first);
    replacement_list_tail.next = @intFromPtr(&list_head);
    replacement_list_tail.prev = @intFromPtr(&list_first);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var replacement_hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&replacement_hlist_tail);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    stale_hlist_tail.next = 0;
    stale_hlist_tail.pprev = @intFromPtr(&hlist_first.next);
    replacement_hlist_tail.next = 0;
    replacement_hlist_tail.pprev = @intFromPtr(&hlist_first.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(
        @as(?*const list_view.ListHead, &replacement_list_tail),
        list.last(),
    );
    try std.testing.expect(list.hasConsistentBacklinks());

    var list_it = list.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list_it.next());
    try std.testing.expectEqual(
        @as(?*const list_view.ListHead, &replacement_list_tail),
        list_it.next(),
    );
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list_it.next());

    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    var hlist_it = hlist.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist_it.next());
    try std.testing.expectEqual(
        @as(?*const hlist_view.HListNode, &replacement_hlist_tail),
        hlist_it.next(),
    );
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist_it.next());

    try std.testing.expectEqual(@intFromPtr(&list_head), stale_list_tail.next);
    try std.testing.expectEqual(@intFromPtr(&list_first), stale_list_tail.prev);
    try std.testing.expectEqual(@as(usize, 0), stale_hlist_tail.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_first.next), stale_hlist_tail.pprev);
}

test "phase3 live single survivors keep distinct tail terminators after tail handoff" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_only = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_list_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_only);
    list_head.prev = @intFromPtr(&list_only);
    list_only.next = @intFromPtr(&list_head);
    list_only.prev = @intFromPtr(&list_head);
    stale_list_tail.next = @intFromPtr(&list_head);
    stale_list_tail.prev = @intFromPtr(&list_only);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_only = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_only);
    hlist_only.next = 0;
    hlist_only.pprev = @intFromPtr(&hlist_head.first);
    stale_hlist_tail.next = 0;
    stale_hlist_tail.pprev = @intFromPtr(&hlist_only.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 1), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_only), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_only), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());
    try std.testing.expectEqual(@intFromPtr(&list_head), list_only.next);
    try std.testing.expectEqual(@intFromPtr(&list_head), list_only.prev);

    try std.testing.expectEqual(@as(usize, 1), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_only), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@intFromPtr(&list_head), stale_list_tail.next);
    try std.testing.expectEqual(@intFromPtr(&list_only), stale_list_tail.prev);
    try std.testing.expectEqual(@as(usize, 0), stale_hlist_tail.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_only.next), stale_hlist_tail.pprev);
}

test "phase3 stale detached tails cannot perturb live list and hlist closing witnesses" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var replacement_list_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_list_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&replacement_list_tail);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&replacement_list_tail);
    list_second.prev = @intFromPtr(&list_first);
    replacement_list_tail.next = @intFromPtr(&list_head);
    replacement_list_tail.prev = @intFromPtr(&list_second);
    stale_list_tail.next = @intFromPtr(&list_head);
    stale_list_tail.prev = @intFromPtr(&list_second);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var replacement_hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = @intFromPtr(&replacement_hlist_tail);
    hlist_second.pprev = @intFromPtr(&hlist_first.next);
    replacement_hlist_tail.next = 0;
    replacement_hlist_tail.pprev = @intFromPtr(&hlist_second.next);
    stale_hlist_tail.next = 0;
    stale_hlist_tail.pprev = @intFromPtr(&hlist_second.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 3), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &replacement_list_tail), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());
    try std.testing.expect(list.firstBrokenBacklink() == null);

    try std.testing.expectEqual(@as(usize, 3), hlist.len());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@intFromPtr(&list_head), stale_list_tail.next);
    try std.testing.expectEqual(@intFromPtr(&list_second), stale_list_tail.prev);
    try std.testing.expectEqual(@as(usize, 0), stale_hlist_tail.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_second.next), stale_hlist_tail.pprev);
}
