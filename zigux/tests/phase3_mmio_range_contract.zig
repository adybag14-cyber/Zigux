const std = @import("std");

const AccessError = error{
    InvalidInteropPolicy,
    UnsafeScopeDenied,
};

const Scope = enum(u8) {
    none = 0,
    volatile_mmio = 1,
    raw_pointer_bridge = 2,
};

const Policy = extern struct {
    panic_mode: u8,
    allocator_mode: u8,
    unsafe_scope: u8,
    reserved: u8,
};

const MmioWindow = extern struct {
    base_addr: usize,
    length: u32,
    stride: u32,
};

fn scopeFromPolicy(policy: Policy) AccessError!Scope {
    if (policy.reserved != 0) return error.InvalidInteropPolicy;
    return switch (policy.unsafe_scope) {
        @intFromEnum(Scope.none) => .none,
        @intFromEnum(Scope.volatile_mmio) => .volatile_mmio,
        @intFromEnum(Scope.raw_pointer_bridge) => .raw_pointer_bridge,
        else => error.InvalidInteropPolicy,
    };
}

fn requireMmioPolicy(policy: Policy) AccessError!void {
    switch (try scopeFromPolicy(policy)) {
        .volatile_mmio => {},
        .none, .raw_pointer_bridge => return error.UnsafeScopeDenied,
    }
}

fn windowEnd(base_addr: usize, length: u32) AccessError!usize {
    if (length == 0) return base_addr;
    return std.math.add(usize, base_addr, @as(usize, @intCast(length)) - 1) catch error.InvalidInteropPolicy;
}

fn windowContainsAccess(window: MmioWindow, byte_offset: usize, byte_len: usize) bool {
    const access_end = std.math.add(usize, byte_offset, byte_len) catch return false;
    return access_end <= @as(usize, @intCast(window.length));
}

fn strideAllowsOffset(window: MmioWindow, byte_offset: usize) bool {
    const stride: usize = @intCast(window.stride);
    return stride == 0 or byte_offset % stride == 0;
}

fn requireAccess(comptime T: type, window: MmioWindow, byte_offset: usize) AccessError!void {
    if (byte_offset % @alignOf(T) != 0) return error.InvalidInteropPolicy;
    if (!strideAllowsOffset(window, byte_offset)) return error.InvalidInteropPolicy;
    if (!windowContainsAccess(window, byte_offset, @sizeOf(T))) return error.InvalidInteropPolicy;
}

test "phase3 mmio range contract accepts only volatile-mmio policy windows" {
    const good = Policy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(Scope.volatile_mmio),
        .reserved = 0,
    };
    const none = Policy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(Scope.none),
        .reserved = 0,
    };
    const raw = Policy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(Scope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved = Policy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(Scope.volatile_mmio),
        .reserved = 1,
    };

    try requireMmioPolicy(good);
    try std.testing.expectError(error.UnsafeScopeDenied, requireMmioPolicy(none));
    try std.testing.expectError(error.UnsafeScopeDenied, requireMmioPolicy(raw));
    try std.testing.expectError(error.InvalidInteropPolicy, requireMmioPolicy(reserved));
}

test "phase3 mmio range contract keeps access width inside the blessed window" {
    const strided = MmioWindow{
        .base_addr = 0x1000,
        .length = 16,
        .stride = 4,
    };
    const packed_window = MmioWindow{
        .base_addr = 0x2000,
        .length = 12,
        .stride = 0,
    };

    try std.testing.expectEqual(@as(usize, 0x100f), try windowEnd(strided.base_addr, strided.length));
    try requireAccess(u8, strided, 0);
    try requireAccess(u16, strided, 4);
    try requireAccess(u32, strided, 8);
    try requireAccess(u16, packed_window, 6);

    try std.testing.expectError(error.InvalidInteropPolicy, requireAccess(u16, strided, 2));
    try std.testing.expectError(error.InvalidInteropPolicy, requireAccess(u32, strided, 6));
    try std.testing.expectError(error.InvalidInteropPolicy, requireAccess(u32, strided, 13));
    try std.testing.expectError(error.InvalidInteropPolicy, requireAccess(u64, packed_window, 8));
    try std.testing.expect(!windowContainsAccess(strided, std.math.maxInt(usize), 4));
}

test "phase3 mmio range contract rejects address overflow before blessing access" {
    try std.testing.expectEqual(@as(usize, 0x10), try windowEnd(0x10, 0));
    try std.testing.expectError(error.InvalidInteropPolicy, windowEnd(std.math.maxInt(usize), 2));
}
