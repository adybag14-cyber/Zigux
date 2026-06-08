const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;

const node_count = 52;
const detached_index = node_count;
const staged_break_index = 32;
const route = [_]usize{
    51, 0,  27, 25, 50, 1,  28, 24, 49, 2,  29, 23, 48,
    3,  30, 22, 47, 4,  31, 21, 46, 5,  32, 20, 45, 6,
    33, 19, 44, 7,  34, 18, 43, 8,  35, 17, 42, 9,  36,
    16, 41, 10, 37, 15, 40, 11, 38, 14, 39, 12, 26, 13,
};

fn ptrToListNode(nodes: *const [node_count + 1]ListHead, index: usize) *const ListHead {
    return &nodes[index];
}

fn ptrToHListNode(nodes: *const [node_count + 1]HListNode, index: usize) *const HListNode {
    return &nodes[index];
}

fn resetListNodes(nodes: *[node_count + 1]ListHead) void {
    for (nodes) |*node| {
        node.* = .{ .next = 0, .prev = 0 };
    }
    nodes[detached_index].next = @intFromPtr(&nodes[detached_index]);
    nodes[detached_index].prev = @intFromPtr(&nodes[detached_index]);
}

fn resetHListNodes(nodes: *[node_count + 1]HListNode) void {
    for (nodes) |*node| {
        node.* = .{ .next = 0, .pprev = 0 };
    }
}

fn wireListForward(head: *ListHead, nodes: *[node_count + 1]ListHead) void {
    head.next = @intFromPtr(&nodes[route[0]]);
    head.prev = @intFromPtr(&nodes[route[route.len - 1]]);
    for (route, 0..) |node_index, route_index| {
        nodes[node_index].next = if (route_index + 1 == route.len)
            @intFromPtr(head)
        else
            @intFromPtr(&nodes[route[route_index + 1]]);
    }
}

fn repairListBacklinks(head: *ListHead, nodes: *[node_count + 1]ListHead, repair_count: usize) void {
    for (route, 0..) |node_index, route_index| {
        if (route_index >= repair_count) break;
        nodes[node_index].prev = if (route_index == 0)
            @intFromPtr(head)
        else
            @intFromPtr(&nodes[route[route_index - 1]]);
    }
    if (repair_count >= route.len) {
        head.prev = @intFromPtr(&nodes[route[route.len - 1]]);
    }
}

fn wireHListForward(head: *HListHead, nodes: *[node_count + 1]HListNode) void {
    head.first = @intFromPtr(&nodes[route[0]]);
    for (route, 0..) |node_index, route_index| {
        nodes[node_index].next = if (route_index + 1 == route.len)
            0
        else
            @intFromPtr(&nodes[route[route_index + 1]]);
    }
}

fn repairHListPrevLinks(head: *HListHead, nodes: *[node_count + 1]HListNode, repair_count: usize) void {
    for (route, 0..) |node_index, route_index| {
        if (route_index >= repair_count) break;
        nodes[node_index].pprev = if (route_index == 0)
            @intFromPtr(&head.first)
        else
            @intFromPtr(&nodes[route[route_index - 1]].next);
    }
}

test "dopentaconta weave-clasp list route exposes staged backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var nodes: [node_count + 1]ListHead = undefined;
    resetListNodes(&nodes);
    wireListForward(&head, &nodes);

    const view = list_view.ListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, node_count), view.len());
    try std.testing.expectEqual(@as(?*const ListHead, ptrToListNode(&nodes, route[0])), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, ptrToListNode(&nodes, route[route.len - 1])), view.last());
    try std.testing.expect(!view.contains(&nodes[detached_index]));

    var it = view.iterator();
    for (route) |node_index| {
        try std.testing.expectEqual(@as(?*const ListHead, ptrToListNode(&nodes, node_index)), it.next());
        try std.testing.expect(view.contains(&nodes[node_index]));
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());

    repairListBacklinks(&head, &nodes, staged_break_index);
    const breakage = view.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, staged_break_index), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&nodes[route[staged_break_index - 1]])), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_prev);
    try std.testing.expect(!view.hasConsistentBacklinks());

    repairListBacklinks(&head, &nodes, route.len);
    try std.testing.expect(view.hasConsistentBacklinks());
}

test "dopentaconta weave-clasp hlist route exposes staged pprev repair" {
    var head = HListHead{ .first = 0 };
    var nodes: [node_count + 1]HListNode = undefined;
    resetHListNodes(&nodes);
    wireHListForward(&head, &nodes);

    const view = hlist_view.HListView.init(&head);
    try std.testing.expect(!view.isEmpty());
    try std.testing.expect(!view.isSingular());
    try std.testing.expectEqual(@as(usize, node_count), view.len());
    try std.testing.expectEqual(@as(?*const HListNode, ptrToHListNode(&nodes, route[0])), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, ptrToHListNode(&nodes, route[route.len - 1])), view.last());
    try std.testing.expect(view.tailNextIsNull());
    try std.testing.expect(!view.contains(&nodes[detached_index]));

    var it = view.iterator();
    for (route) |node_index| {
        try std.testing.expectEqual(@as(?*const HListNode, ptrToHListNode(&nodes, node_index)), it.next());
        try std.testing.expect(view.contains(&nodes[node_index]));
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());

    repairHListPrevLinks(&head, &nodes, staged_break_index);
    const breakage = view.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, staged_break_index), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&nodes[route[staged_break_index - 1]].next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), breakage.actual_pprev);
    try std.testing.expect(!view.hasConsistentPrevLinks());

    repairHListPrevLinks(&head, &nodes, route.len);
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());
}
