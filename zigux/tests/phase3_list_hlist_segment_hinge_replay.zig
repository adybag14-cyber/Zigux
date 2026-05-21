const std = @import("std");

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "phase3 list/hlist hinge replay keeps the live list hinge visible over a detached alternate hinge" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var live_hinge = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var stale_hinge = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_hinge);
    first.prev = @intFromPtr(&head);
    live_hinge.next = @intFromPtr(&tail);
    live_hinge.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_hinge);

    stale_hinge.next = @intFromPtr(&tail);
    stale_hinge.prev = @intFromPtr(&first);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist hinge replay reports the first visible list break when only the tail adopts a stale hinge" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var live_hinge = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var stale_hinge = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&live_hinge);
    first.prev = @intFromPtr(&head);
    live_hinge.next = @intFromPtr(&tail);
    live_hinge.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&stale_hinge);

    stale_hinge.next = @intFromPtr(&tail);
    stale_hinge.prev = @intFromPtr(&first);

    const breakage = ListView.init(&head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_hinge)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&stale_hinge)), breakage.actual_prev);
    try std.testing.expect(!ListView.init(&head).hasConsistentBacklinks());
}

test "phase3 list/hlist hinge replay keeps the live hlist hinge visible over a detached alternate hinge" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var live_hinge = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var stale_hinge = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_hinge);
    first.pprev = @intFromPtr(&head.first);
    live_hinge.next = @intFromPtr(&tail);
    live_hinge.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_hinge.next);

    stale_hinge.next = @intFromPtr(&tail);
    stale_hinge.pprev = @intFromPtr(&first.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}

test "phase3 list/hlist hinge replay reports the first visible hlist break when only the tail adopts a stale hinge" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var live_hinge = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var stale_hinge = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&live_hinge);
    first.pprev = @intFromPtr(&head.first);
    live_hinge.next = @intFromPtr(&tail);
    live_hinge.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&stale_hinge.next);

    stale_hinge.next = @intFromPtr(&tail);
    stale_hinge.pprev = @intFromPtr(&first.next);

    const breakage = HListView.init(&head).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_hinge.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&stale_hinge.next)), breakage.actual_pprev);
    try std.testing.expect(!HListView.init(&head).hasConsistentPrevLinks());
}
