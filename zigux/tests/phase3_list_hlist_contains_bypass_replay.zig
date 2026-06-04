const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

test "list contains tracks visible route after middle bypass" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var skipped = ListHead{ .next = 0, .prev = 0 };
    var last = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&last);
    first.next = @intFromPtr(&skipped);
    first.prev = @intFromPtr(&head);
    skipped.next = @intFromPtr(&last);
    skipped.prev = @intFromPtr(&first);
    last.next = @intFromPtr(&head);
    last.prev = @intFromPtr(&skipped);

    var view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expect(view.contains(&skipped));
    try std.testing.expect(view.hasConsistentBacklinks());

    first.next = @intFromPtr(&last);

    view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(view.contains(&first));
    try std.testing.expect(!view.contains(&skipped));
    try std.testing.expect(view.contains(&last));

    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&skipped)), breakage.actual_prev);

    last.prev = @intFromPtr(&first);

    view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(!view.contains(&skipped));
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "hlist contains tracks visible route after middle bypass" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var skipped = HListNode{ .next = 0, .pprev = 0 };
    var last = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&skipped);
    first.pprev = @intFromPtr(&head.first);
    skipped.next = @intFromPtr(&last);
    skipped.pprev = @intFromPtr(&first.next);
    last.next = 0;
    last.pprev = @intFromPtr(&skipped.next);

    var view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expect(view.contains(&skipped));
    try std.testing.expect(view.hasConsistentPrevLinks());

    first.next = @intFromPtr(&last);

    view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(view.contains(&first));
    try std.testing.expect(!view.contains(&skipped));
    try std.testing.expect(view.contains(&last));

    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&skipped.next)), breakage.actual_pprev);

    last.pprev = @intFromPtr(&first.next);

    view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(!view.contains(&skipped));
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
