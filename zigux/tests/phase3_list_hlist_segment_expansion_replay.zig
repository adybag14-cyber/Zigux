const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListSequence(
    view: list_view.ListView,
    expected: []const *const list_view.ListHead,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const list_view.ListHead, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

fn expectHListSequence(
    view: hlist_view.HListView,
    expected: []const *const hlist_view.HListNode,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const hlist_view.HListNode, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "list view follows an expanded live segment instead of a stale shorter shortcut" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var expansion = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_shortcut = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&expansion);
    middle.prev = @intFromPtr(&first);
    expansion.next = @intFromPtr(&tail);
    expansion.prev = @intFromPtr(&middle);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&expansion);

    // A detached node still remembers the older shorter first->tail route.
    stale_shortcut.next = @intFromPtr(&tail);
    stale_shortcut.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &middle, &expansion, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "list view reports a stale shorter shortcut once the visible route is rewired through it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var expansion = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var stale_shortcut = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&stale_shortcut);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&expansion);
    middle.prev = @intFromPtr(&first);
    expansion.next = @intFromPtr(&tail);
    expansion.prev = @intFromPtr(&middle);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&expansion);

    stale_shortcut.next = @intFromPtr(&tail);
    stale_shortcut.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &stale_shortcut, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&stale_shortcut)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&expansion)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "hlist view follows an expanded live segment instead of a stale shorter shortcut" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var expansion = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_shortcut = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&expansion);
    middle.pprev = @intFromPtr(&first.next);
    expansion.next = @intFromPtr(&tail);
    expansion.pprev = @intFromPtr(&middle.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&expansion.next);

    stale_shortcut.next = @intFromPtr(&tail);
    stale_shortcut.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &middle, &expansion, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "hlist view reports a stale shorter shortcut once the visible route is rewired through it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var expansion = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var stale_shortcut = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&stale_shortcut);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&expansion);
    middle.pprev = @intFromPtr(&first.next);
    expansion.next = @intFromPtr(&tail);
    expansion.pprev = @intFromPtr(&middle.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&expansion.next);

    stale_shortcut.next = @intFromPtr(&tail);
    stale_shortcut.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &stale_shortcut, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&stale_shortcut.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&expansion.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
