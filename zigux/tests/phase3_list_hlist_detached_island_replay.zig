const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list view ignores a detached island until it is spliced visible" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var island_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var island_second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    island_first.next = @intFromPtr(&island_second);
    island_first.prev = @intFromPtr(&head);
    island_second.next = @intFromPtr(&head);
    island_second.prev = @intFromPtr(&head);

    const isolated = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 2), isolated.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), isolated.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &second), isolated.last());
    try testing.expect(isolated.hasConsistentBacklinks());
    try testing.expect(isolated.firstBrokenBacklink() == null);

    var it = isolated.iterator();
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), it.next());
    try testing.expectEqual(@as(?*const list_view.ListHead, &second), it.next());
    try testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());

    second.next = @intFromPtr(&island_first);
    head.prev = @intFromPtr(&island_second);
    island_first.prev = @intFromPtr(&second);
    island_second.prev = @intFromPtr(&island_first);

    const spliced = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), spliced.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), spliced.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &island_second), spliced.last());
    try testing.expect(spliced.hasConsistentBacklinks());
    try testing.expect(spliced.firstBrokenBacklink() == null);
}

test "hlist view ignores a detached island until it is linked visible" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var island_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var island_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    island_first.next = @intFromPtr(&island_second);
    island_first.pprev = @intFromPtr(&head.first);
    island_second.next = 0;
    island_second.pprev = @intFromPtr(&head.first);

    const isolated = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 2), isolated.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), isolated.first());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &second), isolated.last());
    try testing.expect(isolated.firstPprevMatchesHead());
    try testing.expect(isolated.hasConsistentPrevLinks());
    try testing.expect(isolated.tailNextIsNull());

    var it = isolated.iterator();
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), it.next());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &second), it.next());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());

    second.next = @intFromPtr(&island_first);
    island_first.pprev = @intFromPtr(&second.next);
    island_second.pprev = @intFromPtr(&island_first.next);

    const linked = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), linked.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), linked.first());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &island_second), linked.last());
    try testing.expect(linked.firstPprevMatchesHead());
    try testing.expect(linked.hasConsistentPrevLinks());
    try testing.expect(linked.firstBrokenPrevLink() == null);
    try testing.expect(linked.tailNextIsNull());
}
