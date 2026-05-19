const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 three-node list and hlist preserve iterator order through their own tail conventions" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_third = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_third);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_third);
    list_second.prev = @intFromPtr(&list_first);
    list_third.next = @intFromPtr(&list_head);
    list_third.prev = @intFromPtr(&list_second);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_third = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = @intFromPtr(&hlist_third);
    hlist_second.pprev = @intFromPtr(&hlist_first.next);
    hlist_third.next = 0;
    hlist_third.pprev = @intFromPtr(&hlist_second.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 3), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_third), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    var list_it = list.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_second), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_third), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list_it.next());

    try std.testing.expectEqual(@as(usize, 3), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    var hlist_it = hlist.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_second), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_third), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist_it.next());
}

test "phase3 third-node break witnesses stay anchored at index two for list and hlist" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_third = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_third);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_third);
    list_second.prev = @intFromPtr(&list_first);
    list_third.next = @intFromPtr(&list_head);
    list_third.prev = @intFromPtr(&list_head);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_third = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = @intFromPtr(&hlist_third);
    hlist_second.pprev = @intFromPtr(&hlist_first.next);
    hlist_third.next = 0;
    hlist_third.pprev = @intFromPtr(&hlist_head.first);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 3), list.len());
    try std.testing.expectEqual(@as(usize, 3), hlist.len());

    const list_break = list.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), list_break.current_index);
    try std.testing.expectEqual(@intFromPtr(&list_second), list_break.expected_prev);
    try std.testing.expectEqual(@intFromPtr(&list_head), list_break.actual_prev);

    const hlist_break = hlist.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), hlist_break.current_index);
    try std.testing.expectEqual(@intFromPtr(&hlist_second.next), hlist_break.expected_pprev);
    try std.testing.expectEqual(@intFromPtr(&hlist_head.first), hlist_break.actual_pprev);
}

test "phase3 list closing witness at index three stays distinct from a valid hlist null tail" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_third = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_third);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_third);
    list_second.prev = @intFromPtr(&list_first);
    list_third.next = 0;
    list_third.prev = @intFromPtr(&list_second);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_third = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = @intFromPtr(&hlist_third);
    hlist_second.pprev = @intFromPtr(&hlist_first.next);
    hlist_third.next = 0;
    hlist_third.pprev = @intFromPtr(&hlist_second.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 3), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_third), list.last());
    try std.testing.expect(!list.hasConsistentBacklinks());
    const list_break = list.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), list_break.current_index);
    try std.testing.expectEqual(@intFromPtr(&list_third), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), list_break.actual_prev);

    try std.testing.expectEqual(@as(usize, 3), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());
}
