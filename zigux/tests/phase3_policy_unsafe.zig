const std = @import("std");
const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert");
const panic_policy = @import("panic_policy");
const allocator_policy = @import("allocator_policy");
const mmio = @import("mmio_helpers");
const narrow = @import("narrow_unsafe");

test "phase3 focused policy and unsafe replay keeps layout and policy bytes explicit" {
    comptime {
        layout_assert.assertInteropPolicyLayout();
        layout_assert.assertMmioRangeLayout();
        layout_assert.assertRbtreeRootViewLayout();
    }

    const raw_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const no_unsafe_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };

    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, .warn_and_return), panic_policy.actionForInteropPolicy(raw_policy));
    try std.testing.expect(panic_policy.canReturnInteropPolicy(raw_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(reserved_policy));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromInteropPolicy(raw_policy));
    try std.testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(raw_policy));
    try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(raw_policy));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(mmio_policy));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicy(reserved_policy));

    try std.testing.expectEqual(@as(?narrow.UnsafeScopeTag, .raw_pointer_bridge), narrow.scopeFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?narrow.UnsafeScopeTag, .volatile_mmio), narrow.scopeFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?narrow.UnsafeScopeTag, .none), narrow.scopeFromInteropPolicy(no_unsafe_policy));
    try std.testing.expect(narrow.permitsRawPointerBridgeInteropPolicy(raw_policy));
    try std.testing.expect(!narrow.permitsRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expect(!narrow.recognizesInteropPolicy(reserved_policy));
}

test "phase3 focused policy and unsafe replay keeps narrow writes and mmio gates bounded" {
    var values = [_]u32{ 11, 22, 33 };
    const base = narrow.addressOf(&values[0]);
    const third_addr = narrow.byteOffset(base, @sizeOf(u32) * 2);

    const raw_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const no_unsafe_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };

    const scoped_ptr = try narrow.pointerAtInteropPolicy(u32, base, @sizeOf(u32), raw_policy);
    scoped_ptr.* = 44;
    try std.testing.expectEqual(@as(u32, 44), values[1]);

    const scoped_slice = try narrow.constSliceAtInteropPolicy(u32, base, values.len, raw_policy);
    try std.testing.expectEqual(@as(u32, 44), scoped_slice[1]);

    const scoped_const_ptr = try narrow.constPointerAtInteropPolicyBytes(
        u32,
        third_addr,
        @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        0,
    );
    try std.testing.expectEqual(@as(u32, 33), scoped_const_ptr.*);

    try narrow.writeValueAtInteropPolicy(u32, base, 55, raw_policy);
    try std.testing.expectEqual(@as(u32, 55), values[0]);
    try narrow.writeValueAtInteropPolicyBytes(
        u32,
        third_addr,
        66,
        @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        0,
    );
    try std.testing.expectEqual(@as(u32, 66), values[2]);

    try std.testing.expectError(error.UnsafeScopeDenied, narrow.pointerAtInteropPolicy(u32, base, 0, mmio_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.constSliceAtInteropPolicy(u32, base, values.len, no_unsafe_policy));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.constPointerAtInteropPolicyBytes(u32, third_addr, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 1),
    );
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.writeValueAtInteropPolicy(u32, base, 77, reserved_policy));

    var mmio_bytes = [_]u8{0} ** 16;
    const mmio_base = narrow.addressOf(&mmio_bytes[0]);
    const mmio_range = try mmio.rangeInteropPolicy(mmio_base, 16, 4, mmio_policy);
    try std.testing.expectEqual(mmio_base, mmio_range.base_addr);
    try std.testing.expectEqual(@as(u32, 16), mmio_range.length);
    try std.testing.expectEqual(@as(u32, 4), mmio_range.stride);

    try mmio.write8InteropPolicyBytes(mmio_base, 1, 0x44, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0);
    try std.testing.expectEqual(
        @as(u8, 0x44),
        try mmio.read8InteropPolicyBytes(mmio_base, 1, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0),
    );
    try mmio.write32InteropPolicyByte(mmio_base, 4, 0xc001_d00d, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(
        @as(u32, 0xc001_d00d),
        try mmio.read32InteropPolicyByte(mmio_base, 4, @intFromEnum(abi.UnsafeScope.volatile_mmio)),
    );

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8InteropPolicyBytes(mmio_base, 1, 1, 1));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.read32InteropPolicyByte(mmio_base, 4, @intFromEnum(abi.UnsafeScope.none)),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.write32InteropPolicyByte(mmio_base, 4, 0, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge)),
    );
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64InteropPolicyBytes(mmio_base, 8, 0, 0, 0));
}
