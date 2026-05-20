const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores detached bridge claims across the live interior span" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var middle = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var detached_bridge = ListHead{ .next = 0, .prev = 0 };
    var detached_tail_shadow = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&tail);
    middle.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&middle);

    // These detached nodes claim the live first->middle->tail interior bridge
    // without being reachable from the head-rooted route.
    detached_bridge.next = @intFromPtr(&tail);
    detached_bridge.prev = @intFromPtr(&first);
    detached_tail_shadow.next = @intFromPtr(&head);
    detached_tail_shadow.prev = @intFromPtr(&detached_bridge);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &middle), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

test "hlist view ignores detached bridge claims across the live interior span" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var middle = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var detached_bridge = HListNode{ .next = 0, .pprev = 0 };
    var detached_tail_shadow = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&tail);
    middle.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&middle.next);

    detached_bridge.next = @intFromPtr(&tail);
    detached_bridge.pprev = @intFromPtr(&first.next);
    detached_tail_shadow.next = 0;
    detached_tail_shadow.pprev = @intFromPtr(&detached_bridge.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &middle), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "detached bridge claims preserve the live route's canonical interior links" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_first = ListHead{ .next = 0, .prev = 0 };
    var list_middle = ListHead{ .next = 0, .prev = 0 };
    var list_tail = ListHead{ .next = 0, .prev = 0 };
    var list_detached_bridge = ListHead{ .next = 0, .prev = 0 };
    var list_detached_tail_shadow = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&list_middle);
    list_first.prev = @intFromPtr(&list_head);
    list_middle.next = @intFromPtr(&list_tail);
    list_middle.prev = @intFromPtr(&list_first);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_middle);
    list_detached_bridge.next = @intFromPtr(&list_tail);
    list_detached_bridge.prev = @intFromPtr(&list_first);
    list_detached_tail_shadow.next = @intFromPtr(&list_head);
    list_detached_tail_shadow.prev = @intFromPtr(&list_detached_bridge);

    const list_result = ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 3), list_result.len());
    try std.testing.expectEqual(@as(?*const ListHead, &list_tail), list_result.last());
    try std.testing.expect(list_result.hasConsistentBacklinks());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_middle)), list_first.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_first)), list_middle.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_tail)), list_detached_bridge.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_detached_bridge)), list_detached_tail_shadow.prev);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_middle = HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_detached_bridge = HListNode{ .next = 0, .pprev = 0 };
    var hlist_detached_tail_shadow = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_middle);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_middle.next = @intFromPtr(&hlist_tail);
    hlist_middle.pprev = @intFromPtr(&hlist_first.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_middle.next);
    hlist_detached_bridge.next = @intFromPtr(&hlist_tail);
    hlist_detached_bridge.pprev = @intFromPtr(&hlist_first.next);
    hlist_detached_tail_shadow.next = 0;
    hlist_detached_tail_shadow.pprev = @intFromPtr(&hlist_detached_bridge.next);

    const hlist_result = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 3), hlist_result.len());
    try std.testing.expect(hlist_result.firstPprevMatchesHead());
    try std.testing.expect(hlist_result.hasConsistentPrevLinks());
    try std.testing.expect(hlist_result.tailNextIsNull());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_middle)), hlist_first.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_first.next)), hlist_middle.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_tail)), hlist_detached_bridge.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_detached_bridge.next)), hlist_detached_tail_shadow.pprev);
}
