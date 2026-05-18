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

pub fn initListHead(next: usize, prev: usize) ListHead {
    return uapi.initListHead(next, prev);
}

pub fn initEmptyListHead(self_addr: usize) ListHead {
    return uapi.initEmptyListHead(self_addr);
}

pub fn isEmptyListHead(head: ListHead, self_addr: usize) bool {
    return uapi.isEmptyListHead(head, self_addr);
}

pub fn emptyHListHead() HListHead {
    return uapi.emptyHListHead();
}

pub fn initHListHead(first: usize) HListHead {
    return uapi.initHListHead(first);
}

pub fn isEmptyHListHead(head: HListHead) bool {
    return uapi.isEmptyHListHead(head);
}

pub fn emptyHListNode() HListNode {
    return uapi.emptyHListNode();
}

pub fn initHListNode(next: usize, pprev: usize) HListNode {
    return uapi.initHListNode(next, pprev);
}

pub fn isDetachedHListNode(node: HListNode) bool {
    return uapi.isDetachedHListNode(node);
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

test "binding raw constructors preserve the uapi link values" {
    const shift = @bitSizeOf(usize) / 2;
    const list_next = (@as(usize, 0x10) << shift) | 0x20;
    const list_prev = (@as(usize, 0x30) << shift) | 0x40;
    const hfirst = (@as(usize, 0x50) << shift) | 0x60;
    const hnext = (@as(usize, 0x70) << shift) | 0x80;
    const hpprev = (@as(usize, 0x90) << shift) | 0xA0;

    try std.testing.expectEqual(uapi.initListHead(list_next, list_prev), initListHead(list_next, list_prev));
    try std.testing.expectEqual(uapi.initHListHead(hfirst), initHListHead(hfirst));
    try std.testing.expectEqual(uapi.initHListNode(hnext, hpprev), initHListNode(hnext, hpprev));
}

test "binding semantic helpers preserve the uapi empty and detached rules" {
    var list = uapi.initListHead(0, 0);
    const list_addr = @intFromPtr(&list);
    list = initEmptyListHead(list_addr);

    try std.testing.expectEqual(uapi.initEmptyListHead(list_addr), list);
    try std.testing.expectEqual(uapi.isEmptyListHead(list, list_addr), isEmptyListHead(list, list_addr));
    try std.testing.expectEqual(uapi.isEmptyHListHead(uapi.emptyHListHead()), isEmptyHListHead(emptyHListHead()));
    try std.testing.expectEqual(
        uapi.isEmptyHListHead(uapi.initHListHead(list_addr)),
        isEmptyHListHead(initHListHead(list_addr)),
    );
    try std.testing.expectEqual(
        uapi.isDetachedHListNode(uapi.emptyHListNode()),
        isDetachedHListNode(emptyHListNode()),
    );
    try std.testing.expectEqual(
        uapi.isDetachedHListNode(uapi.initHListNode(list_addr, list_addr + @sizeOf(usize))),
        isDetachedHListNode(initHListNode(list_addr, list_addr + @sizeOf(usize))),
    );
}
