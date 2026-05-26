const std = @import("std");
const rbtree = @import("rbtree_bindings");

pub const RootView = rbtree.RootView;
pub const ROOT_FLAG_CACHED = rbtree.ROOT_FLAG_CACHED;
pub const ROOT_FLAG_LEFTMOST_VALID = rbtree.ROOT_FLAG_LEFTMOST_VALID;
pub const KNOWN_FLAG_MASK = rbtree.KNOWN_FLAG_MASK;

pub fn empty() RootView {
    return rbtree.empty();
}

pub fn uncached(root: usize) RootView {
    return rbtree.uncached(root);
}

pub fn cached(root: usize, cached_leftmost: usize) RootView {
    return rbtree.cached(root, cached_leftmost);
}

pub fn isEmpty(view: RootView) bool {
    return rbtree.isEmpty(view);
}

pub fn isCached(view: RootView) bool {
    return rbtree.isCached(view);
}

pub fn hasLeftmost(view: RootView) bool {
    return rbtree.hasLeftmost(view);
}

pub fn hasOnlyKnownFlags(view: RootView) bool {
    return rbtree.hasOnlyKnownFlags(view);
}

pub fn hasRoot(view: RootView) bool {
    return rbtree.hasRoot(view);
}

pub fn isValid(view: RootView) bool {
    return rbtree.isValid(view);
}

pub fn canonicalize(view: RootView) ?RootView {
    return rbtree.canonicalize(view);
}

pub fn isCanonical(view: RootView) bool {
    return rbtree.isCanonical(view);
}

test "phase3 rbtree root view helper keeps dedicated binding aliases explicit" {
    try std.testing.expectEqual(rbtree.ROOT_FLAG_CACHED, ROOT_FLAG_CACHED);
    try std.testing.expectEqual(rbtree.ROOT_FLAG_LEFTMOST_VALID, ROOT_FLAG_LEFTMOST_VALID);
    try std.testing.expectEqual(rbtree.KNOWN_FLAG_MASK, KNOWN_FLAG_MASK);
    try std.testing.expectEqual(@sizeOf(rbtree.RootView), @sizeOf(RootView));
    try std.testing.expectEqual(@alignOf(rbtree.RootView), @alignOf(RootView));
}

test "phase3 rbtree root view helper keeps constructor and canonicalization relays explicit" {
    const empty_view = empty();
    const uncached_view = uncached(0x2200);
    const cached_view = cached(0x4400, 0x3300);
    const normalized = canonicalize(.{
        .root = 0x2200,
        .cached_leftmost = 0,
        .flags = ROOT_FLAG_CACHED,
    }) orelse return error.TestUnexpectedResult;

    try std.testing.expect(isValid(empty_view));
    try std.testing.expect(isEmpty(empty_view));
    try std.testing.expect(isCanonical(empty_view));
    try std.testing.expect(!hasRoot(empty_view));

    try std.testing.expect(isValid(uncached_view));
    try std.testing.expect(!isEmpty(uncached_view));
    try std.testing.expect(!isCached(uncached_view));
    try std.testing.expect(!hasLeftmost(uncached_view));
    try std.testing.expect(isCanonical(uncached_view));
    try std.testing.expect(hasRoot(uncached_view));

    try std.testing.expect(isValid(cached_view));
    try std.testing.expect(isCached(cached_view));
    try std.testing.expect(hasLeftmost(cached_view));
    try std.testing.expect(isCanonical(cached_view));
    try std.testing.expect(hasRoot(cached_view));

    try std.testing.expectEqual(uncached_view, normalized);
}

test "phase3 rbtree root view helper rejects unknown flags and rootless payloads" {
    const unknown_flags = RootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = ROOT_FLAG_CACHED | ROOT_FLAG_LEFTMOST_VALID | 0x4,
    };
    const rootless_payload = RootView{
        .root = 0,
        .cached_leftmost = 0x0800,
        .flags = ROOT_FLAG_CACHED | ROOT_FLAG_LEFTMOST_VALID,
    };
    const cached_without_leftmost = RootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = ROOT_FLAG_CACHED | ROOT_FLAG_LEFTMOST_VALID,
    };

    try std.testing.expectEqual(@as(?RootView, null), canonicalize(unknown_flags));
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(rootless_payload));
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(cached_without_leftmost));
    try std.testing.expect(!isCanonical(unknown_flags));
    try std.testing.expect(!isCanonical(rootless_payload));
    try std.testing.expect(!isCanonical(cached_without_leftmost));
}
