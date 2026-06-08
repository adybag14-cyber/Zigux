const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;

const visible_count = 41;
const detached_index = visible_count;
const stage_break = 23;

const route = [_]usize{
    40, 0,  20, 19, 38, 2,  22, 17, 36, 4,  24,
    15, 34, 6,  26, 13, 32, 8,  28, 11, 30, 10,
    29, 12, 27, 14, 25, 16, 23, 18, 21, 1,  39,
    3,  37, 5,  35, 7,  33, 9,  31,
};

const Node = struct {
    list: ListHead,
    hlist: HListNode,
};

fn initNodes() [visible_count + 1]Node {
    var nodes: [visible_count + 1]Node = undefined;
    for (&nodes) |*node| {
        node.* = .{
            .list = .{ .next = 0, .prev = 0 },
            .hlist = .{ .next = 0, .pprev = 0 },
        };
    }

    nodes[detached_index].list.next = @intFromPtr(&nodes[detached_index].list);
    nodes[detached_index].list.prev = @intFromPtr(&nodes[detached_index].list);
    return nodes;
}

fn installForwardOnly(
    list_head: *ListHead,
    hlist_head: *HListHead,
    nodes: *[visible_count + 1]Node,
) void {
    list_head.next = @intFromPtr(&nodes[route[0]].list);
    list_head.prev = @intFromPtr(&nodes[route[visible_count - 1]].list);
    hlist_head.first = @intFromPtr(&nodes[route[0]].hlist);

    for (route, 0..) |node_index, route_index| {
        const next_index = if (route_index + 1 < visible_count) route[route_index + 1] else null;
        nodes[node_index].list.next = if (next_index) |index| @intFromPtr(&nodes[index].list) else @intFromPtr(list_head);
        nodes[node_index].list.prev = 0;
        nodes[node_index].hlist.next = if (next_index) |index| @intFromPtr(&nodes[index].hlist) else 0;
        nodes[node_index].hlist.pprev = 0;
    }
}

fn repairReverseLinks(
    list_head: *ListHead,
    hlist_head: *HListHead,
    nodes: *[visible_count + 1]Node,
    repaired_count: usize,
) void {
    std.debug.assert(repaired_count <= visible_count);

    for (route[0..repaired_count], 0..) |node_index, route_index| {
        nodes[node_index].list.prev = if (route_index == 0)
            @intFromPtr(list_head)
        else
            @intFromPtr(&nodes[route[route_index - 1]].list);

        nodes[node_index].hlist.pprev = if (route_index == 0)
            @intFromPtr(&hlist_head.first)
        else
            @intFromPtr(&nodes[route[route_index - 1]].hlist.next);
    }
}

fn expectListOrder(view: list_view.ListView, nodes: *[visible_count + 1]Node) !void {
    var it = view.iterator();
    for (route) |node_index| {
        try std.testing.expectEqual(@as(?*const ListHead, &nodes[node_index].list), it.next());
    }
    try std.testing.expectEqual(@as(?*const ListHead, null), it.next());
}

fn expectHListOrder(view: hlist_view.HListView, nodes: *[visible_count + 1]Node) !void {
    var it = view.iterator();
    for (route) |node_index| {
        try std.testing.expectEqual(@as(?*const HListNode, &nodes[node_index].hlist), it.next());
    }
    try std.testing.expectEqual(@as(?*const HListNode, null), it.next());
}

test "hentetraconta inner lattice preserves forward list and hlist visibility before repair" {
    var nodes = initNodes();
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var hlist_head = HListHead{ .first = 0 };
    installForwardOnly(&list_head, &hlist_head, &nodes);

    const list = list_view.ListView.init(&list_head);
    const hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expect(!list.isEmpty());
    try std.testing.expect(!hlist.isEmpty());
    try std.testing.expectEqual(@as(usize, visible_count), list.len());
    try std.testing.expectEqual(@as(usize, visible_count), hlist.len());
    try std.testing.expectEqual(@as(?*const ListHead, &nodes[route[0]].list), list.first());
    try std.testing.expectEqual(@as(?*const HListNode, &nodes[route[0]].hlist), hlist.first());
    try std.testing.expectEqual(@as(?*const ListHead, &nodes[route[visible_count - 1]].list), list.last());
    try std.testing.expectEqual(@as(?*const HListNode, &nodes[route[visible_count - 1]].hlist), hlist.last());
    try expectListOrder(list, &nodes);
    try expectHListOrder(hlist, &nodes);

    for (route) |node_index| {
        try std.testing.expect(list.contains(&nodes[node_index].list));
        try std.testing.expect(hlist.contains(&nodes[node_index].hlist));
    }
    try std.testing.expect(!list.contains(&nodes[detached_index].list));
    try std.testing.expect(!hlist.contains(&nodes[detached_index].hlist));
    try std.testing.expect(hlist.tailNextIsNull());

    const list_break = list.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), list_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), list_break.actual_prev);

    const hlist_break = hlist.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), hlist_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_head.first)), hlist_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), hlist_break.actual_pprev);
    try std.testing.expect(!list.hasConsistentBacklinks());
    try std.testing.expect(!hlist.firstPprevMatchesHead());
    try std.testing.expect(!hlist.hasConsistentPrevLinks());
}

test "hentetraconta inner lattice repairs list backlinks and hlist pprev after offset hinge" {
    var nodes = initNodes();
    var list_head = ListHead{ .next = 0, .prev = 0 };
    var hlist_head = HListHead{ .first = 0 };
    installForwardOnly(&list_head, &hlist_head, &nodes);

    repairReverseLinks(&list_head, &hlist_head, &nodes, stage_break);

    const staged_list = list_view.ListView.init(&list_head);
    const staged_hlist = hlist_view.HListView.init(&hlist_head);

    const list_break = staged_list.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, stage_break), list_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&nodes[route[stage_break - 1]].list)), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, 0), list_break.actual_prev);

    const hlist_break = staged_hlist.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, stage_break), hlist_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&nodes[route[stage_break - 1]].hlist.next)), hlist_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, 0), hlist_break.actual_pprev);

    repairReverseLinks(&list_head, &hlist_head, &nodes, visible_count);

    const repaired_list = list_view.ListView.init(&list_head);
    const repaired_hlist = hlist_view.HListView.init(&hlist_head);

    try std.testing.expect(repaired_list.hasConsistentBacklinks());
    try std.testing.expect(repaired_list.firstBrokenBacklink() == null);
    try std.testing.expect(repaired_hlist.firstPprevMatchesHead());
    try std.testing.expect(repaired_hlist.hasConsistentPrevLinks());
    try std.testing.expect(repaired_hlist.firstBrokenPrevLink() == null);
    try expectListOrder(repaired_list, &nodes);
    try expectHListOrder(repaired_hlist, &nodes);
}
