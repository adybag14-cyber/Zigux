const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores detached aliases that land on staggered live positions" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_first = ListHead{ .next = 0, .prev = 0 };
    var live_middle = ListHead{ .next = 0, .prev = 0 };
    var live_tail = ListHead{ .next = 0, .prev = 0 };
    var alias_to_middle = ListHead{ .next = 0, .prev = 0 };
    var alias_to_tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_first);
    head.prev = @intFromPtr(&live_tail);
    live_first.next = @intFromPtr(&live_middle);
    live_first.prev = @intFromPtr(&head);
    live_middle.next = @intFromPtr(&live_tail);
    live_middle.prev = @intFromPtr(&live_first);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_middle);

    alias_to_middle.next = @intFromPtr(&live_middle);
    alias_to_middle.prev = 0;
    alias_to_tail.next = @intFromPtr(&live_tail);
    alias_to_tail.prev = @intFromPtr(&alias_to_middle);

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

    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_middle)), alias_to_middle.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), alias_to_tail.next);
}

test "hlist view ignores detached aliases that land on staggered live positions" {
    var head = HListHead{ .first = 0 };
    var live_first = HListNode{ .next = 0, .pprev = 0 };
    var live_middle = HListNode{ .next = 0, .pprev = 0 };
    var live_tail = HListNode{ .next = 0, .pprev = 0 };
    var alias_to_middle = HListNode{ .next = 0, .pprev = 0 };
    var alias_to_tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_first);
    live_first.next = @intFromPtr(&live_middle);
    live_first.pprev = @intFromPtr(&head.first);
    live_middle.next = @intFromPtr(&live_tail);
    live_middle.pprev = @intFromPtr(&live_first.next);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_middle.next);

    alias_to_middle.next = @intFromPtr(&live_middle);
    alias_to_middle.pprev = 0;
    alias_to_tail.next = @intFromPtr(&live_tail);
    alias_to_tail.pprev = @intFromPtr(&alias_to_middle.next);

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

    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_middle)), alias_to_middle.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), alias_to_tail.next);
}

test "staggered detached aliases stay off-path after a visible shortcut promotion" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_live_middle = ListHead{ .next = 0, .prev = 0 };
    var list_live_tail = ListHead{ .next = 0, .prev = 0 };
    var list_retired_first = ListHead{ .next = 0, .prev = 0 };
    var list_retired_second = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_live_middle);
    list_head.prev = @intFromPtr(&list_live_tail);
    list_live_middle.next = @intFromPtr(&list_live_tail);
    list_live_middle.prev = @intFromPtr(&list_head);
    list_live_tail.next = @intFromPtr(&list_head);
    list_live_tail.prev = @intFromPtr(&list_live_middle);

    list_retired_first.next = @intFromPtr(&list_live_middle);
    list_retired_first.prev = @intFromPtr(&list_head);
    list_retired_second.next = @intFromPtr(&list_live_tail);
    list_retired_second.prev = @intFromPtr(&list_retired_first);

    const list = ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(?*const ListHead, &list_live_middle), list.first());
    try std.testing.expectEqual(@as(?*const ListHead, &list_live_tail), list.last());
    try std.testing.expect(list.firstBrokenBacklink() == null);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_live_middle = HListNode{ .next = 0, .pprev = 0 };
    var hlist_live_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_retired_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_retired_second = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_live_middle);
    hlist_live_middle.next = @intFromPtr(&hlist_live_tail);
    hlist_live_middle.pprev = @intFromPtr(&hlist_head.first);
    hlist_live_tail.next = 0;
    hlist_live_tail.pprev = @intFromPtr(&hlist_live_middle.next);

    hlist_retired_first.next = @intFromPtr(&hlist_live_middle);
    hlist_retired_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_retired_second.next = @intFromPtr(&hlist_live_tail);
    hlist_retired_second.pprev = @intFromPtr(&hlist_retired_first.next);

    const hlist = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expectEqual(@as(?*const HListNode, &hlist_live_middle), hlist.first());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_live_middle)), list_retired_first.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_live_tail)), list_retired_second.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_live_middle)), hlist_retired_first.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_live_tail)), hlist_retired_second.next);
}
