const std = @import("std");

const hlist_view = @import("hlist_view");
const list_view = @import("list_view");

const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;
const ListHead = list_view.ListHead;
const ListView = list_view.ListView;

test "bridge pair middle claim waits for list tail-side backlink adoption" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var lead = ListHead{ .next = 0, .prev = 0 };
    var bridge_a = ListHead{ .next = 0, .prev = 0 };
    var bridge_b = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&lead);
    head.prev = @intFromPtr(&tail);
    lead.next = @intFromPtr(&tail);
    lead.prev = @intFromPtr(&head);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&lead);

    bridge_a.next = @intFromPtr(&bridge_b);
    bridge_a.prev = @intFromPtr(&lead);
    bridge_b.next = @intFromPtr(&tail);
    bridge_b.prev = @intFromPtr(&bridge_a);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(view.hasConsistentBacklinks());

    lead.next = @intFromPtr(&bridge_a);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_b)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&lead)), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    tail.prev = @intFromPtr(&bridge_b);
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "bridge pair middle claim waits for hlist tail-side prev-link adoption" {
    var head = HListHead{ .first = 0 };
    var lead = HListNode{ .next = 0, .pprev = 0 };
    var bridge_a = HListNode{ .next = 0, .pprev = 0 };
    var bridge_b = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&lead);
    lead.next = @intFromPtr(&tail);
    lead.pprev = @intFromPtr(&head.first);
    tail.next = 0;
    tail.pprev = @intFromPtr(&lead.next);

    bridge_a.next = @intFromPtr(&bridge_b);
    bridge_a.pprev = @intFromPtr(&lead.next);
    bridge_b.next = @intFromPtr(&tail);
    bridge_b.pprev = @intFromPtr(&bridge_a.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    lead.next = @intFromPtr(&bridge_a);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expect(view.tailNextIsNull());

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge_b.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&lead.next)), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    tail.pprev = @intFromPtr(&bridge_b.next);
    try std.testing.expect(view.hasConsistentPrevLinks());
}
