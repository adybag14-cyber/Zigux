const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores a detached front shadow with a head-looking backlink" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_first = ListHead{ .next = 0, .prev = 0 };
    var live_tail = ListHead{ .next = 0, .prev = 0 };
    var front_shadow = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_first);
    head.prev = @intFromPtr(&live_tail);
    live_first.next = @intFromPtr(&live_tail);
    live_first.prev = @intFromPtr(&head);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_first);

    front_shadow.next = @intFromPtr(&live_tail);
    front_shadow.prev = @intFromPtr(&head);

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

    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), front_shadow.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), front_shadow.next);
}

test "hlist view ignores a detached front shadow with a head-looking prev-link" {
    var head = HListHead{ .first = 0 };
    var live_first = HListNode{ .next = 0, .pprev = 0 };
    var live_tail = HListNode{ .next = 0, .pprev = 0 };
    var front_shadow = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_first);
    live_first.next = @intFromPtr(&live_tail);
    live_first.pprev = @intFromPtr(&head.first);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_first.next);

    front_shadow.next = @intFromPtr(&live_tail);
    front_shadow.pprev = @intFromPtr(&head.first);

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

    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), front_shadow.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), front_shadow.next);
}

test "front shadows stay detached after the visible head retargets to a new prefix" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_new_first = ListHead{ .next = 0, .prev = 0 };
    var list_shared_tail = ListHead{ .next = 0, .prev = 0 };
    var list_old_front = ListHead{ .next = 0, .prev = 0 };
    var list_old_bridge = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_new_first);
    list_head.prev = @intFromPtr(&list_shared_tail);
    list_new_first.next = @intFromPtr(&list_shared_tail);
    list_new_first.prev = @intFromPtr(&list_head);
    list_shared_tail.next = @intFromPtr(&list_head);
    list_shared_tail.prev = @intFromPtr(&list_new_first);

    list_old_front.next = @intFromPtr(&list_old_bridge);
    list_old_front.prev = @intFromPtr(&list_head);
    list_old_bridge.next = @intFromPtr(&list_shared_tail);
    list_old_bridge.prev = @intFromPtr(&list_old_front);

    const list = ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 2), list.len());
    try std.testing.expectEqual(@as(?*const ListHead, &list_new_first), list.first());
    try std.testing.expectEqual(@as(?*const ListHead, &list_shared_tail), list.last());
    try std.testing.expect(list.firstBrokenBacklink() == null);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_new_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_shared_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_old_front = HListNode{ .next = 0, .pprev = 0 };
    var hlist_old_bridge = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_new_first);
    hlist_new_first.next = @intFromPtr(&hlist_shared_tail);
    hlist_new_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_shared_tail.next = 0;
    hlist_shared_tail.pprev = @intFromPtr(&hlist_new_first.next);

    hlist_old_front.next = @intFromPtr(&hlist_old_bridge);
    hlist_old_front.pprev = @intFromPtr(&hlist_head.first);
    hlist_old_bridge.next = @intFromPtr(&hlist_shared_tail);
    hlist_old_bridge.pprev = @intFromPtr(&hlist_old_front.next);

    const hlist = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 2), hlist.len());
    try std.testing.expectEqual(@as(?*const HListNode, &hlist_new_first), hlist.first());
    try std.testing.expect(hlist.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist.tailNextIsNull());

    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_old_front.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_old_bridge)), list_old_front.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_head.first)), hlist_old_front.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_old_bridge)), hlist_old_front.next);
}
