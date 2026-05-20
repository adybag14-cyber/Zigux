const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

fn collectListNodes(view: ListView, buffer: []?*const ListHead) []?*const ListHead {
    var it = view.iterator();
    var len: usize = 0;
    while (it.next()) |node| : (len += 1) {
        buffer[len] = node;
    }
    return buffer[0..len];
}

fn collectHListNodes(view: HListView, buffer: []?*const HListNode) []?*const HListNode {
    var it = view.iterator();
    var len: usize = 0;
    while (it.next()) |node| : (len += 1) {
        buffer[len] = node;
    }
    return buffer[0..len];
}

test "detached list shortcut shadow stays unreachable while live interior remains authoritative" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var middle = ListHead{ .next = 0, .prev = 0 };
    var tail = ListHead{ .next = 0, .prev = 0 };
    var shadow = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&tail);
    first.next = @intFromPtr(&middle);
    first.prev = @intFromPtr(&head);
    middle.next = @intFromPtr(&tail);
    middle.prev = @intFromPtr(&first);
    tail.next = @intFromPtr(&head);
    tail.prev = @intFromPtr(&middle);

    // This detached node looks like a middle-bypass shortcut, but nothing on the
    // live chain points at it.
    shadow.next = @intFromPtr(&tail);
    shadow.prev = @intFromPtr(&first);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &tail), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle)), tail.prev);

    var seen: [4]?*const ListHead = [_]?*const ListHead{null} ** 4;
    const nodes = collectListNodes(view, &seen);
    try std.testing.expectEqual(@as(usize, 3), nodes.len);
    try std.testing.expectEqual(@as(?*const ListHead, &first), nodes[0]);
    try std.testing.expectEqual(@as(?*const ListHead, &middle), nodes[1]);
    try std.testing.expectEqual(@as(?*const ListHead, &tail), nodes[2]);
    try std.testing.expect(nodes[0].? != &shadow);
    try std.testing.expect(nodes[1].? != &shadow);
    try std.testing.expect(nodes[2].? != &shadow);
}

test "detached list shortcut shadow cannot replace the live first witness" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };
    var shadow = ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    shadow.next = @intFromPtr(&second);
    shadow.prev = @intFromPtr(&head);

    const view = ListView.init(&head);
    try std.testing.expectEqual(@as(?*const ListHead, &first), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &second), view.last());
    try std.testing.expectEqual(@as(usize, 2), view.len());
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "detached hlist shortcut shadow stays unreachable while live predecessor links remain authoritative" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var middle = HListNode{ .next = 0, .pprev = 0 };
    var tail = HListNode{ .next = 0, .pprev = 0 };
    var shadow = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&middle);
    first.pprev = @intFromPtr(&head.first);
    middle.next = @intFromPtr(&tail);
    middle.pprev = @intFromPtr(&first.next);
    tail.next = 0;
    tail.pprev = @intFromPtr(&middle.next);

    // This detached node claims it should sit between `first` and `tail`, but the
    // live list still reaches `middle`.
    shadow.next = @intFromPtr(&tail);
    shadow.pprev = @intFromPtr(&first.next);

    const view = HListView.init(&head);
    try std.testing.expectEqual(@as(usize, 3), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, &first), view.first());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle.next)), tail.pprev);

    var seen: [4]?*const HListNode = [_]?*const HListNode{null} ** 4;
    const nodes = collectHListNodes(view, &seen);
    try std.testing.expectEqual(@as(usize, 3), nodes.len);
    try std.testing.expectEqual(@as(?*const HListNode, &first), nodes[0]);
    try std.testing.expectEqual(@as(?*const HListNode, &middle), nodes[1]);
    try std.testing.expectEqual(@as(?*const HListNode, &tail), nodes[2]);
    try std.testing.expect(nodes[0].? != &shadow);
    try std.testing.expect(nodes[1].? != &shadow);
    try std.testing.expect(nodes[2].? != &shadow);
}
