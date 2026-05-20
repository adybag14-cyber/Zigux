const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 list shadow predecessor stays detached when the live tail is shared" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_first);
    head.prev = @intFromPtr(&live_tail);
    live_first.next = @intFromPtr(&live_tail);
    live_first.prev = @intFromPtr(&head);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_first);

    shadow.next = @intFromPtr(&live_tail);
    shadow.prev = @intFromPtr(&head);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &live_first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &live_tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &live_first), it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &live_tail), it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

test "phase3 hlist shadow predecessor stays detached when the live tail is shared" {
    var head = hlist_view.HListHead{ .first = 0 };
    var live_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_first);
    live_first.next = @intFromPtr(&live_tail);
    live_first.pprev = @intFromPtr(&head.first);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_first.next);

    shadow.next = @intFromPtr(&live_tail);
    shadow.pprev = @intFromPtr(&head.first);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &live_first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &live_first), it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &live_tail), it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "phase3 single live tail ignores detached shadow predecessor in both views" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_shadow = list_view.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_tail);
    list_head.prev = @intFromPtr(&list_tail);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_head);
    list_shadow.next = @intFromPtr(&list_tail);
    list_shadow.prev = @intFromPtr(&list_head);

    const list_state = list_view.ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 1), list_state.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list_state.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &list_tail), list_state.last());
    try std.testing.expect(list_state.hasConsistentBacklinks());

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_shadow = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_tail);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_head.first);
    hlist_shadow.next = @intFromPtr(&hlist_tail);
    hlist_shadow.pprev = @intFromPtr(&hlist_head.first);

    const hlist_state = hlist_view.HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 1), hlist_state.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &hlist_tail), hlist_state.first());
    try std.testing.expect(hlist_state.firstPprevMatchesHead());
    try std.testing.expect(hlist_state.hasConsistentPrevLinks());
    try std.testing.expect(hlist_state.tailNextIsNull());
}
