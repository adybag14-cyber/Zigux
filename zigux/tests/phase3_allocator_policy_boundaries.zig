const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");

fn makePolicy(mode: abi.AllocatorMode) abi.InteropPolicy {
    return .{
        .panic_mode = 0,
        .allocator_mode = @intFromEnum(mode),
        .unsafe_scope = 0,
        .reserved = 0,
    };
}

test "allocator policy replay keeps byte and interop decoders aligned" {
    const cases = [_]struct {
        mode: abi.AllocatorMode,
        flow: allocator_policy.InitFlow,
        explicit_caller: bool,
        global_fallback: bool,
        initializes_owned_state: bool,
        requires_reset: bool,
    }{
        .{
            .mode = .caller_provided,
            .flow = .caller_prepared,
            .explicit_caller = true,
            .global_fallback = false,
            .initializes_owned_state = false,
            .requires_reset = false,
        },
        .{
            .mode = .kernel_heap,
            .flow = .helper_owned,
            .explicit_caller = false,
            .global_fallback = true,
            .initializes_owned_state = true,
            .requires_reset = false,
        },
        .{
            .mode = .arena,
            .flow = .helper_owned_with_reset,
            .explicit_caller = false,
            .global_fallback = true,
            .initializes_owned_state = true,
            .requires_reset = true,
        },
    };

    for (cases) |case| {
        const raw_mode = @intFromEnum(case.mode);
        const policy = makePolicy(case.mode);

        try testing.expectEqual(@as(?abi.AllocatorMode, case.mode), allocator_policy.modeFromByte(raw_mode));
        try testing.expectEqual(@as(?abi.AllocatorMode, case.mode), allocator_policy.modeFromInteropPolicy(policy));
        try testing.expect(allocator_policy.recognizesByte(raw_mode));
        try testing.expect(allocator_policy.recognizesInteropPolicy(policy));

        try testing.expectEqual(case.flow, allocator_policy.initFlowFor(case.mode));
        try testing.expectEqual(case.explicit_caller, allocator_policy.requiresExplicitCaller(case.mode));
        try testing.expectEqual(case.explicit_caller, allocator_policy.requiresExplicitCallerByte(raw_mode));
        try testing.expectEqual(case.explicit_caller, allocator_policy.requiresExplicitCallerInteropPolicy(policy));
        try testing.expectEqual(case.global_fallback, allocator_policy.permitsGlobalFallback(case.mode));
        try testing.expectEqual(case.global_fallback, allocator_policy.permitsGlobalFallbackByte(raw_mode));
        try testing.expectEqual(case.global_fallback, allocator_policy.permitsGlobalFallbackInteropPolicy(policy));
        try testing.expectEqual(case.initializes_owned_state, allocator_policy.initializesOwnedState(case.mode));
        try testing.expectEqual(case.initializes_owned_state, allocator_policy.initializesOwnedStateByte(raw_mode));
        try testing.expectEqual(case.initializes_owned_state, allocator_policy.initializesOwnedStateInteropPolicy(policy));
        try testing.expectEqual(case.requires_reset, allocator_policy.requiresResetOnInit(case.mode));
        try testing.expectEqual(case.requires_reset, allocator_policy.requiresResetOnInitByte(raw_mode));
        try testing.expectEqual(case.requires_reset, allocator_policy.requiresResetOnInitInteropPolicy(policy));
    }
}

test "allocator policy replay fails closed on reserved and unknown encodings" {
    const reserved = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = 0,
        .reserved = 1,
    };
    const unknown = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 9,
        .unsafe_scope = 0,
        .reserved = 0,
    };

    try testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(unknown));
    try testing.expect(!allocator_policy.recognizesInteropPolicy(reserved));
    try testing.expect(!allocator_policy.recognizesInteropPolicy(unknown));
    try testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(reserved));
    try testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(unknown));
    try testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(reserved));
    try testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(unknown));
    try testing.expect(!allocator_policy.initializesOwnedStateInteropPolicy(reserved));
    try testing.expect(!allocator_policy.initializesOwnedStateInteropPolicy(unknown));
    try testing.expect(!allocator_policy.requiresResetOnInitInteropPolicy(reserved));
    try testing.expect(!allocator_policy.requiresResetOnInitInteropPolicy(unknown));
}
