const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores detached aliases that converge on the same live tail" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_first = ListHead{ .next = 0, .prev = 0 };
    var live_middle = ListHead{ .next = 0, .prev = 0 };
    var live_tail = ListHead{ .next = 0, .prev = 0 };
    var detached_a = ListHead{ .next = 0, .prev = 0 };
    var detached_b = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_first);
    head.prev = @intFromPtr(&live_tail);
    live_first.next = @intFromPtr(&live_middle);
    live_first.prev = @intFromPtr(&head);
    live_middle.next = @intFromPtr(&live_tail);
    live_middle.prev = @intFromPtr(&live_first);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_middle);

    detached_a.next = @intFromPtr(&live_tail);
    detached_a.prev = 0;
    detached_b.next = @intFromPtr(&live_tail);
    detached_b.prev = @intFromPtr(&detached_a);

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

    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), detached_a.next);
    try std.testing.expectEqual(@as(usize, 0), detached_a.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), detached_b.next);
}

test "hlist view ignores detached aliases that converge on the same live tail" {
    var head = HListHead{ .first = 0 };
    var live_first = HListNode{ .next = 0, .pprev = 0 };
    var live_middle = HListNode{ .next = 0, .pprev = 0 };
    var live_tail = HListNode{ .next = 0, .pprev = 0 };
    var detached_a = HListNode{ .next = 0, .pprev = 0 };
    var detached_b = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_first);
    live_first.next = @intFromPtr(&live_middle);
    live_first.pprev = @intFromPtr(&head.first);
    live_middle.next = @intFromPtr(&live_tail);
    live_middle.pprev = @intFromPtr(&live_first.next);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_middle.next);

    detached_a.next = @intFromPtr(&live_tail);
    detached_a.pprev = 0;
    detached_b.next = @intFromPtr(&live_tail);
    detached_b.pprev = @intFromPtr(&detached_a.next);

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

    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), detached_a.next);
    try std.testing.expectEqual(@as(usize, 0), detached_a.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), detached_b.next);
}

test "converging aliases do not create extra visible witnesses after a promoted live shortcut" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_live_first = ListHead{ .next = 0, .prev = 0 };
    var list_live_tail = ListHead{ .next = 0, .prev = 0 };
    var list_alias_a = ListHead{ .next = 0, .prev = 0 };
    var list_alias_b = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_live_first);
    list_head.prev = @intFromPtr(&list_live_tail);
    list_live_first.next = @intFromPtr(&list_live_tail);
    list_live_first.prev = @intFromPtr(&list_head);
    list_live_tail.next = @intFromPtr(&list_head);
    list_live_tail.prev = @intFromPtr(&list_live_first);

    list_alias_a.next = @intFromPtr(&list_live_tail);
    list_alias_a.prev = @intFromPtr(&list_head);
    list_alias_b.next = @intFromPtr(&list_live_tail);
    list_alias_b.prev = 0;

    try std.testing.expectEqual(@as(usize, 2), ListView.init(&list_head).len());
    try std.testing.expect(ListView.init(&list_head).firstBrokenBacklink() == null);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_live_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_live_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_alias_a = HListNode{ .next = 0, .pprev = 0 };
    var hlist_alias_b = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_live_first);
    hlist_live_first.next = @intFromPtr(&hlist_live_tail);
    hlist_live_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_live_tail.next = 0;
    hlist_live_tail.pprev = @intFromPtr(&hlist_live_first.next);

    hlist_alias_a.next = @intFromPtr(&hlist_live_tail);
    hlist_alias_a.pprev = @intFromPtr(&hlist_head.first);
    hlist_alias_b.next = @intFromPtr(&hlist_live_tail);
    hlist_alias_b.pprev = 0;

    const hlist = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_live_tail)), list_alias_a.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_alias_a.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_live_tail)), hlist_alias_a.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_head.first)), hlist_alias_a.pprev);
}
