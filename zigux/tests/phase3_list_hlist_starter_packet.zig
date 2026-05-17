const std = @import("std");
const testing = std.testing;

const list_hlist = @import("list_hlist_binding");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

test "list/hlist starter binding keeps pointer-width layouts explicit" {
    try testing.expectEqual(@as(u32, 1), list_hlist.abi_version);

    try testing.expectEqual(2 * @sizeOf(usize), list_hlist.list_head_size);
    try testing.expectEqual(@alignOf(usize), list_hlist.list_head_align);
    try testing.expectEqual(@as(usize, 0), list_hlist.list_head_next_offset);
    try testing.expectEqual(@sizeOf(usize), list_hlist.list_head_prev_offset);

    try testing.expectEqual(@sizeOf(usize), list_hlist.hlist_head_size);
    try testing.expectEqual(@alignOf(usize), list_hlist.hlist_head_align);
    try testing.expectEqual(@as(usize, 0), list_hlist.hlist_head_first_offset);

    try testing.expectEqual(2 * @sizeOf(usize), list_hlist.hlist_node_size);
    try testing.expectEqual(@alignOf(usize), list_hlist.hlist_node_align);
    try testing.expectEqual(@as(usize, 0), list_hlist.hlist_node_next_offset);
    try testing.expectEqual(@sizeOf(usize), list_hlist.hlist_node_pprev_offset);
}

test "list view keeps bounded circular traversal reviewable" {
    var head = list_hlist.ListHead{ .next = 0, .prev = 0 };
    var first = list_hlist.ListHead{ .next = 0, .prev = 0 };
    var second = list_hlist.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(&head);
    try testing.expect(!view.isEmpty());
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expect(view.isCircular());
    try testing.expectEqual(@as(*const list_hlist.ListHead, &first), view.first().?);
    try testing.expectEqual(@as(*const list_hlist.ListHead, &second), view.last().?);
}

test "hlist view keeps bounded link-back checks explicit" {
    var head = list_hlist.HListHead{ .first = 0 };
    var first = list_hlist.HListNode{ .next = 0, .pprev = 0 };
    var second = list_hlist.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    const view = hlist_view.HListView.init(&head);
    try testing.expect(!view.isEmpty());
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(view.linksBackToPrevious());
    try testing.expect(view.tailNextIsNull());
    try testing.expectEqual(@as(*const list_hlist.HListNode, &first), view.first().?);
}
