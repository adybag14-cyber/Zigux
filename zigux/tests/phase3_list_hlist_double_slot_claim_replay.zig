const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores a detached pair that falsely claims two live handoff slots" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };
    var third = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var detached_first = ListHead{ .next = 0, .prev = 0 };
    var detached_second = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&first);
    third.next = @intFromPtr(&tail);
    third.prev = @intFromPtr(&second);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&third);

    // This detached pair imitates two consecutive live handoff slots but never
    // joins the head-rooted route.
    detached_first.next = @intFromPtr(&detached_second);
    detached_first.prev = @intFromPtr(&second);
    detached_second.next = @intFromPtr(&tail);
    detached_second.prev = @intFromPtr(&third);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &second), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &third), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

test "hlist view ignores a detached pair that falsely claims two live handoff slots" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };
    var third = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var detached_first = HListNode{ .next = 0, .pprev = 0 };
    var detached_second = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&first.next);
    third.next = @intFromPtr(&tail);
    third.pprev = @intFromPtr(&second.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&third.next);

    detached_first.next = @intFromPtr(&detached_second);
    detached_first.pprev = @intFromPtr(&second.next);
    detached_second.next = 0;
    detached_second.pprev = @intFromPtr(&third.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &second), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &third), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "double-slot claim replay keeps the visible route authoritative across both helpers" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_first = ListHead{ .next = 0, .prev = 0 };
    var list_second = ListHead{ .next = 0, .prev = 0 };
    var list_third = ListHead{ .next = 0, .prev = 0 };
    var list_tail = ListHead{ .next = 0, .prev = 0 };
    var list_detached_first = ListHead{ .next = 0, .prev = 0 };
    var list_detached_second = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_third);
    list_second.prev = @intFromPtr(&list_first);
    list_third.next = @intFromPtr(&list_tail);
    list_third.prev = @intFromPtr(&list_second);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_third);
    list_detached_first.next = @intFromPtr(&list_detached_second);
    list_detached_first.prev = @intFromPtr(&list_second);
    list_detached_second.next = @intFromPtr(&list_tail);
    list_detached_second.prev = @intFromPtr(&list_third);

    const list_result = ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 4), list_result.len());
    try std.testing.expectEqual(@as(?*const ListHead, &list_tail), list_result.last());
    try std.testing.expect(list_result.hasConsistentBacklinks());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_third)), list_tail.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_second)), list_detached_first.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_third)), list_detached_second.prev);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = HListNode{ .next = 0, .pprev = 0 };
    var hlist_third = HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_detached_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_detached_second = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = @intFromPtr(&hlist_third);
    hlist_second.pprev = @intFromPtr(&hlist_first.next);
    hlist_third.next = @intFromPtr(&hlist_tail);
    hlist_third.pprev = @intFromPtr(&hlist_second.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_third.next);
    hlist_detached_first.next = @intFromPtr(&hlist_detached_second);
    hlist_detached_first.pprev = @intFromPtr(&hlist_second.next);
    hlist_detached_second.next = 0;
    hlist_detached_second.pprev = @intFromPtr(&hlist_third.next);

    const hlist_result = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 4), hlist_result.len());
    try std.testing.expect(hlist_result.firstPprevMatchesHead());
    try std.testing.expect(hlist_result.hasConsistentPrevLinks());
    try std.testing.expect(hlist_result.tailNextIsNull());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_third.next)), hlist_tail.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_second.next)), hlist_detached_first.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_third.next)), hlist_detached_second.pprev);
}
