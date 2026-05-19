const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 replacement middle nodes become the only visible interior nodes" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_list_middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var replacement_list_middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&replacement_list_middle);
    list_first.prev = @intFromPtr(&list_head);
    stale_list_middle.next = @intFromPtr(&list_tail);
    stale_list_middle.prev = @intFromPtr(&list_first);
    replacement_list_middle.next = @intFromPtr(&list_tail);
    replacement_list_middle.prev = @intFromPtr(&list_first);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&replacement_list_middle);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_hlist_middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var replacement_hlist_middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&replacement_hlist_middle);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    stale_hlist_middle.next = @intFromPtr(&hlist_tail);
    stale_hlist_middle.pprev = @intFromPtr(&hlist_first.next);
    replacement_hlist_middle.next = @intFromPtr(&hlist_tail);
    replacement_hlist_middle.pprev = @intFromPtr(&hlist_first.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&replacement_hlist_middle.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 3), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    var list_it = list.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list_it.next());
    try std.testing.expectEqual(
        @as(?*const list_view.ListHead, &replacement_list_middle),
        list_it.next(),
    );
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list_it.next());

    try std.testing.expectEqual(@as(usize, 3), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    var hlist_it = hlist.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist_it.next());
    try std.testing.expectEqual(
        @as(?*const hlist_view.HListNode, &replacement_hlist_middle),
        hlist_it.next(),
    );
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_tail), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist_it.next());

    try std.testing.expectEqual(@intFromPtr(&list_tail), stale_list_middle.next);
    try std.testing.expectEqual(@intFromPtr(&list_first), stale_list_middle.prev);
    try std.testing.expectEqual(@intFromPtr(&hlist_tail), stale_hlist_middle.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_first.next), stale_hlist_middle.pprev);
}

test "phase3 stale interior nodes stay unreachable during a longer middle handoff" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_list_middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var replacement_list_middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_third = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&replacement_list_middle);
    list_first.prev = @intFromPtr(&list_head);
    stale_list_middle.next = @intFromPtr(&list_third);
    stale_list_middle.prev = @intFromPtr(&list_first);
    replacement_list_middle.next = @intFromPtr(&list_third);
    replacement_list_middle.prev = @intFromPtr(&list_first);
    list_third.next = @intFromPtr(&list_tail);
    list_third.prev = @intFromPtr(&replacement_list_middle);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_third);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_hlist_middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var replacement_hlist_middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_third = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&replacement_hlist_middle);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    stale_hlist_middle.next = @intFromPtr(&hlist_third);
    stale_hlist_middle.pprev = @intFromPtr(&hlist_first.next);
    replacement_hlist_middle.next = @intFromPtr(&hlist_third);
    replacement_hlist_middle.pprev = @intFromPtr(&hlist_first.next);
    hlist_third.next = @intFromPtr(&hlist_tail);
    hlist_third.pprev = @intFromPtr(&replacement_hlist_middle.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_third.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 4), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());
    try std.testing.expect(list.firstBrokenBacklink() == null);

    var list_it = list.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list_it.next());
    try std.testing.expectEqual(
        @as(?*const list_view.ListHead, &replacement_list_middle),
        list_it.next(),
    );
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_third), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list_it.next());

    try std.testing.expectEqual(@as(usize, 4), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.tailNextIsNull());

    var hlist_it = hlist.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist_it.next());
    try std.testing.expectEqual(
        @as(?*const hlist_view.HListNode, &replacement_hlist_middle),
        hlist_it.next(),
    );
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_third), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_tail), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist_it.next());

    try std.testing.expectEqual(@intFromPtr(&list_third), stale_list_middle.next);
    try std.testing.expectEqual(@intFromPtr(&list_first), stale_list_middle.prev);
    try std.testing.expectEqual(@intFromPtr(&hlist_third), stale_hlist_middle.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_first.next), stale_hlist_middle.pprev);
}
