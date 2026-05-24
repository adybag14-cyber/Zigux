const std = @import("std");

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "phase3 list/hlist head-window replay keeps the live head window visible over a detached opening window" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_entry = ListHead{ .next = 0, .prev = 0 };
    var live_window = ListHead{ .next = 0, .prev = 0 };
    var bridge = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow_entry = ListHead{ .next = 0, .prev = 0 };
    var shadow_window = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&live_entry);
    head.prev = @intFromPtr(&tail);
    live_entry.next = @intFromPtr(&live_window);
    live_entry.prev = @intFromPtr(&head);
    live_window.next = @intFromPtr(&bridge);
    live_window.prev = @intFromPtr(&live_entry);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&live_window);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge);

    shadow_entry.next = @intFromPtr(&shadow_window);
    shadow_entry.prev = @intFromPtr(&head);
    shadow_window.next = @intFromPtr(&bridge);
    shadow_window.prev = @intFromPtr(&shadow_entry);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &live_entry), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist head-window replay reports the stale middle backlink after a detached opening window is adopted" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var live_entry = ListHead{ .next = 0, .prev = 0 };
    var live_window = ListHead{ .next = 0, .prev = 0 };
    var bridge = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow_entry = ListHead{ .next = 0, .prev = 0 };
    var shadow_window = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&shadow_entry);
    head.prev = @intFromPtr(&tail);
    live_entry.next = @intFromPtr(&live_window);
    live_entry.prev = @intFromPtr(&head);
    live_window.next = @intFromPtr(&bridge);
    live_window.prev = @intFromPtr(&live_entry);
    bridge.next = @intFromPtr(&tail);
    bridge.prev = @intFromPtr(&live_window);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&bridge);

    shadow_entry.next = @intFromPtr(&shadow_window);
    shadow_entry.prev = @intFromPtr(&head);
    shadow_window.next = @intFromPtr(&bridge);
    shadow_window.prev = @intFromPtr(&shadow_entry);

    const breakage = ListView.init(&head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_window)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_window)), breakage.actual_prev);
    try std.testing.expect(!ListView.init(&head).hasConsistentBacklinks());
}

test "phase3 list/hlist head-window replay keeps the live hlist head window visible over a detached opening window" {
    var head = HListHead{ .first = 0 };
    var live_entry = HListNode{ .next = 0, .pprev = 0 };
    var live_window = HListNode{ .next = 0, .pprev = 0 };
    var bridge = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow_entry = HListNode{ .next = 0, .pprev = 0 };
    var shadow_window = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&live_entry);
    live_entry.next = @intFromPtr(&live_window);
    live_entry.pprev = @intFromPtr(&head.first);
    live_window.next = @intFromPtr(&bridge);
    live_window.pprev = @intFromPtr(&live_entry.next);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&live_window.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge.next);

    shadow_entry.next = @intFromPtr(&shadow_window);
    shadow_entry.pprev = @intFromPtr(&head.first);
    shadow_window.next = @intFromPtr(&bridge);
    shadow_window.pprev = @intFromPtr(&shadow_entry.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 4), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &live_entry), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}

test "phase3 list/hlist head-window replay reports the stale middle prev-link after a detached opening window is adopted" {
    var head = HListHead{ .first = 0 };
    var live_entry = HListNode{ .next = 0, .pprev = 0 };
    var live_window = HListNode{ .next = 0, .pprev = 0 };
    var bridge = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow_entry = HListNode{ .next = 0, .pprev = 0 };
    var shadow_window = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&shadow_entry);
    live_entry.next = @intFromPtr(&live_window);
    live_entry.pprev = @intFromPtr(&head.first);
    live_window.next = @intFromPtr(&bridge);
    live_window.pprev = @intFromPtr(&live_entry.next);
    bridge.next = @intFromPtr(&tail);
    bridge.pprev = @intFromPtr(&live_window.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&bridge.next);

    shadow_entry.next = @intFromPtr(&shadow_window);
    shadow_entry.pprev = @intFromPtr(&head.first);
    shadow_window.next = @intFromPtr(&bridge);
    shadow_window.pprev = @intFromPtr(&shadow_entry.next);

    const breakage = HListView.init(&head).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_window.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&live_window.next)), breakage.actual_pprev);
    try std.testing.expect(!HListView.init(&head).hasConsistentPrevLinks());
}
