const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const panic_policy = @import("panic_policy");

test "policy starter packet decodes shared interop policy records" {
    const bug_heap = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const warn_arena = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 1,
    };

    try testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromInteropPolicy(bug_heap));
    try testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromInteropPolicy(bug_heap));
    try testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromInteropPolicy(warn_arena));
    try testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(warn_arena));
    try testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved));
}

test "panic policy starter packet keeps escalation semantics explicit" {
    try testing.expectEqual(panic_policy.Escalation.immediate_abort, panic_policy.escalationFor(.abort));
    try testing.expectEqual(panic_policy.Escalation.kernel_bug, panic_policy.escalationFor(.bug));
    try testing.expectEqual(panic_policy.Escalation.warning_only, panic_policy.escalationFor(.warn));

    try testing.expect(panic_policy.causesImmediateHalt(.abort));
    try testing.expect(panic_policy.causesImmediateHalt(.bug));
    try testing.expect(!panic_policy.causesImmediateHalt(.warn));
    try testing.expect(panic_policy.emitsKernelBug(.bug));
    try testing.expect(!panic_policy.emitsKernelBug(.warn));
    try testing.expect(panic_policy.permitsWarningOnlyContinuation(.warn));
}

test "allocator policy starter packet keeps init ownership semantics explicit" {
    try testing.expectEqual(allocator_policy.InitFlow.caller_prepared, allocator_policy.initFlowFor(.caller_provided));
    try testing.expectEqual(allocator_policy.InitFlow.helper_owned, allocator_policy.initFlowFor(.kernel_heap));
    try testing.expectEqual(allocator_policy.InitFlow.helper_owned_with_reset, allocator_policy.initFlowFor(.arena));

    try testing.expect(allocator_policy.requiresExplicitCaller(.caller_provided));
    try testing.expect(!allocator_policy.requiresExplicitCaller(.kernel_heap));
    try testing.expect(allocator_policy.permitsGlobalFallback(.kernel_heap));
    try testing.expect(allocator_policy.permitsGlobalFallback(.arena));
    try testing.expect(!allocator_policy.permitsGlobalFallback(.caller_provided));
    try testing.expect(allocator_policy.initializesOwnedState(.kernel_heap));
    try testing.expect(allocator_policy.initializesOwnedState(.arena));
    try testing.expect(!allocator_policy.initializesOwnedState(.caller_provided));
    try testing.expect(allocator_policy.requiresResetOnInit(.arena));
    try testing.expect(!allocator_policy.requiresResetOnInit(.kernel_heap));
}
