const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");

const caller_byte: u8 = abi.ALLOC_CALLER_PROVIDED;
const heap_byte: u8 = abi.ALLOC_KERNEL_HEAP;
const arena_byte: u8 = abi.ALLOC_ARENA;
const unknown_byte: u8 = 9;

fn policyFor(allocator_mode: u8, reserved: u8) abi.InteropPolicy {
    return .{
        .panic_mode = 2,
        .allocator_mode = allocator_mode,
        .unsafe_scope = 1,
        .reserved = reserved,
    };
}

test "allocator policy byte decoders stay aligned with ABI constants" {
    try testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromByte(caller_byte));
    try testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromByte(heap_byte));
    try testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromByte(arena_byte));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromByte(unknown_byte));

    try testing.expectEqual(@as(?allocator_policy.InitFlow, .caller_prepared), allocator_policy.initFlowFromByte(caller_byte));
    try testing.expectEqual(@as(?allocator_policy.InitFlow, .helper_owned), allocator_policy.initFlowFromByte(heap_byte));
    try testing.expectEqual(@as(?allocator_policy.InitFlow, .helper_owned_with_reset), allocator_policy.initFlowFromByte(arena_byte));
    try testing.expectEqual(@as(?allocator_policy.InitFlow, null), allocator_policy.initFlowFromByte(unknown_byte));

    try testing.expectEqual(@as(?allocator_policy.Ownership, .caller_managed), allocator_policy.ownershipFromByte(caller_byte));
    try testing.expectEqual(@as(?allocator_policy.Ownership, .helper_managed), allocator_policy.ownershipFromByte(heap_byte));
    try testing.expectEqual(@as(?allocator_policy.Ownership, .helper_managed_resettable), allocator_policy.ownershipFromByte(arena_byte));
    try testing.expectEqual(@as(?allocator_policy.Ownership, null), allocator_policy.ownershipFromByte(unknown_byte));
}

test "allocator policy keeps caller fallback and reset semantics byte-addressable" {
    try testing.expect(allocator_policy.recognizesByte(caller_byte));
    try testing.expect(allocator_policy.recognizesByte(heap_byte));
    try testing.expect(allocator_policy.recognizesByte(arena_byte));
    try testing.expect(!allocator_policy.recognizesByte(unknown_byte));

    try testing.expect(allocator_policy.requiresExplicitCallerByte(caller_byte));
    try testing.expect(!allocator_policy.requiresExplicitCallerByte(heap_byte));
    try testing.expect(!allocator_policy.requiresExplicitCallerByte(arena_byte));
    try testing.expect(!allocator_policy.requiresExplicitCallerByte(unknown_byte));

    try testing.expect(!allocator_policy.permitsGlobalFallbackByte(caller_byte));
    try testing.expect(allocator_policy.permitsGlobalFallbackByte(heap_byte));
    try testing.expect(allocator_policy.permitsGlobalFallbackByte(arena_byte));
    try testing.expect(!allocator_policy.permitsGlobalFallbackByte(unknown_byte));

    try testing.expect(!allocator_policy.initializesOwnedStateByte(caller_byte));
    try testing.expect(allocator_policy.initializesOwnedStateByte(heap_byte));
    try testing.expect(allocator_policy.initializesOwnedStateByte(arena_byte));
    try testing.expect(!allocator_policy.initializesOwnedStateByte(unknown_byte));

    try testing.expect(!allocator_policy.requiresResetOnInitByte(caller_byte));
    try testing.expect(!allocator_policy.requiresResetOnInitByte(heap_byte));
    try testing.expect(allocator_policy.requiresResetOnInitByte(arena_byte));
    try testing.expect(!allocator_policy.requiresResetOnInitByte(unknown_byte));
}

test "allocator policy fails closed when the reserved interop byte is set" {
    const reserved_arena = policyFor(arena_byte, 1);
    const clear_arena = policyFor(arena_byte, 0);

    try testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(clear_arena));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved_arena));
    try testing.expectEqual(@as(?allocator_policy.InitFlow, null), allocator_policy.initFlowFromInteropPolicy(reserved_arena));
    try testing.expectEqual(@as(?allocator_policy.Ownership, null), allocator_policy.ownershipFromInteropPolicy(reserved_arena));

    try testing.expect(!allocator_policy.recognizesInteropPolicy(reserved_arena));
    try testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(reserved_arena));
    try testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(reserved_arena));
    try testing.expect(!allocator_policy.initializesOwnedStateInteropPolicy(reserved_arena));
    try testing.expect(!allocator_policy.requiresResetOnInitInteropPolicy(reserved_arena));
}

test "allocator policy require helpers distinguish invalid bytes from flow drift" {
    try allocator_policy.requireInitFlow(.caller_provided, .caller_prepared);
    try allocator_policy.requireInitFlowByte(heap_byte, .helper_owned);
    try allocator_policy.requireInitFlowByte(arena_byte, .helper_owned_with_reset);
    try allocator_policy.requireInitFlowPolicyBytes(caller_byte, 0, .caller_prepared);
    try allocator_policy.requireInitFlowInteropPolicy(policyFor(heap_byte, 0), .helper_owned);

    try testing.expectError(
        error.UnexpectedInitFlow,
        allocator_policy.requireInitFlow(.kernel_heap, .caller_prepared),
    );
    try testing.expectError(
        error.UnexpectedInitFlow,
        allocator_policy.requireInitFlowByte(arena_byte, .helper_owned),
    );
    try testing.expectError(
        error.InvalidInteropPolicy,
        allocator_policy.requireInitFlowByte(unknown_byte, .helper_owned),
    );
    try testing.expectError(
        error.InvalidInteropPolicy,
        allocator_policy.requireInitFlowPolicyBytes(arena_byte, 1, .helper_owned_with_reset),
    );
}
