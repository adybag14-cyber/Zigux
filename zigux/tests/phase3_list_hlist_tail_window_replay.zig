const std = @import("std");

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "phase3 list/hlist tail-window replay keeps the live tail window visible over a detached late window" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var entry = ListHead{ .next = 0, .prev = 0 };
    var bridge = ListHead{ .next = 0, .prev = 0 };
    var live_window = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow_window = ListHead{ .next = 0, .prev = 0 };
    var shadow_tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&bridge);
    entry.prev = @intFromPtr(&head);
    bridge.next = @intFromPtr(&live_window);
    bridge.prev = @intFromPtr(&entry);
    live_window.next = @intFromPtr(&tail);
    live_window.prev = @intFromPtr(&bridge);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_window);

    shadow_window.next = @intFromPtr(&shadow_tail);
    shadow_window.prev = @intFromPtr(&bridge);
    shadow_tail.next = @intFromPtr(&tail);
    shadow_tail.prev = @intFromPtr(&shadow_window);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &entry), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist tail-window replay reports the stale tail backlink after a detached late window is adopted" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var entry = ListHead{ .next = 0, .prev = 0 };
    var bridge = ListHead{ .next = 0, .prev = 0 };
    var live_window = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow_window = ListHead{ .next = 0, .prev = 0 };
    var shadow_tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&bridge);
    entry.prev = @intFromPtr(&head);
    bridge.next = @intFromPtr(&shadow_window);
    bridge.prev = @intFromPtr(&entry);
    live_window.next = @intFromPtr(&tail);
    live_window.prev = @intFromPtr(&bridge);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_window);

    shadow_window.next = @intFromPtr(&shadow_tail);
    shadow_window.prev = @intFromPtr(&bridge);
    shadow_tail.next = @intFromPtr(&tail);
    shadow_tail.prev = @intFromPtr(&shadow_window);

    const breakage = ListView.init(&head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_tail)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_window)), breakage.actual_prev);
    try std.testing.expect(!ListView.init(&head).hasConsistentBacklinks());
}

test "phase3 list/hlist tail-window replay keeps the live hlist tail window visible over a detached late window" {
    var head = HListHead{ .first = 0 };
    var entry = HListNode{ .next = 0, .pprev = 0 };
    var bridge = HListNode{ .next = 0, .pprev = 0 };
    var live_window = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow_window = HListNode{ .next = 0, .pprev = 0 };
    var shadow_tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&bridge);
    entry.pprev = @intFromPtr(&head.first);
    bridge.next = @intFromPtr(&live_window);
    bridge.pprev = @intFromPtr(&entry.next);
    live_window.next = @intFromPtr(&tail);
    live_window.pprev = @intFromPtr(&bridge.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_window.next);

    shadow_window.next = @intFromPtr(&shadow_tail);
    shadow_window.pprev = @intFromPtr(&bridge.next);
    shadow_tail.next = @intFromPtr(&tail);
    shadow_tail.pprev = @intFromPtr(&shadow_window.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &entry), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}

test "phase3 list/hlist tail-window replay reports the stale hlist tail prev-link after a detached late window is adopted" {
    var head = HListHead{ .first = 0 };
    var entry = HListNode{ .next = 0, .pprev = 0 };
    var bridge = HListNode{ .next = 0, .pprev = 0 };
    var live_window = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow_window = HListNode{ .next = 0, .pprev = 0 };
    var shadow_tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&bridge);
    entry.pprev = @intFromPtr(&head.first);
    bridge.next = @intFromPtr(&shadow_window);
    bridge.pprev = @intFromPtr(&entry.next);
    live_window.next = @intFromPtr(&tail);
    live_window.pprev = @intFromPtr(&bridge.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_window.next);

    shadow_window.next = @intFromPtr(&shadow_tail);
    shadow_window.pprev = @intFromPtr(&bridge.next);
    shadow_tail.next = @intFromPtr(&tail);
    shadow_tail.pprev = @intFromPtr(&shadow_window.next);

    const breakage = HListView.init(&head).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 4), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_tail.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_window.next)), breakage.actual_pprev);
    try std.testing.expect(!HListView.init(&head).hasConsistentPrevLinks());
}
