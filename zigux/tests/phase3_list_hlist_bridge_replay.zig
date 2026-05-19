const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 inserted bridge nodes extend the visible list and hlist chain" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var inserted_list_bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_list_shortcut = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&inserted_list_bridge);
    list_first.prev = @intFromPtr(&list_head);
    inserted_list_bridge.next = @intFromPtr(&list_tail);
    inserted_list_bridge.prev = @intFromPtr(&list_first);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&inserted_list_bridge);
    stale_list_shortcut.next = @intFromPtr(&list_tail);
    stale_list_shortcut.prev = @intFromPtr(&list_first);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var inserted_hlist_bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_hlist_shortcut = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&inserted_hlist_bridge);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    inserted_hlist_bridge.next = @intFromPtr(&hlist_tail);
    inserted_hlist_bridge.pprev = @intFromPtr(&hlist_first.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&inserted_hlist_bridge.next);
    stale_hlist_shortcut.next = @intFromPtr(&hlist_tail);
    stale_hlist_shortcut.pprev = @intFromPtr(&hlist_first.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 3), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    var list_it = list.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &inserted_list_bridge), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list_it.next());

    try std.testing.expectEqual(@as(usize, 3), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    var hlist_it = hlist.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &inserted_hlist_bridge), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_tail), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist_it.next());

    try std.testing.expectEqual(@intFromPtr(&list_tail), stale_list_shortcut.next);
    try std.testing.expectEqual(@intFromPtr(&list_first), stale_list_shortcut.prev);
    try std.testing.expectEqual(@intFromPtr(&hlist_tail), stale_hlist_shortcut.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_first.next), stale_hlist_shortcut.pprev);
}

test "phase3 bridge growth preserves distinct list and hlist tail terminators after a single-node start" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var inserted_list_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_list_single = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&inserted_list_tail);
    list_first.next = @intFromPtr(&inserted_list_tail);
    list_first.prev = @intFromPtr(&list_head);
    inserted_list_tail.next = @intFromPtr(&list_head);
    inserted_list_tail.prev = @intFromPtr(&list_first);
    stale_list_single.next = @intFromPtr(&list_head);
    stale_list_single.prev = @intFromPtr(&list_head);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var inserted_hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_hlist_single = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&inserted_hlist_tail);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    inserted_hlist_tail.next = 0;
    inserted_hlist_tail.pprev = @intFromPtr(&hlist_first.next);
    stale_hlist_single.next = 0;
    stale_hlist_single.pprev = @intFromPtr(&hlist_head.first);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &inserted_list_tail), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@intFromPtr(&list_head), inserted_list_tail.next);
    try std.testing.expectEqual(@intFromPtr(&list_first), inserted_list_tail.prev);
    try std.testing.expectEqual(@intFromPtr(&list_head), stale_list_single.next);
    try std.testing.expectEqual(@intFromPtr(&list_head), stale_list_single.prev);
    try std.testing.expectEqual(@as(usize, 0), inserted_hlist_tail.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_head.first), stale_hlist_single.pprev);
}

test "phase3 stale shortcut nodes cannot perturb live backlink and prev-link witnesses after bridge insertion" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var inserted_list_bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_list_shortcut = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&inserted_list_bridge);
    list_second.prev = @intFromPtr(&list_first);
    inserted_list_bridge.next = @intFromPtr(&list_tail);
    inserted_list_bridge.prev = @intFromPtr(&list_second);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&inserted_list_bridge);
    stale_list_shortcut.next = @intFromPtr(&list_tail);
    stale_list_shortcut.prev = @intFromPtr(&list_second);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var inserted_hlist_bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_hlist_shortcut = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = @intFromPtr(&inserted_hlist_bridge);
    hlist_second.pprev = @intFromPtr(&hlist_first.next);
    inserted_hlist_bridge.next = @intFromPtr(&hlist_tail);
    inserted_hlist_bridge.pprev = @intFromPtr(&hlist_second.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&inserted_hlist_bridge.next);
    stale_hlist_shortcut.next = @intFromPtr(&hlist_tail);
    stale_hlist_shortcut.pprev = @intFromPtr(&hlist_second.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 4), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());
    try std.testing.expect(list.firstBrokenBacklink() == null);

    try std.testing.expectEqual(@as(usize, 4), hlist.len());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@intFromPtr(&list_tail), stale_list_shortcut.next);
    try std.testing.expectEqual(@intFromPtr(&list_second), stale_list_shortcut.prev);
    try std.testing.expectEqual(@intFromPtr(&hlist_tail), stale_hlist_shortcut.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_second.next), stale_hlist_shortcut.pprev);
}
