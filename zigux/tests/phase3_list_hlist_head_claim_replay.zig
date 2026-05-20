const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores a detached prefix claimant that still points at the live tail" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_first = ListHead{ .next = 0, .prev = 0 };
    var live_second = ListHead{ .next = 0, .prev = 0 };
    var live_tail = ListHead{ .next = 0, .prev = 0 };
    var detached_claim = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_first);
    head.prev = @intFromPtr(&live_tail);
    live_first.next = @intFromPtr(&live_second);
    live_first.prev = @intFromPtr(&head);
    live_second.next = @intFromPtr(&live_tail);
    live_second.prev = @intFromPtr(&live_first);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_second);

    // This detached node still claims the head backlink and points into the
    // real tail segment, but it is not reachable from head.next.
    detached_claim.next = @intFromPtr(&live_tail);
    detached_claim.prev = @intFromPtr(&head);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &live_first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &live_first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &live_second), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

test "hlist view ignores a detached first-slot claimant that still points at the live tail" {
    var head = HListHead{ .first = 0 };
    var live_first = HListNode{ .next = 0, .pprev = 0 };
    var live_second = HListNode{ .next = 0, .pprev = 0 };
    var live_tail = HListNode{ .next = 0, .pprev = 0 };
    var detached_claim = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_first);
    live_first.next = @intFromPtr(&live_second);
    live_first.pprev = @intFromPtr(&head.first);
    live_second.next = @intFromPtr(&live_tail);
    live_second.pprev = @intFromPtr(&live_first.next);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_second.next);

    detached_claim.next = @intFromPtr(&live_tail);
    detached_claim.pprev = @intFromPtr(&head.first);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &live_first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &live_first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &live_second), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &live_tail), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "head claim replay keeps the head-rooted route authoritative across both helpers" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_first = ListHead{ .next = 0, .prev = 0 };
    var list_second = ListHead{ .next = 0, .prev = 0 };
    var list_tail = ListHead{ .next = 0, .prev = 0 };
    var list_claim = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_tail);
    list_second.prev = @intFromPtr(&list_first);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_second);
    list_claim.next = @intFromPtr(&list_tail);
    list_claim.prev = @intFromPtr(&list_head);

    const list_result = ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 3), list_result.len());
    try std.testing.expectEqual(@as(?*const ListHead, &list_tail), list_result.last());
    try std.testing.expect(list_result.hasConsistentBacklinks());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_second)), list_tail.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_claim.prev);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_claim = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = @intFromPtr(&hlist_tail);
    hlist_second.pprev = @intFromPtr(&hlist_first.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_second.next);
    hlist_claim.next = @intFromPtr(&hlist_tail);
    hlist_claim.pprev = @intFromPtr(&hlist_head.first);

    const hlist_result = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 3), hlist_result.len());
    try std.testing.expect(hlist_result.firstPprevMatchesHead());
    try std.testing.expect(hlist_result.hasConsistentPrevLinks());
    try std.testing.expect(hlist_result.tailNextIsNull());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_second.next)), hlist_tail.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_head.first)), hlist_claim.pprev);
}
