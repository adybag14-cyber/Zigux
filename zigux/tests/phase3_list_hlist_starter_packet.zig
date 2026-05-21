const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list starter packet keeps a sentinel-only list empty and reviewable" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    const view = list_view.ListView.init(&head);
    try testing.expect(view.isEmpty());
    try testing.expectEqual(@as(usize, 0), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, null), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, null), view.last());
    try testing.expect(view.hasConsistentBacklinks());
    try testing.expect(view.firstBrokenBacklink() == null);
}

test "list starter packet keeps circular ordering and broken backlinks explicit" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    const ordered = list_view.ListView.init(&head);
    try testing.expect(!ordered.isEmpty());
    try testing.expectEqual(@as(usize, 2), ordered.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), ordered.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &second), ordered.last());
    try testing.expect(ordered.hasConsistentBacklinks());

    second.prev = @intFromPtr(&head);
    const breakage = list_view.ListView.init(&head).firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.actual_prev);
}

test "hlist starter packet keeps empty heads and bounded chains explicit" {
    const empty_head = hlist_view.HListHead{ .first = 0 };
    const empty = hlist_view.HListView.init(&empty_head);
    try testing.expect(empty.isEmpty());
    try testing.expectEqual(@as(usize, 0), empty.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, null), empty.first());
    try testing.expect(empty.firstPprevMatchesHead());
    try testing.expect(empty.hasConsistentPrevLinks());
    try testing.expect(empty.tailNextIsNull());

    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expect(!view.isEmpty());
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.tailNextIsNull());
}

test "hlist starter packet reports the first broken prev-link witness" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&head.first);

    const breakage = hlist_view.HListView.init(&head).firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try testing.expect(!hlist_view.HListView.init(&head).hasConsistentPrevLinks());
}
