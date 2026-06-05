const std = @import("std");
const abi = @import("abi_bindings");
const unsafe_policy = @import("unsafe_policy");

fn policyWithUnsafeScope(scope: u8, reserved: u8) abi.InteropPolicy {
    return .{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = scope,
        .reserved = reserved,
    };
}

test "unsafe policy ABI byte decoding rejects reserved and unknown scope bytes" {
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), unsafe_policy.modeFromByte(abi.UNSAFE_NONE));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), unsafe_policy.modeFromByte(abi.UNSAFE_VOLATILE_MMIO));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), unsafe_policy.modeFromByte(abi.UNSAFE_RAW_POINTER_BRIDGE));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.modeFromByte(9));

    try std.testing.expect(unsafe_policy.recognizesByte(abi.UNSAFE_NONE));
    try std.testing.expect(unsafe_policy.recognizesByte(abi.UNSAFE_VOLATILE_MMIO));
    try std.testing.expect(unsafe_policy.recognizesByte(abi.UNSAFE_RAW_POINTER_BRIDGE));
    try std.testing.expect(!unsafe_policy.recognizesByte(9));

    try std.testing.expectEqual(
        @as(?abi.UnsafeScope, .raw_pointer_bridge),
        unsafe_policy.modeFromInteropPolicyBytes(abi.UNSAFE_RAW_POINTER_BRIDGE, 0),
    );
    try std.testing.expectEqual(
        @as(?abi.UnsafeScope, null),
        unsafe_policy.modeFromInteropPolicyBytes(abi.UNSAFE_RAW_POINTER_BRIDGE, 1),
    );
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.modeFromInteropPolicyBytes(9, 0));

    const raw = policyWithUnsafeScope(abi.UNSAFE_RAW_POINTER_BRIDGE, 0);
    const reserved = policyWithUnsafeScope(abi.UNSAFE_RAW_POINTER_BRIDGE, 1);
    const unknown = policyWithUnsafeScope(9, 0);

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), unsafe_policy.modeFromInteropPolicy(raw));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.modeFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.modeFromInteropPolicy(unknown));
    try std.testing.expect(unsafe_policy.recognizesInteropPolicy(raw));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicy(reserved));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicy(unknown));
}

test "unsafe policy ABI byte routing keeps safe mmio and raw surfaces distinct" {
    try std.testing.expectEqual(unsafe_policy.AccessBoundary.typed_safe, unsafe_policy.accessBoundaryFromByte(abi.UNSAFE_NONE).?);
    try std.testing.expectEqual(unsafe_policy.AccessBoundary.volatile_mmio_window, unsafe_policy.accessBoundaryFromByte(abi.UNSAFE_VOLATILE_MMIO).?);
    try std.testing.expectEqual(unsafe_policy.AccessBoundary.raw_pointer_bridge, unsafe_policy.accessBoundaryFromByte(abi.UNSAFE_RAW_POINTER_BRIDGE).?);
    try std.testing.expectEqual(@as(?unsafe_policy.AccessBoundary, null), unsafe_policy.accessBoundaryFromByte(9));
    try std.testing.expectEqual(
        @as(?unsafe_policy.AccessBoundary, null),
        unsafe_policy.accessBoundaryFromInteropPolicyBytes(abi.UNSAFE_RAW_POINTER_BRIDGE, 1),
    );

    try std.testing.expectEqual(unsafe_policy.Surface.safe_only, unsafe_policy.surfaceFromByte(abi.UNSAFE_NONE).?);
    try std.testing.expectEqual(unsafe_policy.Surface.mmio_only, unsafe_policy.surfaceFromByte(abi.UNSAFE_VOLATILE_MMIO).?);
    try std.testing.expectEqual(unsafe_policy.Surface.raw_pointer_bridge_only, unsafe_policy.surfaceFromByte(abi.UNSAFE_RAW_POINTER_BRIDGE).?);
    try std.testing.expectEqual(@as(?unsafe_policy.Surface, null), unsafe_policy.surfaceFromByte(9));

    try std.testing.expect(unsafe_policy.permitsNoUnsafeByte(abi.UNSAFE_NONE));
    try std.testing.expect(!unsafe_policy.permitsNoUnsafeByte(abi.UNSAFE_VOLATILE_MMIO));
    try std.testing.expect(!unsafe_policy.permitsNoUnsafeByte(abi.UNSAFE_RAW_POINTER_BRIDGE));

    try std.testing.expect(!unsafe_policy.permitsVolatileMmioByte(abi.UNSAFE_NONE));
    try std.testing.expect(unsafe_policy.permitsVolatileMmioByte(abi.UNSAFE_VOLATILE_MMIO));
    try std.testing.expect(!unsafe_policy.permitsVolatileMmioByte(abi.UNSAFE_RAW_POINTER_BRIDGE));

    try std.testing.expect(!unsafe_policy.permitsRawPointerBridgeByte(abi.UNSAFE_NONE));
    try std.testing.expect(!unsafe_policy.permitsRawPointerBridgeByte(abi.UNSAFE_VOLATILE_MMIO));
    try std.testing.expect(unsafe_policy.permitsRawPointerBridgeByte(abi.UNSAFE_RAW_POINTER_BRIDGE));
}

