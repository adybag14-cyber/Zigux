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
}

test "phase3 shared rbtree contract keeps the shared replay root samples explicit" {
    // PHASE3_RBTREE_SHARED_SAMPLE_RECORDS=empty-root,cached-leftmost-root,uncached-root
    const empty_root = rbtree.empty();
    try std.testing.expectEqual(@as(usize, 0), empty_root.root_addr);
    try std.testing.expectEqual(@as(usize, 0), empty_root.leftmost_addr);
    try std.testing.expectEqual(@as(u32, rbtree.ROOT_FLAG_EMPTY), empty_root.flags);
    try std.testing.expectEqual(@as(u32, 0), empty_root.reserved);
    try std.testing.expect(rbtree.isValid(empty_root));
    try std.testing.expect(rbtree.isEmpty(empty_root));
    try std.testing.expect(!rbtree.isCached(empty_root));
    try std.testing.expect(!rbtree.hasLeftmost(empty_root));
    try std.testing.expect(!rbtree.hasRoot(empty_root));
    try std.testing.expect(rbtree.isCanonical(empty_root));

    const cached_root: rbtree.RootView = .{
        .root_addr = 0x2000,
        .leftmost_addr = 0x1800,
        .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(usize, 0x2000), cached_root.root_addr);
    try std.testing.expectEqual(@as(usize, 0x1800), cached_root.leftmost_addr);
    try std.testing.expectEqual(@as(u32, rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID), cached_root.flags);
    try std.testing.expectEqual(@as(u32, 0), cached_root.reserved);
    try std.testing.expect(rbtree.isValid(cached_root));
    try std.testing.expect(!rbtree.isEmpty(cached_root));
    try std.testing.expect(rbtree.isCached(cached_root));
    try std.testing.expect(rbtree.hasLeftmost(cached_root));
    try std.testing.expect(rbtree.hasRoot(cached_root));
    try std.testing.expect(rbtree.isCanonical(cached_root));

    const uncached_root: rbtree.RootView = .{
        .root_addr = 0x2400,
        .leftmost_addr = 0,
        .flags = 0,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(usize, 0x2400), uncached_root.root_addr);
    try std.testing.expectEqual(@as(usize, 0), uncached_root.leftmost_addr);
    try std.testing.expectEqual(@as(u32, 0), uncached_root.flags);
    try std.testing.expectEqual(@as(u32, 0), uncached_root.reserved);
    try std.testing.expect(rbtree.isValid(uncached_root));
    try std.testing.expect(!rbtree.isEmpty(uncached_root));
    try std.testing.expect(!rbtree.isCached(uncached_root));
    try std.testing.expect(!rbtree.hasLeftmost(uncached_root));
    try std.testing.expect(rbtree.hasRoot(uncached_root));
    try std.testing.expect(rbtree.isCanonical(uncached_root));
}
