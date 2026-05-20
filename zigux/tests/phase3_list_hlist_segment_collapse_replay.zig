const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 contracted middle segments shorten the visible list and hlist chain" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var removed_list_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var removed_list_b = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&list_tail);
    list_first.prev = @intFromPtr(&list_head);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_first);
    removed_list_a.next = @intFromPtr(&removed_list_b);
    removed_list_a.prev = @intFromPtr(&list_first);
    removed_list_b.next = @intFromPtr(&list_tail);
    removed_list_b.prev = @intFromPtr(&removed_list_a);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var removed_hlist_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var removed_hlist_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_tail);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_first.next);
    removed_hlist_a.next = @intFromPtr(&removed_hlist_b);
    removed_hlist_a.pprev = @intFromPtr(&hlist_first.next);
    removed_hlist_b.next = @intFromPtr(&hlist_tail);
    removed_hlist_b.pprev = @intFromPtr(&removed_hlist_a.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    var list_it = list.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list_it.next());

    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    var hlist_it = hlist.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_tail), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist_it.next());

    try std.testing.expectEqual(@intFromPtr(&removed_list_b), removed_list_a.next);
    try std.testing.expectEqual(@intFromPtr(&list_first), removed_list_a.prev);
    try std.testing.expectEqual(@intFromPtr(&list_tail), removed_list_b.next);
    try std.testing.expectEqual(@intFromPtr(&removed_list_a), removed_list_b.prev);
    try std.testing.expectEqual(@intFromPtr(&removed_hlist_b), removed_hlist_a.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_first.next), removed_hlist_a.pprev);
    try std.testing.expectEqual(@intFromPtr(&hlist_tail), removed_hlist_b.next);
    try std.testing.expectEqual(@intFromPtr(&removed_hlist_a.next), removed_hlist_b.pprev);
}

test "phase3 collapse back to a single visible node preserves list and hlist terminators" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_survivor = list_view.ListHead{ .next = 0, .prev = 0 };
    var removed_list_bridge = list_view.ListHead{ .next = 0, .prev = 0 };
    var removed_list_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_survivor);
    list_head.prev = @intFromPtr(&list_survivor);
    list_survivor.next = @intFromPtr(&list_head);
    list_survivor.prev = @intFromPtr(&list_head);
    removed_list_bridge.next = @intFromPtr(&removed_list_tail);
    removed_list_bridge.prev = @intFromPtr(&list_survivor);
    removed_list_tail.next = @intFromPtr(&list_head);
    removed_list_tail.prev = @intFromPtr(&removed_list_bridge);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_survivor = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var removed_hlist_bridge = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var removed_hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_survivor);
    hlist_survivor.next = 0;
    hlist_survivor.pprev = @intFromPtr(&hlist_head.first);
    removed_hlist_bridge.next = @intFromPtr(&removed_hlist_tail);
    removed_hlist_bridge.pprev = @intFromPtr(&hlist_survivor.next);
    removed_hlist_tail.next = 0;
    removed_hlist_tail.pprev = @intFromPtr(&removed_hlist_bridge.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 1), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_survivor), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_survivor), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    try std.testing.expectEqual(@as(usize, 1), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_survivor), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@intFromPtr(&list_head), list_survivor.next);
    try std.testing.expectEqual(@intFromPtr(&list_head), list_survivor.prev);
    try std.testing.expectEqual(@intFromPtr(&removed_list_tail), removed_list_bridge.next);
    try std.testing.expectEqual(@intFromPtr(&list_survivor), removed_list_bridge.prev);
    try std.testing.expectEqual(@intFromPtr(&list_head), removed_list_tail.next);
    try std.testing.expectEqual(@intFromPtr(&removed_list_bridge), removed_list_tail.prev);
    try std.testing.expectEqual(@as(usize, 0), hlist_survivor.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_head.first), hlist_survivor.pprev);
    try std.testing.expectEqual(@intFromPtr(&removed_hlist_tail), removed_hlist_bridge.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_survivor.next), removed_hlist_bridge.pprev);
    try std.testing.expectEqual(@as(usize, 0), removed_hlist_tail.next);
    try std.testing.expectEqual(@intFromPtr(&removed_hlist_bridge.next), removed_hlist_tail.pprev);
}

test "phase3 detached contraction segments cannot perturb live backlink and prev-link witnesses" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_list_middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var removed_list_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var removed_list_b = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&live_list_middle);
    list_first.prev = @intFromPtr(&list_head);
    live_list_middle.next = @intFromPtr(&list_tail);
    live_list_middle.prev = @intFromPtr(&list_first);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&live_list_middle);
    removed_list_a.next = @intFromPtr(&removed_list_b);
    removed_list_a.prev = @intFromPtr(&list_first);
    removed_list_b.next = @intFromPtr(&list_tail);
    removed_list_b.prev = @intFromPtr(&removed_list_a);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_hlist_middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var removed_hlist_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var removed_hlist_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&live_hlist_middle);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    live_hlist_middle.next = @intFromPtr(&hlist_tail);
    live_hlist_middle.pprev = @intFromPtr(&hlist_first.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&live_hlist_middle.next);
    removed_hlist_a.next = @intFromPtr(&removed_hlist_b);
    removed_hlist_a.pprev = @intFromPtr(&hlist_first.next);
    removed_hlist_b.next = @intFromPtr(&hlist_tail);
    removed_hlist_b.pprev = @intFromPtr(&removed_hlist_a.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 3), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());
    try std.testing.expect(list.firstBrokenBacklink() == null);

    try std.testing.expectEqual(@as(usize, 3), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@intFromPtr(&removed_list_b), removed_list_a.next);
    try std.testing.expectEqual(@intFromPtr(&list_first), removed_list_a.prev);
    try std.testing.expectEqual(@intFromPtr(&list_tail), removed_list_b.next);
    try std.testing.expectEqual(@intFromPtr(&removed_hlist_b), removed_hlist_a.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_first.next), removed_hlist_a.pprev);
    try std.testing.expectEqual(@intFromPtr(&hlist_tail), removed_hlist_b.next);
}