test "unsafe policy ABI byte guards fail closed for denied and reserved scopes" {
    const safe = policyWithUnsafeScope(abi.UNSAFE_NONE, 0);
    const mmio = policyWithUnsafeScope(abi.UNSAFE_VOLATILE_MMIO, 0);
    const raw = policyWithUnsafeScope(abi.UNSAFE_RAW_POINTER_BRIDGE, 0);
    const reserved_raw = policyWithUnsafeScope(abi.UNSAFE_RAW_POINTER_BRIDGE, 1);

    try std.testing.expect(!unsafe_policy.isUnsafeByte(abi.UNSAFE_NONE));
    try std.testing.expect(unsafe_policy.isUnsafeByte(abi.UNSAFE_VOLATILE_MMIO));
    try std.testing.expect(unsafe_policy.isUnsafeByte(abi.UNSAFE_RAW_POINTER_BRIDGE));
    try std.testing.expect(!unsafe_policy.isUnsafeByte(9));
    try std.testing.expect(!unsafe_policy.isUnsafeInteropPolicy(safe));
    try std.testing.expect(unsafe_policy.isUnsafeInteropPolicy(mmio));
    try std.testing.expect(unsafe_policy.isUnsafeInteropPolicy(raw));
    try std.testing.expect(!unsafe_policy.isUnsafeInteropPolicy(reserved_raw));

    try std.testing.expect(!unsafe_policy.requiresDedicatedAuditByte(abi.UNSAFE_NONE));
    try std.testing.expect(unsafe_policy.requiresDedicatedAuditByte(abi.UNSAFE_VOLATILE_MMIO));
    try std.testing.expect(unsafe_policy.requiresDedicatedAuditByte(abi.UNSAFE_RAW_POINTER_BRIDGE));
    try std.testing.expect(!unsafe_policy.requiresDedicatedAuditByte(9));
    try std.testing.expect(!unsafe_policy.requiresDedicatedAuditInteropPolicy(safe));
    try std.testing.expect(unsafe_policy.requiresDedicatedAuditInteropPolicy(mmio));
    try std.testing.expect(unsafe_policy.requiresDedicatedAuditInteropPolicy(raw));
    try std.testing.expect(!unsafe_policy.requiresDedicatedAuditInteropPolicy(reserved_raw));

    try unsafe_policy.requireNoUnsafeByte(abi.UNSAFE_NONE);
    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireNoUnsafeByte(abi.UNSAFE_VOLATILE_MMIO));
    try unsafe_policy.requireVolatileMmioByte(abi.UNSAFE_VOLATILE_MMIO);
    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireVolatileMmioByte(abi.UNSAFE_RAW_POINTER_BRIDGE));
    try unsafe_policy.requireRawPointerBridgeByte(abi.UNSAFE_RAW_POINTER_BRIDGE);
    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgeByte(abi.UNSAFE_VOLATILE_MMIO));

    try unsafe_policy.requireNoUnsafePolicyBytes(abi.UNSAFE_NONE, 0);
    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireNoUnsafePolicyBytes(abi.UNSAFE_NONE, 1));
    try unsafe_policy.requireVolatileMmioPolicyBytes(abi.UNSAFE_VOLATILE_MMIO, 0);
    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireVolatileMmioPolicyBytes(abi.UNSAFE_VOLATILE_MMIO, 1));
    try unsafe_policy.requireRawPointerBridgePolicyBytes(abi.UNSAFE_RAW_POINTER_BRIDGE, 0);
    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgePolicyBytes(abi.UNSAFE_RAW_POINTER_BRIDGE, 1));
}
