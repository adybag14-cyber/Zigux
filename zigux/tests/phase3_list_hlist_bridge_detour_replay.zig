const std = @import("std");

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "phase3 list/hlist bridge detour replay keeps the live list bridge visible over a detached alternate bridge" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var entry = ListHead{ .next = 0, .prev = 0 };
    var live_bridge = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow_entry = ListHead{ .next = 0, .prev = 0 };
    var shadow_bridge = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&live_bridge);
    entry.prev = @intFromPtr(&head);
    live_bridge.next = @intFromPtr(&tail);
    live_bridge.prev = @intFromPtr(&entry);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_bridge);

    shadow_entry.next = @intFromPtr(&shadow_bridge);
    shadow_entry.prev = @intFromPtr(&shadow_entry);
    shadow_bridge.next = @intFromPtr(&tail);
    shadow_bridge.prev = @intFromPtr(&shadow_entry);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &entry), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
}

test "phase3 list/hlist bridge detour replay reports the adopted list bridge detour before the tail is reached" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var entry = ListHead{ .next = 0, .prev = 0 };
    var live_bridge = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow_entry = ListHead{ .next = 0, .prev = 0 };
    var shadow_bridge = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&entry);
    head.prev = @intFromPtr(&tail);
    entry.next = @intFromPtr(&shadow_bridge);
    entry.prev = @intFromPtr(&head);
    live_bridge.next = @intFromPtr(&tail);
    live_bridge.prev = @intFromPtr(&entry);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&live_bridge);

    shadow_entry.next = @intFromPtr(&shadow_bridge);
    shadow_entry.prev = @intFromPtr(&shadow_entry);
    shadow_bridge.next = @intFromPtr(&tail);
    shadow_bridge.prev = @intFromPtr(&shadow_entry);

    const breakage = ListView.init(&head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entry)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_entry)), breakage.actual_prev);
    try std.testing.expect(!ListView.init(&head).hasConsistentBacklinks());
}

test "phase3 list/hlist bridge detour replay keeps the live hlist bridge visible over a detached alternate bridge" {
    var head = HListHead{ .first = 0 };
    var entry = HListNode{ .next = 0, .pprev = 0 };
    var live_bridge = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow_entry = HListNode{ .next = 0, .pprev = 0 };
    var shadow_bridge = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&live_bridge);
    entry.pprev = @intFromPtr(&head.first);
    live_bridge.next = @intFromPtr(&tail);
    live_bridge.pprev = @intFromPtr(&entry.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_bridge.next);

    shadow_entry.next = @intFromPtr(&shadow_bridge);
    shadow_entry.pprev = @intFromPtr(&shadow_entry.next);
    shadow_bridge.next = @intFromPtr(&tail);
    shadow_bridge.pprev = @intFromPtr(&shadow_entry.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &entry), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
}

test "phase3 list/hlist bridge detour replay reports the adopted hlist bridge detour before the tail is reached" {
    var head = HListHead{ .first = 0 };
    var entry = HListNode{ .next = 0, .pprev = 0 };
    var live_bridge = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow_entry = HListNode{ .next = 0, .pprev = 0 };
    var shadow_bridge = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&entry);
    entry.next = @intFromPtr(&shadow_bridge);
    entry.pprev = @intFromPtr(&head.first);
    live_bridge.next = @intFromPtr(&tail);
    live_bridge.pprev = @intFromPtr(&entry.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&live_bridge.next);

    shadow_entry.next = @intFromPtr(&shadow_bridge);
    shadow_entry.pprev = @intFromPtr(&shadow_entry.next);
    shadow_bridge.next = @intFromPtr(&tail);
    shadow_bridge.pprev = @intFromPtr(&shadow_entry.next);

    const breakage = HListView.init(&head).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&entry.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&shadow_entry.next)), breakage.actual_pprev);
    try std.testing.expect(!HListView.init(&head).hasConsistentPrevLinks());
}
