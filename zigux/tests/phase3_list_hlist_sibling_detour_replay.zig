const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores a detached sibling detour while the live route stays canonical" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var live_second = ListHead{ .next = 0, .prev = 0 };
    var live_tail = ListHead{ .next = 0, .prev = 0 };
    var detached_sibling = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&live_tail);
    first.next = @intFromPtr(&live_second);
    first.prev = @intFromPtr(&head);
    live_second.next = @intFromPtr(&live_tail);
    live_second.prev = @intFromPtr(&first);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_second);

    // This detached node pretends to be a valid sibling handoff between the
    // first visible node and the rest of the route, but it never becomes
    // reachable from the head-rooted walk.
    detached_sibling.next = @intFromPtr(&live_second);
    detached_sibling.prev = @intFromPtr(&first);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &live_second), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

test "hlist view ignores a detached sibling detour while the live route stays canonical" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var live_second = HListNode{ .next = 0, .pprev = 0 };
    var live_tail = HListNode{ .next = 0, .pprev = 0 };
    var detached_sibling = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_second);
    first.pprev = @intFromPtr(&head.first);
    live_second.next = @intFromPtr(&live_tail);
    live_second.pprev = @intFromPtr(&first.next);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_second.next);

    detached_sibling.next = @intFromPtr(&live_second);
    detached_sibling.pprev = @intFromPtr(&first.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &live_second), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &live_tail), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "adopting a stale sibling detour trips the first visible link mismatch" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_first = ListHead{ .next = 0, .prev = 0 };
    var list_live_second = ListHead{ .next = 0, .prev = 0 };
    var list_live_tail = ListHead{ .next = 0, .prev = 0 };
    var list_detached_sibling = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_live_tail);
    list_first.next = @intFromPtr(&list_detached_sibling);
    list_first.prev = @intFromPtr(&list_head);
    list_live_second.next = @intFromPtr(&list_live_tail);
    list_live_second.prev = @intFromPtr(&list_first);
    list_live_tail.next = @intFromPtr(&list_head);
    list_live_tail.prev = @intFromPtr(&list_live_second);
    list_detached_sibling.next = @intFromPtr(&list_live_tail);
    list_detached_sibling.prev = @intFromPtr(&list_first);

    const list_result = ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 3), list_result.len());
    try std.testing.expectEqual(@as(?*const ListHead, &list_live_tail), list_result.last());
    const list_breakage = list_result.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), list_breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_detached_sibling)), list_breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_live_second)), list_breakage.actual_prev);
    try std.testing.expect(!list_result.hasConsistentBacklinks());

    var hlist_head = HListHead{ .first = 0 };
    var hlist_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_live_second = HListNode{ .next = 0, .pprev = 0 };
    var hlist_live_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_detached_sibling = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_detached_sibling);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_live_second.next = @intFromPtr(&hlist_live_tail);
    hlist_live_second.pprev = @intFromPtr(&hlist_first.next);
    hlist_live_tail.next = 0;
    hlist_live_tail.pprev = @intFromPtr(&hlist_live_second.next);
    hlist_detached_sibling.next = @intFromPtr(&hlist_live_tail);
    hlist_detached_sibling.pprev = @intFromPtr(&hlist_first.next);

    const hlist_result = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 3), hlist_result.len());
    try std.testing.expect(hlist_result.firstPprevMatchesHead());
    try std.testing.expect(hlist_result.tailNextIsNull());
    const hlist_breakage = hlist_result.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), hlist_breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_detached_sibling.next)), hlist_breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_live_second.next)), hlist_breakage.actual_pprev);
    try std.testing.expect(!hlist_result.hasConsistentPrevLinks());
}
