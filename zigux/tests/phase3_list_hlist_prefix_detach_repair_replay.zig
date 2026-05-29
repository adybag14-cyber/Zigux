const std = @import("std");

const hlist_view = @import("hlist_view");
const list_view = @import("list_view");

const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;
const ListHead = list_view.ListHead;
const ListView = list_view.ListView;

fn expectListOrder(view: ListView, expected: []const *const ListHead) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const ListHead, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

fn expectHListOrder(view: HListView, expected: []const *const HListNode) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const HListNode, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "list view detects and clears prefix-detach backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var detached_prefix = ListHead{ .next = 0, .prev = 0 };
    var first_live = ListHead{ .next = 0, .prev = 0 };
    var second_live = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first_live);
    head.prev = @intFromPtr(&tail);
    detached_prefix.next = @intFromPtr(&first_live);
    detached_prefix.prev = @intFromPtr(&head);
    first_live.next = @intFromPtr(&second_live);
    first_live.prev = @intFromPtr(&detached_prefix);
    second_live.next = @intFromPtr(&tail);
    second_live.prev = @intFromPtr(&first_live);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&second_live);

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &first_live, &second_live, &tail });
    try std.testing.expectEqual(@as(?*const ListHead, &first_live), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached_prefix)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    first_live.prev = @intFromPtr(&head);
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
    try expectListOrder(view, &.{ &first_live, &second_live, &tail });
}

test "hlist view detects and clears prefix-detach prev-link repair" {
    var head = HListHead{ .first = 0 };
    var detached_prefix = HListNode{ .next = 0, .pprev = 0 };
    var first_live = HListNode{ .next = 0, .pprev = 0 };
    var second_live = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first_live);
    detached_prefix.next = @intFromPtr(&first_live);
    detached_prefix.pprev = @intFromPtr(&head.first);
    first_live.next = @intFromPtr(&second_live);
    first_live.pprev = @intFromPtr(&detached_prefix.next);
    second_live.next = 0;
    second_live.pprev = @intFromPtr(&first_live.next);

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &first_live, &second_live });
    try std.testing.expect(!view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&detached_prefix.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    first_live.pprev = @intFromPtr(&head.first);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try expectHListOrder(view, &.{ &first_live, &second_live });
    try std.testing.expect(view.tailNextIsNull());
}
