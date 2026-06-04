const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view reports stale tail swap metadata before repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var old_tail = ListHead{ .next = 0, .prev = 0 };
    var new_tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&old_tail);
    first.next = @intFromPtr(&old_tail);
    first.prev = @intFromPtr(&head);
    old_tail.next = @intFromPtr(&head);
    old_tail.prev = @intFromPtr(&first);

    var view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &old_tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());

    first.next = @intFromPtr(&new_tail);
    new_tail.next = @intFromPtr(&head);
    new_tail.prev = @intFromPtr(&old_tail);

    view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &old_tail), view.last());
    try std.testing.expect(!view.hasConsistentBacklinks());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_tail)), breakage.actual_prev);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &new_tail), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());

    new_tail.prev = @intFromPtr(&first);
    head.prev = @intFromPtr(&new_tail);

    view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &new_tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist view reports stale tail swap prev-link before repair" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var old_tail = HListNode{ .next = 0, .pprev = 0 };
    var new_tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&old_tail);
    first.pprev = @intFromPtr(&head.first);
    old_tail.next = 0;
    old_tail.pprev = @intFromPtr(&first.next);

    var view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &old_tail), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    first.next = @intFromPtr(&new_tail);
    new_tail.next = 0;
    new_tail.pprev = @intFromPtr(&old_tail.next);

    view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &new_tail), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_tail.next)), breakage.actual_pprev);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &new_tail), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());

    new_tail.pprev = @intFromPtr(&first.next);

    view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &new_tail), view.last());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}
