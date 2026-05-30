const std = @import("std");
const abi = @import("abi_bindings");

test "rbtree root view relay exposes the ABI layout contract" {
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), abi.rbtree_root_view_align);
    try std.testing.expectEqual(@as(usize, 0), abi.rbtree_root_view_root_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), abi.rbtree_root_view_cached_leftmost_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), abi.rbtree_root_view_flags_offset);
    try std.testing.expectEqual(@sizeOf(abi.RbtreeRootView), abi.rbtree_root_view_size);
}

test "rbtree root view relay classifies cached and uncached views" {
    const uncached = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = 0,
    };
    const cached = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x1080,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED |
            abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };
    const leftmost_flag_without_cache = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x1080,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };
    const cache_flag_without_leftmost = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x1080,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED,
    };
    const cache_flags_without_address = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED |
            abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };

    try std.testing.expect(!abi.rbtreeRootViewIsCached(uncached));
    try std.testing.expect(!abi.rbtreeRootViewHasLeftmost(uncached));
    try std.testing.expect(abi.rbtreeRootViewIsValid(uncached));

    try std.testing.expect(abi.rbtreeRootViewIsCached(cached));
    try std.testing.expect(abi.rbtreeRootViewHasLeftmost(cached));
    try std.testing.expect(abi.rbtreeRootViewIsValid(cached));

    try std.testing.expect(!abi.rbtreeRootViewIsValid(.{
        .root = 0,
        .cached_leftmost = 0,
        .flags = 0,
    }));
    try std.testing.expect(!abi.rbtreeRootViewIsValid(leftmost_flag_without_cache));
    try std.testing.expect(!abi.rbtreeRootViewIsValid(cache_flag_without_leftmost));
    try std.testing.expect(!abi.rbtreeRootViewIsValid(cache_flags_without_address));
}

test "rbtree root view relay canonicalizes cache metadata" {
    const empty = abi.canonicalizeRbtreeRootView(.{
        .root = 0,
        .cached_leftmost = 0x80,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED,
    });
    const uncached = abi.canonicalizeRbtreeRootView(.{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED |
            abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    });
    const cached = abi.canonicalizeRbtreeRootView(.{
        .root = 0x1000,
        .cached_leftmost = 0x1080,
        .flags = 0,
    });

    try std.testing.expectEqual(@as(usize, 0), empty.root);
    try std.testing.expectEqual(@as(usize, 0), empty.cached_leftmost);
    try std.testing.expectEqual(@as(u32, 0), empty.flags);

    try std.testing.expectEqual(@as(usize, 0x1000), uncached.root);
    try std.testing.expectEqual(@as(usize, 0), uncached.cached_leftmost);
    try std.testing.expectEqual(@as(u32, 0), uncached.flags);
    try std.testing.expect(abi.rbtreeRootViewIsValid(uncached));

    try std.testing.expectEqual(@as(usize, 0x1000), cached.root);
    try std.testing.expectEqual(@as(usize, 0x1080), cached.cached_leftmost);
    try std.testing.expectEqual(
        @as(u32, abi.RBTREE_ROOT_VIEW_FLAG_CACHED | abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID),
        cached.flags,
    );
    try std.testing.expect(abi.rbtreeRootViewIsValid(cached));
}
