const std = @import("std");

pub const UnsafeScopeTag = enum(u8) {
    none = 0,
    volatile_mmio = 1,
    raw_pointer_bridge = 2,
};

pub const ScopeError = error{
    UnsafeScopeDenied,
    MisalignedAccess,
    AddressOverflow,
};

pub fn addressOf(ptr: anytype) usize {
    return @intFromPtr(ptr);
}

pub fn byteOffset(base: usize, offset: usize) usize {
    return checkedByteOffset(base, offset) catch unreachable;
}

pub fn checkedByteOffset(base: usize, offset: usize) ScopeError!usize {
    return std.math.add(usize, base, offset) catch error.AddressOverflow;
}

pub fn checkedSpanBytes(comptime T: type, len: usize) ScopeError!usize {
    return std.math.mul(usize, len, @sizeOf(T)) catch error.AddressOverflow;
}

pub fn checkedSpanEnd(comptime T: type, base: usize, len: usize) ScopeError!usize {
    return checkedByteOffset(base, try checkedSpanBytes(T, len));
}

pub fn isAddressAlignedFor(comptime T: type, addr: usize) bool {
    return addr % @alignOf(T) == 0;
}

pub fn ensureAddressAlignedFor(comptime T: type, addr: usize) ScopeError!void {
    if (!isAddressAlignedFor(T, addr)) {
        return error.MisalignedAccess;
    }
}

pub fn permitsVolatileMmio(scope: UnsafeScopeTag) bool {
    return scope == .volatile_mmio;
}

pub fn permitsRawPointerBridge(scope: UnsafeScopeTag) bool {
    return scope == .raw_pointer_bridge;
}

pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {
    if (reserved != 0) {
        return null;
    }
    return switch (unsafe_scope) {
        @intFromEnum(UnsafeScopeTag.none) => .none,
        @intFromEnum(UnsafeScopeTag.volatile_mmio) => .volatile_mmio,
        @intFromEnum(UnsafeScopeTag.raw_pointer_bridge) => .raw_pointer_bridge,
        else => null,
    };
}

pub fn scopeFromInteropPolicy(policy: anytype) ?UnsafeScopeTag {
    return scopeFromInteropPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn permitsVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return switch (scopeFromInteropPolicyBytes(unsafe_scope, reserved) orelse return false) {
        .volatile_mmio => true,
        else => false,
    };
}

pub fn permitsVolatileMmioPolicy(policy: anytype) bool {
    return permitsVolatileMmioPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return switch (scopeFromInteropPolicyBytes(unsafe_scope, reserved) orelse return false) {
        .raw_pointer_bridge => true,
        else => false,
    };
}

pub fn permitsRawPointerBridgePolicy(policy: anytype) bool {
    return permitsRawPointerBridgePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn recognizesInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) != null;
}

pub fn recognizesInteropPolicy(policy: anytype) bool {
    return scopeFromInteropPolicy(policy) != null;
}

pub fn pointerAt(comptime T: type, scope: UnsafeScopeTag, base: usize, offset: usize) ScopeError!*volatile T {
    return scopedPointerAt(T, scope, base, offset);
}

fn rawConstSliceAt(comptime T: type, base: usize, len: usize) []const T {
    const ptr: [*]const T = @ptrFromInt(base);
    return ptr[0..len];
}

fn rawConstPointerAt(comptime T: type, addr: usize) *const T {
    return @ptrFromInt(addr);
}

fn rawConstValueAt(comptime T: type, addr: usize) T {
    return rawConstPointerAt(T, addr).*;
}

pub fn constSliceAt(comptime T: type, scope: UnsafeScopeTag, base: usize, len: usize) ScopeError![]const T {
    return scopedConstSliceAt(T, scope, base, len);
}

pub fn constPointerAt(comptime T: type, scope: UnsafeScopeTag, addr: usize) ScopeError!*const T {
    return scopedConstPointerAt(T, scope, addr);
}

pub fn constValueAt(comptime T: type, scope: UnsafeScopeTag, addr: usize) ScopeError!T {
    return scopedConstValueAt(T, scope, addr);
}

pub fn scopedPointerAt(comptime T: type, scope: UnsafeScopeTag, base: usize, offset: usize) ScopeError!*volatile T {
    if (!permitsVolatileMmio(scope)) return error.UnsafeScopeDenied;
    const addr = try checkedByteOffset(base, offset);
    try ensureAddressAlignedFor(T, addr);
    return @ptrFromInt(addr);
}

