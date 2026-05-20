const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view keeps an empty head authoritative over detached populated shadows" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var detached_first = ListHead{ .next = 0, .prev = 0 };
    var detached_second = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    detached_first.next = @intFromPtr(&detached_second);
    detached_first.prev = @intFromPtr(&detached_second);
    detached_second.next = @intFromPtr(&detached_first);
    detached_second.prev = @intFromPtr(&detached_first);

    const view = ListView.init(&head);
    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, null), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, null), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);

    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached_second)), detached_first.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached_first)), detached_second.prev);
}

test "hlist view keeps an empty head authoritative over detached populated shadows" {
    var head = HListHead{ .first = 0 };
    var detached_first = HListNode{ .next = 0, .pprev = 0 };
    var detached_second = HListNode{ .next = 0, .pprev = 0 };
    var detached_anchor: usize = 0;

    detached_first.next = @intFromPtr(&detached_second);
    detached_first.pprev = @intFromPtr(&detached_anchor);
    detached_second.next = 0;
    detached_second.pprev = @intFromPtr(&detached_first.next);

    const view = HListView.init(&head);
    try std.testing.expect(view.isEmpty());
    try std.testing.expectEqual(@as(usize, 0), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, null), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());

    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached_second)), detached_first.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached_first.next)), detached_second.pprev);
}

test "empty-head shadow replay keeps both helpers pinned to the head-rooted route" {
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var list_shadow = ListHead{ .next = 0, .prev = 0 };
    var list_shadow_tail = ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_head);
    list_head.prev = @intFromPtr(&list_head);
    list_shadow.next = @intFromPtr(&list_shadow_tail);
    list_shadow.prev = @intFromPtr(&list_shadow_tail);
    list_shadow_tail.next = @intFromPtr(&list_shadow);
    list_shadow_tail.prev = @intFromPtr(&list_shadow);

    const list_result = ListView.init(&list_head);
    var list_it = list_result.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, null), list_it.next());
    try std.testing.expect(list_result.firstBrokenBacklink() == null);

    var hlist_head = HListHead{ .first = 0 };
    var hlist_shadow = HListNode{ .next = 0, .pprev = 0 };
    var hlist_shadow_tail = HListNode{ .next = 0, .pprev = 0 };
    var hlist_shadow_anchor: usize = 0;

    hlist_shadow.next = @intFromPtr(&hlist_shadow_tail);
    hlist_shadow.pprev = @intFromPtr(&hlist_shadow_anchor);
    hlist_shadow_tail.next = 0;
    hlist_shadow_tail.pprev = @intFromPtr(&hlist_shadow.next);

    const hlist_result = HListView.init(&hlist_head);
    var hlist_it = hlist_result.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, null), hlist_it.next());
    try std.testing.expect(hlist_result.firstBrokenPrevLink() == null);
    try std.testing.expect(hlist_result.tailNextIsNull());
}
