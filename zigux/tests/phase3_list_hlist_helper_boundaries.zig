const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 empty list and hlist boundaries stay distinct across helper views" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    const list_self = @intFromPtr(&list_head);
    list_head.next = list_self;
    list_head.prev = list_self;

    const hlist_head = hlist_view.HListHead{ .first = 0 };

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expect(list.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());

    try std.testing.expect(hlist.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), hlist.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expect(list_head.next != hlist_head.first);
}

test "phase3 malformed boundary empties stay visible instead of collapsing" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_head);
    list_head.prev = 0;

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    hlist_head.first = @intFromPtr(&first);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expect(!list.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), list.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list.last());
    try std.testing.expect(!list.hasConsistentBacklinks());

    const list_break = list.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), list_break.current_index);
    try std.testing.expectEqual(@intFromPtr(&list_head), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), list_break.actual_prev);

    try std.testing.expect(!hlist.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), hlist.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), @intFromPtr(hlist.first().?));
    try std.testing.expect(!hlist.firstPprevMatchesHead());
    try std.testing.expect(!hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    const hlist_break = hlist.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), hlist_break.current_index);
    try std.testing.expectEqual(@intFromPtr(&hlist_head.first), hlist_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), hlist_break.actual_pprev);
}

test "phase3 single-node list and hlist keep distinct tail terminators" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_node = list_view.ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_node);
    list_head.prev = @intFromPtr(&list_node);
    list_node.next = @intFromPtr(&list_head);
    list_node.prev = @intFromPtr(&list_head);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_node = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    hlist_head.first = @intFromPtr(&hlist_node);
    hlist_node.next = 0;
    hlist_node.pprev = @intFromPtr(&hlist_head.first);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expect(!list.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), list.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_node)), @intFromPtr(list.first().?));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_node)), @intFromPtr(list.last().?));
    try std.testing.expect(list.hasConsistentBacklinks());
    try std.testing.expectEqual(@intFromPtr(&list_head), list_node.next);

    try std.testing.expect(!hlist.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), hlist.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_node)), @intFromPtr(hlist.first().?));
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());
    try std.testing.expectEqual(@as(usize, 0), hlist_node.next);

    try std.testing.expect(list_node.next != hlist_node.next);
}

test "phase3 stale list tail cache stays visible while single-node hlist still walks cleanly" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_node = list_view.ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_node);
    list_head.prev = @intFromPtr(&list_head);
    list_node.next = @intFromPtr(&list_head);
    list_node.prev = @intFromPtr(&list_head);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_node = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    hlist_head.first = @intFromPtr(&hlist_node);
    hlist_node.next = 0;
    hlist_node.pprev = @intFromPtr(&hlist_head.first);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expect(!list.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), list.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_node)), @intFromPtr(list.first().?));
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), list.last());
    try std.testing.expect(!list.hasConsistentBacklinks());

    const list_break = list.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), list_break.current_index);
    try std.testing.expectEqual(@intFromPtr(&list_node), list_break.expected_prev);
    try std.testing.expectEqual(@intFromPtr(&list_head), list_break.actual_prev);

    try std.testing.expect(!hlist.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), hlist.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_node)), @intFromPtr(hlist.first().?));
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@intFromPtr(&list_head), list_head.prev);
    try std.testing.expectEqual(@as(usize, 0), hlist_node.next);
}

test "phase3 stale single-node hlist head link stays visible while list still closes cleanly" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_node = list_view.ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_node);
    list_head.prev = @intFromPtr(&list_node);
    list_node.next = @intFromPtr(&list_head);
    list_node.prev = @intFromPtr(&list_head);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_node = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    hlist_head.first = @intFromPtr(&hlist_node);
    hlist_node.next = 0;
    hlist_node.pprev = @intFromPtr(&hlist_node.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expect(!list.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), list.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_node)), @intFromPtr(list.first().?));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_node)), @intFromPtr(list.last().?));
    try std.testing.expect(list.hasConsistentBacklinks());

    try std.testing.expect(!hlist.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), hlist.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_node)), @intFromPtr(hlist.first().?));
    try std.testing.expect(!hlist.firstPprevMatchesHead());
    try std.testing.expect(!hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());

    const hlist_break = hlist.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), hlist_break.current_index);
    try std.testing.expectEqual(@intFromPtr(&hlist_head.first), hlist_break.expected_pprev);
    try std.testing.expectEqual(@intFromPtr(&hlist_node.next), hlist_break.actual_pprev);

    try std.testing.expectEqual(@intFromPtr(&list_head), list_node.next);
    try std.testing.expectEqual(@as(usize, 0), hlist_node.next);
}

test "phase3 bounded two-node list and hlist chains keep their own tail contracts" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_second);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_head);
    list_second.prev = @intFromPtr(&list_first);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_first.next);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_first)), @intFromPtr(list.first().?));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_second)), @intFromPtr(list.last().?));
    try std.testing.expect(list.hasConsistentBacklinks());
    try std.testing.expectEqual(@intFromPtr(&list_head), list_second.next);

    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_first)), @intFromPtr(hlist.first().?));
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.tailNextIsNull());
    try std.testing.expectEqual(@as(usize, 0), hlist_second.next);
}

test "phase3 second-node break witnesses stay anchored at index one for list and hlist" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_second);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_head);
    list_second.prev = @intFromPtr(&list_head);

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_head.first);

    const list_break = list_view.ListView.init(&list_head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), list_break.current_index);
    try std.testing.expectEqual(@intFromPtr(&list_first), list_break.expected_prev);
    try std.testing.expectEqual(@intFromPtr(&list_head), list_break.actual_prev);

    const hlist_break = hlist_view.HListView.init(&hlist_head).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), hlist_break.current_index);
    try std.testing.expectEqual(@intFromPtr(&hlist_first.next), hlist_break.expected_pprev);
    try std.testing.expectEqual(@intFromPtr(&hlist_head.first), hlist_break.actual_pprev);
}
