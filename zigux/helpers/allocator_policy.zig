const std = @import("std");
const abi = @import("abi_bindings");

pub const InitFlow = enum {
    caller_prepared,
    helper_owned,
    helper_owned_with_reset,
};

pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {
    return switch (mode) {
        .caller_provided => .caller_prepared,
        .kernel_heap => .helper_owned,
        .arena => .helper_owned_with_reset,
    };
}

pub fn modeFromInteropPolicyByte(allocator_mode: u8) ?abi.AllocatorMode {
    return switch (allocator_mode) {
        @intFromEnum(abi.AllocatorMode.caller_provided) => .caller_provided,
        @intFromEnum(abi.AllocatorMode.kernel_heap) => .kernel_heap,
        @intFromEnum(abi.AllocatorMode.arena) => .arena,
        else => null,
    };
}

pub fn recognizesInteropPolicyByte(allocator_mode: u8) bool {
    return modeFromInteropPolicyByte(allocator_mode) != null;
}

pub fn requiresExplicitCaller(mode: abi.AllocatorMode) bool {
    return initFlowFor(mode) == .caller_prepared;
}

pub fn requiresExplicitCallerPolicyByte(allocator_mode: u8) bool {
    return requiresExplicitCaller(modeFromInteropPolicyByte(allocator_mode) orelse return false);
}

pub fn permitsGlobalFallback(mode: abi.AllocatorMode) bool {
    return switch (initFlowFor(mode)) {
        .caller_prepared => false,
        .helper_owned, .helper_owned_with_reset => true,
    };
}

pub fn permitsGlobalFallbackPolicyByte(allocator_mode: u8) bool {
    return permitsGlobalFallback(modeFromInteropPolicyByte(allocator_mode) orelse return false);
}

pub fn initializesOwnedState(mode: abi.AllocatorMode) bool {
    return switch (initFlowFor(mode)) {
        .caller_prepared => false,
        .helper_owned, .helper_owned_with_reset => true,
    };
}

pub fn initializesOwnedStatePolicyByte(allocator_mode: u8) bool {
    return initializesOwnedState(modeFromInteropPolicyByte(allocator_mode) orelse return false);
}

pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {
    return initFlowFor(mode) == .helper_owned_with_reset;
}

pub fn requiresResetOnInitPolicyByte(allocator_mode: u8) bool {
    return requiresResetOnInit(modeFromInteropPolicyByte(allocator_mode) orelse return false);
}

test "phase3 allocator policy stays explicit" {
    try std.testing.expectEqual(InitFlow.caller_prepared, initFlowFor(.caller_provided));
    try std.testing.expectEqual(InitFlow.helper_owned, initFlowFor(.kernel_heap));
    try std.testing.expectEqual(InitFlow.helper_owned_with_reset, initFlowFor(.arena));

    try std.testing.expect(requiresExplicitCaller(.caller_provided));
    try std.testing.expect(!permitsGlobalFallback(.caller_provided));
    try std.testing.expect(!initializesOwnedState(.caller_provided));
    try std.testing.expect(!requiresResetOnInit(.caller_provided));

    try std.testing.expect(permitsGlobalFallback(.kernel_heap));
    try std.testing.expect(initializesOwnedState(.kernel_heap));
    try std.testing.expect(!requiresResetOnInit(.kernel_heap));

    try std.testing.expect(permitsGlobalFallback(.arena));
    try std.testing.expect(initializesOwnedState(.arena));
    try std.testing.expect(requiresResetOnInit(.arena));

    try std.testing.expectEqual(abi.AllocatorMode.caller_provided, modeFromInteropPolicyByte(@intFromEnum(abi.AllocatorMode.caller_provided)).?);
    try std.testing.expectEqual(abi.AllocatorMode.kernel_heap, modeFromInteropPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)).?);
    try std.testing.expectEqual(abi.AllocatorMode.arena, modeFromInteropPolicyByte(@intFromEnum(abi.AllocatorMode.arena)).?);
    try std.testing.expect(recognizesInteropPolicyByte(@intFromEnum(abi.AllocatorMode.arena)));
    try std.testing.expect(!recognizesInteropPolicyByte(9));
    try std.testing.expect(requiresExplicitCallerPolicyByte(@intFromEnum(abi.AllocatorMode.caller_provided)));
    try std.testing.expect(!requiresExplicitCallerPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)));
    try std.testing.expect(!requiresExplicitCallerPolicyByte(9));
    try std.testing.expect(permitsGlobalFallbackPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)));
    try std.testing.expect(initializesOwnedStatePolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)));
    try std.testing.expect(requiresResetOnInitPolicyByte(@intFromEnum(abi.AllocatorMode.arena)));
    try std.testing.expect(!permitsGlobalFallbackPolicyByte(9));
    try std.testing.expect(!initializesOwnedStatePolicyByte(9));
    try std.testing.expect(!requiresResetOnInitPolicyByte(9));
}
