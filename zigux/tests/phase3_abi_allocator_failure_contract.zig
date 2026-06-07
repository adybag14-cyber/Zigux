const std = @import("std");
const allocator_policy = @import("allocator_policy");
const abi = @import("abi_bindings");

fn policy(allocator_mode: u8, reserved: u8) abi.InteropPolicy {
    return .{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = allocator_mode,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = reserved,
    };
}

test "allocator failure contract keeps valid modes explicit" {
    const caller = policy(@intFromEnum(abi.AllocatorMode.caller_provided), 0);
    const heap = policy(@intFromEnum(abi.AllocatorMode.kernel_heap), 0);
    const arena = policy(@intFromEnum(abi.AllocatorMode.arena), 0);

    try std.testing.expectEqual(@as(?allocator_policy.InitFlow, .caller_prepared), allocator_policy.initFlowFromInteropPolicy(caller));
    try std.testing.expectEqual(@as(?allocator_policy.InitFlow, .helper_owned), allocator_policy.initFlowFromInteropPolicy(heap));
    try std.testing.expectEqual(@as(?allocator_policy.InitFlow, .helper_owned_with_reset), allocator_policy.initFlowFromInteropPolicy(arena));

    try std.testing.expectEqual(@as(?allocator_policy.Ownership, .caller_managed), allocator_policy.ownershipFromInteropPolicy(caller));
    try std.testing.expectEqual(@as(?allocator_policy.Ownership, .helper_managed), allocator_policy.ownershipFromInteropPolicy(heap));
    try std.testing.expectEqual(@as(?allocator_policy.Ownership, .helper_managed_resettable), allocator_policy.ownershipFromInteropPolicy(arena));

    try std.testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(caller));
    try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(caller));
    try std.testing.expect(!allocator_policy.initializesOwnedStateInteropPolicy(caller));
    try std.testing.expect(!allocator_policy.requiresResetOnInitInteropPolicy(caller));

    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(heap));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(heap));
    try std.testing.expect(allocator_policy.initializesOwnedStateInteropPolicy(heap));
    try std.testing.expect(!allocator_policy.requiresResetOnInitInteropPolicy(heap));

    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(arena));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(arena));
    try std.testing.expect(allocator_policy.initializesOwnedStateInteropPolicy(arena));
    try std.testing.expect(allocator_policy.requiresResetOnInitInteropPolicy(arena));
}

test "allocator failure contract rejects unknown allocator bytes without partial success" {
    const unknown_modes = [_]u8{ 3, 9, 0xff };

    for (unknown_modes) |mode| {
        const unknown = policy(mode, 0);

        try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(unknown));
        try std.testing.expectEqual(@as(?allocator_policy.InitFlow, null), allocator_policy.initFlowFromInteropPolicy(unknown));
        try std.testing.expectEqual(@as(?allocator_policy.Ownership, null), allocator_policy.ownershipFromInteropPolicy(unknown));
        try std.testing.expect(!allocator_policy.recognizesInteropPolicy(unknown));
        try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(unknown));
        try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(unknown));
        try std.testing.expect(!allocator_policy.initializesOwnedStateInteropPolicy(unknown));
        try std.testing.expect(!allocator_policy.requiresResetOnInitInteropPolicy(unknown));
    }
}

test "allocator failure contract rejects reserved policy bytes before mode handling" {
    const valid_modes = [_]u8{
        @intFromEnum(abi.AllocatorMode.caller_provided),
        @intFromEnum(abi.AllocatorMode.kernel_heap),
        @intFromEnum(abi.AllocatorMode.arena),
    };

    for (valid_modes) |mode| {
        const reserved = policy(mode, 1);

        try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved));
        try std.testing.expectEqual(@as(?allocator_policy.InitFlow, null), allocator_policy.initFlowFromInteropPolicy(reserved));
        try std.testing.expectEqual(@as(?allocator_policy.Ownership, null), allocator_policy.ownershipFromInteropPolicy(reserved));
        try std.testing.expect(!allocator_policy.recognizesInteropPolicy(reserved));
        try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(reserved));
        try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(reserved));
        try std.testing.expect(!allocator_policy.initializesOwnedStateInteropPolicy(reserved));
        try std.testing.expect(!allocator_policy.requiresResetOnInitInteropPolicy(reserved));
    }
}

test "allocator failure contract distinguishes invalid policy from flow mismatch" {
    const heap = policy(@intFromEnum(abi.AllocatorMode.kernel_heap), 0);
    const arena = policy(@intFromEnum(abi.AllocatorMode.arena), 0);
    const unknown = policy(0xfe, 0);
    const reserved_arena = policy(@intFromEnum(abi.AllocatorMode.arena), 7);

    try allocator_policy.requireInitFlowInteropPolicy(heap, .helper_owned);
    try allocator_policy.requireInitFlowInteropPolicy(arena, .helper_owned_with_reset);

    try std.testing.expectError(
        error.UnexpectedInitFlow,
        allocator_policy.requireInitFlowInteropPolicy(heap, .caller_prepared),
    );
    try std.testing.expectError(
        error.UnexpectedInitFlow,
        allocator_policy.requireInitFlowInteropPolicy(arena, .helper_owned),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        allocator_policy.requireInitFlowInteropPolicy(unknown, .helper_owned),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        allocator_policy.requireInitFlowInteropPolicy(reserved_arena, .helper_owned_with_reset),
    );
}
