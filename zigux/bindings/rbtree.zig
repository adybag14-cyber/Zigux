const std = @import("std");

pub const ROOT_FLAG_EMPTY: u32 = 1;
pub const ROOT_FLAG_CACHED: u32 = 2;
pub const ROOT_FLAG_LEFTMOST_VALID: u32 = 4;

pub const RootView = extern struct {
    root_addr: usize,
    leftmost_addr: usize,
    flags: u32,
    reserved: u32,
};

pub fn isEmpty(view: RootView) bool {
    return (view.flags & ROOT_FLAG_EMPTY) != 0;
}

pub fn isCached(view: RootView) bool {
    return (view.flags & ROOT_FLAG_CACHED) != 0;
}

pub fn hasLeftmost(view: RootView) bool {
    return (view.flags & ROOT_FLAG_LEFTMOST_VALID) != 0;
}

pub fn isValid(view: RootView) bool {
    if (view.reserved != 0) return false;
    if (isEmpty(view) and view.root_addr != 0) return false;
    if (!isCached(view) and view.leftmost_addr != 0) return false;
    if (!hasLeftmost(view) and view.leftmost_addr != 0) return false;
    return true;
}

test "phase3 rbtree binding keeps the root view layout stable" {
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2 + 8), @sizeOf(RootView));
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(RootView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(RootView, "root_addr"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(RootView, "leftmost_addr"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(RootView, "flags"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2 + 4), @offsetOf(RootView, "reserved"));
}

test "phase3 rbtree binding keeps root flags explicit" {
    const empty: RootView = .{
        .root_addr = 0,
        .leftmost_addr = 0,
        .flags = ROOT_FLAG_EMPTY,
        .reserved = 0,
    };
    try std.testing.expect(isValid(empty));
    try std.testing.expect(isEmpty(empty));
    try std.testing.expect(!isCached(empty));
    try std.testing.expect(!hasLeftmost(empty));

    const cached: RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0x1000,
        .flags = ROOT_FLAG_CACHED | ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expect(isValid(cached));
    try std.testing.expect(!isEmpty(cached));
    try std.testing.expect(isCached(cached));
    try std.testing.expect(hasLeftmost(cached));

    const invalid_uncached_leftmost: RootView = .{
        .root_addr = 0x1000,
        .leftmost_addr = 0x1000,
        .flags = ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expect(!isValid(invalid_uncached_leftmost));
}
