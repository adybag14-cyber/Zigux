const std = @import("std");

const hlist_view = @import("hlist_view");
const list_view = @import("list_view");

const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;
const ListHead = list_view.ListHead;
const ListView = list_view.ListView;

test "list prefix adoption exposes stale first backlink before repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var old_first = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var new_prefix = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&old_first);
    head.prev = @intFromPtr(&tail);
    old_first.next = @intFromPtr(&tail);
    old_first.prev = @intFromPtr(&head);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&old_first);

    const original = ListView.init(&head);
    try std.testing.expectEqual(@as(?*const ListHead, &old_first), original.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), original.last());
    try std.testing.expectEqual(@as(usize, 2), original.len());
    try std.testing.expect(original.hasConsistentBacklinks());

    head.next = @intFromPtr(&new_prefix);
    new_prefix.next = @intFromPtr(&old_first);
    new_prefix.prev = @intFromPtr(&head);

    const adopted_prefix = ListView.init(&head);
    try std.testing.expectEqual(@as(?*const ListHead, &new_prefix), adopted_prefix.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), adopted_prefix.last());
    try std.testing.expectEqual(@as(usize, 3), adopted_prefix.len());
    try std.testing.expect(!adopted_prefix.isSingular());

    const breakage = adopted_prefix.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&new_prefix)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);

    old_first.prev = @intFromPtr(&new_prefix);
    try std.testing.expect(ListView.init(&head).hasConsistentBacklinks());
}

test "hlist prefix adoption exposes stale first successor pprev before repair" {
    var head = HListHead{ .first = 0 };
    var old_first = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var new_prefix = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&old_first);
    old_first.next = @intFromPtr(&tail);
    old_first.pprev = @intFromPtr(&head.first);
    tail.next = 0;
    tail.pprev = @intFromPtr(&old_first.next);

    const original = HListView.init(&head);
    try std.testing.expectEqual(@as(?*const HListNode, &old_first), original.first());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), original.last());
    try std.testing.expectEqual(@as(usize, 2), original.len());
    try std.testing.expect(original.firstPprevMatchesHead());
    try std.testing.expect(original.hasConsistentPrevLinks());
    try std.testing.expect(original.tailNextIsNull());

    head.first = @intFromPtr(&new_prefix);
    new_prefix.next = @intFromPtr(&old_first);
    new_prefix.pprev = @intFromPtr(&head.first);

    const adopted_prefix = HListView.init(&head);
    try std.testing.expectEqual(@as(?*const HListNode, &new_prefix), adopted_prefix.first());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), adopted_prefix.last());
    try std.testing.expectEqual(@as(usize, 3), adopted_prefix.len());
    try std.testing.expect(adopted_prefix.firstPprevMatchesHead());
    try std.testing.expect(adopted_prefix.tailNextIsNull());

    const breakage = adopted_prefix.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&new_prefix.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);

    old_first.pprev = @intFromPtr(&new_prefix.next);
    try std.testing.expect(HListView.init(&head).hasConsistentPrevLinks());
}
