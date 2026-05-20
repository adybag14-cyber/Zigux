const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores a detached competing successor that still claims the live predecessor" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_first = ListHead{ .next = 0, .prev = 0 };
    var live_tail = ListHead{ .next = 0, .prev = 0 };
    var detached_challenger = ListHead{ .next = 0, .prev = 0 };
    var detached_shadow_tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_first);
    head.prev = @intFromPtr(&live_tail);
    live_first.next = @intFromPtr(&live_tail);
    live_first.prev = @intFromPtr(&head);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_first);

    // This challenger still claims the same predecessor slot as the live tail,
    // but the actual live walk should keep following the official next pointer.
    detached_challenger.next = @intFromPtr(&detached_shadow_tail);
    detached_challenger.prev = @intFromPtr(&live_first);
    detached_shadow_tail.next = @intFromPtr(&live_tail);
    detached_shadow_tail.prev = @intFromPtr(&detached_challenger);

    const view = ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &live_first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);

    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), live_first.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_first)), detached_challenger.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached_shadow_tail)), detached_challenger.next);
}

test "hlist view ignores a detached competing successor that still claims the live next slot" {
    var head = HListHead{ .first = 0 };
    var live_first = HListNode{ .next = 0, .pprev = 0 };
    var live_tail = HListNode{ .next = 0, .pprev = 0 };
    var detached_challenger = HListNode{ .next = 0, .pprev = 0 };
    var detached_shadow_tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_first);
    live_first.next = @intFromPtr(&live_tail);
    live_first.pprev = @intFromPtr(&head.first);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_first.next);

    // This challenger still points at the same logical predecessor slot as the
    // live tail, but it is unreachable because the head-rooted next pointer now
    // selects the official tail.
    detached_challenger.next = @intFromPtr(&detached_shadow_tail);
    detached_challenger.pprev = @intFromPtr(&live_first.next);
    detached_shadow_tail.next = @intFromPtr(&live_tail);
    detached_shadow_tail.pprev = @intFromPtr(&detached_challenger.next);

    const view = HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &live_first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());

    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), live_first.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_first.next)), detached_challenger.pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached_shadow_tail)), detached_challenger.next);
}

test "competing successor replay keeps the visible chain authoritative across both helpers" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_live_first = ListHead{ .next = 0, .prev = 0 };
    var list_live_second = ListHead{ .next = 0, .prev = 0 };
    var list_contender = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_live_first);
    list_head.prev = @intFromPtr(&list_live_second);
    list_live_first.next = @intFromPtr(&list_live_second);
    list_live_first.prev = @intFromPtr(&list_head);
    list_live_second.next = @intFromPtr(&list_head);
    list_live_second.prev = @intFromPtr(&list_live_first);

    list_contender.next = @intFromPtr(&list_live_second);
    list_contender.prev = @intFromPtr(&list_live_first);

    const list_view_result = ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 2), list_view_result.len());
    try std.testing.expect(list_view_result.firstBrokenBacklink() == null);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_live_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_live_second = HListNode{ .next = 0, .pprev = 0 };
    var hlist_contender = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_live_first);
    hlist_live_first.next = @intFromPtr(&hlist_live_second);
    hlist_live_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_live_second.next = 0;
    hlist_live_second.pprev = @intFromPtr(&hlist_live_first.next);

    hlist_contender.next = @intFromPtr(&hlist_live_second);
    hlist_contender.pprev = @intFromPtr(&hlist_live_first.next);

    const hlist_view_result = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 2), hlist_view_result.len());
    try std.testing.expect(hlist_view_result.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist_view_result.tailNextIsNull());
}
