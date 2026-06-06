const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;

fn ptr(raw: anytype) usize {
    return @intFromPtr(raw);
}

fn expectListOrder(view: list_view.ListView, expected: []const *const ListHead) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const ListHead, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

fn expectListBreak(view: list_view.ListView, index: usize, expected_prev: usize, actual_prev: usize) !void {
    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(index, breakage.current_index);
    try std.testing.expectEqual(expected_prev, breakage.expected_prev);
    try std.testing.expectEqual(actual_prev, breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());
}

fn expectHListOrder(view: hlist_view.HListView, expected: []const *const HListNode) !void {
    try std.testing.expectEqual(expected.len, view.len());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const HListNode, node), it.next());
        try std.testing.expect(view.contains(node));
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

fn expectHListBreak(view: hlist_view.HListView, index: usize, expected_pprev: usize, actual_pprev: usize) !void {
    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(index, breakage.current_index);
    try std.testing.expectEqual(expected_pprev, breakage.expected_pprev);
    try std.testing.expectEqual(actual_pprev, breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());
}

fn seedCleanList(head: *ListHead, nodes: *[6]ListHead) void {
    head.next = ptr(&nodes[0]);
    head.prev = ptr(&nodes[5]);

    for (nodes, 0..) |*node, index| {
        node.next = if (index == nodes.len - 1) ptr(head) else ptr(&nodes[index + 1]);
        node.prev = if (index == 0) ptr(head) else ptr(&nodes[index - 1]);
    }
}

fn accordionShuffleListForwardOnly(head: *ListHead, nodes: *[6]ListHead) void {
    const order = [_]usize{ 0, 5, 1, 4, 2, 3 };

    head.next = ptr(&nodes[order[0]]);
    for (order, 0..) |node_index, route_index| {
        nodes[node_index].next = if (route_index == order.len - 1)
            ptr(head)
        else
            ptr(&nodes[order[route_index + 1]]);
    }
}

fn seedCleanHList(head: *HListHead, nodes: *[6]HListNode) void {
    head.first = ptr(&nodes[0]);

    for (nodes, 0..) |*node, index| {
        node.next = if (index == nodes.len - 1) 0 else ptr(&nodes[index + 1]);
        node.pprev = if (index == 0) ptr(&head.first) else ptr(&nodes[index - 1].next);
    }
}

fn accordionShuffleHListForwardOnly(head: *HListHead, nodes: *[6]HListNode) void {
    const order = [_]usize{ 0, 5, 1, 4, 2, 3 };

    head.first = ptr(&nodes[order[0]]);
    for (order, 0..) |node_index, route_index| {
        nodes[node_index].next = if (route_index == order.len - 1)
            0
        else
            ptr(&nodes[order[route_index + 1]]);
    }
}

test "list view accordion-shuffle route exposes forward order before backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var nodes = [_]ListHead{.{ .next = 0, .prev = 0 }} ** 6;
    seedCleanList(&head, &nodes);
    accordionShuffleListForwardOnly(&head, &nodes);

    const view = list_view.ListView.init(&head);
    const order = [_]*const ListHead{ &nodes[0], &nodes[5], &nodes[1], &nodes[4], &nodes[2], &nodes[3] };
    try expectListOrder(view, &order);
    try std.testing.expectEqual(@as(?*const ListHead, &nodes[0]), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, &nodes[5]), view.last());
    try std.testing.expect(!view.isSingular());

    try expectListBreak(view, 1, ptr(&nodes[0]), ptr(&nodes[4]));
    nodes[5].prev = ptr(&nodes[0]);
    try expectListBreak(view, 2, ptr(&nodes[5]), ptr(&nodes[0]));
    nodes[1].prev = ptr(&nodes[5]);
    try expectListBreak(view, 3, ptr(&nodes[1]), ptr(&nodes[3]));
    nodes[4].prev = ptr(&nodes[1]);
    try expectListBreak(view, 4, ptr(&nodes[4]), ptr(&nodes[1]));
    nodes[2].prev = ptr(&nodes[4]);
    try expectListBreak(view, 6, ptr(&nodes[3]), ptr(&nodes[5]));
    head.prev = ptr(&nodes[3]);

    try std.testing.expect(view.hasConsistentBacklinks());
    try std.testing.expect(view.firstBrokenBacklink() == null);
    try std.testing.expectEqual(@as(?*const ListHead, &nodes[3]), view.last());
}

test "hlist view accordion-shuffle route exposes forward order before prev-link repair" {
    var head = HListHead{ .first = 0 };
    var nodes = [_]HListNode{.{ .next = 0, .pprev = 0 }} ** 6;
    seedCleanHList(&head, &nodes);
    accordionShuffleHListForwardOnly(&head, &nodes);

    const view = hlist_view.HListView.init(&head);
    const order = [_]*const HListNode{ &nodes[0], &nodes[5], &nodes[1], &nodes[4], &nodes[2], &nodes[3] };
    try expectHListOrder(view, &order);
    try std.testing.expectEqual(@as(?*const HListNode, &nodes[0]), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, &nodes[3]), view.last());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(view.firstPprevMatchesHead());

    try expectHListBreak(view, 1, ptr(&nodes[0].next), ptr(&nodes[4].next));
    nodes[5].pprev = ptr(&nodes[0].next);
    try expectHListBreak(view, 2, ptr(&nodes[5].next), ptr(&nodes[0].next));
    nodes[1].pprev = ptr(&nodes[5].next);
    try expectHListBreak(view, 3, ptr(&nodes[1].next), ptr(&nodes[3].next));
    nodes[4].pprev = ptr(&nodes[1].next);
    try expectHListBreak(view, 4, ptr(&nodes[4].next), ptr(&nodes[1].next));
    nodes[2].pprev = ptr(&nodes[4].next);

    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.firstBrokenPrevLink() == null);
    try std.testing.expect(view.tailNextIsNull());
}
