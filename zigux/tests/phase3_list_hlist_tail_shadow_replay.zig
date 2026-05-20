const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores a detached tail shadow with a head-looking terminator" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_first = ListHead{ .next = 0, .prev = 0 };
    var live_tail = ListHead{ .next = 0, .prev = 0 };
    var tail_shadow = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_first);
    head.prev = @intFromPtr(&live_tail);
    live_first.next = @intFromPtr(&live_tail);
    live_first.prev = @intFromPtr(&head);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_first);

    tail_shadow.next = @intFromPtr(&head);
    tail_shadow.prev = @intFromPtr(&live_first);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &live_first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &live_first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());

    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), tail_shadow.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_first)), tail_shadow.prev);
}

test "hlist view ignores a detached tail shadow with a null terminator" {
    var head = HListHead{ .first = 0 };
    var live_first = HListNode{ .next = 0, .pprev = 0 };
    var live_tail = HListNode{ .next = 0, .pprev = 0 };
    var tail_shadow = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_first);
    live_first.next = @intFromPtr(&live_tail);
    live_first.pprev = @intFromPtr(&head.first);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_first.next);

    tail_shadow.next = 0;
    tail_shadow.pprev = @intFromPtr(&live_first.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &live_first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &live_first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &live_tail), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());

    try std.testing.expectEqual(@as(usize, 0), tail_shadow.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_first.next)), tail_shadow.pprev);
}

test "tail shadows stay detached after the visible tail shortens to a singleton" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_only = ListHead{ .next = 0, .prev = 0 };
    var old_list_tail = ListHead{ .next = 0, .prev = 0 };
    var old_list_shadow = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_only);
    list_head.prev = @intFromPtr(&list_only);
    list_only.next = @intFromPtr(&list_head);
    list_only.prev = @intFromPtr(&list_head);

    old_list_tail.next = @intFromPtr(&old_list_shadow);
    old_list_tail.prev = @intFromPtr(&list_only);
    old_list_shadow.next = @intFromPtr(&list_head);
    old_list_shadow.prev = @intFromPtr(&old_list_tail);

    const list = ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 1), list.len());
    try std.testing.expectEqual(@as(?*const ListHead, &list_only), list.first());
    try std.testing.expectEqual(@as(?*const ListHead, &list_only), list.last());
    try std.testing.expect(list.hasConsistentBacklinks());
    try std.testing.expect(list.firstBrokenBacklink() == null);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_only = HListNode{ .next = 0, .pprev = 0 };
    var old_hlist_tail = HListNode{ .next = 0, .pprev = 0 };
    var old_hlist_shadow = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_only);
    hlist_only.next = 0;
    hlist_only.pprev = @intFromPtr(&hlist_head.first);

    old_hlist_tail.next = @intFromPtr(&old_hlist_shadow);
    old_hlist_tail.pprev = @intFromPtr(&hlist_only.next);
    old_hlist_shadow.next = 0;
    old_hlist_shadow.pprev = @intFromPtr(&old_hlist_tail.next);

    const hlist = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 1), hlist.len());
    try std.testing.expectEqual(@as(?*const HListNode, &hlist_only), hlist.first());
    try std.testing.expect(hlist.firstPprevMatchesHead());
    try std.testing.expect(hlist.hasConsistentPrevLinks());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_list_shadow)), old_list_tail.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_only)), old_list_tail.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_hlist_shadow)), old_hlist_tail.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_only.next)), old_hlist_tail.pprev);
}
