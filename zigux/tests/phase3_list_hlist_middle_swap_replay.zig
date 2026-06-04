const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view reports stale middle swap metadata before repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var left = ListHead{ .next = 0, .prev = 0 };
    var old_mid_a = ListHead{ .next = 0, .prev = 0 };
    var old_mid_b = ListHead{ .next = 0, .prev = 0 };
    var right = ListHead{ .next = 0, .prev = 0 };
    var new_mid_a = ListHead{ .next = 0, .prev = 0 };
    var new_mid_b = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&left);
    head.prev = @intFromPtr(&right);
    left.next = @intFromPtr(&old_mid_a);
    left.prev = @intFromPtr(&head);
    old_mid_a.next = @intFromPtr(&old_mid_b);
    old_mid_a.prev = @intFromPtr(&left);
    old_mid_b.next = @intFromPtr(&right);
    old_mid_b.prev = @intFromPtr(&old_mid_a);
    right.next = @intFromPtr(&head);
    right.prev = @intFromPtr(&old_mid_b);

    var view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &left), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &right), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());

    left.next = @intFromPtr(&new_mid_a);
    new_mid_a.next = @intFromPtr(&new_mid_b);
    new_mid_a.prev = @intFromPtr(&old_mid_b);
    new_mid_b.next = @intFromPtr(&right);
    new_mid_b.prev = @intFromPtr(&new_mid_a);

    view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &left), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &right), view.last());
    try std.testing.expect(!view.hasConsistentBacklinks());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_mid_b)), breakage.actual_prev);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &left), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &new_mid_a), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &new_mid_b), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &right), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());

    new_mid_a.prev = @intFromPtr(&left);
    right.prev = @intFromPtr(&new_mid_b);

    view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &right), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist view reports stale middle swap prev-link before repair" {
    var head = HListHead{ .first = 0 };
    var left = HListNode{ .next = 0, .pprev = 0 };
    var old_mid_a = HListNode{ .next = 0, .pprev = 0 };
    var old_mid_b = HListNode{ .next = 0, .pprev = 0 };
    var right = HListNode{ .next = 0, .pprev = 0 };
    var new_mid_a = HListNode{ .next = 0, .pprev = 0 };
    var new_mid_b = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&left);
    left.next = @intFromPtr(&old_mid_a);
    left.pprev = @intFromPtr(&head.first);
    old_mid_a.next = @intFromPtr(&old_mid_b);
    old_mid_a.pprev = @intFromPtr(&left.next);
    old_mid_b.next = @intFromPtr(&right);
    old_mid_b.pprev = @intFromPtr(&old_mid_a.next);
    right.next = 0;
    right.pprev = @intFromPtr(&old_mid_b.next);

    var view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &left), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &right), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    left.next = @intFromPtr(&new_mid_a);
    new_mid_a.next = @intFromPtr(&new_mid_b);
    new_mid_a.pprev = @intFromPtr(&old_mid_b.next);
    new_mid_b.next = @intFromPtr(&right);
    new_mid_b.pprev = @intFromPtr(&new_mid_a.next);

    view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &left), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &right), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&left.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_mid_b.next)), breakage.actual_pprev);

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &left), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &new_mid_a), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &new_mid_b), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &right), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());

    new_mid_a.pprev = @intFromPtr(&left.next);
    right.pprev = @intFromPtr(&new_mid_b.next);

    view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &right), view.last());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}
