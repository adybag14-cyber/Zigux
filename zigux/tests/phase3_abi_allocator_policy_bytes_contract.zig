const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");

test "phase3 allocator policy rejects reserved interop-policy bytes before mode routing" {
    const valid_arena = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
    const reserved_arena = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 1,
    };

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(valid_arena));
    try std.testing.expectEqual(@as(?allocator_policy.InitFlow, .helper_owned_with_reset), allocator_policy.initFlowFromInteropPolicy(valid_arena));
    try std.testing.expectEqual(@as(?allocator_policy.Ownership, .helper_managed_resettable), allocator_policy.ownershipFromInteropPolicy(valid_arena));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved_arena));
    try std.testing.expectEqual(@as(?allocator_policy.InitFlow, null), allocator_policy.initFlowFromInteropPolicy(reserved_arena));
    try std.testing.expectEqual(@as(?allocator_policy.Ownership, null), allocator_policy.ownershipFromInteropPolicy(reserved_arena));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicy(reserved_arena));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicyBytes(abi.ALLOC_ARENA, 1));
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        allocator_policy.requireInitFlowPolicyBytes(abi.ALLOC_ARENA, 1, .helper_owned_with_reset),
    );
}

test "phase3 allocator policy rejects invalid allocator mode bytes without widening fallback behavior" {
    const unknown_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_ABORT,
        .allocator_mode = 9,
        .unsafe_scope = abi.UNSAFE_NONE,
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromByte(9));
    try std.testing.expectEqual(@as(?allocator_policy.InitFlow, null), allocator_policy.initFlowFromByte(9));
    try std.testing.expectEqual(@as(?allocator_policy.Ownership, null), allocator_policy.ownershipFromByte(9));
    try std.testing.expect(!allocator_policy.recognizesByte(9));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerByte(9));
    try std.testing.expect(!allocator_policy.permitsGlobalFallbackByte(9));
    try std.testing.expect(!allocator_policy.initializesOwnedStateByte(9));
    try std.testing.expect(!allocator_policy.requiresResetOnInitByte(9));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?allocator_policy.InitFlow, null), allocator_policy.initFlowFromInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?allocator_policy.Ownership, null), allocator_policy.ownershipFromInteropPolicy(unknown_policy));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicy(unknown_policy));
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        allocator_policy.requireInitFlowByte(9, .caller_prepared),
    );
}

test "phase3 allocator policy keeps ABI allocator bytes aligned with init ownership routing" {
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromByte(abi.ALLOC_ARENA));

    try std.testing.expectEqual(@as(?allocator_policy.InitFlow, .caller_prepared), allocator_policy.initFlowFromByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expectEqual(@as(?allocator_policy.InitFlow, .helper_owned), allocator_policy.initFlowFromByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expectEqual(@as(?allocator_policy.InitFlow, .helper_owned_with_reset), allocator_policy.initFlowFromByte(abi.ALLOC_ARENA));

    try std.testing.expectEqual(@as(?allocator_policy.Ownership, .caller_managed), allocator_policy.ownershipFromByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expectEqual(@as(?allocator_policy.Ownership, .helper_managed), allocator_policy.ownershipFromByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expectEqual(@as(?allocator_policy.Ownership, .helper_managed_resettable), allocator_policy.ownershipFromByte(abi.ALLOC_ARENA));

    try std.testing.expect(allocator_policy.requiresExplicitCallerByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerByte(abi.ALLOC_ARENA));

    try std.testing.expect(!allocator_policy.permitsGlobalFallbackByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackByte(abi.ALLOC_ARENA));

    try std.testing.expect(!allocator_policy.initializesOwnedStateByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expect(allocator_policy.initializesOwnedStateByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expect(allocator_policy.initializesOwnedStateByte(abi.ALLOC_ARENA));

    try std.testing.expect(!allocator_policy.requiresResetOnInitByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expect(!allocator_policy.requiresResetOnInitByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expect(allocator_policy.requiresResetOnInitByte(abi.ALLOC_ARENA));
}
