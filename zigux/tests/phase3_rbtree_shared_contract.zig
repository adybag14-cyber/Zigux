const std = @import("std");
const rbtree = @import("rbtree_bindings");

test "phase3 shared rbtree contract keeps the dedicated root view layout" {
    // PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2 + 8), @sizeOf(rbtree.RootView));
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(rbtree.RootView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(rbtree.RootView, "root_addr"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(rbtree.RootView, "leftmost_addr"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(rbtree.RootView, "flags"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2 + 4), @offsetOf(rbtree.RootView, "reserved"));
}

test "phase3 shared rbtree contract keeps the dedicated root flags explicit" {
    // PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT=root_flag_empty,root_flag_cached,root_flag_leftmost_valid
    try std.testing.expectEqual(@as(u32, 1), rbtree.ROOT_FLAG_EMPTY);
    try std.testing.expectEqual(@as(u32, 2), rbtree.ROOT_FLAG_CACHED);
    try std.testing.expectEqual(@as(u32, 4), rbtree.ROOT_FLAG_LEFTMOST_VALID);

    const cached: rbtree.RootView = .{
        .root_addr = 0x2000,
        .leftmost_addr = 0x1800,
        .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expect(rbtree.isValid(cached));
    try std.testing.expect(!rbtree.isEmpty(cached));
    try std.testing.expect(rbtree.isCached(cached));
    try std.testing.expect(rbtree.hasLeftmost(cached));
}
