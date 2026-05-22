const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const panic_policy = @import("panic_policy");
const unsafe_policy = @import("unsafe_policy");

test "phase3 abi keeps raw-pointer bridge gate helpers and init-flow relays explicit" {
    const safe_policy = abi.defaultInteropPolicy();
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const raw_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_raw_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };

    const safe_mode = allocator_policy.modeFromInteropPolicy(safe_policy) orelse return error.TestUnexpectedResult;
    const mmio_mode = allocator_policy.modeFromInteropPolicy(mmio_policy) orelse return error.TestUnexpectedResult;
    const raw_mode = allocator_policy.modeFromInteropPolicy(raw_policy) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(allocator_policy.InitFlow.caller_prepared, allocator_policy.initFlowFor(safe_mode));
    try std.testing.expectEqual(allocator_policy.InitFlow.helper_owned, allocator_policy.initFlowFor(mmio_mode));
    try std.testing.expectEqual(allocator_policy.InitFlow.helper_owned_with_reset, allocator_policy.initFlowFor(raw_mode));

    try std.testing.expectEqual(@as(?panic_policy.Escalation, .immediate_abort), panic_policy.escalationFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .kernel_bug), panic_policy.escalationFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .warning_only), panic_policy.escalationFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, null), panic_policy.escalationFromInteropPolicy(reserved_raw_policy));

    const safe_scope = unsafe_policy.scopeFromInteropPolicy(safe_policy) orelse return error.TestUnexpectedResult;
    const mmio_scope = unsafe_policy.scopeFromInteropPolicy(mmio_policy) orelse return error.TestUnexpectedResult;
    const raw_scope = unsafe_policy.scopeFromInteropPolicy(raw_policy) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), unsafe_policy.scopeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), unsafe_policy.scopeFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), unsafe_policy.scopeFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.scopeFromInteropPolicy(reserved_raw_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), unsafe_policy.scopeFromByte(abi.UNSAFE_RAW_POINTER_BRIDGE));

    try std.testing.expect(!unsafe_policy.permitsRawPointerBridge(safe_scope));
    try std.testing.expect(!unsafe_policy.permitsRawPointerBridge(mmio_scope));
    try std.testing.expect(unsafe_policy.permitsRawPointerBridge(raw_scope));

    try std.testing.expect(!unsafe_policy.allowsRawPointerBridgeInteropPolicy(safe_policy));
    try std.testing.expect(unsafe_policy.allowsRawPointerBridgeInteropPolicy(raw_policy));
    try std.testing.expect(!unsafe_policy.allowsRawPointerBridgeInteropPolicy(reserved_raw_policy));

    try std.testing.expect(!unsafe_policy.permitsRawPointerBridgeInteropPolicy(safe_policy));
    try std.testing.expect(unsafe_policy.permitsRawPointerBridgeInteropPolicy(raw_policy));
    try std.testing.expect(!unsafe_policy.permitsRawPointerBridgeInteropPolicy(reserved_raw_policy));

    try std.testing.expect(!unsafe_policy.allowsRawPointerBridgePolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved));
    try std.testing.expect(unsafe_policy.allowsRawPointerBridgePolicyBytes(raw_policy.unsafe_scope, raw_policy.reserved));
    try std.testing.expect(!unsafe_policy.allowsRawPointerBridgePolicyBytes(reserved_raw_policy.unsafe_scope, reserved_raw_policy.reserved));

    try std.testing.expect(!unsafe_policy.permitsRawPointerBridgeByte(mmio_policy.unsafe_scope));
    try std.testing.expect(unsafe_policy.permitsRawPointerBridgeByte(raw_policy.unsafe_scope));

    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgeInteropPolicy(safe_policy));
    try unsafe_policy.requireRawPointerBridgeInteropPolicy(raw_policy);
    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgeInteropPolicy(reserved_raw_policy));

    try std.testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgePolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved));
    try unsafe_policy.requireRawPointerBridgePolicyBytes(raw_policy.unsafe_scope, raw_policy.reserved);
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        unsafe_policy.requireRawPointerBridgePolicyBytes(reserved_raw_policy.unsafe_scope, reserved_raw_policy.reserved),
    );
}
