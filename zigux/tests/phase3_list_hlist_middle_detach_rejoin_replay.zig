const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn linkListPair(head: *list_view.ListHead, first: *list_view.ListHead, second: *list_view.ListHead) void {
    head.next = @intFromPtr(first);
    head.prev = @intFromPtr(second);
    first.next = @intFromPtr(second);
    first.prev = @intFromPtr(head);
    second.next = @intFromPtr(head);
    second.prev = @intFromPtr(first);
}

fn linkHListPair(head: *hlist_view.HListHead, first: *hlist_view.HListNode, second: *hlist_view.HListNode) void {
    head.first = @intFromPtr(first);
    first.next = @intFromPtr(second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);
}

test "list view reports skipped middle node until rejoined" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var middle = list_view.ListHead{ .next = 0, .prev = 0 };
    var last = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&last);
    first.next = @intFromPtr(&last);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&last);
    middle.prev = @intFromPtr(&first);
    last.next = @intFromPtr(&head);
    last.prev = @intFromPtr(&middle);

    var view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(view.contains(&first));
    try std.testing.expect(!view.contains(&middle));
    try std.testing.expect(view.contains(&last));
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &last), view.last());

    const skipped_middle = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), skipped_middle.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first)), skipped_middle.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle)), skipped_middle.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    first.next = @intFromPtr(&middle);
    view = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expect(view.contains(&middle));
    try std.testing.expect(view.hasConsistentBacklinks());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &first), it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &middle), it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &last), it.next());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

test "hlist view reports skipped middle node until rejoined" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var middle = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var last = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&last);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&last);
    middle.pprev = @intFromPtr(&first.next);
    last.next = 0;
    last.pprev = @intFromPtr(&middle.next);

    var view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(view.contains(&first));
    try std.testing.expect(!view.contains(&middle));
    try std.testing.expect(view.contains(&last));
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &last), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.tailNextIsNull());

    const skipped_middle = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), skipped_middle.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&first.next)), skipped_middle.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), skipped_middle.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    first.next = @intFromPtr(&middle);
    view = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expect(view.contains(&middle));
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &first), it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &middle), it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &last), it.next());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "shared two-node helpers remain well formed" {
    var list_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_second = list_view.ListHead{ .next = 0, .prev = 0 };
    linkListPair(&list_head, &list_first, &list_second);
    try std.testing.expect(list_view.ListView.init(&list_head).hasConsistentBacklinks());

    var hlist_head = hlist_view.HListHead{ .first = 0 };
    var hlist_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    linkHListPair(&hlist_head, &hlist_first, &hlist_second);
    try std.testing.expect(hlist_view.HListView.init(&hlist_head).hasConsistentPrevLinks());
}
