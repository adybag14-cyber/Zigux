const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListNode = struct {
    label: []const u8,
    link: list_view.ListHead = .{ .next = 0, .prev = 0 },
};

const HListNode = struct {
    label: []const u8,
    link: hlist_view.HListNode = .{ .next = 0, .pprev = 0 },
};

fn wireList(head: *list_view.ListHead, nodes: []const *ListNode) void {
    if (nodes.len == 0) {
        head.next = @intFromPtr(head);
        head.prev = @intFromPtr(head);
        return;
    }

    head.next = @intFromPtr(&nodes[0].link);
    head.prev = @intFromPtr(&nodes[nodes.len - 1].link);
    for (nodes, 0..) |node, index| {
        node.link.prev = if (index == 0) @intFromPtr(head) else @intFromPtr(&nodes[index - 1].link);
        node.link.next = if (index + 1 == nodes.len) @intFromPtr(head) else @intFromPtr(&nodes[index + 1].link);
    }
}

fn wireHList(head: *hlist_view.HListHead, nodes: []const *HListNode) void {
    if (nodes.len == 0) {
        head.first = 0;
        return;
    }

    head.first = @intFromPtr(&nodes[0].link);
    for (nodes, 0..) |node, index| {
        node.link.pprev = if (index == 0) @intFromPtr(&head.first) else @intFromPtr(&nodes[index - 1].link.next);
        node.link.next = if (index + 1 == nodes.len) 0 else @intFromPtr(&nodes[index + 1].link);
    }
}

fn expectListOrder(head: *const list_view.ListHead, expected: []const *const ListNode) !void {
    const view = list_view.ListView.init(head);
    try std.testing.expectEqual(expected.len, view.len());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &expected[0].link), view.first());
    try std.testing.expectEqual(@as(?*const list_view.ListHead, &expected[expected.len - 1].link), view.last());
    try std.testing.expect(view.hasConsistentBacklinks());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const list_view.ListHead, &node.link), it.next());
        try std.testing.expect(view.contains(&node.link));
    }
    try std.testing.expectEqual(@as(?*const list_view.ListHead, null), it.next());
}

fn expectHListOrder(head: *const hlist_view.HListHead, expected: []const *const HListNode) !void {
    const view = hlist_view.HListView.init(head);
    try std.testing.expectEqual(expected.len, view.len());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &expected[0].link), view.first());
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &expected[expected.len - 1].link), view.last());
    try std.testing.expect(view.firstPprevMatchesHead());
    try std.testing.expect(view.hasConsistentPrevLinks());
    try std.testing.expect(view.tailNextIsNull());

    var it = view.iterator();
    for (expected) |node| {
        try std.testing.expectEqual(@as(?*const hlist_view.HListNode, &node.link), it.next());
        try std.testing.expect(view.contains(&node.link));
    }
    try std.testing.expectEqual(@as(?*const hlist_view.HListNode, null), it.next());
}

test "lane28 mirror splice preserves list view membership and repair witnesses" {
    var head = list_view.ListHead{ .next = 0, .prev = 0 };
    var one = ListNode{ .label = "one" };
    var two = ListNode{ .label = "two" };
    var three = ListNode{ .label = "three" };
    var four = ListNode{ .label = "four" };
    var five = ListNode{ .label = "five" };
    var six = ListNode{ .label = "six" };
    const original = [_]*ListNode{ &one, &two, &three, &four, &five, &six };
    const mirrored = [_]*ListNode{ &six, &one, &five, &two, &four, &three };

    wireList(&head, &original);
    try expectListOrder(&head, &.{ &one, &two, &three, &four, &five, &six });

    head.next = @intFromPtr(&six.link);
    head.prev = @intFromPtr(&three.link);
    six.link.next = @intFromPtr(&one.link);
    one.link.next = @intFromPtr(&five.link);
    five.link.next = @intFromPtr(&two.link);
    two.link.next = @intFromPtr(&four.link);
    four.link.next = @intFromPtr(&three.link);
    three.link.next = @intFromPtr(&head);

    var breakage = list_view.ListView.init(&head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five.link)), breakage.actual_prev);

    six.link.prev = @intFromPtr(&head);
    one.link.prev = @intFromPtr(&six.link);
    five.link.prev = @intFromPtr(&one.link);
    breakage = list_view.ListView.init(&head).firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five.link)), breakage.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&one.link)), breakage.actual_prev);

    wireList(&head, &mirrored);
    try expectListOrder(&head, &.{ &six, &one, &five, &two, &four, &three });
    try std.testing.expect(!list_view.ListView.init(&head).contains(&head));
}

test "lane28 mirror splice preserves hlist view membership and repair witnesses" {
    var head = hlist_view.HListHead{ .first = 0 };
    var one = HListNode{ .label = "one" };
    var two = HListNode{ .label = "two" };
    var three = HListNode{ .label = "three" };
    var four = HListNode{ .label = "four" };
    var five = HListNode{ .label = "five" };
    var six = HListNode{ .label = "six" };
    const original = [_]*HListNode{ &one, &two, &three, &four, &five, &six };
    const mirrored = [_]*HListNode{ &six, &one, &five, &two, &four, &three };

    wireHList(&head, &original);
    try expectHListOrder(&head, &.{ &one, &two, &three, &four, &five, &six });

    head.first = @intFromPtr(&six.link);
    six.link.next = @intFromPtr(&one.link);
    one.link.next = @intFromPtr(&five.link);
    five.link.next = @intFromPtr(&two.link);
    two.link.next = @intFromPtr(&four.link);
    four.link.next = @intFromPtr(&three.link);
    three.link.next = 0;

    var breakage = hlist_view.HListView.init(&head).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five.link.next)), breakage.actual_pprev);

    six.link.pprev = @intFromPtr(&head.first);
    one.link.pprev = @intFromPtr(&six.link.next);
    five.link.pprev = @intFromPtr(&one.link.next);
    breakage = hlist_view.HListView.init(&head).firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 3), breakage.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&five.link.next)), breakage.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&one.link.next)), breakage.actual_pprev);

    wireHList(&head, &mirrored);
    try expectHListOrder(&head, &.{ &six, &one, &five, &two, &four, &three });
    try std.testing.expect(hlist_view.HListView.init(&head).tailNextIsNull());
}
