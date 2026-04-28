const std = @import("std");
const abi = @import("abi_bindings");
const panic_policy = @import("panic_policy");
const allocator_policy = @import("allocator_policy");
const narrow = @import("narrow_unsafe");

test "phase3 policy helpers stay ABI aligned" {
    try std.testing.expectEqual(panic_policy.Action.abort_now, panic_policy.actionFor(.abort));
    try std.testing.expectEqual(panic_policy.Action.bug_check, panic_policy.actionFor(.bug));
    try std.testing.expectEqual(panic_policy.Action.warn_and_return, panic_policy.actionFor(.warn));
    try std.testing.expect(!panic_policy.canReturn(.abort));
    try std.testing.expect(!panic_policy.canReturn(.bug));
    try std.testing.expect(panic_policy.canReturn(.warn));

    try std.testing.expectEqual(allocator_policy.InitFlow.caller_prepared, allocator_policy.initFlowFor(.caller_provided));
    try std.testing.expectEqual(allocator_policy.InitFlow.helper_owned, allocator_policy.initFlowFor(.kernel_heap));
    try std.testing.expectEqual(allocator_policy.InitFlow.helper_owned_with_reset, allocator_policy.initFlowFor(.arena));
    try std.testing.expect(allocator_policy.requiresExplicitCaller(.caller_provided));
    try std.testing.expect(!allocator_policy.permitsGlobalFallback(.caller_provided));
    try std.testing.expect(allocator_policy.permitsGlobalFallback(.kernel_heap));
    try std.testing.expect(allocator_policy.requiresResetOnInit(.arena));
}

test "phase3 policy layout stays explicit at the ABI boundary" {
    comptime {
        if (@sizeOf(abi.InteropPolicy) != 4) {
            @compileError("InteropPolicy size drifted");
        }
        if (@offsetOf(abi.InteropPolicy, "panic_mode") != 0) {
            @compileError("InteropPolicy.panic_mode offset drifted");
        }
        if (@offsetOf(abi.InteropPolicy, "allocator_mode") != 1) {
            @compileError("InteropPolicy.allocator_mode offset drifted");
        }
        if (@offsetOf(abi.InteropPolicy, "unsafe_scope") != 2) {
            @compileError("InteropPolicy.unsafe_scope offset drifted");
        }
        if (@offsetOf(abi.InteropPolicy, "reserved") != 3) {
            @compileError("InteropPolicy.reserved offset drifted");
        }
    }

    const policy: abi.InteropPolicy = .{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    try std.testing.expectEqual(@intFromEnum(abi.PanicMode.warn), policy.panic_mode);
    try std.testing.expectEqual(@intFromEnum(abi.AllocatorMode.arena), policy.allocator_mode);
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge), policy.unsafe_scope);
}

test "phase3 narrow unsafe helpers stay explicit" {
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.none), @intFromEnum(narrow.UnsafeScopeTag.none));
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.volatile_mmio), @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio));
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge), @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge));

    try std.testing.expect(!narrow.permitsVolatileMmio(.none));
    try std.testing.expect(narrow.permitsVolatileMmio(.volatile_mmio));
    try std.testing.expect(!narrow.permitsVolatileMmio(.raw_pointer_bridge));

    try std.testing.expect(!narrow.permitsRawPointerBridge(.none));
    try std.testing.expect(!narrow.permitsRawPointerBridge(.volatile_mmio));
    try std.testing.expect(narrow.permitsRawPointerBridge(.raw_pointer_bridge));

    var words = [_]u32{ 7, 11 };
    const base = narrow.addressOf(&words[0]);
    try std.testing.expectEqual(base + @sizeOf(u32), narrow.byteOffset(base, @sizeOf(u32)));
    try std.testing.expectEqual(@as(u32, 7), narrow.constSliceAt(u32, base, words.len)[0]);
    try std.testing.expectEqual(@as(u32, 11), narrow.constPointerAt(u32, base + @sizeOf(u32)).*);
}

test "phase3 policy gate decodes interop-policy unsafe bytes explicitly" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const invalid_scope_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = 9,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 1,
    };

    try std.testing.expectEqual(narrow.UnsafeScopeTag.volatile_mmio, narrow.scopeFromInteropPolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved).?);
    try std.testing.expect(narrow.recognizesInteropPolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved));
    try std.testing.expect(narrow.permitsVolatileMmioPolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved));
    try std.testing.expect(!narrow.permitsRawPointerBridgePolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved));

    try std.testing.expectEqual(narrow.UnsafeScopeTag.raw_pointer_bridge, narrow.scopeFromInteropPolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved).?);
    try std.testing.expect(narrow.recognizesInteropPolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved));
    try std.testing.expect(!narrow.permitsVolatileMmioPolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved));
    try std.testing.expect(narrow.permitsRawPointerBridgePolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved));

    try std.testing.expectEqual(@as(?narrow.UnsafeScopeTag, null), narrow.scopeFromInteropPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));
    try std.testing.expect(!narrow.recognizesInteropPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));
    try std.testing.expect(!narrow.permitsVolatileMmioPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));
    try std.testing.expect(!narrow.permitsRawPointerBridgePolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));

    try std.testing.expectEqual(@as(?narrow.UnsafeScopeTag, null), narrow.scopeFromInteropPolicyBytes(reserved_policy.unsafe_scope, reserved_policy.reserved));
    try std.testing.expect(!narrow.recognizesInteropPolicyBytes(reserved_policy.unsafe_scope, reserved_policy.reserved));
}

test "phase3 policy gate enforces the declared unsafe scope" {
    var value: u32 = 11;
    const base = narrow.addressOf(&value);

    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedPointerAt(u32, .none, base, 0));
    const mmio_ptr = try narrow.scopedPointerAt(u32, .volatile_mmio, base, 0);
    mmio_ptr.* = 17;
    try std.testing.expectEqual(@as(u32, 17), value);

    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstSliceAt(u32, .volatile_mmio, base, 1));
    const raw_slice = try narrow.scopedConstSliceAt(u32, .raw_pointer_bridge, base, 1);
    try std.testing.expectEqual(@as(u32, 17), raw_slice[0]);

    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstPointerAt(u32, .volatile_mmio, base));
    const raw_ptr = try narrow.scopedConstPointerAt(u32, .raw_pointer_bridge, base);
    try std.testing.expectEqual(@as(u32, 17), raw_ptr.*);
}
