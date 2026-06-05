const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn initListHead(head: *list_view.ListHead) void {
    head.next = @intFromPtr(head);
    head.prev = @intFromPtr(head);
}

test "list head adoption keeps the new sentinel authoritative" {
    var old_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var new_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };

    old_head.next = @intFromPtr(&first);
    old_head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&old_head);
    second.next = @intFromPtr(&old_head);
    second.prev = @intFromPtr(&first);
    initListHead(&new_head);

    new_head.next = @intFromPtr(&first);
    new_head.prev = @intFromPtr(&second);
    first.prev = @intFromPtr(&new_head);
    second.next = @intFromPtr(&new_head);

    const adopted = list_view.ListView.init(&new_head);
    try testing.expect(!adopted.isEmpty());
    try testing.expectEqual(@as(usize, 2), adopted.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), adopted.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &second), adopted.last());
    try testing.expect(adopted.contains(&first));
    try testing.expect(adopted.contains(&second));
    try testing.expect(!adopted.contains(&old_head));
    try testing.expect(adopted.hasConsistentBacklinks());

    const stale = list_view.ListView.init(&old_head).firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 0), stale.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&old_head)), stale.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&new_head)), stale.actual_prev);
}

test "hlist head adoption keeps the head pprev boundary explicit" {
    var old_head = hlist_view.HListHead{ .first = 0 };
    var new_head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    old_head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&old_head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    new_head.first = @intFromPtr(&first);
    first.pprev = @intFromPtr(&new_head.first);

    const adopted = hlist_view.HListView.init(&new_head);
    try testing.expect(!adopted.isEmpty());
    try testing.expect(!adopted.isSingular());
    try testing.expectEqual(@as(usize, 2), adopted.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), adopted.first());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &second), adopted.last());
    try testing.expect(adopted.contains(&first));
    try testing.expect(adopted.contains(&second));
    try testing.expect(adopted.firstPprevMatchesHead());
    try testing.expect(adopted.hasConsistentPrevLinks());
    try testing.expect(adopted.tailNextIsNull());

    const stale = hlist_view.HListView.init(&old_head).firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 0), stale.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&old_head.first)), stale.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&new_head.first)), stale.actual_pprev);
}
