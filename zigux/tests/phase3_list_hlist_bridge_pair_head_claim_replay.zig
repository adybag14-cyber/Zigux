const std = @import("std");

const hlist_view = @import("hlist_view");
const list_view = @import("list_view");

const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;
const ListHead = list_view.ListHead;
const ListView = list_view.ListView;

test "bridge pair head claim waits for list first backlink adoption" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var claimed_head = ListHead{ .next = 0, .prev = 0 };
    var bridge = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&claimed_head);
    head.prev = @intFromPtr(&tail);
    claimed_head.next = @intFromPtr(&bridge);
    claimed_head.prev = @intFromPtr(&tail);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&claimed_head);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &claimed_head), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    claimed_head.prev = @intFromPtr(&head);
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "bridge pair head claim waits for hlist first prev-link adoption" {
    var head = HListHead{ .first = 0 };
    var claimed_head = HListNode{ .next = 0, .pprev = 0 };
    var bridge = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&claimed_head);
    claimed_head.next = @intFromPtr(&bridge);
    claimed_head.pprev = @intFromPtr(&tail.next);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&claimed_head.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &claimed_head), view.first());
    try std.testing.expect(!view.firstPprevMatchesHead());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    claimed_head.pprev = @intFromPtr(&head.first);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
