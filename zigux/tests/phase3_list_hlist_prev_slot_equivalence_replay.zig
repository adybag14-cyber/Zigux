const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list replay accepts hlist-style pprev slots as previous-node bases" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first.next);

    try testing.expectEqual(@as(usize, @intFromPtr(&first)), @intFromPtr(&first.next));

    const view = list_view.ListView.init(&head);
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, &second), view.last());
    try testing.expect(view.hasConsistentBacklinks());
    try testing.expect(view.firstBrokenBacklink() == null);
}

test "hlist replay accepts list-style previous-node bases as pprev slots" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first);

    try testing.expectEqual(@as(usize, @intFromPtr(&first.next)), @intFromPtr(&first));

    const view = hlist_view.HListView.init(&head);
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.tailNextIsNull());
    try testing.expect(view.hasConsistentPrevLinks());
    try testing.expect(view.firstBrokenPrevLink() == null);
}

test "prev-slot equivalence still rejects non-leading slot aliases" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.pprev);

    const breakage = hlist_view.HListView.init(&head).firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&first.pprev)), breakage.actual_pprev);
}
