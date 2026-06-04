const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn expectListOrder(
    view: list_view.ListView,
    expected_first: *const list_view.ListHead,
    expected_last: *const list_view.ListHead,
    expected_len: usize,
) !void {
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(expected_len, view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, expected_first), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, expected_last), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
}

fn expectHListOrder(
    view: hlist_view.HListView,
    expected_first: *const hlist_view.HListNode,
    expected_last: *const hlist_view.HListNode,
    expected_len: usize,
) !void {
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(expected_len, view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, expected_first), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, expected_last), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}

test "list singleton can grow and shrink without losing first-last shape" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&first);
    first.next = @intFromPtr(&head);
    first.prev = @intFromPtr(&head);

    try expectListOrder(list_view.ListView.init(&head), &first, &first, 1);

    first.next = @intFromPtr(&second);
    second.prev = @intFromPtr(&first);
    second.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&second);

    try expectListOrder(list_view.ListView.init(&head), &first, &second, 2);

    first.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&first);
    second.next = 0;
    second.prev = 0;

    try expectListOrder(list_view.ListView.init(&head), &first, &first, 1);
}

test "hlist singleton can adopt a successor and rebase back to one live node" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = 0;
    first.pprev = @intFromPtr(&head.first);

    try expectHListOrder(hlist_view.HListView.init(&head), &first, &first, 1);

    first.next = @intFromPtr(&second);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    try expectHListOrder(hlist_view.HListView.init(&head), &first, &second, 2);

    head.first = @intFromPtr(&second);
    second.pprev = @intFromPtr(&head.first);
    first.next = 0;
    first.pprev = 0;

    try expectHListOrder(hlist_view.HListView.init(&head), &second, &second, 1);
}
