const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 bypassed prefix nodes stay out of list and hlist iterator order" {
    var stale_list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    stale_list_first.next = @intFromPtr(&list_second);
    stale_list_first.prev = @intFromPtr(&list_head);
    list_head.next = @intFromPtr(&list_second);
    list_head.prev = @intFromPtr(&list_tail);
    list_second.next = @intFromPtr(&list_tail);
    list_second.prev = @intFromPtr(&list_head);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_second);

    var stale_hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    stale_hlist_first.next = @intFromPtr(&hlist_second);
    stale_hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_head.first = @intFromPtr(&hlist_second);
    hlist_second.next = @intFromPtr(&hlist_tail);
    hlist_second.pprev = @intFromPtr(&hlist_head.first);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_second.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_second), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    var list_it = list.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_second), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list_it.next());

    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_second), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    var hlist_it = hlist.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_second), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_tail), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist_it.next());

    try std.testing.expectEqual(@intFromPtr(&list_second), stale_list_first.next);
    try std.testing.expectEqual(@intFromPtr(&list_head), stale_list_first.prev);
    try std.testing.expectEqual(@intFromPtr(&hlist_second), stale_hlist_first.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_head.first), stale_hlist_first.pprev);
}

test "phase3 bypass direct to tail preserves single live list and hlist survivor" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_list_middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_tail);
    list_head.prev = @intFromPtr(&list_tail);
    stale_list_first.next = @intFromPtr(&stale_list_middle);
    stale_list_first.prev = @intFromPtr(&list_head);
    stale_list_middle.next = @intFromPtr(&list_tail);
    stale_list_middle.prev = @intFromPtr(&stale_list_first);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_head);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var stale_hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_hlist_middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_tail);
    stale_hlist_first.next = @intFromPtr(&stale_hlist_middle);
    stale_hlist_first.pprev = @intFromPtr(&hlist_head.first);
    stale_hlist_middle.next = @intFromPtr(&hlist_tail);
    stale_hlist_middle.pprev = @intFromPtr(&stale_hlist_first.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_head.first);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 1), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    try std.testing.expectEqual(@as(usize, 1), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_tail), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@intFromPtr(&list_head), list_tail.next);
    try std.testing.expectEqual(@intFromPtr(&list_head), list_tail.prev);
    try std.testing.expectEqual(@intFromPtr(&stale_list_middle), stale_list_first.next);
    try std.testing.expectEqual(@intFromPtr(&list_tail), stale_list_middle.next);
    try std.testing.expectEqual(@as(usize, 0), hlist_tail.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_head.first), hlist_tail.pprev);
    try std.testing.expectEqual(@intFromPtr(&stale_hlist_middle), stale_hlist_first.next);
    try std.testing.expectEqual(@intFromPtr(&hlist_tail), stale_hlist_middle.next);
}

test "phase3 skipped prefix metadata cannot perturb live list and hlist witnesses" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var skipped_list_a = list_view.ListHead{ .next = 0, .prev = 0 };
    var skipped_list_b = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_list_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&live_list_first);
    list_head.prev = @intFromPtr(&live_list_tail);
    skipped_list_a.next = @intFromPtr(&skipped_list_b);
    skipped_list_a.prev = @intFromPtr(&list_head);
    skipped_list_b.next = @intFromPtr(&live_list_first);
    skipped_list_b.prev = @intFromPtr(&skipped_list_a);
    live_list_first.next = @intFromPtr(&live_list_tail);
    live_list_first.prev = @intFromPtr(&list_head);
    live_list_tail.next = @intFromPtr(&list_head);
    live_list_tail.prev = @intFromPtr(&live_list_first);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var skipped_hlist_a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var skipped_hlist_b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&live_hlist_first);
    skipped_hlist_a.next = @intFromPtr(&skipped_hlist_b);
    skipped_hlist_a.pprev = @intFromPtr(&hlist_head.first);
    skipped_hlist_b.next = @intFromPtr(&live_hlist_first);
    skipped_hlist_b.pprev = @intFromPtr(&skipped_hlist_a.next);
    live_hlist_first.next = @intFromPtr(&live_hlist_tail);
    live_hlist_first.pprev = @intFromPtr(&hlist_head.first);
    live_hlist_tail.next = 0;
    live_hlist_tail.pprev = @intFromPtr(&live_hlist_first.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &live_list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &live_list_tail), list.last());
    try std.testing.expect(list.firstBrokenBacklink() == null);
    try std.testing.expect(list.hasConsistentBacklinks());

    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &live_hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@intFromPtr(&skipped_list_b), skipped_list_a.next);
    try std.testing.expectEqual(@intFromPtr(&live_list_first), skipped_list_b.next);
    try std.testing.expectEqual(@intFromPtr(&skipped_hlist_b), skipped_hlist_a.next);
    try std.testing.expectEqual(@intFromPtr(&live_hlist_first), skipped_hlist_b.next);
}
