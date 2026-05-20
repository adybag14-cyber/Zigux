const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores unreachable malformed witnesses after a live tail retarget" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_first = ListHead{ .next = 0, .prev = 0 };
    var live_second = ListHead{ .next = 0, .prev = 0 };
    var live_tail = ListHead{ .next = 0, .prev = 0 };
    var detached_shadow = ListHead{ .next = 0, .prev = 0 };
    var detached_tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_first);
    head.prev = @intFromPtr(&live_tail);
    live_first.next = @intFromPtr(&live_second);
    live_first.prev = @intFromPtr(&head);
    live_second.next = @intFromPtr(&live_tail);
    live_second.prev = @intFromPtr(&live_first);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_second);

    // This detached path keeps stale pointers and malformed backlinks, but it is
    // unreachable from the sentinel and should not affect the visible witnesses.
    detached_shadow.next = @intFromPtr(&live_second);
    detached_shadow.prev = 0;
    detached_tail.next = @intFromPtr(&detached_shadow);
    detached_tail.prev = @intFromPtr(&head);

    const view = ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &live_first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);

    try std.testing.expectEqual(@as(usize, 0), detached_shadow.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_second)), detached_shadow.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached_shadow)), detached_tail.next);
}

test "hlist view ignores unreachable malformed prev-link witnesses beside a clean live prefix" {
    var head = HListHead{ .first = 0 };
    var live_first = HListNode{ .next = 0, .pprev = 0 };
    var live_second = HListNode{ .next = 0, .pprev = 0 };
    var live_tail = HListNode{ .next = 0, .pprev = 0 };
    var detached_shadow = HListNode{ .next = 0, .pprev = 0 };
    var detached_tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_first);
    live_first.next = @intFromPtr(&live_second);
    live_first.pprev = @intFromPtr(&head.first);
    live_second.next = @intFromPtr(&live_tail);
    live_second.pprev = @intFromPtr(&live_first.next);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_second.next);

    // This detached branch still points into the live chain, but its malformed
    // pprev fields stay off the head-rooted walk and must remain invisible.
    detached_shadow.next = @intFromPtr(&live_second);
    detached_shadow.pprev = 0;
    detached_tail.next = @intFromPtr(&detached_shadow);
    detached_tail.pprev = @intFromPtr(&head.first);

    const view = HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &live_first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());

    try std.testing.expectEqual(@as(usize, 0), detached_shadow.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_second)), detached_shadow.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached_shadow)), detached_tail.next);
}

test "off-path witness isolation keeps visible indices stable after head-rooted reroutes" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_live_first = ListHead{ .next = 0, .prev = 0 };
    var list_live_tail = ListHead{ .next = 0, .prev = 0 };
    var list_old_first = ListHead{ .next = 0, .prev = 0 };
    var list_old_second = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_live_first);
    list_head.prev = @intFromPtr(&list_live_tail);
    list_live_first.next = @intFromPtr(&list_live_tail);
    list_live_first.prev = @intFromPtr(&list_head);
    list_live_tail.next = @intFromPtr(&list_head);
    list_live_tail.prev = @intFromPtr(&list_live_first);

    list_old_first.next = @intFromPtr(&list_old_second);
    list_old_first.prev = @intFromPtr(&list_head);
    list_old_second.next = @intFromPtr(&list_live_tail);
    list_old_second.prev = 0;

    const list_break = ListView.init(&list_head).firstBrokenBacklink();
    try std.testing.expect(list_break == null);
    try std.testing.expectEqual(@as(usize, 2), ListView.init(&list_head).len());

    var hlist_head = HListHead{ .first = 0 };
    var hlist_live_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_live_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_old_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_old_second = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_live_first);
    hlist_live_first.next = @intFromPtr(&hlist_live_tail);
    hlist_live_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_live_tail.next = 0;
    hlist_live_tail.pprev = @intFromPtr(&hlist_live_first.next);

    hlist_old_first.next = @intFromPtr(&hlist_old_second);
    hlist_old_first.pprev = 0;
    hlist_old_second.next = @intFromPtr(&hlist_live_tail);
    hlist_old_second.pprev = @intFromPtr(&hlist_old_first.next);

    const hlist_break = HListView.init(&hlist_head).firstBrokenPrevLink();
    try std.testing.expect(hlist_break == null);
    try std.testing.expectEqual(@as(usize, 2), HListView.init(&hlist_head).len());
    try std.testing.expect(HListView.init(&hlist_head).tailNextIsNull());
}
