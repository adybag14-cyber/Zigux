const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores a detached middle-slot claimant that mirrors the live handoff" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_first = ListHead{ .next = 0, .prev = 0 };
    var live_middle = ListHead{ .next = 0, .prev = 0 };
    var live_tail = ListHead{ .next = 0, .prev = 0 };
    var detached_claim = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_first);
    head.prev = @intFromPtr(&live_tail);
    live_first.next = @intFromPtr(&live_middle);
    live_first.prev = @intFromPtr(&head);
    live_middle.next = @intFromPtr(&live_tail);
    live_middle.prev = @intFromPtr(&live_first);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_middle);

    // The detached node reuses the live middle handoff shape, but it is never
    // reachable from head.next, so the visible chain must stay authoritative.
    detached_claim.next = @intFromPtr(&live_tail);
    detached_claim.prev = @intFromPtr(&live_first);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &live_first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &live_first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &live_middle), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

test "hlist view ignores a detached middle-slot claimant that mirrors the live handoff" {
    var head = HListHead{ .first = 0 };
    var live_first = HListNode{ .next = 0, .pprev = 0 };
    var live_middle = HListNode{ .next = 0, .pprev = 0 };
    var live_tail = HListNode{ .next = 0, .pprev = 0 };
    var detached_claim = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_first);
    live_first.next = @intFromPtr(&live_middle);
    live_first.pprev = @intFromPtr(&head.first);
    live_middle.next = @intFromPtr(&live_tail);
    live_middle.pprev = @intFromPtr(&live_first.next);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_middle.next);

    detached_claim.next = @intFromPtr(&live_tail);
    detached_claim.pprev = @intFromPtr(&live_first.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &live_first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &live_first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &live_middle), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &live_tail), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "middle-slot claim replay keeps the live interior handoff authoritative across both helpers" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_first = ListHead{ .next = 0, .prev = 0 };
    var list_middle = ListHead{ .next = 0, .prev = 0 };
    var list_tail = ListHead{ .next = 0, .prev = 0 };
    var list_claim = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&list_middle);
    list_first.prev = @intFromPtr(&list_head);
    list_middle.next = @intFromPtr(&list_tail);
    list_middle.prev = @intFromPtr(&list_first);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_middle);
    list_claim.next = @intFromPtr(&list_tail);
    list_claim.prev = @intFromPtr(&list_first);

    const list_result = ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 3), list_result.len());
    try std.testing.expectEqual(@as(?*const ListHead, &list_tail), list_result.last());
    try std.testing.expect(list_result.hasConsistentBacklinks());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_middle)), list_tail.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_first)), list_claim.prev);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_middle = HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_claim = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_middle);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_middle.next = @intFromPtr(&hlist_tail);
    hlist_middle.pprev = @intFromPtr(&hlist_first.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_middle.next);
    hlist_claim.next = @intFromPtr(&hlist_tail);
    hlist_claim.pprev = @intFromPtr(&hlist_first.next);

    const hlist_result = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 3), hlist_result.len());
    try std.testing.expect(hlist_result.firstPprevMatchesHead());
    try std.testing.expect(hlist_result.hasConsistentPrevLinks());
    try std.testing.expect(hlist_result.tailNextIsNull());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_middle.next)), hlist_tail.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_first.next)), hlist_claim.pprev);
}
