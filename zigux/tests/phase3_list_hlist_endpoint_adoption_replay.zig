const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 list head adoption reports stale and repaired tail endpoints" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var old_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var adopted = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&adopted);
    head.prev = @intFromPtr(&old_first);
    adopted.next = @intFromPtr(&head);
    adopted.prev = @intFromPtr(&head);
    old_first.next = @intFromPtr(&old_first);
    old_first.prev = @intFromPtr(&old_first);

    const stale_view = list_view.ListView.init(&head);
    try std.testing.expect(!stale_view.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), stale_view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &adopted), stale_view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &old_first), stale_view.last());
    try std.testing.expect(!stale_view.hasConsistentBacklinks());

    const breakage = stale_view.firstBrokenBacklink() orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&adopted)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_first)), breakage.actual_prev);

    head.prev = @intFromPtr(&adopted);

    const repaired_view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 1), repaired_view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &adopted), repaired_view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &adopted), repaired_view.last());
    try std.testing.expect(repaired_view.hasConsistentBacklinks());
}

test "phase3 hlist head adoption reports stale and repaired first pprev" {
    var head = hlist_view.HListHead{ .first = 0 };
    var old_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var adopted = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&adopted);
    adopted.next = 0;
    adopted.pprev = @intFromPtr(&old_first.next);
    old_first.next = 0;
    old_first.pprev = @intFromPtr(&old_first.next);

    const stale_view = hlist_view.HListView.init(&head);
    try std.testing.expect(!stale_view.isEmpty());
    try std.testing.expectEqual(@as(usize, 1), stale_view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &adopted), stale_view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &adopted), stale_view.last());
    try std.testing.expect(!stale_view.firstPprevMatchesHead());
    try std.testing.expect(!stale_view.hasConsistentPrevLinks());

    const breakage = stale_view.firstBrokenPrevLink() orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_first.next)), breakage.actual_pprev);

    adopted.pprev = @intFromPtr(&head.first);

    const repaired_view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 1), repaired_view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &adopted), repaired_view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &adopted), repaired_view.last());
    try std.testing.expect(repaired_view.firstPprevMatchesHead());
    try std.testing.expect(repaired_view.hasConsistentPrevLinks());
    try std.testing.expect(repaired_view.tailNextIsNull());
}
