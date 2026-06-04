const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

fn expectListOrder(view: ListView, expected: []const *const ListHead) !void {
    try std.testing.expectEqual(expected.len, view.len());
    try std.testing.expectEqual(@as(?*const ListHead, expected[0]), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, expected[expected.len - 1]), view.last());
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(expected.len == 1, view.isSingular());
    try std.testing.expect(view.hasConsistentBacklinks());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const ListHead, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

fn expectHListOrder(view: HListView, expected: []const *const HListNode) !void {
    try std.testing.expectEqual(expected.len, view.len());
    try std.testing.expectEqual(@as(?*const HListNode, expected[0]), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, expected[expected.len - 1]), view.last());
    try std.testing.expect(!view.isEmpty());
    try std.testing.expectEqual(expected.len == 1, view.isSingular());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const HListNode, node), it.next());
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "list view follows head tail rebase after front node rotation" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var front = ListHead{ .next = 0, .prev = 0 };
    var middle = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&front);
    head.prev = @intFromPtr(&tail);
    front.next = @intFromPtr(&middle);
    front.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&tail);
    middle.prev = @intFromPtr(&front);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&middle);

    try expectListOrder(ListView.init(&head), &.{ &front, &middle, &tail });

    head.next = @intFromPtr(&middle);
    head.prev = @intFromPtr(&front);
    middle.prev = @intFromPtr(&head);
    tail.next = @intFromPtr(&front);
    front.prev = @intFromPtr(&tail);
    front.next = @intFromPtr(&head);

    try expectListOrder(ListView.init(&head), &.{ &middle, &tail, &front });

    head.next = @intFromPtr(&front);
    head.prev = @intFromPtr(&tail);
    front.prev = @intFromPtr(&head);
    front.next = @intFromPtr(&middle);
    middle.prev = @intFromPtr(&front);
    tail.next = @intFromPtr(&head);

    try expectListOrder(ListView.init(&head), &.{ &front, &middle, &tail });
}

test "hlist view follows head tail rebase after front node rotation" {
    var head = HListHead{ .first = 0 };
    var front = HListNode{ .next = 0, .pprev = 0 };
    var middle = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&front);
    front.next = @intFromPtr(&middle);
    front.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&tail);
    middle.pprev = @intFromPtr(&front.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&middle.next);

    try expectHListOrder(HListView.init(&head), &.{ &front, &middle, &tail });

    head.first = @intFromPtr(&middle);
    middle.pprev = @intFromPtr(&head.first);
    tail.next = @intFromPtr(&front);
    front.pprev = @intFromPtr(&tail.next);
    front.next = 0;

    try expectHListOrder(HListView.init(&head), &.{ &middle, &tail, &front });

    head.first = @intFromPtr(&front);
    front.pprev = @intFromPtr(&head.first);
    front.next = @intFromPtr(&middle);
    middle.pprev = @intFromPtr(&front.next);
    tail.next = 0;

    try expectHListOrder(HListView.init(&head), &.{ &front, &middle, &tail });
}
