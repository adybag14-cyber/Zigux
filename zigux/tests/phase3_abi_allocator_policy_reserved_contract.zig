const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");

fn policy(allocator_mode: u8, reserved: u8) abi.InteropPolicy {
    return .{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = allocator_mode,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = reserved,
    };
}

test "allocator policy rejects reserved bytes before deriving ownership" {
    const reserved_modes = [_]u8{
        abi.ALLOC_CALLER_PROVIDED,
        abi.ALLOC_KERNEL_HEAP,
        abi.ALLOC_ARENA,
    };

    for (reserved_modes) |mode| {
        const rejected = policy(mode, 1);

        try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(rejected));
        try std.testing.expect(!allocator_policy.recognizesInteropPolicy(rejected));
        try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(rejected));
        try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(rejected));
    }
}

test "allocator policy rejects unknown bytes even when reserved is clear" {
    const unknown_modes = [_]u8{ 3, 9, 0xff };

    for (unknown_modes) |mode| {
        const rejected = policy(mode, 0);

        try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromByte(mode));
        try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(rejected));
        try std.testing.expect(!allocator_policy.recognizesByte(mode));
        try std.testing.expect(!allocator_policy.recognizesInteropPolicy(rejected));
        try std.testing.expect(!allocator_policy.requiresExplicitCallerByte(mode));
        try std.testing.expect(!allocator_policy.permitsGlobalFallbackByte(mode));
    }
}

test "allocator policy accepts only the current three clear-reserved modes" {
    const caller = policy(abi.ALLOC_CALLER_PROVIDED, 0);
    const heap = policy(abi.ALLOC_KERNEL_HEAP, 0);
    const arena = policy(abi.ALLOC_ARENA, 0);

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromInteropPolicy(caller));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromInteropPolicy(heap));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(arena));

    try std.testing.expect(allocator_policy.recognizesInteropPolicy(caller));
    try std.testing.expect(allocator_policy.recognizesInteropPolicy(heap));
    try std.testing.expect(allocator_policy.recognizesInteropPolicy(arena));

    try std.testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(caller));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(heap));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(arena));

    try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(caller));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(heap));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(arena));
}
