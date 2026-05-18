const std = @import("std");

pub const abi_version: u32 = 1;

pub const ListHead = extern struct {
    next: usize,
    prev: usize,
};

pub const HListHead = extern struct {
    first: usize,
};

pub const HListNode = extern struct {
    next: usize,
    pprev: usize,
};

pub fn emptyListHead() ListHead {
    return .{ .next = 0, .prev = 0 };
}

pub fn initListHead(next: usize, prev: usize) ListHead {
    return .{ .next = next, .prev = prev };
}

pub fn emptyHListHead() HListHead {
    return .{ .first = 0 };
}

pub fn initHListHead(first: usize) HListHead {
    return .{ .first = first };
}

pub fn emptyHListNode() HListNode {
    return .{ .next = 0, .pprev = 0 };
}

pub fn initHListNode(next: usize, pprev: usize) HListNode {
    return .{ .next = next, .pprev = pprev };
}

comptime {
    std.debug.assert(@sizeOf(ListHead) == 2 * @sizeOf(usize));
    std.debug.assert(@alignOf(ListHead) == @alignOf(usize));
    std.debug.assert(@offsetOf(ListHead, "next") == 0);
    std.debug.assert(@offsetOf(ListHead, "prev") == @sizeOf(usize));

    std.debug.assert(@sizeOf(HListHead) == @sizeOf(usize));
    std.debug.assert(@alignOf(HListHead) == @alignOf(usize));
    std.debug.assert(@offsetOf(HListHead, "first") == 0);

    std.debug.assert(@sizeOf(HListNode) == 2 * @sizeOf(usize));
    std.debug.assert(@alignOf(HListNode) == @alignOf(usize));
    std.debug.assert(@offsetOf(HListNode, "next") == 0);
    std.debug.assert(@offsetOf(HListNode, "pprev") == @sizeOf(usize));
}

test "uapi list/hlist layouts stay pointer-width explicit" {
    try std.testing.expectEqual(@as(u32, 1), abi_version);

    try std.testing.expectEqual(@as(usize, 2 * @sizeOf(usize)), @sizeOf(ListHead));
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(ListHead));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ListHead, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(ListHead, "prev"));

    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @sizeOf(HListHead));
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListHead));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(HListHead, "first"));

    try std.testing.expectEqual(@as(usize, 2 * @sizeOf(usize)), @sizeOf(HListNode));
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListNode));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(HListNode, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(HListNode, "pprev"));
}

test "uapi list/hlist empty constructors zero every field" {
    const list = emptyListHead();
    const hhead = emptyHListHead();
    const hnode = emptyHListNode();

    try std.testing.expectEqual(@as(usize, 0), list.next);
    try std.testing.expectEqual(@as(usize, 0), list.prev);
    try std.testing.expectEqual(@as(usize, 0), hhead.first);
    try std.testing.expectEqual(@as(usize, 0), hnode.next);
    try std.testing.expectEqual(@as(usize, 0), hnode.pprev);
}

test "uapi list/hlist raw constructors keep explicit link values" {
    const shift = @bitSizeOf(usize) / 2;
    const list_next = (@as(usize, 0x11) << shift) | 0x22;
    const list_prev = (@as(usize, 0x33) << shift) | 0x44;
    const hfirst = (@as(usize, 0x55) << shift) | 0x66;
    const hnext = (@as(usize, 0x77) << shift) | 0x88;
    const hpprev = (@as(usize, 0x99) << shift) | 0xAA;

    const list = initListHead(list_next, list_prev);
    const hhead = initHListHead(hfirst);
    const hnode = initHListNode(hnext, hpprev);

    try std.testing.expectEqual(list_next, list.next);
    try std.testing.expectEqual(list_prev, list.prev);
    try std.testing.expectEqual(hfirst, hhead.first);
    try std.testing.expectEqual(hnext, hnode.next);
    try std.testing.expectEqual(hpprev, hnode.pprev);
}
