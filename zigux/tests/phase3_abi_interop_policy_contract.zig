const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");

test "ABI interop policy keeps its published byte layout" {
    try testing.expectEqual(@as(usize, 4), abi.interop_policy_size);
    try testing.expectEqual(@as(usize, 1), abi.interop_policy_align);
    try testing.expectEqual(@as(usize, 0), abi.interop_policy_panic_mode_offset);
    try testing.expectEqual(@as(usize, 1), abi.interop_policy_allocator_mode_offset);
    try testing.expectEqual(@as(usize, 2), abi.interop_policy_unsafe_scope_offset);
    try testing.expectEqual(@as(usize, 3), abi.interop_policy_reserved_offset);

    const policy = abi.defaultInteropPolicy();
    try testing.expectEqual(@as(u8, abi.PANIC_ABORT), policy.panic_mode);
    try testing.expectEqual(@as(u8, abi.ALLOC_CALLER_PROVIDED), policy.allocator_mode);
    try testing.expectEqual(@as(u8, abi.UNSAFE_NONE), policy.unsafe_scope);
    try testing.expectEqual(@as(u8, 0), policy.reserved);
    try testing.expect(abi.interopPolicyReservedClear(policy));
    try testing.expect(abi.interopPolicyIsRecognized(policy));
}

test "ABI interop policy decoders accept only closed byte domains" {
    try testing.expectEqual(@as(?abi.PanicMode, .abort), abi.panicModeFromByte(abi.PANIC_ABORT));
    try testing.expectEqual(@as(?abi.PanicMode, .bug), abi.panicModeFromByte(abi.PANIC_BUG));
    try testing.expectEqual(@as(?abi.PanicMode, .warn), abi.panicModeFromByte(abi.PANIC_WARN));
    try testing.expectEqual(@as(?abi.PanicMode, null), abi.panicModeFromByte(3));
    try testing.expectEqual(@as(?abi.PanicMode, null), abi.panicModeFromByte(0xff));

    try testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), abi.allocatorModeFromByte(abi.ALLOC_CALLER_PROVIDED));
    try testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), abi.allocatorModeFromByte(abi.ALLOC_KERNEL_HEAP));
    try testing.expectEqual(@as(?abi.AllocatorMode, .arena), abi.allocatorModeFromByte(abi.ALLOC_ARENA));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), abi.allocatorModeFromByte(3));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), abi.allocatorModeFromByte(0xff));

    try testing.expectEqual(@as(?abi.UnsafeScope, .none), abi.unsafeScopeFromByte(abi.UNSAFE_NONE));
    try testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), abi.unsafeScopeFromByte(abi.UNSAFE_VOLATILE_MMIO));
    try testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), abi.unsafeScopeFromByte(abi.UNSAFE_RAW_POINTER_BRIDGE));
    try testing.expectEqual(@as(?abi.UnsafeScope, null), abi.unsafeScopeFromByte(3));
    try testing.expectEqual(@as(?abi.UnsafeScope, null), abi.unsafeScopeFromByte(0xff));
}

test "ABI interop policy recognition is field local when reserved is clear" {
    const valid = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
    const unknown_panic = abi.InteropPolicy{
        .panic_mode = 0xff,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
    const unknown_allocator = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = 0xff,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
    const unknown_scope = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = 0xff,
        .reserved = 0,
    };

    try testing.expectEqual(@as(?abi.PanicMode, .warn), abi.panicModeFromInteropPolicy(valid));
    try testing.expectEqual(@as(?abi.AllocatorMode, .arena), abi.allocatorModeFromInteropPolicy(valid));
    try testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), abi.unsafeScopeFromInteropPolicy(valid));
    try testing.expect(abi.interopPolicyIsRecognized(valid));

    try testing.expectEqual(@as(?abi.PanicMode, null), abi.panicModeFromInteropPolicy(unknown_panic));
    try testing.expectEqual(@as(?abi.AllocatorMode, .arena), abi.allocatorModeFromInteropPolicy(unknown_panic));
    try testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), abi.unsafeScopeFromInteropPolicy(unknown_panic));
    try testing.expect(!abi.interopPolicyIsRecognized(unknown_panic));

    try testing.expectEqual(@as(?abi.PanicMode, .warn), abi.panicModeFromInteropPolicy(unknown_allocator));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), abi.allocatorModeFromInteropPolicy(unknown_allocator));
    try testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), abi.unsafeScopeFromInteropPolicy(unknown_allocator));
    try testing.expect(!abi.interopPolicyIsRecognized(unknown_allocator));

    try testing.expectEqual(@as(?abi.PanicMode, .warn), abi.panicModeFromInteropPolicy(unknown_scope));
    try testing.expectEqual(@as(?abi.AllocatorMode, .arena), abi.allocatorModeFromInteropPolicy(unknown_scope));
    try testing.expectEqual(@as(?abi.UnsafeScope, null), abi.unsafeScopeFromInteropPolicy(unknown_scope));
    try testing.expect(!abi.interopPolicyIsRecognized(unknown_scope));
}

test "ABI interop policy reserved byte blocks all policy decoders" {
    const reserved = abi.InteropPolicy{
        .panic_mode = abi.PANIC_BUG,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 1,
    };

    try testing.expect(!abi.interopPolicyReservedClear(reserved));
    try testing.expectEqual(@as(?abi.PanicMode, null), abi.panicModeFromInteropPolicy(reserved));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), abi.allocatorModeFromInteropPolicy(reserved));
    try testing.expectEqual(@as(?abi.UnsafeScope, null), abi.unsafeScopeFromInteropPolicy(reserved));
    try testing.expect(!abi.interopPolicyIsRecognized(reserved));
}