pub fn scopedConstSliceAt(comptime T: type, scope: UnsafeScopeTag, base: usize, len: usize) ScopeError![]const T {
    if (!permitsRawPointerBridge(scope)) return error.UnsafeScopeDenied;
    try ensureAddressAlignedFor(T, base);
    _ = try checkedSpanEnd(T, base, len);
    return rawConstSliceAt(T, base, len);
}

pub fn scopedConstPointerAt(comptime T: type, scope: UnsafeScopeTag, addr: usize) ScopeError!*const T {
    if (!permitsRawPointerBridge(scope)) return error.UnsafeScopeDenied;
    try ensureAddressAlignedFor(T, addr);
    return rawConstPointerAt(T, addr);
}

pub fn scopedConstValueAt(comptime T: type, scope: UnsafeScopeTag, addr: usize) ScopeError!T {
    if (!permitsRawPointerBridge(scope)) return error.UnsafeScopeDenied;
    try ensureAddressAlignedFor(T, addr);
    return rawConstValueAt(T, addr);
}

test "phase3 narrow unsafe wrappers stay bounded" {
    var value: u32 = 0;
    const base = addressOf(&value);
    try std.testing.expectEqual(base + @sizeOf(u32), try checkedByteOffset(base, @sizeOf(u32)));
    const ptr = try pointerAt(u32, .volatile_mmio, base, 0);
    ptr.* = 11;
    try std.testing.expectEqual(@as(u32, 11), value);

    const slice = try constSliceAt(u32, .raw_pointer_bridge, base, 1);
    try std.testing.expectEqual(@as(u32, 11), slice[0]);

    const const_ptr = try constPointerAt(u32, .raw_pointer_bridge, base);
    try std.testing.expectEqual(@as(u32, 11), const_ptr.*);
    try std.testing.expectEqual(@as(u32, 11), try constValueAt(u32, .raw_pointer_bridge, base));
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

test "phase3 narrow unsafe scoped helpers reject misaligned addresses" {
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = addressOf(&bytes[0]);

    try std.testing.expect(isAddressAlignedFor(u16, base));
    try std.testing.expect(!isAddressAlignedFor(u32, base + 1));
    try ensureAddressAlignedFor(u16, base);
    try std.testing.expectError(error.MisalignedAccess, ensureAddressAlignedFor(u32, base + 1));
    try std.testing.expectError(error.MisalignedAccess, scopedPointerAt(u32, .volatile_mmio, base, 1));
    try std.testing.expectError(error.MisalignedAccess, scopedConstSliceAt(u32, .raw_pointer_bridge, base + 1, 1));
    try std.testing.expectError(error.MisalignedAccess, scopedConstPointerAt(u32, .raw_pointer_bridge, base + 1));
    try std.testing.expectError(error.MisalignedAccess, scopedConstValueAt(u32, .raw_pointer_bridge, base + 1));
}

test "phase3 narrow unsafe scoped helpers reject overflowed address math" {
    const max = std.math.maxInt(usize);

    try std.testing.expectError(error.AddressOverflow, checkedByteOffset(max, 1));
    try std.testing.expectError(error.AddressOverflow, checkedSpanBytes(u32, max));
    try std.testing.expectError(error.AddressOverflow, checkedSpanEnd(u32, 4, max));
    try std.testing.expectError(error.AddressOverflow, scopedPointerAt(u32, .volatile_mmio, max, 1));
    try std.testing.expectError(error.AddressOverflow, scopedConstSliceAt(u32, .raw_pointer_bridge, 4, max));
}

test "phase3 narrow unsafe interop policy decoding stays explicit" {
    const mmio_policy = struct {
        unsafe_scope: u8,
        reserved: u8,
    }{
        .unsafe_scope = 1,
        .reserved = 0,
    };
    const raw_pointer_policy = struct {
        unsafe_scope: u8,
        reserved: u8,
    }{
        .unsafe_scope = 2,
        .reserved = 0,
    };
    const invalid_scope_policy = struct {
        unsafe_scope: u8,
        reserved: u8,
    }{
        .unsafe_scope = 9,
        .reserved = 0,
    };
    const reserved_policy = struct {
        unsafe_scope: u8,
        reserved: u8,
    }{
        .unsafe_scope = 0,
        .reserved = 1,
    };

    try std.testing.expectEqual(UnsafeScopeTag.volatile_mmio, scopeFromInteropPolicy(mmio_policy).?);
    try std.testing.expect(recognizesInteropPolicy(mmio_policy));
    try std.testing.expect(permitsVolatileMmioPolicy(mmio_policy));
    try std.testing.expect(!permitsRawPointerBridgePolicy(mmio_policy));
    try std.testing.expectEqual(UnsafeScopeTag.volatile_mmio, scopeFromInteropPolicyBytes(1, 0).?);
    try std.testing.expect(recognizesInteropPolicyBytes(1, 0));
    try std.testing.expect(permitsVolatileMmioPolicyBytes(1, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(1, 0));

    try std.testing.expectEqual(UnsafeScopeTag.raw_pointer_bridge, scopeFromInteropPolicy(raw_pointer_policy).?);
    try std.testing.expect(recognizesInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!permitsVolatileMmioPolicy(raw_pointer_policy));
    try std.testing.expect(permitsRawPointerBridgePolicy(raw_pointer_policy));
    try std.testing.expectEqual(UnsafeScopeTag.raw_pointer_bridge, scopeFromInteropPolicyBytes(2, 0).?);
    try std.testing.expect(recognizesInteropPolicyBytes(2, 0));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(2, 0));
    try std.testing.expect(permitsRawPointerBridgePolicyBytes(2, 0));

    try std.testing.expectEqual(@as(?UnsafeScopeTag, null), scopeFromInteropPolicy(invalid_scope_policy));
    try std.testing.expect(!recognizesInteropPolicy(invalid_scope_policy));
    try std.testing.expect(!permitsVolatileMmioPolicy(invalid_scope_policy));
    try std.testing.expect(!permitsRawPointerBridgePolicy(invalid_scope_policy));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, null), scopeFromInteropPolicyBytes(9, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(9, 0));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(9, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(9, 0));

    try std.testing.expectEqual(@as(?UnsafeScopeTag, null), scopeFromInteropPolicy(reserved_policy));
    try std.testing.expect(!recognizesInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, null), scopeFromInteropPolicyBytes(0, 1));
    try std.testing.expect(!recognizesInteropPolicyBytes(0, 1));
}

