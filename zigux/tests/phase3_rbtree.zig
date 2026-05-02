const std = @import("std");
const rbtree = @import("rbtree_bindings");

test "phase3 rbtree root view keeps ABI constants reviewable" {
    try std.testing.expectEqual(@as(u32, 1), rbtree.ROOT_FLAG_EMPTY);
    try std.testing.expectEqual(@as(u32, 2), rbtree.ROOT_FLAG_CACHED);
    try std.testing.expectEqual(@as(u32, 4), rbtree.ROOT_FLAG_LEFTMOST_VALID);
}

test "phase3 rbtree root view distinguishes empty cached and uncached states" {
    const empty_uncached: rbtree.RootView = .{
        .root_addr = 0,
        .leftmost_addr = 0,
        .flags = rbtree.ROOT_FLAG_EMPTY,
        .reserved = 0,
    };
    try std.testing.expect(rbtree.isValid(empty_uncached));
    try std.testing.expect(rbtree.isEmpty(empty_uncached));

    const nonempty_cached: rbtree.RootView = .{
        .root_addr = 0x2000,
        .leftmost_addr = 0x1000,
        .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expect(rbtree.isValid(nonempty_cached));
    try std.testing.expect(!rbtree.isEmpty(nonempty_cached));
    try std.testing.expect(rbtree.isCached(nonempty_cached));
    try std.testing.expect(rbtree.hasLeftmost(nonempty_cached));
}

test "phase3 rbtree root view rejects leftover reserved state" {
    const invalid: rbtree.RootView = .{
        .root_addr = 0,
        .leftmost_addr = 0,
        .flags = rbtree.ROOT_FLAG_EMPTY,
        .reserved = 99,
    };
    try std.testing.expect(!rbtree.isValid(invalid));
}
