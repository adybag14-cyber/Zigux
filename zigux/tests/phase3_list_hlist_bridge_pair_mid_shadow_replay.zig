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

test "list bridge-pair mid shadow stays off-route until the visible middle adopts it" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var live_right = list_view.ListHead{ .next = 0, .prev = 0 };
    var tail = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_left = list_view.ListHead{ .next = 0, .prev = 0 };
    var shadow_right = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&live_right);
    middle.prev = @intFromPtr(&first);
    live_right.next = @intFromPtr(&tail);
    live_right.prev = @intFromPtr(&middle);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_right);

    shadow_left.next = @intFromPtr(&shadow_right);
    shadow_left.prev = @intFromPtr(&middle);
    shadow_right.next = @intFromPtr(&live_right);
    shadow_right.prev = @intFromPtr(&shadow_left);

    const stable = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 4), stable.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), stable.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), stable.last());
    try expectListSequence(stable, &.{ &first, &middle, &live_right, &tail });
    try testing.expect(stable.hasConsistentBacklinks());

    middle.next = @intFromPtr(&shadow_left);

    const broken = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 6), broken.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &tail), broken.last());
    try expectListSequence(
        broken,
        &.{ &first, &middle, &shadow_left, &shadow_right, &live_right, &tail },
    );

    const breakage = broken.firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 4), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&shadow_right)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&middle)), breakage.actual_prev);
    try testing.expect(!broken.hasConsistentBacklinks());
}

test "hlist bridge-pair mid shadow stays off-route until the visible middle adopts it" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var live_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var tail = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var shadow_right = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&live_right);
    middle.pprev = @intFromPtr(&first.next);
    live_right.next = @intFromPtr(&tail);
    live_right.pprev = @intFromPtr(&middle.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_right.next);

    shadow_left.next = @intFromPtr(&shadow_right);
    shadow_left.pprev = @intFromPtr(&middle.next);
    shadow_right.next = @intFromPtr(&live_right);
    shadow_right.pprev = @intFromPtr(&shadow_left.next);

    const stable = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 4), stable.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), stable.first());
    try expectHListSequence(stable, &.{ &first, &middle, &live_right, &tail });
    try testing.expect(stable.firstPprevMatchesHead());
    try testing.expect(stable.hasConsistentPrevLinks());
    try testing.expect(stable.tailNextIsNull());

    middle.next = @intFromPtr(&shadow_left);

    const broken = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 6), broken.len());
    try expectHListSequence(
        broken,
        &.{ &first, &middle, &shadow_left, &shadow_right, &live_right, &tail },
    );
    try testing.expect(broken.tailNextIsNull());

    const breakage = broken.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 4), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&shadow_right.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), breakage.actual_pprev);
    try testing.expect(!broken.hasConsistentPrevLinks());
}
