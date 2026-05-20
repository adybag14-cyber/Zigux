const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores a detached interior echo that mirrors the live middle node" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_first = ListHead{ .next = 0, .prev = 0 };
    var live_middle = ListHead{ .next = 0, .prev = 0 };
    var live_tail = ListHead{ .next = 0, .prev = 0 };
    var detached_middle_echo = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_first);
    head.prev = @intFromPtr(&live_tail);
    live_first.next = @intFromPtr(&live_middle);
    live_first.prev = @intFromPtr(&head);
    live_middle.next = @intFromPtr(&live_tail);
    live_middle.prev = @intFromPtr(&live_first);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_middle);

    // The detached echo still looks like the interior node from the outside,
    // but the visible chain must keep following the actual head-rooted links.
    detached_middle_echo.next = @intFromPtr(&live_tail);
    detached_middle_echo.prev = @intFromPtr(&live_first);

    const view = ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &live_first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);

    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_middle)), live_first.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), detached_middle_echo.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_first)), detached_middle_echo.prev);
}

test "hlist view ignores a detached interior echo that mirrors the live middle node" {
    var head = HListHead{ .first = 0 };
    var live_first = HListNode{ .next = 0, .pprev = 0 };
    var live_middle = HListNode{ .next = 0, .pprev = 0 };
    var live_tail = HListNode{ .next = 0, .pprev = 0 };
    var detached_middle_echo = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_first);
    live_first.next = @intFromPtr(&live_middle);
    live_first.pprev = @intFromPtr(&head.first);
    live_middle.next = @intFromPtr(&live_tail);
    live_middle.pprev = @intFromPtr(&live_first.next);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_middle.next);

    detached_middle_echo.next = @intFromPtr(&live_tail);
    detached_middle_echo.pprev = @intFromPtr(&live_first.next);

    const view = HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &live_first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());

    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_middle)), live_first.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), detached_middle_echo.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_first.next)), detached_middle_echo.pprev);
}

test "interior echo replay keeps the live middle authoritative across both helpers" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_first = ListHead{ .next = 0, .prev = 0 };
    var list_middle = ListHead{ .next = 0, .prev = 0 };
    var list_tail = ListHead{ .next = 0, .prev = 0 };
    var list_echo = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&list_middle);
    list_first.prev = @intFromPtr(&list_head);
    list_middle.next = @intFromPtr(&list_tail);
    list_middle.prev = @intFromPtr(&list_first);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_middle);
    list_echo.next = @intFromPtr(&list_tail);
    list_echo.prev = @intFromPtr(&list_first);

    const list_result = ListView.init(&list_head);
    var list_it = list_result.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &list_first), list_it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &list_middle), list_it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &list_tail), list_it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), list_it.next());
    try std.testing.expect(list_result.firstBrokenBacklink() == null);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_middle = HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_echo = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_middle);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_middle.next = @intFromPtr(&hlist_tail);
    hlist_middle.pprev = @intFromPtr(&hlist_first.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_middle.next);
    hlist_echo.next = @intFromPtr(&hlist_tail);
    hlist_echo.pprev = @intFromPtr(&hlist_first.next);

    const hlist_result = HListView.init(&hlist_head);
    var hlist_it = hlist_result.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &hlist_first), hlist_it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &hlist_middle), hlist_it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &hlist_tail), hlist_it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), hlist_it.next());
    try std.testing.expect(hlist_result.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist_result.tailNextIsNull());
}
