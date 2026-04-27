const std = @import("std");
const abi = @import("abi_bindings");

pub fn addressOf(ptr: anytype) usize {
    return @intFromPtr(ptr);
}

pub fn byteOffset(base: usize, offset: usize) usize {
    return base + offset;
}

pub fn permitsVolatileMmio(scope: abi.UnsafeScope) bool {
    return scope == .volatile_mmio;
}

pub fn permitsRawPointerBridge(scope: abi.UnsafeScope) bool {
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
    try std.testing.expect(!permitsVolatileMmio(.none));
    try std.testing.expect(permitsVolatileMmio(.volatile_mmio));
    try std.testing.expect(!permitsVolatileMmio(.raw_pointer_bridge));

    try std.testing.expect(!permitsRawPointerBridge(.none));
    try std.testing.expect(!permitsRawPointerBridge(.volatile_mmio));
    try std.testing.expect(permitsRawPointerBridge(.raw_pointer_bridge));
}
