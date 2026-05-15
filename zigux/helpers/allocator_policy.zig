const std = @import("std");
const abi = @import("abi_bindings");

pub const InitFlow = enum {
    caller_prepared,
    helper_owned,
    helper_owned_with_reset,
};

pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.AllocatorMode {
    const decoded = abi.decodeInteropPolicyBytes(@intFromEnum(abi.PanicMode.abort), mode, @intFromEnum(abi.UnsafeScope.none), reserved) orelse return null;
    return decoded.allocator_mode;
}

pub fn modeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.AllocatorMode {
    return (abi.decodeInteropPolicy(policy) orelse return null).allocator_mode;
}

pub fn modeFromByte(mode: u8) ?abi.AllocatorMode {
    return modeFromInteropPolicyBytes(mode, 0);
}

pub fn recognizesInteropPolicyBytes(mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(mode, reserved) != null;
}

pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {
    return modeFromInteropPolicy(policy) != null;
}

pub fn recognizesByte(mode: u8) bool {
    return recognizesInteropPolicyBytes(mode, 0);
}

pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {
    return switch (mode) {
        .caller_provided => .caller_prepared,
        .kernel_heap => .helper_owned,
        .arena => .helper_owned_with_reset,
    };
}

pub fn requiresExplicitCaller(mode: abi.AllocatorMode) bool {
    return mode == .caller_provided;
}

pub fn requiresExplicitCallerPolicyBytes(mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(mode, reserved) == .caller_provided;
}

