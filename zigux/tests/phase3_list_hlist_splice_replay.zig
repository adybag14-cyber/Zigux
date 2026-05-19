const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 front-spliced nodes stay out of list and hlist iterator order" {
    var detached_list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_third = list_view.ListHead{ .next = 0, .prev = 0 };

    detached_list_first.next = @intFromPtr(&detached_list_first);
    detached_list_first.prev = @intFromPtr(&detached_list_first);
    list_head.next = @intFromPtr(&list_second);
    list_head.prev = @intFromPtr(&list_third);
    list_second.next = @intFromPtr(&list_third);
    list_second.prev = @intFromPtr(&list_head);
    list_third.next = @intFromPtr(&list_head);
    list_third.prev = @intFromPtr(&list_second);

    var detached_hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_third = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    detached_hlist_first.next = 0;
    detached_hlist_first.pprev = 0;
    hlist_head.first = @intFromPtr(&hlist_second);
    hlist_second.next = @intFromPtr(&hlist_third);
    hlist_second.pprev = @intFromPtr(&hlist_head.first);
    hlist_third.next = 0;
    hlist_third.pprev = @intFromPtr(&hlist_second.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_second), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_third), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    var list_it = list.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_second), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_third), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list_it.next());

    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_second), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    var hlist_it = hlist.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_second), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_third), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist_it.next());
}

test "phase3 middle-spliced nodes preserve the live two-node list and hlist chain" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var detached_list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_third = list_view.ListHead{ .next = 0, .prev = 0 };

    detached_list_second.next = @intFromPtr(&detached_list_second);
    detached_list_second.prev = @intFromPtr(&detached_list_second);
    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_third);
    list_first.next = @intFromPtr(&list_third);
    list_first.prev = @intFromPtr(&list_head);
    list_third.next = @intFromPtr(&list_head);
    list_third.prev = @intFromPtr(&list_first);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var detached_hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_third = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    detached_hlist_second.next = 0;
    detached_hlist_second.pprev = 0;
    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_third);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_third.next = 0;
    hlist_third.pprev = @intFromPtr(&hlist_first.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_third), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    var list_it = list.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_third), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list_it.next());

    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    var hlist_it = hlist.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_third), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist_it.next());
}

test "phase3 stale detached nodes stay unreachable even when they still remember old neighbors" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_third = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_third);
    list_first.next = @intFromPtr(&list_third);
    list_first.prev = @intFromPtr(&list_head);
    stale_list_second.next = @intFromPtr(&list_third);
    stale_list_second.prev = @intFromPtr(&list_first);
    list_third.next = @intFromPtr(&list_head);
    list_third.prev = @intFromPtr(&list_first);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_third = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_third);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    stale_hlist_second.next = @intFromPtr(&hlist_third);
    stale_hlist_second.pprev = @intFromPtr(&hlist_first.next);
    hlist_third.next = 0;
    hlist_third.pprev = @intFromPtr(&hlist_first.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_third), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@intFromPtr(&list_third), stale_list_second.next);
    try std.testing.expectEqual(@intFromPtr(&list_first), stale_list_second.prev);
    try std.testing.expectEqual(@intFromPtr(&hlist_third), stale_hlist_second.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_first.next), stale_hlist_second.pprev);
}
