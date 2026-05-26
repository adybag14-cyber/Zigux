const std = @import("std");
const abi = @import("abi_bindings");

pub const RootView = abi.RbtreeRootView;

pub const ROOT_FLAG_CACHED: u32 = abi.RBTREE_ROOT_VIEW_FLAG_CACHED;
pub const ROOT_FLAG_LEFTMOST_VALID: u32 = abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID;
pub const KNOWN_FLAG_MASK: u32 = ROOT_FLAG_CACHED | ROOT_FLAG_LEFTMOST_VALID;

pub fn empty() RootView {
    return .{
        .root = 0,
        .cached_leftmost = 0,
        .flags = 0,
    };
}

pub fn uncached(root: usize) RootView {
    std.debug.assert(root != 0);
    return .{
        .root = root,
        .cached_leftmost = 0,
        .flags = 0,
    };
}

pub fn cached(root: usize, cached_leftmost: usize) RootView {
    std.debug.assert(root != 0);
    std.debug.assert(cached_leftmost != 0);
    return .{
        .root = root,
        .cached_leftmost = cached_leftmost,
        .flags = ROOT_FLAG_CACHED | ROOT_FLAG_LEFTMOST_VALID,
    };
}

pub fn isEmpty(view: RootView) bool {
    return view.root == 0 and view.cached_leftmost == 0 and view.flags == 0;
}

pub fn isCached(view: RootView) bool {
    return abi.rbtreeRootViewIsCached(view);
}

pub fn hasLeftmost(view: RootView) bool {
    return abi.rbtreeRootViewHasLeftmost(view) and view.cached_leftmost != 0;
}

pub fn hasOnlyKnownFlags(view: RootView) bool {
    return (view.flags & ~KNOWN_FLAG_MASK) == 0;
}

pub fn hasRoot(view: RootView) bool {
    return view.root != 0;
}

pub fn canonicalize(view: RootView) ?RootView {
    if (!hasOnlyKnownFlags(view)) return null;
    if (isEmpty(view)) return view;
    if (!hasRoot(view)) return null;

    const canonical = abi.canonicalizeRbtreeRootView(view);
    if (!abi.rbtreeRootViewIsValid(canonical)) return null;
    return canonical;
}

pub fn isValid(view: RootView) bool {
    return canonicalize(view) != null;
}

pub fn isCanonical(view: RootView) bool {
    const canonical = canonicalize(view) orelse return false;
    return std.meta.eql(canonical, view);
}

test "rbtree root binding keeps the published abi layout visible" {
    try std.testing.expectEqual(@sizeOf(abi.RbtreeRootView), @sizeOf(RootView));
    try std.testing.expectEqual(@alignOf(abi.RbtreeRootView), @alignOf(RootView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(RootView, "root"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(RootView, "cached_leftmost"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(RootView, "flags"));
}

test "rbtree root binding keeps empty uncached and cached constructors explicit" {
    const empty_view = empty();
    const uncached_view = uncached(0x2200);
    const cached_view = cached(0x4400, 0x3300);

    try std.testing.expect(isEmpty(empty_view));
    try std.testing.expect(isValid(empty_view));
    try std.testing.expect(isCanonical(empty_view));

    try std.testing.expect(isValid(uncached_view));
    try std.testing.expect(!isCached(uncached_view));
    try std.testing.expect(!hasLeftmost(uncached_view));
    try std.testing.expect(isCanonical(uncached_view));

    try std.testing.expect(isValid(cached_view));
    try std.testing.expect(isCached(cached_view));
    try std.testing.expect(hasLeftmost(cached_view));
    try std.testing.expect(isCanonical(cached_view));
}

test "rbtree root binding keeps malformed cached-leftmost shapes narrow" {
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
    const uncached_with_cached_flag = RootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = ROOT_FLAG_CACHED,
    };

    try std.testing.expectEqual(@as(?RootView, null), canonicalize(unknown_flags));
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(rootless_payload));
    try std.testing.expectEqual(@as(?RootView, null), canonicalize(cached_without_leftmost));

    const normalized = canonicalize(uncached_with_cached_flag) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(uncached(0x1000), normalized);
    try std.testing.expect(!isCanonical(uncached_with_cached_flag));
}
