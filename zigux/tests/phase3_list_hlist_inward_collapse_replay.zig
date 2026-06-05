const std = @import("std");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

const ListHead = list_view.ListHead;
const HListHead = hlist_view.HListHead;
const HListNode = hlist_view.HListNode;

fn linkList(head: *ListHead, nodes: []const *ListHead) void {
    if (nodes.len == 0) {
        head.next = @intFromPtr(head);
        head.prev = @intFromPtr(head);
        return;
    }

    head.next = @intFromPtr(nodes[0]);
    head.prev = @intFromPtr(nodes[nodes.len - 1]);
    for (nodes, 0..) |node, index| {
        node.prev = if (index == 0) @intFromPtr(head) else @intFromPtr(nodes[index - 1]);
        node.next = if (index + 1 == nodes.len) @intFromPtr(head) else @intFromPtr(nodes[index + 1]);
    }
}

fn linkHList(head: *HListHead, nodes: []const *HListNode) void {
    if (nodes.len == 0) {
        head.first = 0;
        return;
    }

    head.first = @intFromPtr(nodes[0]);
    for (nodes, 0..) |node, index| {
        node.pprev = if (index == 0) @intFromPtr(&head.first) else @intFromPtr(&nodes[index - 1].next);
        node.next = if (index + 1 == nodes.len) 0 else @intFromPtr(nodes[index + 1]);
    }
}

test "list view tracks inward collapse before staged backlink repair" {
    var head = ListHead{ .next = 0, .prev = 0 };
    var old_first = ListHead{ .next = 0, .prev = 0 };
    var left = ListHead{ .next = 0, .prev = 0 };
    var middle = ListHead{ .next = 0, .prev = 0 };
    var right = ListHead{ .next = 0, .prev = 0 };
    var old_tail = ListHead{ .next = 0, .prev = 0 };

    linkList(&head, &.{ &old_first, &left, &middle, &right, &old_tail });

    head.next = @intFromPtr(&left);
    right.next = @intFromPtr(&head);

    const collapsed = list_view.ListView.init(&head);
    try std.testing.expectEqual(@as(?*const ListHead, &left), collapsed.first());
    try std.testing.expectEqual(@as(?*const ListHead, &old_tail), collapsed.last());
    try std.testing.expectEqual(@as(usize, 3), collapsed.len());
    try std.testing.expect(!collapsed.contains(&old_first));
    try std.testing.expect(collapsed.contains(&left));
    try std.testing.expect(collapsed.contains(&middle));
    try std.testing.expect(collapsed.contains(&right));
    try std.testing.expect(!collapsed.contains(&old_tail));

    const first_break = collapsed.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 0), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head)), first_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_first)), first_break.actual_prev);

    left.prev = @intFromPtr(&head);
    const tail_break = collapsed.firstBrokenBacklink().?;
    try std.testing.expectEqual(@as(usize, 3), tail_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&right)), tail_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_tail)), tail_break.actual_prev);
    try std.testing.expectEqual(@as(?*const ListHead, &old_tail), collapsed.last());

    head.prev = @intFromPtr(&right);
    try std.testing.expectEqual(@as(?*const ListHead, &right), collapsed.last());
    try std.testing.expect(collapsed.hasConsistentBacklinks());
}

test "hlist view tracks inward collapse before first pprev repair" {
    var head = HListHead{ .first = 0 };
    var old_first = HListNode{ .next = 0, .pprev = 0 };
    var left = HListNode{ .next = 0, .pprev = 0 };
    var middle = HListNode{ .next = 0, .pprev = 0 };
    var right = HListNode{ .next = 0, .pprev = 0 };
    var old_tail = HListNode{ .next = 0, .pprev = 0 };

    linkHList(&head, &.{ &old_first, &left, &middle, &right, &old_tail });

    head.first = @intFromPtr(&left);
    right.next = 0;

    const collapsed = hlist_view.HListView.init(&head);
    try std.testing.expectEqual(@as(?*const HListNode, &left), collapsed.first());
    try std.testing.expectEqual(@as(?*const HListNode, &right), collapsed.last());
    try std.testing.expectEqual(@as(usize, 3), collapsed.len());
    try std.testing.expect(!collapsed.contains(&old_first));
    try std.testing.expect(collapsed.contains(&left));
    try std.testing.expect(collapsed.contains(&middle));
    try std.testing.expect(collapsed.contains(&right));
    try std.testing.expect(!collapsed.contains(&old_tail));
    try std.testing.expect(!collapsed.firstPprevMatchesHead());
    try std.testing.expect(collapsed.tailNextIsNull());

    const first_break = collapsed.firstBrokenPrevLink().?;
    try std.testing.expectEqual(@as(usize, 0), first_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&head.first)), first_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&old_first.next)), first_break.actual_pprev);

    left.pprev = @intFromPtr(&head.first);
    try std.testing.expect(collapsed.firstPprevMatchesHead());
    try std.testing.expect(collapsed.hasConsistentPrevLinks());
    try std.testing.expect(collapsed.tailNextIsNull());
}
