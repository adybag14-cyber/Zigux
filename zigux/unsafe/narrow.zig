const std = @import("std");

// Mirror the Phase 3 ABI unsafe-scope tags locally so this helper stays
// self-contained inside the existing narrow unsafe module wiring.
pub const UnsafeScopeTag = enum(u8) {
    none = 0,
    volatile_mmio = 1,
    raw_pointer_bridge = 2,
};

pub const ScopeError = error{
    UnsafeScopeDenied,
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

pub fn scopedPointerAt(comptime T: type, scope: UnsafeScopeTag, base: usize, offset: usize) ScopeError!*volatile T {
    if (!permitsVolatileMmio(scope)) return error.UnsafeScopeDenied;
    return pointerAt(T, base, offset);
}

pub fn scopedConstSliceAt(comptime T: type, scope: UnsafeScopeTag, base: usize, len: usize) ScopeError![]const T {
    if (!permitsRawPointerBridge(scope)) return error.UnsafeScopeDenied;
    return constSliceAt(T, base, len);
}

pub fn scopedConstPointerAt(comptime T: type, scope: UnsafeScopeTag, addr: usize) ScopeError!*const T {
    if (!permitsRawPointerBridge(scope)) return error.UnsafeScopeDenied;
    return constPointerAt(T, addr);
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

test "phase3 scoped unsafe helpers require the declared scope" {
    var value: u32 = 11;
    const base = addressOf(&value);

    try std.testing.expectError(error.UnsafeScopeDenied, scopedPointerAt(u32, .none, base, 0));
    const mmio_ptr = try scopedPointerAt(u32, .volatile_mmio, base, 0);
    mmio_ptr.* = 17;
    try std.testing.expectEqual(@as(u32, 17), value);

    try std.testing.expectError(error.UnsafeScopeDenied, scopedConstSliceAt(u32, .volatile_mmio, base, 1));
    const raw_slice = try scopedConstSliceAt(u32, .raw_pointer_bridge, base, 1);
    try std.testing.expectEqual(@as(u32, 17), raw_slice[0]);

    try std.testing.expectError(error.UnsafeScopeDenied, scopedConstPointerAt(u32, .volatile_mmio, base));
    const raw_ptr = try scopedConstPointerAt(u32, .raw_pointer_bridge, base);
    try std.testing.expectEqual(@as(u32, 17), raw_ptr.*);
}
