const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListSequence(
    view: list_view.ListView,
    expected: []const *const list_view.ListHead,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try testing.expectEqual(@as(?*const list_view.ListHead, node), it.next());
    }
    try testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

fn expectHListSequence(
    view: hlist_view.HListView,
    expected: []const *const hlist_view.HListNode,
) !void {
    var it = view.iterator();
    for (expected) |node| {
        try testing.expectEqual(@as(?*const hlist_view.HListNode, node), it.next());
    }
    try testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "list bridge-pair head claim stays off-route until the visible bridge adopts it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var entry = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var bridge_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var claim_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var claim_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&bridge_left);
    entry.prev = @intFromPtr(&head);
    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.prev = @intFromPtr(&entry);
    bridge_right.next = @intFromPtr(&tail);
    bridge_right.prev = @intFromPtr(&bridge_left);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge_right);

    claim_left.next = @intFromPtr(&claim_right);
    claim_left.prev = @intFromPtr(&head);
    claim_right.next = @intFromPtr(&bridge_left);
    claim_right.prev = @intFromPtr(&claim_left);

    const stable = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), stable.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &entry), stable.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), stable.last());
    try expectListSequence(stable, &.{ &entry, &bridge_left, &bridge_right, &tail });
    try testing.expect(stable.hasConsistentBacklinks());

    bridge_left.prev = @intFromPtr(&claim_right);

    const broken = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), broken.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &entry), broken.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), broken.last());
    try expectListSequence(broken, &.{ &entry, &bridge_left, &bridge_right, &tail });

    const breakage = broken.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&entry)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&claim_right)), breakage.actual_prev);
    try testing.expect(!broken.hasConsistentBacklinks());
}

test "hlist bridge-pair head claim stays off-route until the visible bridge adopts it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var entry = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var bridge_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var claim_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var claim_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&bridge_left);
    entry.pprev = @intFromPtr(&head.first);
    bridge_left.next = @intFromPtr(&bridge_right);
    bridge_left.pprev = @intFromPtr(&entry.next);
    bridge_right.next = @intFromPtr(&tail);
    bridge_right.pprev = @intFromPtr(&bridge_left.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge_right.next);

    claim_left.next = @intFromPtr(&claim_right);
    claim_left.pprev = @intFromPtr(&head.first);
    claim_right.next = @intFromPtr(&bridge_left);
    claim_right.pprev = @intFromPtr(&claim_left.next);

    const stable = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), stable.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &entry), stable.first());
    try expectHListSequence(stable, &.{ &entry, &bridge_left, &bridge_right, &tail });
    try testing.expect(stable.firstPprevMatchesHead());
    try testing.expect(stable.hasConsistentPrevLinks());
    try testing.expect(stable.tailNextIsNull());

    bridge_left.pprev = @intFromPtr(&claim_right.next);

    const broken = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), broken.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &entry), broken.first());
    try expectHListSequence(broken, &.{ &entry, &bridge_left, &bridge_right, &tail });
    try testing.expect(broken.firstPprevMatchesHead());
    try testing.expect(broken.tailNextIsNull());

    const breakage = broken.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&entry.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&claim_right.next)), breakage.actual_pprev);
    try testing.expect(!broken.hasConsistentPrevLinks());
}
