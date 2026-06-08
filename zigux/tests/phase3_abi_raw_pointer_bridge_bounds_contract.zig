const std = @import("std");

const abi = @import("abi_bindings");
const narrow = @import("narrow_unsafe");

fn rawPolicy() abi.InteropPolicy {
    return .{
        .panic_mode = abi.PANIC_ABORT,
        .allocator_mode = abi.ALLOC_CALLER_PROVIDED,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
}

fn safePolicy() abi.InteropPolicy {
    return .{
        .panic_mode = abi.PANIC_ABORT,
        .allocator_mode = abi.ALLOC_CALLER_PROVIDED,
        .unsafe_scope = abi.UNSAFE_NONE,
        .reserved = 0,
    };
}

test "phase3 raw pointer bridge rejects denied scopes before pointer materialization" {
    var value: u32 = 0x1020_3040;
    const address = @intFromPtr(&value);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.pointerAtInteropPolicy(u32, address, @sizeOf(u32), safePolicy()),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.pointerAtInteropPolicyBytes(u32, address, @sizeOf(u32), abi.UNSAFE_RAW_POINTER_BRIDGE, 1),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.constPointerAtByte(u32, address, abi.UNSAFE_VOLATILE_MMIO),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.sliceAtByte(u32, address, 1, abi.UNSAFE_NONE),
    );
}

test "phase3 raw pointer bridge rejects short byte coverage" {
    var value: u32 = 0x5566_7788;
    const address = @intFromPtr(&value);

    try std.testing.expectError(
        error.ByteLengthTooSmall,
        narrow.pointerAtByte(u32, address, @sizeOf(u16), abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
    try std.testing.expectError(
        error.ByteLengthTooSmall,
        narrow.readValueAtInteropPolicy(u32, address, @sizeOf(u16), rawPolicy()),
    );
}

test "phase3 raw pointer bridge reports address and length overflow distinctly" {
    const overflowing_address = std.math.maxInt(usize);
    var values = [_]u16{ 3, 5, 8 };
    const address = @intFromPtr(&values[0]);

    try std.testing.expectError(
        error.AddressOverflow,
        narrow.pointerAtByte(u8, overflowing_address, 2, abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
    try std.testing.expectError(
        error.AddressOverflow,
        narrow.readValueAtByte(u8, overflowing_address, 2, abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
    try std.testing.expectError(
        error.LengthOverflow,
        narrow.constSliceAtByte(u16, address, std.math.maxInt(usize), abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
}

test "phase3 raw pointer bridge keeps valid scoped access usable" {
    var values = [_]u32{ 11, 17, 23 };
    const first = @intFromPtr(&values[0]);
    const second = @intFromPtr(&values[1]);

    const ptr = try narrow.pointerAtInteropPolicy(u32, first, @sizeOf(u32), rawPolicy());
    try std.testing.expectEqual(@as(u32, 11), ptr.*);

    const slice = try narrow.sliceAtByte(u32, first, values.len, abi.UNSAFE_RAW_POINTER_BRIDGE);
    try std.testing.expectEqual(@as(usize, values.len), slice.len);
    try std.testing.expectEqual(@as(u32, 17), slice[1]);

    try std.testing.expectEqual(@as(u32, 17), try narrow.readValueAtByte(u32, second, @sizeOf(u32), abi.UNSAFE_RAW_POINTER_BRIDGE));
    try narrow.writeValueAtInteropPolicy(u32, second, 29, rawPolicy());
    try std.testing.expectEqual(@as(u32, 29), values[1]);
    try std.testing.expectEqual(@as(u32, 29), try narrow.exchangeValueAtByte(u32, second, @sizeOf(u32), 31, abi.UNSAFE_RAW_POINTER_BRIDGE));
    try std.testing.expectEqual(@as(u32, 31), values[1]);
}
