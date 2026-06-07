const std = @import("std");
const abi = @import("abi_bindings");
const narrow = @import("unsafe_narrow");

fn rawPolicy() abi.InteropPolicy {
    return .{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
}

fn mmioPolicy() abi.InteropPolicy {
    return .{
        .panic_mode = abi.PANIC_ABORT,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
}

test "phase3 ABI raw pointer bridge accepts only the dedicated unsafe scope" {
    const policy = rawPolicy();

    try std.testing.expectEqual(@as(?narrow.UnsafeScopeTag, .raw_pointer_bridge), narrow.scopeFromInteropPolicy(policy));
    try std.testing.expectEqual(
        @as(?narrow.AccessBoundary, .raw_pointer_bridge),
        narrow.accessBoundaryFromInteropPolicy(policy),
    );
    try std.testing.expectEqual(@as(?narrow.Surface, .raw_pointer_bridge_only), narrow.surfaceFromInteropPolicy(policy));
    try std.testing.expect(narrow.requiresDedicatedAuditInteropPolicy(policy));
    try std.testing.expect(narrow.permitsRawPointerBridgeInteropPolicy(policy));
    try std.testing.expect(narrow.permitsRawPointerBridgeByte(abi.UNSAFE_RAW_POINTER_BRIDGE));
    try narrow.requireRawPointerBridgeInteropPolicy(policy);

    try std.testing.expectError(error.UnsafeScopeDenied, narrow.requireRawPointerBridgeByte(abi.UNSAFE_NONE));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.requireRawPointerBridgeInteropPolicy(mmioPolicy()));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.requireRawPointerBridgePolicyBytes(abi.UNSAFE_RAW_POINTER_BRIDGE, 1),
    );
}

test "phase3 ABI raw pointer bridge rejects undersized and overflowing spans" {
    var values = [_]u32{ 0x11111111, 0x22222222 };
    const base = @intFromPtr(&values[0]);

    try std.testing.expectError(
        error.ByteLengthTooSmall,
        narrow.pointerAtByte(u32, base, @sizeOf(u16), abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
    try std.testing.expectError(
        error.ByteLengthTooSmall,
        narrow.readValueAtByte(u32, base, @sizeOf(u16), abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
    try std.testing.expectError(
        error.AddressOverflow,
        narrow.constPointerAtByte(u32, std.math.maxInt(usize), abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
    try std.testing.expectError(
        error.LengthOverflow,
        narrow.sliceAtByte(u16, base, (std.math.maxInt(usize) / @sizeOf(u16)) + 1, abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.pointerAtByte(u32, base, @sizeOf(u32), abi.UNSAFE_VOLATILE_MMIO),
    );
}

test "phase3 ABI raw pointer bridge preserves unaligned byte-addressed access" {
    var storage = [_]u8{ 0, 0x34, 0x12, 0, 0 };
    const addr = @intFromPtr(&storage[1]);

    const ptr = try narrow.pointerAtByte(u16, addr, @sizeOf(u16), abi.UNSAFE_RAW_POINTER_BRIDGE);
    try std.testing.expectEqual(@as(u16, 0x1234), ptr.*);

    try narrow.writeValueAtByte(u16, addr, 0xabcd, abi.UNSAFE_RAW_POINTER_BRIDGE);
    try std.testing.expectEqual(@as(u16, 0xabcd), try narrow.readValueAtByte(u16, addr, @sizeOf(u16), abi.UNSAFE_RAW_POINTER_BRIDGE));

    try std.testing.expectEqual(
        @as(u16, 0xabcd),
        try narrow.exchangeValueAtByte(u16, addr, @sizeOf(u16), 0x4567, abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
    try std.testing.expectEqual(@as(u16, 0x4567), ptr.*);
}

test "phase3 ABI raw pointer bridge slices use element counts and policy bytes" {
    var values = [_]u32{ 3, 5, 8, 13 };
    const base = @intFromPtr(&values[0]);

    const policy_slice = try narrow.sliceAtInteropPolicy(u32, base, values.len, rawPolicy());
    try std.testing.expectEqual(@as(usize, values.len), policy_slice.len);
    policy_slice[2] = 21;
    try std.testing.expectEqual(@as(u32, 21), values[2]);

    const byte_slice = try narrow.constSliceAtInteropPolicyBytes(
        u32,
        base,
        values.len,
        abi.UNSAFE_RAW_POINTER_BRIDGE,
        0,
    );
    try std.testing.expectEqual(@as(u32, 13), byte_slice[3]);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.constSliceAtInteropPolicyBytes(u32, base, values.len, abi.UNSAFE_RAW_POINTER_BRIDGE, 1),
    );
}
