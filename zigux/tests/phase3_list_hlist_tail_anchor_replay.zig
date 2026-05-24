const std = @import("std");

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "phase3 list/hlist tail-anchor replay keeps the live list tail anchored through the visible chain" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var entry = ListHead{ .next = 0, .prev = 0 };
    var bridge = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&bridge);
    entry.prev = @intFromPtr(&head);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&entry);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge);

    shadow.next = @intFromPtr(&tail);
    shadow.prev = @intFromPtr(&bridge);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &entry), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist tail-anchor replay reports the visible list tail break when the anchor borrows a detached tail window" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var entry = ListHead{ .next = 0, .prev = 0 };
    var bridge = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&bridge);
    entry.prev = @intFromPtr(&head);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&entry);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&shadow);

    shadow.next = @intFromPtr(&tail);
    shadow.prev = @intFromPtr(&bridge);

    const breakage = ListView.init(&head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow)), breakage.actual_prev);
    try std.testing.expect(!ListView.init(&head).hasConsistentBacklinks());
}

test "phase3 list/hlist tail-anchor replay keeps the live hlist tail anchored through the visible chain" {
    var head = HListHead{ .first = 0 };
    var entry = HListNode{ .next = 0, .pprev = 0 };
    var bridge = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&bridge);
    entry.pprev = @intFromPtr(&head.first);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&entry.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge.next);

    shadow.next = @intFromPtr(&tail);
    shadow.pprev = @intFromPtr(&bridge.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &entry), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}

test "phase3 list/hlist tail-anchor replay reports the visible hlist tail break when the anchor borrows a detached tail window" {
    var head = HListHead{ .first = 0 };
    var entry = HListNode{ .next = 0, .pprev = 0 };
    var bridge = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&bridge);
    entry.pprev = @intFromPtr(&head.first);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&entry.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&shadow.next);

    shadow.next = @intFromPtr(&tail);
    shadow.pprev = @intFromPtr(&bridge.next);

    const breakage = HListView.init(&head).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&bridge.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow.next)), breakage.actual_pprev);
    try std.testing.expect(!HListView.init(&head).hasConsistentPrevLinks());
}
