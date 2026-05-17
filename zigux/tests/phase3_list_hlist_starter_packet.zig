const std = @import("std");
const testing = std.testing;

const list_hlist = @import("list_hlist_bindings");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn asListViewHead(head: *const list_hlist.ListHead) *const list_view.ListHead {
    return @ptrCast(head);
}

fn asHListViewHead(head: *const list_hlist.HListHead) *const hlist_view.HListHead {
    return @ptrCast(head);
}

fn asListNode(node: *const list_hlist.ListHead) *const list_view.ListHead {
    return @ptrCast(node);
}

fn asHListNode(node: *const list_hlist.HListNode) *const hlist_view.HListNode {
    return @ptrCast(node);
}

test "list and hlist helpers preserve the shared binding layouts" {
    try testing.expectEqual(@as(u32, 1), list_hlist.abi_version);

    try testing.expectEqual(@sizeOf(list_view.ListHead), @sizeOf(list_hlist.ListHead));
    try testing.expectEqual(@alignOf(list_view.ListHead), @alignOf(list_hlist.ListHead));
    try testing.expectEqual(@offsetOf(list_view.ListHead, "next"), list_hlist.list_head_next_offset);
    try testing.expectEqual(@offsetOf(list_view.ListHead, "prev"), list_hlist.list_head_prev_offset);

    try testing.expectEqual(@sizeOf(hlist_view.HListHead), @sizeOf(list_hlist.HListHead));
    try testing.expectEqual(@alignOf(hlist_view.HListHead), @alignOf(list_hlist.HListHead));
    try testing.expectEqual(@offsetOf(hlist_view.HListHead, "first"), list_hlist.hlist_head_first_offset);

    try testing.expectEqual(@sizeOf(hlist_view.HListNode), @sizeOf(list_hlist.HListNode));
    try testing.expectEqual(@alignOf(hlist_view.HListNode), @alignOf(list_hlist.HListNode));
    try testing.expectEqual(@offsetOf(hlist_view.HListNode, "next"), list_hlist.hlist_node_next_offset);
    try testing.expectEqual(@offsetOf(hlist_view.HListNode, "pprev"), list_hlist.hlist_node_pprev_offset);
}

test "list starter packet walks binding-backed circular storage through the helper view" {
    var head = list_hlist.ListHead{ .next = 0, .prev = 0 };
    var first = list_hlist.ListHead{ .next = 0, .prev = 0 };
    var second = list_hlist.ListHead{ .next = 0, .prev = 0 };

    head.next = @intFromPtr(&first);
    head.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&head);
    second.next = @intFromPtr(&head);
    second.prev = @intFromPtr(&first);

    const view = list_view.ListView.init(asListViewHead(&head));
    try testing.expect(!view.isEmpty());
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expectEqual(@as(?*const list_view.ListHead, asListNode(&first)), view.first());
    try testing.expectEqual(@as(?*const list_view.ListHead, asListNode(&second)), view.last());
    try testing.expect(view.hasConsistentBacklinks());
}

test "hlist starter packet finds a broken prev-link witness on binding-backed storage" {
    var head = list_hlist.HListHead{ .first = 0 };
    var first = list_hlist.HListNode{ .next = 0, .pprev = 0 };
    var second = list_hlist.HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&head.first);

    const view = hlist_view.HListView.init(asHListViewHead(&head));
    try testing.expect(!view.isEmpty());
    try testing.expectEqual(@as(usize, 2), view.len());
    try testing.expectEqual(@as(?*const hlist_view.HListNode, asHListNode(&first)), view.first());
    try testing.expect(view.firstPprevMatchesHead());
    try testing.expect(!view.hasConsistentPrevLinks());

    const breakage = view.firstBrokenPrevLink().?;
    try testing.expectEqual(@as(usize, 1), breakage.current_index);
    try testing.expectEqual(@as(usize, @intFromPtr(&first.next)), breakage.expected_pprev);
    try testing.expectEqual(@as(usize, @intFromPtr(&head.first)), breakage.actual_pprev);
    try testing.expect(view.tailNextIsNull());
}