pub fn requiresExplicitCallerInteropPolicy(policy: abi.InteropPolicy) bool {
    return requiresExplicitCallerPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn requiresExplicitCallerByte(mode: u8) bool {
    return requiresExplicitCallerPolicyBytes(mode, 0);
}

pub fn usesKernelHeap(mode: abi.AllocatorMode) bool {
    return mode == .kernel_heap;
}

pub fn usesKernelHeapPolicyBytes(mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(mode, reserved) == .kernel_heap;
}

pub fn usesKernelHeapInteropPolicy(policy: abi.InteropPolicy) bool {
    return usesKernelHeapPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn usesKernelHeapByte(mode: u8) bool {
    return usesKernelHeapPolicyBytes(mode, 0);
}

pub fn usesArena(mode: abi.AllocatorMode) bool {
    return mode == .arena;
}

pub fn usesArenaPolicyBytes(mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(mode, reserved) == .arena;
}

pub fn usesArenaInteropPolicy(policy: abi.InteropPolicy) bool {
    return usesArenaPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn usesArenaByte(mode: u8) bool {
    return usesArenaPolicyBytes(mode, 0);
}

pub fn permitsGlobalFallback(mode: abi.AllocatorMode) bool {
    return usesKernelHeap(mode) or usesArena(mode);
}

pub fn permitsGlobalFallbackPolicyBytes(mode: u8, reserved: u8) bool {
    const resolved = modeFromInteropPolicyBytes(mode, reserved) orelse return false;
    return usesKernelHeap(resolved) or usesArena(resolved);
}

pub fn permitsGlobalFallbackInteropPolicy(policy: abi.InteropPolicy) bool {
    return permitsGlobalFallbackPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn permitsGlobalFallbackByte(mode: u8) bool {
    return permitsGlobalFallbackPolicyBytes(mode, 0);
}

pub fn initializesOwnedState(mode: abi.AllocatorMode) bool {
    return switch (initFlowFor(mode)) {
        .caller_prepared => false,
        .helper_owned, .helper_owned_with_reset => true,
    };
}

pub fn initializesOwnedStatePolicyBytes(mode: u8, reserved: u8) bool {
    return initializesOwnedState(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn initializesOwnedStateInteropPolicy(policy: abi.InteropPolicy) bool {
    return initializesOwnedStatePolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn initializesOwnedStateByte(mode: u8) bool {
    return initializesOwnedStatePolicyBytes(mode, 0);
}

pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {
    return initFlowFor(mode) == .helper_owned_with_reset;
}

pub fn requiresResetOnInitPolicyBytes(mode: u8, reserved: u8) bool {
    return requiresResetOnInit(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn requiresResetOnInitInteropPolicy(policy: abi.InteropPolicy) bool {
    return requiresResetOnInitPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn requiresResetOnInitByte(mode: u8) bool {
    return requiresResetOnInitPolicyBytes(mode, 0);
}

test "phase3 allocator policy keeps init ownership explicit" {
    try std.testing.expectEqual(InitFlow.caller_prepared, initFlowFor(.caller_provided));
    try std.testing.expectEqual(InitFlow.helper_owned, initFlowFor(.kernel_heap));
    try std.testing.expectEqual(InitFlow.helper_owned_with_reset, initFlowFor(.arena));

    try std.testing.expect(!initializesOwnedState(.caller_provided));
    try std.testing.expect(initializesOwnedState(.kernel_heap));
    try std.testing.expect(initializesOwnedState(.arena));

    try std.testing.expect(!requiresResetOnInit(.caller_provided));
    try std.testing.expect(!requiresResetOnInit(.kernel_heap));
    try std.testing.expect(requiresResetOnInit(.arena));
}

test "phase3 allocator policy stays explicit" {
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromByte(9));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), modeFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), modeFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), modeFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicyBytes(2, 1));

    try std.testing.expect(recognizesInteropPolicyBytes(0, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(1, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(2, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(9, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(2, 1));

    try std.testing.expect(recognizesByte(0));
    try std.testing.expect(recognizesByte(1));
    try std.testing.expect(recognizesByte(2));
    try std.testing.expect(!recognizesByte(9));

    const caller_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const heap_policy = abi.InteropPolicy{
        .panic_mode = 1,
        .allocator_mode = 1,
        .unsafe_scope = 1,
        .reserved = 0,
    };
    const arena_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 2,
        .unsafe_scope = 2,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 2,
        .unsafe_scope = 2,
        .reserved = 1,
    };
    const unknown_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 9,
        .unsafe_scope = 0,
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), modeFromInteropPolicy(caller_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), modeFromInteropPolicy(heap_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), modeFromInteropPolicy(arena_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicy(reserved_policy));

    try std.testing.expect(recognizesInteropPolicy(caller_policy));
    try std.testing.expect(recognizesInteropPolicy(heap_policy));
    try std.testing.expect(recognizesInteropPolicy(arena_policy));
    try std.testing.expect(!recognizesInteropPolicy(unknown_policy));
    try std.testing.expect(!recognizesInteropPolicy(reserved_policy));

    try std.testing.expect(requiresExplicitCaller(.caller_provided));
    try std.testing.expect(requiresExplicitCallerByte(0));
    try std.testing.expect(requiresExplicitCallerPolicyBytes(0, 0));
    try std.testing.expect(requiresExplicitCallerInteropPolicy(caller_policy));
    try std.testing.expect(!requiresExplicitCallerInteropPolicy(heap_policy));
    try std.testing.expect(!requiresExplicitCallerInteropPolicy(arena_policy));
    try std.testing.expect(!requiresExplicitCallerInteropPolicy(reserved_policy));
    try std.testing.expect(!requiresExplicitCallerPolicyBytes(1, 0));
    try std.testing.expect(!requiresExplicitCallerPolicyBytes(2, 1));
    try std.testing.expect(!requiresExplicitCallerByte(1));
    try std.testing.expect(!requiresExplicitCallerByte(9));

    try std.testing.expect(!usesKernelHeap(.caller_provided));
    try std.testing.expect(usesKernelHeap(.kernel_heap));
    try std.testing.expect(!usesKernelHeap(.arena));
    try std.testing.expect(!usesKernelHeapByte(0));
    try std.testing.expect(usesKernelHeapByte(1));
    try std.testing.expect(!usesKernelHeapByte(2));
    try std.testing.expect(!usesKernelHeapByte(9));
    try std.testing.expect(!usesKernelHeapPolicyBytes(0, 0));
    try std.testing.expect(usesKernelHeapPolicyBytes(1, 0));
    try std.testing.expect(!usesKernelHeapPolicyBytes(2, 0));
    try std.testing.expect(!usesKernelHeapPolicyBytes(9, 0));
    try std.testing.expect(!usesKernelHeapPolicyBytes(1, 1));
    try std.testing.expect(!usesKernelHeapInteropPolicy(caller_policy));
    try std.testing.expect(usesKernelHeapInteropPolicy(heap_policy));
    try std.testing.expect(!usesKernelHeapInteropPolicy(arena_policy));
    try std.testing.expect(!usesKernelHeapInteropPolicy(reserved_policy));

    try std.testing.expect(!usesArena(.caller_provided));
    try std.testing.expect(!usesArena(.kernel_heap));
    try std.testing.expect(usesArena(.arena));
    try std.testing.expect(!usesArenaByte(0));
    try std.testing.expect(!usesArenaByte(1));
    try std.testing.expect(usesArenaByte(2));
    try std.testing.expect(!usesArenaByte(9));
    try std.testing.expect(!usesArenaPolicyBytes(0, 0));
    try std.testing.expect(!usesArenaPolicyBytes(1, 0));
    try std.testing.expect(usesArenaPolicyBytes(2, 0));
    try std.testing.expect(!usesArenaPolicyBytes(9, 0));
    try std.testing.expect(!usesArenaPolicyBytes(2, 1));
    try std.testing.expect(!usesArenaInteropPolicy(caller_policy));
    try std.testing.expect(!usesArenaInteropPolicy(heap_policy));
    try std.testing.expect(usesArenaInteropPolicy(arena_policy));
    try std.testing.expect(!usesArenaInteropPolicy(reserved_policy));

    try std.testing.expect(!permitsGlobalFallback(.caller_provided));
    try std.testing.expect(!permitsGlobalFallbackByte(0));
    try std.testing.expect(!permitsGlobalFallbackPolicyBytes(0, 0));
    try std.testing.expect(!permitsGlobalFallbackInteropPolicy(caller_policy));
    try std.testing.expect(permitsGlobalFallback(.kernel_heap));
    try std.testing.expect(permitsGlobalFallback(.arena));
    try std.testing.expect(permitsGlobalFallbackByte(1));
    try std.testing.expect(permitsGlobalFallbackByte(2));
    try std.testing.expect(permitsGlobalFallbackPolicyBytes(1, 0));
    try std.testing.expect(permitsGlobalFallbackPolicyBytes(2, 0));
    try std.testing.expect(permitsGlobalFallbackInteropPolicy(heap_policy));
    try std.testing.expect(permitsGlobalFallbackInteropPolicy(arena_policy));
    try std.testing.expect(!permitsGlobalFallbackInteropPolicy(reserved_policy));
    try std.testing.expect(!permitsGlobalFallbackPolicyBytes(2, 1));
    try std.testing.expect(!permitsGlobalFallbackByte(9));

    try std.testing.expect(!initializesOwnedStateByte(0));
    try std.testing.expect(initializesOwnedStateByte(1));
    try std.testing.expect(initializesOwnedStateByte(2));
    try std.testing.expect(!initializesOwnedStateByte(9));
    try std.testing.expect(!initializesOwnedStatePolicyBytes(0, 0));
    try std.testing.expect(initializesOwnedStatePolicyBytes(1, 0));
    try std.testing.expect(initializesOwnedStatePolicyBytes(2, 0));
    try std.testing.expect(!initializesOwnedStatePolicyBytes(2, 1));
    try std.testing.expect(!initializesOwnedStateInteropPolicy(caller_policy));
    try std.testing.expect(initializesOwnedStateInteropPolicy(heap_policy));
    try std.testing.expect(initializesOwnedStateInteropPolicy(arena_policy));
    try std.testing.expect(!initializesOwnedStateInteropPolicy(reserved_policy));
    try std.testing.expect(!initializesOwnedStateInteropPolicy(unknown_policy));

    try std.testing.expect(!requiresResetOnInitByte(0));
    try std.testing.expect(!requiresResetOnInitByte(1));
    try std.testing.expect(requiresResetOnInitByte(2));
    try std.testing.expect(!requiresResetOnInitByte(9));
    try std.testing.expect(!requiresResetOnInitPolicyBytes(0, 0));
    try std.testing.expect(!requiresResetOnInitPolicyBytes(1, 0));
    try std.testing.expect(requiresResetOnInitPolicyBytes(2, 0));
    try std.testing.expect(!requiresResetOnInitPolicyBytes(2, 1));
    try std.testing.expect(!requiresResetOnInitInteropPolicy(caller_policy));
    try std.testing.expect(!requiresResetOnInitInteropPolicy(heap_policy));
    try std.testing.expect(requiresResetOnInitInteropPolicy(arena_policy));
    try std.testing.expect(!requiresResetOnInitInteropPolicy(reserved_policy));
    try std.testing.expect(!requiresResetOnInitInteropPolicy(unknown_policy));
}
