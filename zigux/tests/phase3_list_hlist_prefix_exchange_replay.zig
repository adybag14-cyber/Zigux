const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListPair(
    view: list_view.ListView,
    first: *const list_view.ListHead,
    last: *const list_view.ListHead,
) !void {
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, last), view.last());
    try std.testing.expect(view.contains(first));
    try std.testing.expect(view.contains(last));
    try std.testing.expect(view.hasConsistentBacklinks());
}

fn expectHListPair(
    view: hlist_view.HListView,
    first: *const hlist_view.HListNode,
    last: *const hlist_view.HListNode,
) !void {
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, first), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, last), view.last());
    try std.testing.expect(view.contains(first));
    try std.testing.expect(view.contains(last));
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "list prefix exchange exposes stale circular backlinks before repair" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var old_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var old_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var new_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var new_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&old_left);
    head.prev = @intFromPtr(&old_right);
    old_left.next = @intFromPtr(&old_right);
    old_left.prev = @intFromPtr(&head);
    old_right.next = @intFromPtr(&head);
    old_right.prev = @intFromPtr(&old_left);

    try expectListPair(list_view.ListView.init(&head), &old_left, &old_right);

    head.next = @intFromPtr(&new_left);
    new_left.next = @intFromPtr(&new_right);
    new_left.prev = @intFromPtr(&old_left);
    new_right.next = @intFromPtr(&head);
    new_right.prev = @intFromPtr(&new_left);

    const stale_prefix = list_view.ListView.init(&head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), stale_prefix.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), stale_prefix.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_left)), stale_prefix.actual_prev);
    try std.testing.expect(!list_view.ListView.init(&head).hasConsistentBacklinks());

    new_left.prev = @intFromPtr(&head);
    head.prev = @intFromPtr(&new_right);
    old_left.next = @intFromPtr(&old_left);
    old_left.prev = @intFromPtr(&old_left);
    old_right.next = @intFromPtr(&old_right);
    old_right.prev = @intFromPtr(&old_right);

    const repaired = list_view.ListView.init(&head);
    try expectListPair(repaired, &new_left, &new_right);
    try std.testing.expect(!repaired.contains(&old_left));
    try std.testing.expect(!repaired.contains(&old_right));
}

test "hlist prefix exchange exposes stale pprev links before repair" {
    var head = hlist_view.HListHead{ .first = 0 };
    var old_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var old_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var new_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var new_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&old_left);
    old_left.next = @intFromPtr(&old_right);
    old_left.pprev = @intFromPtr(&head.first);
    old_right.next = 0;
    old_right.pprev = @intFromPtr(&old_left.next);

    try expectHListPair(hlist_view.HListView.init(&head), &old_left, &old_right);

    head.first = @intFromPtr(&new_left);
    new_left.next = @intFromPtr(&new_right);
    new_left.pprev = @intFromPtr(&old_left.next);
    new_right.next = 0;
    new_right.pprev = @intFromPtr(&new_left.next);

    const stale_prefix = hlist_view.HListView.init(&head).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), stale_prefix.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), stale_prefix.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_left.next)), stale_prefix.actual_pprev);
    try std.testing.expect(!hlist_view.HListView.init(&head).firstPprevMatchesHead());
    try std.testing.expect(!hlist_view.HListView.init(&head).hasConsistentPrevLinks());

    new_left.pprev = @intFromPtr(&head.first);
    old_left.next = 0;
    old_left.pprev = 0;
    old_right.next = 0;
    old_right.pprev = 0;

    const repaired = hlist_view.HListView.init(&head);
    try expectHListPair(repaired, &new_left, &new_right);
    try std.testing.expect(!repaired.contains(&old_left));
    try std.testing.expect(!repaired.contains(&old_right));
}
