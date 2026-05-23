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

test "phase3 list/hlist tail shadow rejoin replay keeps the live list tail route visible while a shadow rejoin stays off path" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail_entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&tail_entry);
    middle.prev = @intFromPtr(&first);
    tail_entry.next = @intFromPtr(&tail);
    tail_entry.prev = @intFromPtr(&middle);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&tail_entry);

    shadow_entry.next = @intFromPtr(&shadow_tail);
    shadow_entry.prev = @intFromPtr(&tail_entry);
    shadow_tail.next = @intFromPtr(&tail);
    shadow_tail.prev = @intFromPtr(&shadow_entry);

    const view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &first, &middle, &tail_entry, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist tail shadow rejoin replay reports the first visible list break when the shadow tail rejoins early" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail_entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_tail = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&tail_entry);
    middle.prev = @intFromPtr(&first);
    tail_entry.next = @intFromPtr(&shadow_entry);
    tail_entry.prev = @intFromPtr(&middle);
    shadow_entry.next = @intFromPtr(&tail);
    shadow_entry.prev = @intFromPtr(&tail_entry);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&shadow_tail);

    shadow_tail.next = @intFromPtr(&tail);
    shadow_tail.prev = @intFromPtr(&shadow_entry);

    const view = list_view.ListView.init(&head);
    try expectListSequence(view, &.{ &first, &middle, &tail_entry, &shadow_entry, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_entry)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_tail)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist tail shadow rejoin replay keeps the live hlist tail route visible while a shadow rejoin stays off path" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail_entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&tail_entry);
    middle.pprev = @intFromPtr(&first.next);
    tail_entry.next = @intFromPtr(&tail);
    tail_entry.pprev = @intFromPtr(&middle.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&tail_entry.next);

    shadow_entry.next = @intFromPtr(&shadow_tail);
    shadow_entry.pprev = 0;
    shadow_tail.next = @intFromPtr(&tail);
    shadow_tail.pprev = @intFromPtr(&shadow_entry.next);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try expectHListSequence(view, &.{ &first, &middle, &tail_entry, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "phase3 list/hlist tail shadow rejoin replay reports the first visible hlist break when the shadow tail rejoins early" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail_entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&tail_entry);
    middle.pprev = @intFromPtr(&first.next);
    tail_entry.next = @intFromPtr(&shadow_entry);
    tail_entry.pprev = @intFromPtr(&middle.next);
    shadow_entry.next = @intFromPtr(&tail);
    shadow_entry.pprev = @intFromPtr(&tail_entry.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&shadow_tail.next);

    shadow_tail.next = @intFromPtr(&tail);
    shadow_tail.pprev = @intFromPtr(&shadow_entry.next);

    const view = hlist_view.HListView.init(&head);
    try expectHListSequence(view, &.{ &first, &middle, &tail_entry, &shadow_entry, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_entry.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_tail.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
