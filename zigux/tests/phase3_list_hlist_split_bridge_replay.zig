const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "phase3 list split bridge reports stale and repaired right segment" {
    var left_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var right_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var a = list_view.ListHead{ .next = 0, .prev = 0 };
    var b = list_view.ListHead{ .next = 0, .prev = 0 };
    var c = list_view.ListHead{ .next = 0, .prev = 0 };
    var d = list_view.ListHead{ .next = 0, .prev = 0 };

    left_head.next = @intFromPtr(&a);
    left_head.prev = @intFromPtr(&b);
    a.next = @intFromPtr(&b);
    a.prev = @intFromPtr(&left_head);
    b.next = @intFromPtr(&left_head);
    b.prev = @intFromPtr(&a);

    right_head.next = @intFromPtr(&c);
    right_head.prev = @intFromPtr(&d);
    c.next = @intFromPtr(&d);
    c.prev = @intFromPtr(&b);
    d.next = @intFromPtr(&right_head);
    d.prev = @intFromPtr(&c);

    const left_view = list_view.ListView.init(&left_head);
    try std.testing.expectEqual(@as(usize, 2), left_view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &a), left_view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &b), left_view.last());
    try std.testing.expect(left_view.hasConsistentBacklinks());

    const stale_right = list_view.ListView.init(&right_head);
    try std.testing.expectEqual(@as(usize, 2), stale_right.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &c), stale_right.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &d), stale_right.last());
    try std.testing.expect(!stale_right.hasConsistentBacklinks());

    const breakage = stale_right.firstBrokenBacklink() orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right_head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&b)), breakage.actual_prev);

    c.prev = @intFromPtr(&right_head);

    const repaired_right = list_view.ListView.init(&right_head);
    try std.testing.expectEqual(@as(usize, 2), repaired_right.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &c), repaired_right.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &d), repaired_right.last());
    try std.testing.expect(repaired_right.hasConsistentBacklinks());
}

test "phase3 hlist split bridge reports stale and repaired right segment" {
    var left_head = hlist_view.HListHead{ .first = 0 };
    var right_head = hlist_view.HListHead{ .first = 0 };
    var a = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var b = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var c = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var d = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    left_head.first = @intFromPtr(&a);
    a.next = @intFromPtr(&b);
    a.pprev = @intFromPtr(&left_head.first);
    b.next = 0;
    b.pprev = @intFromPtr(&a.next);

    right_head.first = @intFromPtr(&c);
    c.next = @intFromPtr(&d);
    c.pprev = @intFromPtr(&b.next);
    d.next = 0;
    d.pprev = @intFromPtr(&c.next);

    const left_view = hlist_view.HListView.init(&left_head);
    try std.testing.expectEqual(@as(usize, 2), left_view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &a), left_view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &b), left_view.last());
    try std.testing.expect(left_view.firstPprevMatchesHead());
    try std.testing.expect(left_view.hasConsistentPrevLinks());
    try std.testing.expect(left_view.tailNextIsNull());

    const stale_right = hlist_view.HListView.init(&right_head);
    try std.testing.expectEqual(@as(usize, 2), stale_right.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &c), stale_right.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &d), stale_right.last());
    try std.testing.expect(!stale_right.firstPprevMatchesHead());
    try std.testing.expect(!stale_right.hasConsistentPrevLinks());
    try std.testing.expect(stale_right.tailNextIsNull());

    const breakage = stale_right.firstBrokenPrevLink() orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right_head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&b.next)), breakage.actual_pprev);

    c.pprev = @intFromPtr(&right_head.first);

    const repaired_right = hlist_view.HListView.init(&right_head);
    try std.testing.expectEqual(@as(usize, 2), repaired_right.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &c), repaired_right.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &d), repaired_right.last());
    try std.testing.expect(repaired_right.firstPprevMatchesHead());
    try std.testing.expect(repaired_right.hasConsistentPrevLinks());
    try std.testing.expect(repaired_right.tailNextIsNull());
}
