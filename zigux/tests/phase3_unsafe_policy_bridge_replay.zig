const std = @import("std");

const abi = @import("abi_bindings");
const narrow = @import("narrow");
const unsafe_policy = @import("unsafe_policy");

test "phase3 unsafe-policy bridge replay keeps raw-pointer policy bytes aligned with narrow" {
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), unsafe_policy.scopeFromByte(2));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), unsafe_policy.scopeFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), unsafe_policy.scopeFromByte(0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.scopeFromByte(9));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.scopeFromInteropPolicyBytes(2, 1));

    try std.testing.expect(unsafe_policy.permitsRawPointerBridgeByte(2));
    try std.testing.expect(!unsafe_policy.permitsRawPointerBridgeByte(1));
    try std.testing.expect(unsafe_policy.allowsRawPointerBridgePolicyBytes(2, 0));
    try std.testing.expect(!unsafe_policy.allowsRawPointerBridgePolicyBytes(1, 0));
    try std.testing.expect(!unsafe_policy.allowsRawPointerBridgePolicyBytes(2, 1));

    try std.testing.expect(narrow.permitsRawPointerBridge(.raw_pointer_bridge));
    try std.testing.expect(!narrow.permitsRawPointerBridge(.volatile_mmio));
    try std.testing.expectEqual(
        @as(?narrow.AccessBoundary, .raw_pointer_bridge),
        narrow.accessBoundaryFromInteropPolicyBytes(2, 0),
    );
    try std.testing.expectEqual(@as(?narrow.AccessBoundary, null), narrow.accessBoundaryFromInteropPolicyBytes(2, 1));

    try unsafe_policy.requireRawPointerBridgePolicyBytes(2, 0);
    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgePolicyBytes(1, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgePolicyBytes(2, 1));
}

test "phase3 unsafe-policy bridge replay keeps interop-policy records explicit" {
    const raw_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_BUG,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 1,
    };

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), unsafe_policy.scopeFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), unsafe_policy.scopeFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.scopeFromInteropPolicy(reserved_policy));

    try std.testing.expect(unsafe_policy.permitsRawPointerBridgeInteropPolicy(raw_policy));
    try std.testing.expect(unsafe_policy.allowsRawPointerBridgeInteropPolicy(raw_policy));
    try std.testing.expect(!unsafe_policy.permitsRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expect(!unsafe_policy.allowsRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expect(!unsafe_policy.permitsRawPointerBridgeInteropPolicy(reserved_policy));
    try std.testing.expect(!unsafe_policy.allowsRawPointerBridgeInteropPolicy(reserved_policy));

    try std.testing.expectEqual(@as(?narrow.Surface, .raw_pointer_bridge_only), narrow.surfaceFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?narrow.Surface, .mmio_only), narrow.surfaceFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?narrow.Surface, null), narrow.surfaceFromInteropPolicy(reserved_policy));

    try unsafe_policy.requireRawPointerBridgeInteropPolicy(raw_policy);
    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgeInteropPolicy(reserved_policy));
}

test "phase3 unsafe-policy bridge replay keeps helper gating aligned with raw-pointer bridge access" {
    const raw_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
    const denied_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_ABORT,
        .allocator_mode = abi.ALLOC_CALLER_PROVIDED,
        .unsafe_scope = abi.UNSAFE_NONE,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 1,
    };

    var words = [_]u32{ 0x0102_0304, 0x1122_3344, 0x5566_7788 };
    const base_addr = @intFromPtr(&words[0]);
    const second_addr = @intFromPtr(&words[1]);

    const raw_ptr = try narrow.pointerAtInteropPolicyBytes(
        u32,
        base_addr,
        @sizeOf(u32),
        raw_policy.unsafe_scope,
        raw_policy.reserved,
    );
    try std.testing.expectEqual(@as(u32, 0x0102_0304), raw_ptr.*);

    const raw_const_ptr = try narrow.constPointerAtInteropPolicy(u32, second_addr, raw_policy);
    try std.testing.expectEqual(@as(u32, 0x1122_3344), raw_const_ptr.*);

    const raw_slice = try narrow.sliceAtInteropPolicy(u32, base_addr, words.len, raw_policy);
    raw_slice[2] = 0xAABB_CCDD;
    try std.testing.expectEqual(@as(u32, 0xAABB_CCDD), words[2]);

    const raw_const_slice = try narrow.constSliceAtInteropPolicyBytes(
        u32,
        base_addr,
        words.len,
        raw_policy.unsafe_scope,
        raw_policy.reserved,
    );
    try std.testing.expectEqual(@as(u32, 0xAABB_CCDD), raw_const_slice[2]);

    try narrow.writeValueAtInteropPolicy(u32, second_addr, 0xDEAD_BEEF, raw_policy);
    try std.testing.expectEqual(@as(u32, 0xDEAD_BEEF), words[1]);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.pointerAtInteropPolicy(u32, base_addr, @sizeOf(u32), denied_policy),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.constPointerAtInteropPolicy(u32, base_addr, reserved_policy),
    );
    try std.testing.expectError(
        error.ByteLengthTooSmall,
        narrow.pointerAtInteropPolicyBytes(
            u32,
            base_addr,
            @sizeOf(u16),
            raw_policy.unsafe_scope,
            raw_policy.reserved,
        ),
    );
}
