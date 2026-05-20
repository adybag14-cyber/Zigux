const std = @import("std");
const rbtree = @import("rbtree_bindings");

pub const RootView = rbtree.RootView;
pub const ROOT_FLAG_EMPTY = rbtree.ROOT_FLAG_EMPTY;
pub const ROOT_FLAG_CACHED = rbtree.ROOT_FLAG_CACHED;
pub const ROOT_FLAG_LEFTMOST_VALID = rbtree.ROOT_FLAG_LEFTMOST_VALID;
pub const KNOWN_FLAG_MASK = rbtree.KNOWN_FLAG_MASK;

pub fn empty() RootView {
    return rbtree.empty();
}

pub fn uncached(root_addr: usize) RootView {
    return rbtree.uncached(root_addr);
}

pub fn cached(root_addr: usize, leftmost_addr: usize) RootView {
    return rbtree.cached(root_addr, leftmost_addr);
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
    try std.testing.expectEqual(rbtree.ROOT_FLAG_EMPTY, ROOT_FLAG_EMPTY);
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
}

test "phase3 rbtree root view helper rejects the same drift as the dedicated binding" {
    const reserved_bits: RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0x0800,
        .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 1,
    };
    const rootless_uncached: RootView = .{
        .root_addr = 0,
        .leftmost_addr = 0,
        .flags = 0,
        .reserved = 0,
    };
    const cached_without_leftmost: RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0,
        .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?RootView, null), canonicalize(reserved_bits));
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(rootless_uncached));
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(cached_without_leftmost));
    try std.testing.expect(!isCanonical(reserved_bits));
    try std.testing.expect(!isCanonical(rootless_uncached));
    try std.testing.expect(!isCanonical(cached_without_leftmost));
}
