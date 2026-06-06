const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const ListView = list_view.ListView;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;
const HListView = hlist_view.HListView;

const Node = struct {
    label: []const u8,
    list: ListHead = .{ .next = 0, .prev = 0 },
    hnode: HListNode = .{ .next = 0, .pprev = 0 },
};

fn expectListOrder(view: ListView, expected: []const *const ListHead) !void {
    try std.testing.expectEqual(expected.len, view.len());
    try std.testing.expectEqual(@as(?*const ListHead, expected[0]), view.first());
    try std.testing.expectEqual(@as(?*const ListHead, expected[expected.len - 1]), view.last());

    var it = view.iterator();
    var index: usize = 0;
    while (it.next()) |node| : (index += 1) {
        try std.testing.expect(index < expected.len);
        try std.testing.expectEqual(expected[index], node);
        try std.testing.expect(view.contains(node));
    }

    try std.testing.expectEqual(expected.len, index);
}

fn expectHListOrder(view: HListView, expected: []const *const HListNode) !void {
    try std.testing.expectEqual(expected.len, view.len());
    try std.testing.expectEqual(@as(?*const HListNode, expected[0]), view.first());
    try std.testing.expectEqual(@as(?*const HListNode, expected[expected.len - 1]), view.last());
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    var index: usize = 0;
    while (it.next()) |node| : (index += 1) {
        try std.testing.expect(index < expected.len);
        try std.testing.expectEqual(expected[index], node);
        try std.testing.expect(view.contains(node));
    }

    try std.testing.expectEqual(expected.len, index);
}

fn linkListForward(head: *ListHead, route: []const *Node) void {
    head.next = @intFromPtr(&route[0].list);
    head.prev = @intFromPtr(&route[route.len - 1].list);

    for (route, 0..) |node, index| {
        node.list.next = if (index + 1 == route.len)
            @intFromPtr(head)
        else
            @intFromPtr(&route[index + 1].list);
    }
}

fn seedListOldBacklinks(head: *ListHead, nodes: []Node) void {
    nodes[0].list.prev = @intFromPtr(head);
    for (nodes[1..], 1..) |*node, index| {
        node.list.prev = @intFromPtr(&nodes[index - 1].list);
    }
}

fn repairListBacklinks(head: *ListHead, route: []const *Node) void {
    route[0].list.prev = @intFromPtr(head);
    for (route[1..], 1..) |node, index| {
        node.list.prev = @intFromPtr(&route[index - 1].list);
    }
    head.prev = @intFromPtr(&route[route.len - 1].list);
}

fn linkHListForward(head: *HListHead, route: []const *Node) void {
    head.first = @intFromPtr(&route[0].hnode);

    for (route, 0..) |node, index| {
        node.hnode.next = if (index + 1 == route.len)
            0
        else
            @intFromPtr(&route[index + 1].hnode);
    }
}

fn seedHListOldPrevLinks(head: *HListHead, nodes: []Node) void {
    nodes[0].hnode.pprev = @intFromPtr(&head.first);
    for (nodes[1..], 1..) |*node, index| {
        node.hnode.pprev = @intFromPtr(&nodes[index - 1].hnode.next);
    }
}

fn repairHListPrevLinks(head: *HListHead, route: []const *Node) void {
    route[0].hnode.pprev = @intFromPtr(&head.first);
    for (route[1..], 1..) |node, index| {
        node.hnode.pprev = @intFromPtr(&route[index - 1].hnode.next);
    }
}

test "list view preserves offset-ring forward order before backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var nodes = [_]Node{
        .{ .label = "one" },
        .{ .label = "two" },
        .{ .label = "three" },
        .{ .label = "four" },
        .{ .label = "five" },
        .{ .label = "six" },
    };

    const route = [_]*Node{
        &nodes[4],
        &nodes[2],
        &nodes[0],
        &nodes[5],
        &nodes[3],
        &nodes[1],
    };
    const expected = [_]*const ListHead{
        &nodes[4].list,
        &nodes[2].list,
        &nodes[0].list,
        &nodes[5].list,
        &nodes[3].list,
        &nodes[1].list,
    };

    linkListForward(&head, &route);
    seedListOldBacklinks(&head, &nodes);

    const view_before_repair = ListView.init(&head);
    try std.testing.expect(!view_before_repair.isEmpty());
    try std.testing.expect(!view_before_repair.isSingular());
    try expectListOrder(view_before_repair, &expected);
    try std.testing.expect(!view_before_repair.hasConsistentBacklinks());

    const first_break = view_before_repair.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), first_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&nodes[3].list)), first_break.actual_prev);

    route[0].list.prev = @intFromPtr(&head);
    const second_break = ListView.init(&head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 1), second_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&nodes[4].list)), second_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&nodes[1].list)), second_break.actual_prev);

    repairListBacklinks(&head, &route);
    const repaired_view = ListView.init(&head);
    try expectListOrder(repaired_view, &expected);
    try std.testing.expect(repaired_view.hasConsistentBacklinks());
    try std.testing.expect(repaired_view.firstBrokenBacklink() == null);
}

test "hlist view preserves offset-ring forward order before pprev repair" {
    var head = HListHead{ .first = 0 };
    var nodes = [_]Node{
        .{ .label = "one" },
        .{ .label = "two" },
        .{ .label = "three" },
        .{ .label = "four" },
        .{ .label = "five" },
        .{ .label = "six" },
    };

    const route = [_]*Node{
        &nodes[4],
        &nodes[2],
        &nodes[0],
        &nodes[5],
        &nodes[3],
        &nodes[1],
    };
    const expected = [_]*const HListNode{
        &nodes[4].hnode,
        &nodes[2].hnode,
        &nodes[0].hnode,
        &nodes[5].hnode,
        &nodes[3].hnode,
        &nodes[1].hnode,
    };

    linkHListForward(&head, &route);
    seedHListOldPrevLinks(&head, &nodes);

    const view_before_repair = HListView.init(&head);
    try std.testing.expect(!view_before_repair.isEmpty());
    try std.testing.expect(!view_before_repair.isSingular());
    try expectHListOrder(view_before_repair, &expected);
    try std.testing.expect(!view_before_repair.firstPprevMatchesHead());
    try std.testing.expect(!view_before_repair.hasConsistentPrevLinks());

    const first_break = view_before_repair.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), first_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&nodes[3].hnode.next)), first_break.actual_pprev);

    route[0].hnode.pprev = @intFromPtr(&head.first);
    const second_break = HListView.init(&head).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 1), second_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&nodes[4].hnode.next)), second_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&nodes[1].hnode.next)), second_break.actual_pprev);

    repairHListPrevLinks(&head, &route);
    const repaired_view = HListView.init(&head);
    try expectHListOrder(repaired_view, &expected);
    try std.testing.expect(repaired_view.firstPprevMatchesHead());
    try std.testing.expect(repaired_view.hasConsistentPrevLinks());
    try std.testing.expect(repaired_view.firstBrokenPrevLink() == null);
}
