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

test "list view detects and clears an inner-window backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };
    var third = ListHead{ .next = 0, .prev = 0 };
    var fourth = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&fourth);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&third);
    second.prev = @intFromPtr(&head);
    third.next = @intFromPtr(&fourth);
    third.prev = @intFromPtr(&second);
    fourth.next = @intFromPtr(&head);
    fourth.prev = @intFromPtr(&third);

    const view = ListView.init(&head);
    try expectListOrder(view, &.{ &first, &second, &third, &fourth });

    const first_break = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), first_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), first_break.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    second.prev = @intFromPtr(&first);
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
    try expectListOrder(view, &.{ &first, &second, &third, &fourth });
}

test "hlist view detects and clears an inner-window prev-link repair" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };
    var third = HListNode{ .next = 0, .pprev = 0 };
    var fourth = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = @intFromPtr(&third);
    second.pprev = @intFromPtr(&head.first);
    third.next = @intFromPtr(&fourth);
    third.pprev = @intFromPtr(&second.next);
    fourth.next = 0;
    fourth.pprev = @intFromPtr(&third.next);

    const view = HListView.init(&head);
    try expectHListOrder(view, &.{ &first, &second, &third, &fourth });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());

    const first_break = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), first_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), first_break.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    second.pprev = @intFromPtr(&first.next);
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try expectHListOrder(view, &.{ &first, &second, &third, &fourth });
    try std.testing.expect(view.tailNextIsNull());
}
