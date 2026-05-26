const std = @import("std");
const testing = std.testing;

const rbtree_binding = @import("rbtree_bindings");
const rbtree_root_view = @import("rbtree_root_view");

test "rbtree root starter packet keeps the empty helper lane explicit" {
    const view = rbtree_root_view.empty();

    try testing.expect(rbtree_root_view.isEmpty(view));
    try testing.expect(rbtree_root_view.isValid(view));
    try testing.expect(rbtree_root_view.isCanonical(view));
    try testing.expect(!rbtree_root_view.hasRoot(view));
}

test "rbtree root starter packet keeps uncached rooted views canonical" {
    const view = rbtree_root_view.uncached(0x2200);

    try testing.expect(rbtree_root_view.isValid(view));
    try testing.expect(!rbtree_root_view.isCached(view));
    try testing.expect(!rbtree_root_view.hasLeftmost(view));
    try testing.expect(rbtree_root_view.hasOnlyKnownFlags(view));
    try testing.expect(rbtree_root_view.isCanonical(view));
    try testing.expectEqual(view, rbtree_binding.uncached(0x2200));
}

test "rbtree root starter packet keeps cached leftmost relays explicit" {
    const view = rbtree_root_view.cached(0x4400, 0x3300);

    try testing.expect(rbtree_root_view.isValid(view));
    try testing.expect(rbtree_root_view.isCached(view));
    try testing.expect(rbtree_root_view.hasLeftmost(view));
    try testing.expect(rbtree_root_view.hasOnlyKnownFlags(view));
    try testing.expect(rbtree_root_view.isCanonical(view));
    try testing.expectEqual(
        @as(u32, rbtree_binding.ROOT_FLAG_CACHED | rbtree_binding.ROOT_FLAG_LEFTMOST_VALID),
        view.flags,
    );
}

test "rbtree root starter packet keeps cached flag drift narrow" {
    const drift = rbtree_root_view.RootView{
        .root = 0x2200,
        .cached_leftmost = 0,
        .flags = rbtree_root_view.ROOT_FLAG_CACHED,
    };
    const normalized = rbtree_root_view.canonicalize(drift) orelse return error.TestUnexpectedResult;

    try testing.expect(rbtree_root_view.isValid(drift));
    try testing.expect(!rbtree_root_view.isCanonical(drift));
    try testing.expectEqual(rbtree_root_view.uncached(0x2200), normalized);
}

test "rbtree root starter packet rejects unknown flags and rootless payloads" {
    const unknown_flags = rbtree_root_view.RootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = rbtree_root_view.ROOT_FLAG_CACHED | rbtree_root_view.ROOT_FLAG_LEFTMOST_VALID | 0x4,
    };
    const rootless_payload = rbtree_root_view.RootView{
        .root = 0,
        .cached_leftmost = 0x0800,
        .flags = rbtree_root_view.ROOT_FLAG_CACHED | rbtree_root_view.ROOT_FLAG_LEFTMOST_VALID,
    };

    try testing.expectEqual(@as(?rbtree_root_view.RootView, null), rbtree_root_view.canonicalize(unknown_flags));
    try testing.expectEqual(@as(?rbtree_root_view.RootView, null), rbtree_root_view.canonicalize(rootless_payload));
}
