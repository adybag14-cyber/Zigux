const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list view reports tail-side self-loop endpoint before repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&tail);
    first.prev = @intFromPtr(&head);
    tail.next = @intFromPtr(&tail);
    tail.prev = @intFromPtr(&first);

    const stale = ListView.init(&head);
    try std.testing.expectEqual(@as(?*const ListHead, &first), stale.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), stale.last());

    var it = stale.iterator();
    try std.testing.expectEqual(@as(?*const ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), it.next());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), it.next());

    const breakage = stale.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.actual_prev);
    try std.testing.expect(!stale.hasConsistentBacklinks());

    tail.next = @intFromPtr(&head);

    const repaired = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), repaired.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), repaired.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), repaired.last());
    try std.testing.expect(repaired.hasConsistentBacklinks());
}

test "hlist view reports tail self-loop before null-tail repair" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&tail);
    first.pprev = @intFromPtr(&head.first);
    tail.next = @intFromPtr(&tail);
    tail.pprev = @intFromPtr(&first.next);

    const stale = HListView.init(&head);
    try std.testing.expectEqual(@as(?*const HListNode, &first), stale.first());

    var it = stale.iterator();
    try std.testing.expectEqual(@as(?*const HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), it.next());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), it.next());

    const breakage = stale.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 2), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.actual_pprev);
    try std.testing.expect(!stale.hasConsistentPrevLinks());

    tail.next = 0;

    const repaired = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), repaired.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), repaired.first());
    try std.testing.expectEqual(@as(?*const HListNode, &tail), repaired.last());
    try std.testing.expect(repaired.hasConsistentPrevLinks());
    try std.testing.expect(repaired.tailNextIsNull());
}
