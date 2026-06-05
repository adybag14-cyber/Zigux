const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const testing = std.testing;

test "list head transplant reports stale adopted head backlink before repair" {
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

    new_head.next = @intFromPtr(&first);
    new_head.prev = @intFromPtr(&second);
    second.next = @intFromPtr(&new_head);

    const adopted = list_view.ListView.init(&new_head);
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), adopted.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &second), adopted.last());
    try testing.expectEqual(@as(usize, 2), adopted.len());
    try testing.expect(adopted.contains(&first));
    try testing.expect(adopted.contains(&second));

    const stale_head = adopted.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 0), stale_head.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&new_head)), stale_head.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&old_head)), stale_head.actual_prev);
    try testing.expect(!adopted.hasConsistentBacklinks());

    first.prev = @intFromPtr(&new_head);

    try testing.expect(list_view.ListView.init(&new_head).hasConsistentBacklinks());
    try testing.expectEqual(@as(usize, 2), list_view.ListView.init(&new_head).len());
}

test "hlist head transplant reports stale adopted first pprev before repair" {
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

    const adopted = hlist_view.HListView.init(&new_head);
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), adopted.first());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &second), adopted.last());
    try testing.expectEqual(@as(usize, 2), adopted.len());
    try testing.expect(adopted.contains(&first));
    try testing.expect(adopted.contains(&second));
    try testing.expect(adopted.tailNextIsNull());

    const stale_head = adopted.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 0), stale_head.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&new_head.first)), stale_head.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&old_head.first)), stale_head.actual_pprev);
    try testing.expect(!adopted.firstPprevMatchesHead());
    try testing.expect(!adopted.hasConsistentPrevLinks());

    first.pprev = @intFromPtr(&new_head.first);

    try testing.expect(hlist_view.HListView.init(&new_head).firstPprevMatchesHead());
    try testing.expect(hlist_view.HListView.init(&new_head).hasConsistentPrevLinks());
    try testing.expectEqual(@as(usize, 2), hlist_view.HListView.init(&new_head).len());
}
