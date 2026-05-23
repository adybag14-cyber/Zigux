const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const panic_policy = @import("panic_policy");

test "phase3 abi keeps shared policy recognition aligned with published panic and allocator bytes" {
    const safe_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_ABORT,
        .allocator_mode = abi.ALLOC_CALLER_PROVIDED,
        .unsafe_scope = abi.UNSAFE_NONE,
        .reserved = 0,
    };
    const bug_heap_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_BUG,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
    const warn_arena_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 1,
    };
    const unknown_panic_policy = abi.InteropPolicy{
        .panic_mode = 9,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
    const unknown_allocator_policy = abi.InteropPolicy{
        .panic_mode = abi.PANIC_BUG,
        .allocator_mode = 9,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromInteropPolicy(bug_heap_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromInteropPolicy(warn_arena_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(unknown_panic_policy));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromInteropPolicy(bug_heap_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(warn_arena_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(unknown_allocator_policy));

    try std.testing.expect(panic_policy.recognizesInteropPolicy(safe_policy));
    try std.testing.expect(panic_policy.recognizesInteropPolicy(bug_heap_policy));
    try std.testing.expect(panic_policy.recognizesInteropPolicy(warn_arena_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(unknown_panic_policy));

    try std.testing.expect(allocator_policy.recognizesInteropPolicy(safe_policy));
    try std.testing.expect(allocator_policy.recognizesInteropPolicy(bug_heap_policy));
    try std.testing.expect(allocator_policy.recognizesInteropPolicy(warn_arena_policy));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicy(unknown_allocator_policy));
}

test "phase3 abi keeps byte-level policy relays aligned with published panic and allocator constants" {
    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromByte(abi.PANIC_ABORT));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromByte(abi.PANIC_BUG));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromByte(abi.PANIC_WARN));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromByte(9));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .immediate_abort), panic_policy.escalationFromByte(abi.PANIC_ABORT));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .kernel_bug), panic_policy.escalationFromByte(abi.PANIC_BUG));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .warning_only), panic_policy.escalationFromByte(abi.PANIC_WARN));
    try std.testing.expect(panic_policy.causesImmediateHaltByte(abi.PANIC_ABORT));
    try std.testing.expect(panic_policy.causesImmediateHaltByte(abi.PANIC_BUG));
    try std.testing.expect(!panic_policy.causesImmediateHaltByte(abi.PANIC_WARN));
    try std.testing.expect(panic_policy.permitsWarningOnlyContinuationByte(abi.PANIC_WARN));
    try std.testing.expect(!panic_policy.recognizesInteropPolicyBytes(abi.PANIC_WARN, 1));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromByte(abi.ALLOC_ARENA));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromByte(9));
    try std.testing.expect(allocator_policy.requiresExplicitCallerByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackByte(abi.ALLOC_ARENA));
    try std.testing.expect(allocator_policy.requiresResetOnInitByte(abi.ALLOC_ARENA));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicyBytes(abi.ALLOC_ARENA, 1));
}
