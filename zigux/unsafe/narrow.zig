const std = @import("std");

pub const UnsafeScopeTag = enum(u8) {
    none = 0,
    volatile_mmio = 1,
    raw_pointer_bridge = 2,
};

pub fn addressOf(ptr: anytype) usize {
    return @intFromPtr(ptr);
}

pub fn byteOffset(base: usize, offset: usize) usize {
    return std.math.add(usize, base, offset) catch @panic("phase3 narrow unsafe byte offset overflow");
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

pub fn writeValueAt(comptime T: type, addr: usize, value: T) void {
    const ptr: *T = @ptrFromInt(addr);
    ptr.* = value;
}

pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {
    if (reserved != 0) return null;
    return switch (unsafe_scope) {
        @intFromEnum(UnsafeScopeTag.none) => .none,
        @intFromEnum(UnsafeScopeTag.volatile_mmio) => .volatile_mmio,
        @intFromEnum(UnsafeScopeTag.raw_pointer_bridge) => .raw_pointer_bridge,
        else => null,
    };
}

pub fn recognizesInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) != null;
}

pub fn permitsNoUnsafePolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) == .none;
}

pub fn permitsVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) == .volatile_mmio;
}

pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) == .raw_pointer_bridge;
}

test "phase3 narrow unsafe wrappers stay bounded" {
    try std.testing.expectEqual(@as(usize, 12), byteOffset(9, 3));
    try std.testing.expectEqual(std.math.maxInt(usize), byteOffset(std.math.maxInt(usize) - 4, 4));

    var value: u32 = 0;
    const base = addressOf(&value);
    const ptr = pointerAt(u32, base, 0);
    ptr.* = 11;
    try std.testing.expectEqual(@as(u32, 11), value);

    const slice = constSliceAt(u32, base, 1);
    try std.testing.expectEqual(@as(u32, 11), slice[0]);

    const const_ptr = constPointerAt(u32, base);
    try std.testing.expectEqual(@as(u32, 11), const_ptr.*);

    writeValueAt(u32, base, 19);
    try std.testing.expectEqual(@as(u32, 19), value);
}

test "phase3 narrow unsafe scope bytes stay explicit" {
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .none), scopeFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .volatile_mmio), scopeFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .raw_pointer_bridge), scopeFromInteropPolicyBytes(2, 0));

    try std.testing.expect(recognizesInteropPolicyBytes(0, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(1, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(2, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(9, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(1, 1));

    try std.testing.expect(permitsNoUnsafePolicyBytes(0, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(1, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(2, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(9, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(0, 1));

    try std.testing.expect(!permitsVolatileMmioPolicyBytes(0, 0));
    try std.testing.expect(permitsVolatileMmioPolicyBytes(1, 0));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(2, 0));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(9, 0));

    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(0, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(1, 0));
    try std.testing.expect(permitsRawPointerBridgePolicyBytes(2, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(2, 1));
}
