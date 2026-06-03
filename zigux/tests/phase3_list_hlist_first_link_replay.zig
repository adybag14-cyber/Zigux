const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "empty list and hlist heads keep sentinel surfaces inert" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_head);
    list_head.prev = @intFromPtr(&list_head);
    const list = list_view.ListView.init(&list_head);

    try std.testing.expect(list.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());
    try std.testing.expect(list.firstBrokenBacklink() == null);

    const hlist_head = hlist_view.HListHead{ .first = 0 };
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expect(hlist.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.tailNextIsNull());
}

test "single-node list and hlist first links anchor to their heads" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_node = list_view.ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_node);
    list_head.prev = @intFromPtr(&list_node);
    list_node.next = @intFromPtr(&list_head);
    list_node.prev = @intFromPtr(&list_head);

    const list = list_view.ListView.init(&list_head);
    try std.testing.expect(!list.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_node), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_node), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_node = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    hlist_head.first = @intFromPtr(&hlist_node);
    hlist_node.next = 0;
    hlist_node.pprev = @intFromPtr(&hlist_head.first);

    const hlist = hlist_view.HListView.init(&hlist_head);
    try std.testing.expect(!hlist.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_node), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());
}

test "first-node backlink breakage reports index zero witnesses" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_node = list_view.ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_node);
    list_head.prev = @intFromPtr(&list_node);
    list_node.next = @intFromPtr(&list_head);
    list_node.prev = 0;

    const list_break = list_view.ListView.init(&list_head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), list_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), list_break.actual_prev);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_node = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    hlist_head.first = @intFromPtr(&hlist_node);
    hlist_node.next = 0;
    hlist_node.pprev = 0;

    const hlist = hlist_view.HListView.init(&hlist_head);
    try std.testing.expect(!hlist.firstPprevMatchesHead());

    const hlist_break = hlist.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), hlist_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_head.first)), hlist_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), hlist_break.actual_pprev);
}
