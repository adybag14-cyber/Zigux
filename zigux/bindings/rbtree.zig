const std = @import("std");

pub const ROOT_FLAG_EMPTY: u32 = 1;
pub const ROOT_FLAG_CACHED: u32 = 2;
pub const ROOT_FLAG_LEFTMOST_VALID: u32 = 4;

pub const KNOWN_FLAG_MASK: u32 =
    ROOT_FLAG_EMPTY |
    ROOT_FLAG_CACHED |
    ROOT_FLAG_LEFTMOST_VALID;

pub const RootView = extern struct {
    root_addr: usize,
    leftmost_addr: usize,
    flags: u32,
    reserved: u32,
};

pub fn empty() RootView {
    return .{
        .root_addr = 0,
        .leftmost_addr = 0,
        .flags = ROOT_FLAG_EMPTY,
        .reserved = 0,
    };
}

pub fn uncached(root_addr: usize) RootView {
    return .{
        .root_addr = root_addr,
        .leftmost_addr = 0,
        .flags = 0,
        .reserved = 0,
    };
}

pub fn cached(root_addr: usize, leftmost_addr: usize) RootView {
    return .{
        .root_addr = root_addr,
        .leftmost_addr = leftmost_addr,
        .flags = ROOT_FLAG_CACHED | ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
}

pub fn isEmpty(view: RootView) bool {
    return (view.flags & ROOT_FLAG_EMPTY) != 0;
}

pub fn isCached(view: RootView) bool {
    return (view.flags & ROOT_FLAG_CACHED) != 0;
}

pub fn hasLeftmost(view: RootView) bool {
    return (view.flags & ROOT_FLAG_LEFTMOST_VALID) != 0;
}

pub fn hasOnlyKnownFlags(view: RootView) bool {
    return (view.flags & ~KNOWN_FLAG_MASK) == 0;
}

pub fn hasRoot(view: RootView) bool {
    return !isEmpty(view) and view.root_addr != 0;
}

pub fn isValid(view: RootView) bool {
    if (!hasOnlyKnownFlags(view)) return false;
    if (view.reserved != 0) return false;
    if (isEmpty(view) and view.root_addr != 0) return false;
    if (!isEmpty(view) and view.root_addr == 0) return false;
    if (hasLeftmost(view) != isCached(view)) return false;
    if (isCached(view) and view.leftmost_addr == 0) return false;
    if (!isCached(view) and view.leftmost_addr != 0) return false;
    return true;
}

pub fn canonicalize(view: RootView) ?RootView {
    if (!isValid(view)) return null;
    if (isEmpty(view)) return empty();
    if (isCached(view)) return cached(view.root_addr, view.leftmost_addr);
    return uncached(view.root_addr);
}

pub fn isCanonical(view: RootView) bool {
    const normalized = canonicalize(view) orelse return false;
    return std.meta.eql(normalized, view);
}

test "phase3 rbtree binding keeps the root view layout stable" {
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2 + 8), @sizeOf(RootView));
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(RootView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(RootView, "root_addr"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(RootView, "leftmost_addr"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(RootView, "flags"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2 + 4), @offsetOf(RootView, "reserved"));
}

test "phase3 rbtree binding keeps direct constructor and canonicalization helpers explicit" {
    try std.testing.expectEqual(@as(u32, 7), KNOWN_FLAG_MASK);

    const empty_view = empty();
    try std.testing.expect(isValid(empty_view));
    try std.testing.expect(isEmpty(empty_view));
    try std.testing.expect(isCanonical(empty_view));
    try std.testing.expect(!hasRoot(empty_view));

    const uncached_view = uncached(0x2200);
    try std.testing.expect(isValid(uncached_view));
    try std.testing.expect(!isEmpty(uncached_view));
    try std.testing.expect(!isCached(uncached_view));
    try std.testing.expect(!hasLeftmost(uncached_view));
    try std.testing.expect(isCanonical(uncached_view));
    try std.testing.expect(hasRoot(uncached_view));

    const cached_view = cached(0x4400, 0x3300);
    try std.testing.expect(isValid(cached_view));
    try std.testing.expect(isCached(cached_view));
    try std.testing.expect(hasLeftmost(cached_view));
    try std.testing.expect(isCanonical(cached_view));
    try std.testing.expect(hasRoot(cached_view));
}

test "phase3 rbtree binding canonicalization rejects drift" {
    const unknown_flag: RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0,
        .flags = 8,
        .reserved = 0,
    };
    try std.testing.expect(!hasOnlyKnownFlags(unknown_flag));
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(unknown_flag));

    const inconsistent_empty: RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0,
        .flags = ROOT_FLAG_EMPTY,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(inconsistent_empty));

    const reserved_bits: RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0x0800,
        .flags = ROOT_FLAG_CACHED | ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 1,
    };
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(reserved_bits));

    const rootless_uncached: RootView = .{
        .root_addr = 0,
        .leftmost_addr = 0,
        .flags = 0,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(rootless_uncached));

    const cached_without_leftmost_flag: RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0x0800,
        .flags = ROOT_FLAG_CACHED,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(cached_without_leftmost_flag));

    const leftmost_without_cached_flag: RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0,
        .flags = ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(leftmost_without_cached_flag));

    const cached_without_root: RootView = .{
        .root_addr = 0,
        .leftmost_addr = 0x0800,
        .flags = ROOT_FLAG_CACHED | ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(cached_without_root));

    const cached_without_leftmost: RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0,
        .flags = ROOT_FLAG_CACHED | ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(cached_without_leftmost));
}
