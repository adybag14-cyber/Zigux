const std = @import("std");
const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const panic_policy = @import("panic_policy");
const narrow = @import("narrow");

test "phase3 policy gate relay keeps default caller-safe contract explicit" {
    const policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };

    try std.testing.expectEqual(
        @as(?abi.AllocatorMode, .caller_provided),
        allocator_policy.modeFromInteropPolicy(policy),
    );
    try std.testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(policy));
    try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(policy));

    try std.testing.expect(panic_policy.mustAbortInteropPolicy(policy));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(policy));
    try std.testing.expectEqual(
        @as(?panic_policy.Action, .abort_now),
        panic_policy.actionForInteropPolicy(policy),
    );

    try std.testing.expect(narrow.permitsNoUnsafeInteropPolicy(policy));
    try std.testing.expectEqual(
        @as(?narrow.UnsafeScopeTag, .none),
        narrow.scopeFromInteropPolicy(policy),
    );

    var word: u32 = 31;
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.writeValueAtInteropPolicy(u32, @intFromPtr(&word), 99, policy),
    );
    try std.testing.expectEqual(@as(u32, 31), word);
}

test "phase3 policy gate relay keeps helper-owned raw-bridge contract aligned" {
    const policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };

    try std.testing.expectEqual(
        @as(?abi.AllocatorMode, .kernel_heap),
        allocator_policy.modeFromInteropPolicy(policy),
    );
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(policy));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(policy));

    try std.testing.expect(!panic_policy.mustAbortInteropPolicy(policy));
    try std.testing.expect(panic_policy.canReturnInteropPolicy(policy));
    try std.testing.expectEqual(
        @as(?panic_policy.Action, .warn_and_return),
        panic_policy.actionForInteropPolicy(policy),
    );

    try std.testing.expect(narrow.permitsRawPointerBridgeInteropPolicy(policy));
    try narrow.requireRawPointerBridgeInteropPolicy(policy);
    try std.testing.expectEqual(
        @as(?narrow.UnsafeScopeTag, .raw_pointer_bridge),
        narrow.scopeFromInteropPolicy(policy),
    );

    var bridge_words = [_]u32{ 11, 17 };
    const first_addr = @intFromPtr(&bridge_words[0]);
    const second_addr = @intFromPtr(&bridge_words[1]);

    try narrow.writeValueAtInteropPolicy(u32, second_addr, 23, policy);
    try std.testing.expectEqual(@as(u32, 23), bridge_words[1]);

    const view = try narrow.constSliceAtInteropPolicy(u32, first_addr, bridge_words.len, policy);
    try std.testing.expectEqual(@as(usize, bridge_words.len), view.len);
    try std.testing.expectEqual(@as(u32, 11), view[0]);
    try std.testing.expectEqual(@as(u32, 23), view[1]);
}

test "phase3 policy gate relay fails closed on reserved policy bytes" {
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };

    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(
        @as(?panic_policy.Action, null),
        panic_policy.actionForInteropPolicy(reserved_policy),
    );
    try std.testing.expectEqual(
        @as(?narrow.UnsafeScopeTag, null),
        narrow.scopeFromInteropPolicy(reserved_policy),
    );

    var word: u32 = 5;
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.pointerAtInteropPolicy(u32, @intFromPtr(&word), @sizeOf(u32), reserved_policy),
    );
}
