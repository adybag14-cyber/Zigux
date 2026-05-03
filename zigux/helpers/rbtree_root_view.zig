const std = @import("std");
const rbtree = @import("rbtree_bindings");

pub const KNOWN_FLAG_MASK: u32 =
    rbtree.ROOT_FLAG_EMPTY |
    rbtree.ROOT_FLAG_CACHED |
    rbtree.ROOT_FLAG_LEFTMOST_VALID;

pub fn empty() rbtree.RootView {
    return .{
        .root_addr = 0,
        .leftmost_addr = 0,
        .flags = rbtree.ROOT_FLAG_EMPTY,
        .reserved = 0,
    };
}

pub fn uncached(root_addr: usize) rbtree.RootView {
    return .{
        .root_addr = root_addr,
        .leftmost_addr = 0,
        .flags = 0,
        .reserved = 0,
    };
}

pub fn cached(root_addr: usize, leftmost_addr: usize) rbtree.RootView {
    return .{
        .root_addr = root_addr,
        .leftmost_addr = leftmost_addr,
        .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
}

pub fn hasOnlyKnownFlags(view: rbtree.RootView) bool {
    return (view.flags & ~KNOWN_FLAG_MASK) == 0;
}

pub fn hasRoot(view: rbtree.RootView) bool {
    return !rbtree.isEmpty(view) and view.root_addr != 0;
}

pub fn canonicalize(view: rbtree.RootView) ?rbtree.RootView {
    if (!hasOnlyKnownFlags(view)) return null;
    if (!rbtree.isValid(view)) return null;
    if (rbtree.isEmpty(view)) return empty();
    if (rbtree.isCached(view)) return cached(view.root_addr, view.leftmost_addr);
    return uncached(view.root_addr);
}

pub fn isCanonical(view: rbtree.RootView) bool {
    const normalized = canonicalize(view) orelse return false;
    return std.meta.eql(normalized, view);
}

test "phase3 rbtree root view constructors stay canonical" {
    const empty_view = empty();
    try std.testing.expect(rbtree.isValid(empty_view));
    try std.testing.expect(rbtree.isEmpty(empty_view));
    try std.testing.expect(isCanonical(empty_view));
    try std.testing.expect(!hasRoot(empty_view));

    const uncached_view = uncached(0x2200);
    try std.testing.expect(rbtree.isValid(uncached_view));
    try std.testing.expect(!rbtree.isEmpty(uncached_view));
    try std.testing.expect(!rbtree.isCached(uncached_view));
    try std.testing.expect(!rbtree.hasLeftmost(uncached_view));
    try std.testing.expect(isCanonical(uncached_view));
    try std.testing.expect(hasRoot(uncached_view));

    const cached_view = cached(0x4400, 0x3300);
    try std.testing.expect(rbtree.isValid(cached_view));
    try std.testing.expect(rbtree.isCached(cached_view));
    try std.testing.expect(rbtree.hasLeftmost(cached_view));
    try std.testing.expect(isCanonical(cached_view));
    try std.testing.expect(hasRoot(cached_view));
}

test "phase3 rbtree root view canonicalization rejects drift" {
    const unknown_flag: rbtree.RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0,
        .flags = 8,
        .reserved = 0,
    };
    try std.testing.expect(!hasOnlyKnownFlags(unknown_flag));
    try std.testing.expectEqual(@as(?rbtree.RootView, null), canonicalize(unknown_flag));

    const inconsistent_empty: rbtree.RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0,
        .flags = rbtree.ROOT_FLAG_EMPTY,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(?rbtree.RootView, null), canonicalize(inconsistent_empty));

    const reserved_bits: rbtree.RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0x0800,
        .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 1,
    };
    try std.testing.expectEqual(@as(?rbtree.RootView, null), canonicalize(reserved_bits));
}
