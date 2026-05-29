const std = @import("std");

const hlist_view = @import("hlist_view");
const list_view = @import("list_view");

const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;
const ListHead = list_view.ListHead;
const ListView = list_view.ListView;

test "bridge pair tail claim waits for list backlink adoption" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var entry = ListHead{ .next = 0, .prev = 0 };
    var bridge = ListHead{ .next = 0, .prev = 0 };
    var claimed_tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&claimed_tail);
    entry.next = @intFromPtr(&bridge);
    entry.prev = @intFromPtr(&head);
    bridge.next = @intFromPtr(&claimed_tail);
    bridge.prev = @intFromPtr(&entry);
    claimed_tail.next = @intFromPtr(&head);
    claimed_tail.prev = @intFromPtr(&entry);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &claimed_tail), view.last());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entry)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    claimed_tail.prev = @intFromPtr(&bridge);
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "bridge pair tail claim waits for hlist prev-link adoption" {
    var head = HListHead{ .first = 0 };
    var entry = HListNode{ .next = 0, .pprev = 0 };
    var bridge = HListNode{ .next = 0, .pprev = 0 };
    var claimed_tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&bridge);
    entry.pprev = @intFromPtr(&head.first);
    bridge.next = @intFromPtr(&claimed_tail);
    bridge.pprev = @intFromPtr(&entry.next);
    claimed_tail.next = 0;
    claimed_tail.pprev = @intFromPtr(&entry.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entry.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    claimed_tail.pprev = @intFromPtr(&bridge.next);
    try std.testing.expect(view.hasConsistentPrevLinks());
}
