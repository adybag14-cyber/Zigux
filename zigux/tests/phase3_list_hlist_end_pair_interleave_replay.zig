const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListOrder(view: list_view.ListView, expected: []const *const list_view.ListHead) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const list_view.ListHead, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

fn expectHListOrder(view: hlist_view.HListView, expected: []const *const hlist_view.HListNode) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const hlist_view.HListNode, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

fn expectListBreak(view: list_view.ListView, index: usize, expected_prev: *const list_view.ListHead, actual_prev: *const list_view.ListHead) !void {
    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(index, breakage.current_index);
    try std.testing.expectEqual(@intFromPtr(expected_prev), breakage.expected_prev);
    try std.testing.expectEqual(@intFromPtr(actual_prev), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

fn expectHListBreak(view: hlist_view.HListView, index: usize, expected_pprev: *const usize, actual_pprev: *const usize) !void {
    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(index, breakage.current_index);
    try std.testing.expectEqual(@intFromPtr(expected_pprev), breakage.expected_pprev);
    try std.testing.expectEqual(@intFromPtr(actual_pprev), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}

test "list view follows end-pair interleave before staged backlinks are repaired" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var pre_tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&middle_left);
    second.prev = @intFromPtr(&first);
    middle_left.next = @intFromPtr(&middle_right);
    middle_left.prev = @intFromPtr(&second);
    middle_right.next = @intFromPtr(&pre_tail);
    middle_right.prev = @intFromPtr(&middle_left);
    pre_tail.next = @intFromPtr(&tail);
    pre_tail.prev = @intFromPtr(&middle_right);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&pre_tail);

    first.next = @intFromPtr(&tail);
    tail.next = @intFromPtr(&second);
    second.next = @intFromPtr(&pre_tail);
    pre_tail.next = @intFromPtr(&middle_left);
    middle_left.next = @intFromPtr(&middle_right);
    middle_right.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&middle_right);

    const view = list_view.ListView.init(&head);
    const order = [_]*const list_view.ListHead{ &first, &tail, &second, &pre_tail, &middle_left, &middle_right };

    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &middle_right), view.last());
    try expectListOrder(view, &order);
    try expectListBreak(view, 1, &first, &pre_tail);

    tail.prev = @intFromPtr(&first);
    try expectListBreak(view, 2, &tail, &first);

    second.prev = @intFromPtr(&tail);
    try expectListBreak(view, 3, &second, &middle_right);

    pre_tail.prev = @intFromPtr(&second);
    try expectListBreak(view, 4, &pre_tail, &second);

    middle_left.prev = @intFromPtr(&pre_tail);
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist view follows end-pair interleave before staged pprev links are repaired" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var pre_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&middle_left);
    second.pprev = @intFromPtr(&first.next);
    middle_left.next = @intFromPtr(&middle_right);
    middle_left.pprev = @intFromPtr(&second.next);
    middle_right.next = @intFromPtr(&pre_tail);
    middle_right.pprev = @intFromPtr(&middle_left.next);
    pre_tail.next = @intFromPtr(&tail);
    pre_tail.pprev = @intFromPtr(&middle_right.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&pre_tail.next);

    first.next = @intFromPtr(&tail);
    tail.next = @intFromPtr(&second);
    second.next = @intFromPtr(&pre_tail);
    pre_tail.next = @intFromPtr(&middle_left);
    middle_left.next = @intFromPtr(&middle_right);
    middle_right.next = 0;

    const view = hlist_view.HListView.init(&head);
    const order = [_]*const hlist_view.HListNode{ &first, &tail, &second, &pre_tail, &middle_left, &middle_right };

    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &middle_right), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());
    try expectHListOrder(view, &order);
    try expectHListBreak(view, 1, &first.next, &pre_tail.next);

    tail.pprev = @intFromPtr(&first.next);
    try expectHListBreak(view, 2, &tail.next, &first.next);

    second.pprev = @intFromPtr(&tail.next);
    try expectHListBreak(view, 3, &second.next, &middle_right.next);

    pre_tail.pprev = @intFromPtr(&second.next);
    try expectHListBreak(view, 4, &pre_tail.next, &second.next);

    middle_left.pprev = @intFromPtr(&pre_tail.next);
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}