test "phase3 scoped unsafe helpers require the declared scope" {
    var value: u32 = 11;
    const base = addressOf(&value);

    try std.testing.expectError(error.UnsafeScopeDenied, pointerAt(u32, .none, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, scopedPointerAt(u32, .none, base, 0));
    const mmio_ptr = try pointerAt(u32, .volatile_mmio, base, 0);
    mmio_ptr.* = 17;
    try std.testing.expectEqual(@as(u32, 17), value);

    try std.testing.expectError(error.UnsafeScopeDenied, constSliceAt(u32, .volatile_mmio, base, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, scopedConstSliceAt(u32, .volatile_mmio, base, 1));
    const raw_slice = try constSliceAt(u32, .raw_pointer_bridge, base, 1);
    try std.testing.expectEqual(@as(u32, 17), raw_slice[0]);

    try std.testing.expectError(error.UnsafeScopeDenied, constPointerAt(u32, .volatile_mmio, base));
    try std.testing.expectError(error.UnsafeScopeDenied, scopedConstPointerAt(u32, .volatile_mmio, base));
    const raw_ptr = try constPointerAt(u32, .raw_pointer_bridge, base);
    try std.testing.expectEqual(@as(u32, 17), raw_ptr.*);
    try std.testing.expectError(error.UnsafeScopeDenied, constValueAt(u32, .volatile_mmio, base));
    try std.testing.expectEqual(@as(u32, 17), try constValueAt(u32, .raw_pointer_bridge, base));

    try std.testing.expectError(error.MisalignedAccess, scopedPointerAt(u32, .volatile_mmio, base, 1));
    try std.testing.expectError(error.MisalignedAccess, scopedConstSliceAt(u32, .raw_pointer_bridge, base + 1, 1));
    try std.testing.expectError(error.MisalignedAccess, scopedConstPointerAt(u32, .raw_pointer_bridge, base + 1));
    try std.testing.expectError(error.MisalignedAccess, scopedConstValueAt(u32, .raw_pointer_bridge, base + 1));
}
