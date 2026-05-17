const std = @import("std");
const uapi = @import("uapi_list_hlist");

pub const abi_version = uapi.abi_version;

pub const list_head_size: usize = @sizeOf(uapi.ListHead);
pub const list_head_align: usize = @alignOf(uapi.ListHead);
pub const list_head_next_offset: usize = @offsetOf(uapi.ListHead, "next");
pub const list_head_prev_offset: usize = @offsetOf(uapi.ListHead, "prev");

pub const hlist_head_size: usize = @sizeOf(uapi.HListHead);
pub const hlist_head_align: usize = @alignOf(uapi.HListHead);
pub const hlist_head_first_offset: usize = @offsetOf(uapi.HListHead, "first");

pub const hlist_node_size: usize = @sizeOf(uapi.HListNode);
pub const hlist_node_align: usize = @alignOf(uapi.HListNode);
pub const hlist_node_next_offset: usize = @offsetOf(uapi.HListNode, "next");
pub const hlist_node_pprev_offset: usize = @offsetOf(uapi.HListNode, "pprev");

pub const ListHead = uapi.ListHead;
pub const HListHead = uapi.HListHead;
pub const HListNode = uapi.HListNode;

pub fn emptyListHead() ListHead {
    return uapi.emptyListHead();
}

pub fn emptyHListHead() HListHead {
    return uapi.emptyHListHead();
}

pub fn emptyHListNode() HListNode {
    return uapi.emptyHListNode();
}

comptime {
    std.debug.assert(abi_version == 1);

    std.debug.assert(list_head_size == 2 * @sizeOf(usize));
    std.debug.assert(list_head_align == @alignOf(usize));
    std.debug.assert(list_head_next_offset == 0);
    std.debug.assert(list_head_prev_offset == @sizeOf(usize));

    std.debug.assert(hlist_head_size == @sizeOf(usize));
    std.debug.assert(hlist_head_align == @alignOf(usize));
    std.debug.assert(hlist_head_first_offset == 0);

    std.debug.assert(hlist_node_size == 2 * @sizeOf(usize));
    std.debug.assert(hlist_node_align == @alignOf(usize));
    std.debug.assert(hlist_node_next_offset == 0);
    std.debug.assert(hlist_node_pprev_offset == @sizeOf(usize));
}

test "binding mirrors uapi list and hlist layouts" {
    try std.testing.expectEqual(@as(u32, 1), abi_version);

    try std.testing.expectEqual(@as(usize, @sizeOf(ListHead)), list_head_size);
    try std.testing.expectEqual(@as(usize, @alignOf(ListHead)), list_head_align);
    try std.testing.expectEqual(@as(usize, @offsetOf(ListHead, "next")), list_head_next_offset);
    try std.testing.expectEqual(@as(usize, @offsetOf(ListHead, "prev")), list_head_prev_offset);

    try std.testing.expectEqual(@as(usize, @sizeOf(HListHead)), hlist_head_size);
    try std.testing.expectEqual(@as(usize, @alignOf(HListHead)), hlist_head_align);
    try std.testing.expectEqual(@as(usize, @offsetOf(HListHead, "first")), hlist_head_first_offset);

    try std.testing.expectEqual(@as(usize, @sizeOf(HListNode)), hlist_node_size);
    try std.testing.expectEqual(@as(usize, @alignOf(HListNode)), hlist_node_align);
    try std.testing.expectEqual(@as(usize, @offsetOf(HListNode, "next")), hlist_node_next_offset);
    try std.testing.expectEqual(@as(usize, @offsetOf(HListNode, "pprev")), hlist_node_pprev_offset);
}

test "binding empty constructors preserve the uapi zero state" {
    const list = emptyListHead();
    const hhead = emptyHListHead();
    const hnode = emptyHListNode();

    try std.testing.expectEqual(uapi.emptyListHead(), list);
    try std.testing.expectEqual(uapi.emptyHListHead(), hhead);
    try std.testing.expectEqual(uapi.emptyHListNode(), hnode);
}
