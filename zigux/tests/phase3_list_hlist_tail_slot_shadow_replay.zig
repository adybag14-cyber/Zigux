const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view ignores a detached tail-slot shadow until the head-rooted route changes" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_first = ListHead{ .next = 0, .prev = 0 };
    var live_second = ListHead{ .next = 0, .prev = 0 };
    var live_tail = ListHead{ .next = 0, .prev = 0 };
    var detached_shadow = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_first);
    head.prev = @intFromPtr(&live_tail);
    live_first.next = @intFromPtr(&live_second);
    live_first.prev = @intFromPtr(&head);
    live_second.next = @intFromPtr(&live_tail);
    live_second.prev = @intFromPtr(&live_first);
    live_tail.next = @intFromPtr(&head);
    live_tail.prev = @intFromPtr(&live_second);

    detached_shadow.next = @intFromPtr(&head);
    detached_shadow.prev = @intFromPtr(&live_second);

    const stable_view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), stable_view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), stable_view.last());
    try std.testing.expect(stable_view.hasConsistentBacklinks());
    try std.testing.expect(stable_view.firstBrokenBacklink() == null);

    live_second.next = @intFromPtr(&detached_shadow);

    const rewired_view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), rewired_view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &live_tail), rewired_view.last());
    const breakage = rewired_view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached_shadow)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_tail)), breakage.actual_prev);
    try std.testing.expect(!rewired_view.hasConsistentBacklinks());
}

test "hlist view ignores a detached tail-slot shadow until the visible chain adopts it" {
    var head = HListHead{ .first = 0 };
    var live_first = HListNode{ .next = 0, .pprev = 0 };
    var live_second = HListNode{ .next = 0, .pprev = 0 };
    var live_tail = HListNode{ .next = 0, .pprev = 0 };
    var detached_shadow = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_first);
    live_first.next = @intFromPtr(&live_second);
    live_first.pprev = @intFromPtr(&head.first);
    live_second.next = @intFromPtr(&live_tail);
    live_second.pprev = @intFromPtr(&live_first.next);
    live_tail.next = 0;
    live_tail.pprev = @intFromPtr(&live_second.next);

    detached_shadow.next = 0;
    detached_shadow.pprev = @intFromPtr(&live_second.next);

    const stable_view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), stable_view.len());
    try std.testing.expect(stable_view.firstPprevMatchesHead());
    try std.testing.expect(stable_view.hasConsistentPrevLinks());
    try std.testing.expect(stable_view.tailNextIsNull());

    live_second.next = @intFromPtr(&detached_shadow);
    detached_shadow.pprev = @intFromPtr(&head.first);

    const rewired_view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), rewired_view.len());
    try std.testing.expect(rewired_view.firstPprevMatchesHead());
    try std.testing.expect(rewired_view.tailNextIsNull());
    const breakage = rewired_view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_second.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try std.testing.expect(!rewired_view.hasConsistentPrevLinks());
}

test "tail-slot shadow replay keeps the detached stale tails off the visible route" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_first = ListHead{ .next = 0, .prev = 0 };
    var list_second = ListHead{ .next = 0, .prev = 0 };
    var list_tail = ListHead{ .next = 0, .prev = 0 };
    var list_shadow = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_tail);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_tail);
    list_second.prev = @intFromPtr(&list_first);
    list_tail.next = @intFromPtr(&list_head);
    list_tail.prev = @intFromPtr(&list_second);
    list_shadow.next = @intFromPtr(&list_head);
    list_shadow.prev = @intFromPtr(&list_second);

    const list_result = ListView.init(&list_head);
    try std.testing.expectEqual(@as(usize, 3), list_result.len());
    try std.testing.expectEqual(@as(?*const ListHead, &list_tail), list_result.last());
    try std.testing.expect(list_result.hasConsistentBacklinks());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_second)), list_tail.prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_tail.next);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_first = HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = HListNode{ .next = 0, .pprev = 0 };
    var hlist_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_shadow = HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = @intFromPtr(&hlist_tail);
    hlist_second.pprev = @intFromPtr(&hlist_first.next);
    hlist_tail.next = 0;
    hlist_tail.pprev = @intFromPtr(&hlist_second.next);
    hlist_shadow.next = 0;
    hlist_shadow.pprev = @intFromPtr(&hlist_second.next);

    const hlist_result = HListView.init(&hlist_head);
    try std.testing.expectEqual(@as(usize, 3), hlist_result.len());
    try std.testing.expect(hlist_result.firstPprevMatchesHead());
    try std.testing.expect(hlist_result.hasConsistentPrevLinks());
    try std.testing.expect(hlist_result.tailNextIsNull());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_second.next)), hlist_tail.pprev);
    try std.testing.expectEqual(@as(usize, 0), hlist_tail.next);
}
