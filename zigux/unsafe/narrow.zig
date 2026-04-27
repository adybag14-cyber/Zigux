const std = @import("std");

// Mirror the Phase 3 ABI unsafe-scope tags locally so this helper stays
// self-contained inside the existing narrow unsafe module wiring.
pub const UnsafeScopeTag = enum(u8) {
    none = 0,
    volatile_mmio = 1,
    raw_pointer_bridge = 2,
};

pub fn addressOf(ptr: anytype) usize {
    return @intFromPtr(ptr);
}

pub fn byteOffset(base: usize, offset: usize) usize {
    return base + offset;
}

pub fn permitsVolatileMmio(scope: UnsafeScopeTag) bool {
    return scope == .volatile_mmio;
}

pub fn permitsRawPointerBridge(scope: UnsafeScopeTag) bool {
    return scope == .raw_pointer_bridge;
}

pub fn pointerAt(comptime T: type, base: usize, offset: usize) *volatile T {
    return @ptrFromInt(byteOffset(base, offset));
}

pub fn constSliceAt(comptime T: type, base: usize, len: usize) []const T {
    const ptr: [*]const T = @ptrFromInt(base);
    return ptr[0..len];
}

pub fn constPointerAt(comptime T: type, addr: usize) *const T {
    return @ptrFromInt(addr);
}

test "phase3 narrow unsafe wrappers stay bounded" {
    var value: u32 = 0;
    const base = addressOf(&value);
    const ptr = pointerAt(u32, base, 0);
    ptr.* = 11;
    try std.testing.expectEqual(@as(u32, 11), value);

    const slice = constSliceAt(u32, base, 1);
    try std.testing.expectEqual(@as(u32, 11), slice[0]);

    const const_ptr = constPointerAt(u32, base);
    try std.testing.expectEqual(@as(u32, 11), const_ptr.*);
}

test "phase3 narrow unsafe scope stays explicit" {
    try std.testing.expectEqual(@as(u8, 0), @intFromEnum(UnsafeScopeTag.none));
    try std.testing.expectEqual(@as(u8, 1), @intFromEnum(UnsafeScopeTag.volatile_mmio));
    try std.testing.expectEqual(@as(u8, 2), @intFromEnum(UnsafeScopeTag.raw_pointer_bridge));

    try std.testing.expect(!permitsVolatileMmio(.none));
    try std.testing.expect(permitsVolatileMmio(.volatile_mmio));
    try std.testing.expect(!permitsVolatileMmio(.raw_pointer_bridge));

    try std.testing.expect(!permitsRawPointerBridge(.none));
    try std.testing.expect(!permitsRawPointerBridge(.volatile_mmio));
    try std.testing.expect(permitsRawPointerBridge(.raw_pointer_bridge));
}
