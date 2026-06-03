const std = @import("std");
const testing = std.testing;

const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list iterator remains exhausted after sentinel termination" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var first = list_view.ListHead{ .next = 0, .prev = 0 };
    var second = list_view.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    var it = list_view.ListView.init(&head).iterator();
    try testing.expectEqual(@as(?*const list_view.ListHead, &first), it.next());
    try testing.expectEqual(@as(?*const list_view.ListHead, &second), it.next());
    try testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
    try testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
    try testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

test "empty list iterator remains exhausted after first null result" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    head.next = @intFromPtr(&head);
    head.prev = @intFromPtr(&head);

    var it = list_view.ListView.init(&head).iterator();
    try testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
    try testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
    try testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

test "hlist iterator remains exhausted after null termination" {
    var head = hlist_view.HListHead{ .first = 0 };
    var first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var second = hlist_view.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    var it = hlist_view.HListView.init(&head).iterator();
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &first), it.next());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, &second), it.next());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "empty hlist iterator remains exhausted after first null result" {
    const head = hlist_view.HListHead{ .first = 0 };

    var it = hlist_view.HListView.init(&head).iterator();
    try testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}
