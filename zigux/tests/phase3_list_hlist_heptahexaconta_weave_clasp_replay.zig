const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;

const node_count = 67;
const detached_index = node_count;
const staged_break_index = 47;
const route = [_]usize{
    66, 0,  41, 40, 65, 1,  42, 39, 64, 2,  43, 38, 63, 3,
    44, 37, 62, 4,  45, 36, 61, 5,  46, 35, 60, 6,  47, 34,
    59, 7,  48, 33, 58, 8,  49, 32, 57, 9,  50, 31, 56, 10,
    51, 30, 55, 11, 52, 29, 54, 12, 53, 28, 27, 13, 26, 25,
    24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14,
};

comptime {
    if (route.len != node_count) @compileError("route must cover each visible node once");
}

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

test "heptahexaconta weave-clasp list route exposes staged backlink repair" {
    var seen = [_]bool{false} ** node_count;
    for (route) |node_index| {
        try std.testing.expect(node_index < node_count);
        try std.testing.expect(!seen[node_index]);
        seen[node_index] = true;
    }

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

test "heptahexaconta weave-clasp hlist route exposes staged pprev repair" {
    var seen = [_]bool{false} ** node_count;
    for (route) |node_index| {
        try std.testing.expect(node_index < node_count);
        try std.testing.expect(!seen[node_index]);
        seen[node_index] = true;
    }

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
