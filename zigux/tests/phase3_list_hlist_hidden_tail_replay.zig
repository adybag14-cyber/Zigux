const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 detached tail nodes stay out of list and hlist iterator order" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_hidden_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_hidden_tail);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = 0;
    list_second.prev = @intFromPtr(&list_first);
    list_hidden_tail.next = @intFromPtr(&list_head);
    list_hidden_tail.prev = @intFromPtr(&list_second);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_hidden_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_first.next);
    hlist_hidden_tail.next = 0;
    hlist_hidden_tail.pprev = @intFromPtr(&hlist_second.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(usize, 2), hlist.len());

    var list_it = list.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_second), list_it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list_it.next());

    var hlist_it = hlist.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_second), hlist_it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist_it.next());
}

test "phase3 list stale head tail remains observable after a truncated visible prefix" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_hidden_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_hidden_tail);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = 0;
    list_second.prev = @intFromPtr(&list_first);
    list_hidden_tail.next = @intFromPtr(&list_head);
    list_hidden_tail.prev = @intFromPtr(&list_second);

    const list = list_view.ListView.init(&list_head);

    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_first), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_hidden_tail), list.last());
    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expect(!list.hasConsistentBacklinks());

    const breakage = list.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@intFromPtr(&list_second), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_prev);
}

test "phase3 hlist keeps the same truncated prefix well formed without a hidden tail slot" {
    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_hidden_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_first.next);
    hlist_hidden_tail.next = 0;
    hlist_hidden_tail.pprev = @intFromPtr(&hlist_second.next);

    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_first), hlist.first());
    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.tailNextIsNull());
}
