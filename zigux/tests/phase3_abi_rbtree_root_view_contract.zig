const std = @import("std");

const abi = @import("abi_bindings");

fn expectRootView(
    view: abi.RbtreeRootView,
    root: usize,
    cached_leftmost: usize,
    flags: u32,
) !void {
    try std.testing.expectEqual(root, view.root);
    try std.testing.expectEqual(cached_leftmost, view.cached_leftmost);
    try std.testing.expectEqual(flags, view.flags);
}

test "phase3 abi rbtree root view keeps published layout and flags" {
    try std.testing.expectEqual(abi.rbtree_root_view_size, @sizeOf(abi.RbtreeRootView));
    try std.testing.expectEqual(abi.rbtree_root_view_align, @alignOf(abi.RbtreeRootView));
    try std.testing.expectEqual(abi.rbtree_root_view_root_offset, @offsetOf(abi.RbtreeRootView, "root"));
    try std.testing.expectEqual(
        abi.rbtree_root_view_cached_leftmost_offset,
        @offsetOf(abi.RbtreeRootView, "cached_leftmost"),
    );
    try std.testing.expectEqual(abi.rbtree_root_view_flags_offset, @offsetOf(abi.RbtreeRootView, "flags"));

    try std.testing.expectEqual(@as(u32, 1), abi.RBTREE_ROOT_VIEW_FLAG_CACHED);
    try std.testing.expectEqual(@as(u32, 2), abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID);
}

test "phase3 abi rbtree root view validity requires root and matched cached-leftmost state" {
    const uncached = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = 0,
    };
    const cached = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED | abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };
    const rootless = abi.RbtreeRootView{
        .root = 0,
        .cached_leftmost = 0,
        .flags = 0,
    };
    const cached_without_leftmost_addr = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED | abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };
    const cached_without_leftmost_flag = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED,
    };
    const leftmost_without_cached_flag = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };

    try std.testing.expect(abi.rbtreeRootViewIsValid(uncached));
    try std.testing.expect(!abi.rbtreeRootViewIsCached(uncached));
    try std.testing.expect(!abi.rbtreeRootViewHasLeftmost(uncached));

    try std.testing.expect(abi.rbtreeRootViewIsValid(cached));
    try std.testing.expect(abi.rbtreeRootViewIsCached(cached));
    try std.testing.expect(abi.rbtreeRootViewHasLeftmost(cached));

    try std.testing.expect(!abi.rbtreeRootViewIsValid(rootless));
    try std.testing.expect(!abi.rbtreeRootViewIsValid(cached_without_leftmost_addr));
    try std.testing.expect(!abi.rbtreeRootViewIsValid(cached_without_leftmost_flag));
    try std.testing.expect(!abi.rbtreeRootViewIsValid(leftmost_without_cached_flag));
}

test "phase3 abi rbtree root view canonicalization clears malformed metadata" {
    const uncached_with_flag = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED,
    };
    const cached_without_flags = abi.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = 0,
    };
    const rootless_cached = abi.RbtreeRootView{
        .root = 0,
        .cached_leftmost = 0x0800,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED | abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };

    const canonical_uncached = abi.canonicalizeRbtreeRootView(uncached_with_flag);
    const canonical_cached = abi.canonicalizeRbtreeRootView(cached_without_flags);
    const canonical_rootless = abi.canonicalizeRbtreeRootView(rootless_cached);

    try expectRootView(canonical_uncached, 0x1000, 0, 0);
    try std.testing.expect(abi.rbtreeRootViewIsValid(canonical_uncached));

    try expectRootView(
        canonical_cached,
        0x1000,
        0x0800,
        abi.RBTREE_ROOT_VIEW_FLAG_CACHED | abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    );
    try std.testing.expect(abi.rbtreeRootViewIsValid(canonical_cached));

    try expectRootView(canonical_rootless, 0, 0, 0);
    try std.testing.expect(!abi.rbtreeRootViewIsValid(canonical_rootless));
}
