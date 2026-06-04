const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const testing = std.testing;

fn listView(head: *const list_view.ListHead) list_view.ListView {
    return list_view.ListView.init(head);
}

fn hlistView(head: *const hlist_view.HListHead) hlist_view.HListView {
    return hlist_view.HListView.init(head);
}

test "list suffix graft exposes stale tail backlink before repair" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var left = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var suffix = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&left);
    head.prev = @intFromPtr(&middle);
    left.next = @intFromPtr(&middle);
    left.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&head);
    middle.prev = @intFromPtr(&left);
    suffix.next = @intFromPtr(&head);
    suffix.prev = @intFromPtr(&middle);

    try testing.expectEqual(@as(usize, 2), listView(&head).len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &middle), listView(&head).last());
    try testing.expect(listView(&head).hasConsistentBacklinks());

    middle.next = @intFromPtr(&suffix);

    try testing.expectEqual(@as(usize, 3), listView(&head).len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &middle), listView(&head).last());

    const stale_tail = listView(&head).firstBrokenBacklink().?;
    try testing.expectEqual(@as(usize, 3), stale_tail.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&suffix)), stale_tail.expected_prev);
    try testing.expectEqual(@as(usize, @intFromPtr(&middle)), stale_tail.actual_prev);

    head.prev = @intFromPtr(&suffix);

    try testing.expectEqual(@as(usize, 3), listView(&head).len());
    try testing.expectEqual(@as(?*const list_view.ListHead, &suffix), listView(&head).last());
    try testing.expect(listView(&head).hasConsistentBacklinks());
}

test "hlist suffix graft exposes stale tail pprev before repair" {
    var head = hlist_view.HListHead{ .first = 0 };
    var left = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var suffix = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&left);
    left.next = @intFromPtr(&middle);
    left.pprev = @intFromPtr(&head.first);
    middle.next = 0;
    middle.pprev = @intFromPtr(&left.next);
    suffix.next = 0;
    suffix.pprev = @intFromPtr(&middle.next);

    try testing.expectEqual(@as(usize, 2), hlistView(&head).len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &middle), hlistView(&head).last());
    try testing.expect(hlistView(&head).tailNextIsNull());
    try testing.expect(hlistView(&head).hasConsistentPrevLinks());

    middle.next = @intFromPtr(&suffix);
    suffix.pprev = @intFromPtr(&left.next);

    try testing.expectEqual(@as(usize, 3), hlistView(&head).len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &suffix), hlistView(&head).last());
    try testing.expect(hlistView(&head).tailNextIsNull());

    const stale_pprev = hlistView(&head).firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 2), stale_pprev.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), stale_pprev.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&left.next)), stale_pprev.actual_pprev);
    try testing.expect(!hlistView(&head).hasConsistentPrevLinks());

    suffix.pprev = @intFromPtr(&middle.next);

    try testing.expectEqual(@as(usize, 3), hlistView(&head).len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &suffix), hlistView(&head).last());
    try testing.expect(hlistView(&head).tailNextIsNull());
    try testing.expect(hlistView(&head).hasConsistentPrevLinks());
}
