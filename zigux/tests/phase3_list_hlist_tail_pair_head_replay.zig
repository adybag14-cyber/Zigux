const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;

fn expectListRoute(view: list_view.ListView, expected: []const *const ListHead) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const ListHead, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

fn expectHListRoute(view: hlist_view.HListView, expected: []const *const HListNode) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const HListNode, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "list view sees tail pair promoted after old head drop before backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var old_first = ListHead{ .next = 0, .prev = 0 };
    var middle = ListHead{ .next = 0, .prev = 0 };
    var tail_a = ListHead{ .next = 0, .prev = 0 };
    var tail_b = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&old_first);
    head.prev = @intFromPtr(&tail_b);
    old_first.next = @intFromPtr(&middle);
    old_first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&tail_a);
    middle.prev = @intFromPtr(&old_first);
    tail_a.next = @intFromPtr(&tail_b);
    tail_a.prev = @intFromPtr(&middle);
    tail_b.next = @intFromPtr(&head);
    tail_b.prev = @intFromPtr(&tail_a);

    head.next = @intFromPtr(&tail_a);
    middle.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&middle);
    tail_b.next = @intFromPtr(&middle);

    const staged = list_view.ListView.init(&head);
    try std.testing.expect(!staged.isEmpty());
    try std.testing.expect(!staged.isSingular());
    try std.testing.expectEqual(@as(?*const ListHead, &tail_a), staged.first());
    try std.testing.expectEqual(@as(?*const ListHead, &middle), staged.last());
    try expectListRoute(staged, &.{ &tail_a, &tail_b, &middle });
    try std.testing.expect(!staged.contains(&old_first));

    const first_break = staged.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), first_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle)), first_break.actual_prev);

    tail_a.prev = @intFromPtr(&head);
    const second_break = staged.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), second_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail_b)), second_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_first)), second_break.actual_prev);

    middle.prev = @intFromPtr(&tail_b);
    try std.testing.expect(staged.hasConsistentBacklinks());
}

test "hlist view sees tail pair promoted after old head drop before prev-link repair" {
    var head = HListHead{ .first = 0 };
    var old_first = HListNode{ .next = 0, .pprev = 0 };
    var middle = HListNode{ .next = 0, .pprev = 0 };
    var tail_a = HListNode{ .next = 0, .pprev = 0 };
    var tail_b = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&old_first);
    old_first.next = @intFromPtr(&middle);
    old_first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&tail_a);
    middle.pprev = @intFromPtr(&old_first.next);
    tail_a.next = @intFromPtr(&tail_b);
    tail_a.pprev = @intFromPtr(&middle.next);
    tail_b.next = 0;
    tail_b.pprev = @intFromPtr(&tail_a.next);

    head.first = @intFromPtr(&tail_a);
    tail_b.next = @intFromPtr(&middle);
    middle.next = 0;

    const staged = hlist_view.HListView.init(&head);
    try std.testing.expect(!staged.isEmpty());
    try std.testing.expect(!staged.isSingular());
    try std.testing.expectEqual(@as(?*const HListNode, &tail_a), staged.first());
    try std.testing.expectEqual(@as(?*const HListNode, &middle), staged.last());
    try expectHListRoute(staged, &.{ &tail_a, &tail_b, &middle });
    try std.testing.expect(!staged.contains(&old_first));
    try std.testing.expect(staged.tailNextIsNull());
    try std.testing.expect(!staged.firstPprevMatchesHead());

    const first_break = staged.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), first_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), first_break.actual_pprev);

    tail_a.pprev = @intFromPtr(&head.first);
    const second_break = staged.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), second_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail_b.next)), second_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_first.next)), second_break.actual_pprev);

    middle.pprev = @intFromPtr(&tail_b.next);
    try std.testing.expect(staged.firstPprevMatchesHead());
    try std.testing.expect(staged.hasConsistentPrevLinks());
}
