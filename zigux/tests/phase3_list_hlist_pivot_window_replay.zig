const std = @import("std");

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

fn expectListSequence(
    view: ListView,
    expected: []const *const ListHead,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const ListHead, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

fn expectHListSequence(
    view: HListView,
    expected: []const *const HListNode,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const HListNode, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "phase3 list/hlist pivot-window replay keeps the live pivot window visible over a detached alternate pivot window" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var entry = ListHead{ .next = 0, .prev = 0 };
    var live_left = ListHead{ .next = 0, .prev = 0 };
    var live_pivot = ListHead{ .next = 0, .prev = 0 };
    var live_right = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow_left = ListHead{ .next = 0, .prev = 0 };
    var shadow_pivot = ListHead{ .next = 0, .prev = 0 };
    var shadow_right = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&live_left);
    entry.prev = @intFromPtr(&head);
    live_left.next = @intFromPtr(&live_pivot);
    live_left.prev = @intFromPtr(&entry);
    live_pivot.next = @intFromPtr(&live_right);
    live_pivot.prev = @intFromPtr(&live_left);
    live_right.next = @intFromPtr(&tail);
    live_right.prev = @intFromPtr(&live_pivot);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_right);

    shadow_left.next = @intFromPtr(&shadow_pivot);
    shadow_left.prev = @intFromPtr(&entry);
    shadow_pivot.next = @intFromPtr(&shadow_right);
    shadow_pivot.prev = @intFromPtr(&shadow_left);
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.prev = @intFromPtr(&shadow_pivot);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &entry), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &entry, &live_left, &live_pivot, &live_right, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist pivot-window replay reports the stale list tail backlink after an alternate pivot window is adopted" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var entry = ListHead{ .next = 0, .prev = 0 };
    var live_left = ListHead{ .next = 0, .prev = 0 };
    var live_pivot = ListHead{ .next = 0, .prev = 0 };
    var live_right = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow_left = ListHead{ .next = 0, .prev = 0 };
    var shadow_pivot = ListHead{ .next = 0, .prev = 0 };
    var shadow_right = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&shadow_left);
    entry.prev = @intFromPtr(&head);
    live_left.next = @intFromPtr(&live_pivot);
    live_left.prev = @intFromPtr(&entry);
    live_pivot.next = @intFromPtr(&live_right);
    live_pivot.prev = @intFromPtr(&live_left);
    live_right.next = @intFromPtr(&tail);
    live_right.prev = @intFromPtr(&live_pivot);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_right);

    shadow_left.next = @intFromPtr(&shadow_pivot);
    shadow_left.prev = @intFromPtr(&entry);
    shadow_pivot.next = @intFromPtr(&shadow_right);
    shadow_pivot.prev = @intFromPtr(&shadow_left);
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.prev = @intFromPtr(&shadow_pivot);

    const view = ListView.init(&head);
    try expectListSequence(view, &.{ &entry, &shadow_left, &shadow_pivot, &shadow_right, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_right)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_right)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist pivot-window replay keeps the live pivot hlist window visible over a detached alternate pivot window" {
    var head = HListHead{ .first = 0 };
    var entry = HListNode{ .next = 0, .pprev = 0 };
    var live_left = HListNode{ .next = 0, .pprev = 0 };
    var live_pivot = HListNode{ .next = 0, .pprev = 0 };
    var live_right = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow_left = HListNode{ .next = 0, .pprev = 0 };
    var shadow_pivot = HListNode{ .next = 0, .pprev = 0 };
    var shadow_right = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&live_left);
    entry.pprev = @intFromPtr(&head.first);
    live_left.next = @intFromPtr(&live_pivot);
    live_left.pprev = @intFromPtr(&entry.next);
    live_pivot.next = @intFromPtr(&live_right);
    live_pivot.pprev = @intFromPtr(&live_left.next);
    live_right.next = @intFromPtr(&tail);
    live_right.pprev = @intFromPtr(&live_pivot.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_right.next);

    shadow_left.next = @intFromPtr(&shadow_pivot);
    shadow_left.pprev = @intFromPtr(&entry.next);
    shadow_pivot.next = @intFromPtr(&shadow_right);
    shadow_pivot.pprev = @intFromPtr(&shadow_left.next);
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.pprev = @intFromPtr(&shadow_pivot.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &entry), view.first());
    try expectHListSequence(view, &.{ &entry, &live_left, &live_pivot, &live_right, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}

test "phase3 list/hlist pivot-window replay reports the stale hlist tail prev-link after an alternate pivot window is adopted" {
    var head = HListHead{ .first = 0 };
    var entry = HListNode{ .next = 0, .pprev = 0 };
    var live_left = HListNode{ .next = 0, .pprev = 0 };
    var live_pivot = HListNode{ .next = 0, .pprev = 0 };
    var live_right = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow_left = HListNode{ .next = 0, .pprev = 0 };
    var shadow_pivot = HListNode{ .next = 0, .pprev = 0 };
    var shadow_right = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&shadow_left);
    entry.pprev = @intFromPtr(&head.first);
    live_left.next = @intFromPtr(&live_pivot);
    live_left.pprev = @intFromPtr(&entry.next);
    live_pivot.next = @intFromPtr(&live_right);
    live_pivot.pprev = @intFromPtr(&live_left.next);
    live_right.next = @intFromPtr(&tail);
    live_right.pprev = @intFromPtr(&live_pivot.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_right.next);

    shadow_left.next = @intFromPtr(&shadow_pivot);
    shadow_left.pprev = @intFromPtr(&entry.next);
    shadow_pivot.next = @intFromPtr(&shadow_right);
    shadow_pivot.pprev = @intFromPtr(&shadow_left.next);
    shadow_right.next = @intFromPtr(&tail);
    shadow_right.pprev = @intFromPtr(&shadow_pivot.next);

    const view = HListView.init(&head);
    try expectHListSequence(view, &.{ &entry, &shadow_left, &shadow_pivot, &shadow_right, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_right.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_right.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
