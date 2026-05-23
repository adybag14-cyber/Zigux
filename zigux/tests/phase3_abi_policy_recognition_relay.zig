const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const panic_policy = @import("panic_policy");
const unsafe_policy = @import("unsafe_policy");

test "phase3 abi keeps interop-policy recognition aligned with dedicated policy helpers" {
    const bug_heap = abi.InteropPolicy{
        .panic_mode = abi.PANIC_BUG,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
    const warn_arena = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };

    try std.testing.expectEqual(abi.panicModeFromInteropPolicy(bug_heap), panic_policy.modeFromInteropPolicy(bug_heap));
    try std.testing.expectEqual(abi.allocatorModeFromInteropPolicy(bug_heap), allocator_policy.modeFromInteropPolicy(bug_heap));
    try std.testing.expectEqual(abi.unsafeScopeFromInteropPolicy(bug_heap), unsafe_policy.modeFromInteropPolicy(bug_heap));
    try std.testing.expect(abi.interopPolicyIsRecognized(bug_heap));
    try std.testing.expect(panic_policy.recognizesInteropPolicy(bug_heap));
    try std.testing.expect(allocator_policy.recognizesInteropPolicy(bug_heap));
    try std.testing.expect(unsafe_policy.recognizesInteropPolicy(bug_heap));

    try std.testing.expectEqual(abi.panicModeFromInteropPolicy(warn_arena), panic_policy.modeFromInteropPolicy(warn_arena));
    try std.testing.expectEqual(abi.allocatorModeFromInteropPolicy(warn_arena), allocator_policy.modeFromInteropPolicy(warn_arena));
    try std.testing.expectEqual(abi.unsafeScopeFromInteropPolicy(warn_arena), unsafe_policy.scopeFromInteropPolicy(warn_arena));
    try std.testing.expect(abi.interopPolicyIsRecognized(warn_arena));
    try std.testing.expect(panic_policy.recognizesInteropPolicy(warn_arena));
    try std.testing.expect(allocator_policy.recognizesInteropPolicy(warn_arena));
    try std.testing.expect(unsafe_policy.recognizesInteropPolicy(warn_arena));
}

test "phase3 abi rejects reserved and unknown interop-policy bytes consistently across policy helpers" {
    const reserved = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 1,
    };
    const unknown = abi.InteropPolicy{
        .panic_mode = 9,
        .allocator_mode = 9,
        .unsafe_scope = 9,
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?abi.PanicMode, null), abi.panicModeFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), abi.allocatorModeFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), abi.unsafeScopeFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.scopeFromInteropPolicy(reserved));
    try std.testing.expect(!abi.interopPolicyIsRecognized(reserved));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(reserved));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicy(reserved));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicy(reserved));

    try std.testing.expectEqual(@as(?abi.PanicMode, null), abi.panicModeFromInteropPolicy(unknown));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), abi.allocatorModeFromInteropPolicy(unknown));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), abi.unsafeScopeFromInteropPolicy(unknown));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(unknown));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(unknown));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.modeFromInteropPolicy(unknown));
    try std.testing.expect(!abi.interopPolicyIsRecognized(unknown));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(unknown));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicy(unknown));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicy(unknown));
}
