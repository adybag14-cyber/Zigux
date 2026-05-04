const std = @import("std");
const abi = @import("abi_bindings");
const rbtree = @import("rbtree_bindings");

fn expectSameRootView(shared: abi.RbtreeRootView, dedicated: rbtree.RootView) !void {
    try std.testing.expectEqual(dedicated.root_addr, shared.root_addr);
    try std.testing.expectEqual(dedicated.leftmost_addr, shared.leftmost_addr);
    try std.testing.expectEqual(dedicated.flags, shared.flags);
    try std.testing.expectEqual(dedicated.reserved, shared.reserved);
}

test "phase3 shared rbtree contract keeps the shared root view layout aligned with the dedicated packet" {
    // PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2 + 8), @sizeOf(abi.RbtreeRootView));
    try std.testing.expectEqual(@sizeOf(rbtree.RootView), @sizeOf(abi.RbtreeRootView));
    try std.testing.expectEqual(@alignOf(rbtree.RootView), @alignOf(abi.RbtreeRootView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.RbtreeRootView, "root_addr"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.RbtreeRootView, "leftmost_addr"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(abi.RbtreeRootView, "flags"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2 + 4), @offsetOf(abi.RbtreeRootView, "reserved"));
    try std.testing.expectEqual(@offsetOf(rbtree.RootView, "root_addr"), @offsetOf(abi.RbtreeRootView, "root_addr"));
    try std.testing.expectEqual(@offsetOf(rbtree.RootView, "leftmost_addr"), @offsetOf(abi.RbtreeRootView, "leftmost_addr"));
    try std.testing.expectEqual(@offsetOf(rbtree.RootView, "flags"), @offsetOf(abi.RbtreeRootView, "flags"));
    try std.testing.expectEqual(@offsetOf(rbtree.RootView, "reserved"), @offsetOf(abi.RbtreeRootView, "reserved"));
}

test "phase3 shared rbtree contract keeps the shared root flags explicit and equal to the dedicated packet" {
    // PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT=root_flag_empty,root_flag_cached,root_flag_leftmost_valid
    try std.testing.expectEqual(@as(u32, 1), abi.RBTREE_ROOT_FLAG_EMPTY);
    try std.testing.expectEqual(@as(u32, 2), abi.RBTREE_ROOT_FLAG_CACHED);
    try std.testing.expectEqual(@as(u32, 4), abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID);
    try std.testing.expectEqual(abi.RBTREE_ROOT_FLAG_EMPTY, rbtree.ROOT_FLAG_EMPTY);
    try std.testing.expectEqual(abi.RBTREE_ROOT_FLAG_CACHED, rbtree.ROOT_FLAG_CACHED);
    try std.testing.expectEqual(abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID, rbtree.ROOT_FLAG_LEFTMOST_VALID);
}

test "phase3 shared rbtree contract keeps the shared replay root samples explicit" {
    // PHASE3_RBTREE_SHARED_SAMPLE_RECORDS=empty-root,cached-leftmost-root,uncached-root
    const empty_root: abi.RbtreeRootView = .{
        .root_addr = 0,
        .leftmost_addr = 0,
        .flags = abi.RBTREE_ROOT_FLAG_EMPTY,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(usize, 0), empty_root.root_addr);
    try std.testing.expectEqual(@as(usize, 0), empty_root.leftmost_addr);
    try std.testing.expectEqual(@as(u32, abi.RBTREE_ROOT_FLAG_EMPTY), empty_root.flags);
    try std.testing.expectEqual(@as(u32, 0), empty_root.reserved);
    try expectSameRootView(empty_root, rbtree.empty());

    const cached_root: abi.RbtreeRootView = .{
        .root_addr = 0x2000,
        .leftmost_addr = 0x1800,
        .flags = abi.RBTREE_ROOT_FLAG_CACHED | abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(usize, 0x2000), cached_root.root_addr);
    try std.testing.expectEqual(@as(usize, 0x1800), cached_root.leftmost_addr);
    try std.testing.expectEqual(@as(u32, abi.RBTREE_ROOT_FLAG_CACHED | abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID), cached_root.flags);
    try std.testing.expectEqual(@as(u32, 0), cached_root.reserved);
    try expectSameRootView(cached_root, .{
        .root_addr = 0x2000,
        .leftmost_addr = 0x1800,
        .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    });

    const uncached_root: abi.RbtreeRootView = .{
        .root_addr = 0x2400,
        .leftmost_addr = 0,
        .flags = 0,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(usize, 0x2400), uncached_root.root_addr);
    try std.testing.expectEqual(@as(usize, 0), uncached_root.leftmost_addr);
    try std.testing.expectEqual(@as(u32, 0), uncached_root.flags);
    try std.testing.expectEqual(@as(u32, 0), uncached_root.reserved);
    try expectSameRootView(uncached_root, .{
        .root_addr = 0x2400,
        .leftmost_addr = 0,
        .flags = 0,
        .reserved = 0,
    });
}
