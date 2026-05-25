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

test "phase3 list/hlist pivot-hinge replay keeps the live pivot hinge visible over a detached alternate hinge" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var entry = ListHead{ .next = 0, .prev = 0 };
    var pivot = ListHead{ .next = 0, .prev = 0 };
    var live_hinge = ListHead{ .next = 0, .prev = 0 };
    var live_bridge = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow_hinge = ListHead{ .next = 0, .prev = 0 };
    var shadow_bridge = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&pivot);
    entry.prev = @intFromPtr(&head);
    pivot.next = @intFromPtr(&live_hinge);
    pivot.prev = @intFromPtr(&entry);
    live_hinge.next = @intFromPtr(&live_bridge);
    live_hinge.prev = @intFromPtr(&pivot);
    live_bridge.next = @intFromPtr(&tail);
    live_bridge.prev = @intFromPtr(&live_hinge);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_bridge);

    shadow_hinge.next = @intFromPtr(&shadow_bridge);
    shadow_hinge.prev = @intFromPtr(&pivot);
    shadow_bridge.next = @intFromPtr(&live_bridge);
    shadow_bridge.prev = @intFromPtr(&shadow_hinge);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &entry), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try expectListSequence(view, &.{ &entry, &pivot, &live_hinge, &live_bridge, &tail });
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist pivot-hinge replay reports the first rejoin backlink break after an alternate hinge is adopted" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var entry = ListHead{ .next = 0, .prev = 0 };
    var pivot = ListHead{ .next = 0, .prev = 0 };
    var live_hinge = ListHead{ .next = 0, .prev = 0 };
    var live_bridge = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow_hinge = ListHead{ .next = 0, .prev = 0 };
    var shadow_bridge = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&pivot);
    entry.prev = @intFromPtr(&head);
    pivot.next = @intFromPtr(&shadow_hinge);
    pivot.prev = @intFromPtr(&entry);
    live_hinge.next = @intFromPtr(&live_bridge);
    live_hinge.prev = @intFromPtr(&pivot);
    live_bridge.next = @intFromPtr(&tail);
    live_bridge.prev = @intFromPtr(&live_hinge);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_bridge);

    shadow_hinge.next = @intFromPtr(&shadow_bridge);
    shadow_hinge.prev = @intFromPtr(&pivot);
    shadow_bridge.next = @intFromPtr(&live_bridge);
    shadow_bridge.prev = @intFromPtr(&shadow_hinge);

    const view = ListView.init(&head);
    try expectListSequence(view, &.{ &entry, &pivot, &shadow_hinge, &shadow_bridge, &live_bridge, &tail });

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_bridge)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_hinge)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

test "phase3 list/hlist pivot-hinge replay keeps the live hlist pivot hinge visible over a detached alternate hinge" {
    var head = HListHead{ .first = 0 };
    var entry = HListNode{ .next = 0, .pprev = 0 };
    var pivot = HListNode{ .next = 0, .pprev = 0 };
    var live_hinge = HListNode{ .next = 0, .pprev = 0 };
    var live_bridge = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow_hinge = HListNode{ .next = 0, .pprev = 0 };
    var shadow_bridge = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&pivot);
    entry.pprev = @intFromPtr(&head.first);
    pivot.next = @intFromPtr(&live_hinge);
    pivot.pprev = @intFromPtr(&entry.next);
    live_hinge.next = @intFromPtr(&live_bridge);
    live_hinge.pprev = @intFromPtr(&pivot.next);
    live_bridge.next = @intFromPtr(&tail);
    live_bridge.pprev = @intFromPtr(&live_hinge.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_bridge.next);

    shadow_hinge.next = @intFromPtr(&shadow_bridge);
    shadow_hinge.pprev = @intFromPtr(&pivot.next);
    shadow_bridge.next = @intFromPtr(&live_bridge);
    shadow_bridge.pprev = @intFromPtr(&shadow_hinge.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 5), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &entry), view.first());
    try expectHListSequence(view, &.{ &entry, &pivot, &live_hinge, &live_bridge, &tail });
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}

test "phase3 list/hlist pivot-hinge replay reports the first hlist rejoin prev-link break after an alternate hinge is adopted" {
    var head = HListHead{ .first = 0 };
    var entry = HListNode{ .next = 0, .pprev = 0 };
    var pivot = HListNode{ .next = 0, .pprev = 0 };
    var live_hinge = HListNode{ .next = 0, .pprev = 0 };
    var live_bridge = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow_hinge = HListNode{ .next = 0, .pprev = 0 };
    var shadow_bridge = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&pivot);
    entry.pprev = @intFromPtr(&head.first);
    pivot.next = @intFromPtr(&shadow_hinge);
    pivot.pprev = @intFromPtr(&entry.next);
    live_hinge.next = @intFromPtr(&live_bridge);
    live_hinge.pprev = @intFromPtr(&pivot.next);
    live_bridge.next = @intFromPtr(&tail);
    live_bridge.pprev = @intFromPtr(&live_hinge.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_bridge.next);

    shadow_hinge.next = @intFromPtr(&shadow_bridge);
    shadow_hinge.pprev = @intFromPtr(&pivot.next);
    shadow_bridge.next = @intFromPtr(&live_bridge);
    shadow_bridge.pprev = @intFromPtr(&shadow_hinge.next);

    const view = HListView.init(&head);
    try expectHListSequence(view, &.{ &entry, &pivot, &shadow_hinge, &shadow_bridge, &live_bridge, &tail });

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_bridge.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_hinge.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}
