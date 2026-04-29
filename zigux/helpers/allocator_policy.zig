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

pub fn modeFromInteropPolicyBytes(allocator_mode: u8, reserved: u8) ?abi.AllocatorMode {
    if (reserved != 0) {
        return null;
    }
    return modeFromInteropPolicyByte(allocator_mode);
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

pub fn recognizesInteropPolicyBytes(allocator_mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(allocator_mode, reserved) != null;
}

pub fn requiresExplicitCaller(mode: abi.AllocatorMode) bool {
    return initFlowFor(mode) == .caller_prepared;
}

pub fn requiresExplicitCallerPolicyBytes(allocator_mode: u8, reserved: u8) bool {
    return requiresExplicitCaller(modeFromInteropPolicyBytes(allocator_mode, reserved) orelse return false);
}

pub fn requiresExplicitCallerPolicyByte(allocator_mode: u8) bool {
    return requiresExplicitCallerPolicyBytes(allocator_mode, 0);
}

pub fn permitsGlobalFallback(mode: abi.AllocatorMode) bool {
    return switch (initFlowFor(mode)) {
        .caller_prepared => false,
        .helper_owned, .helper_owned_with_reset => true,
    };
}

pub fn permitsGlobalFallbackPolicyBytes(allocator_mode: u8, reserved: u8) bool {
    return permitsGlobalFallback(modeFromInteropPolicyBytes(allocator_mode, reserved) orelse return false);
}

pub fn permitsGlobalFallbackPolicyByte(allocator_mode: u8) bool {
    return permitsGlobalFallbackPolicyBytes(allocator_mode, 0);
}

pub fn initializesOwnedState(mode: abi.AllocatorMode) bool {
    return switch (initFlowFor(mode)) {
        .caller_prepared => false,
        .helper_owned, .helper_owned_with_reset => true,
    };
}

pub fn initializesOwnedStatePolicyBytes(allocator_mode: u8, reserved: u8) bool {
    return initializesOwnedState(modeFromInteropPolicyBytes(allocator_mode, reserved) orelse return false);
}

pub fn initializesOwnedStatePolicyByte(allocator_mode: u8) bool {
    return initializesOwnedStatePolicyBytes(allocator_mode, 0);
}

pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {
    return initFlowFor(mode) == .helper_owned_with_reset;
}

pub fn requiresResetOnInitPolicyBytes(allocator_mode: u8, reserved: u8) bool {
    return requiresResetOnInit(modeFromInteropPolicyBytes(allocator_mode, reserved) orelse return false);
}

pub fn requiresResetOnInitPolicyByte(allocator_mode: u8) bool {
    return requiresResetOnInitPolicyBytes(allocator_mode, 0);
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
    try std.testing.expectEqual(abi.AllocatorMode.arena, modeFromInteropPolicyBytes(@intFromEnum(abi.AllocatorMode.arena), 0).?);
    try std.testing.expect(recognizesInteropPolicyBytes(@intFromEnum(abi.AllocatorMode.arena), 0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicyBytes(@intFromEnum(abi.AllocatorMode.arena), 1));
    try std.testing.expect(!recognizesInteropPolicyBytes(@intFromEnum(abi.AllocatorMode.arena), 1));
    try std.testing.expect(requiresExplicitCallerPolicyByte(@intFromEnum(abi.AllocatorMode.caller_provided)));
    try std.testing.expect(!requiresExplicitCallerPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)));
    try std.testing.expect(requiresExplicitCallerPolicyBytes(@intFromEnum(abi.AllocatorMode.caller_provided), 0));
    try std.testing.expect(!requiresExplicitCallerPolicyBytes(@intFromEnum(abi.AllocatorMode.caller_provided), 1));
    try std.testing.expect(permitsGlobalFallbackPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)));
    try std.testing.expect(permitsGlobalFallbackPolicyBytes(@intFromEnum(abi.AllocatorMode.kernel_heap), 0));
    try std.testing.expect(!permitsGlobalFallbackPolicyBytes(@intFromEnum(abi.AllocatorMode.kernel_heap), 1));
    try std.testing.expect(initializesOwnedStatePolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)));
    try std.testing.expect(initializesOwnedStatePolicyBytes(@intFromEnum(abi.AllocatorMode.kernel_heap), 0));
    try std.testing.expect(!initializesOwnedStatePolicyBytes(@intFromEnum(abi.AllocatorMode.kernel_heap), 1));
    try std.testing.expect(requiresResetOnInitPolicyByte(@intFromEnum(abi.AllocatorMode.arena)));
    try std.testing.expect(requiresResetOnInitPolicyBytes(@intFromEnum(abi.AllocatorMode.arena), 0));
    try std.testing.expect(!requiresResetOnInitPolicyBytes(@intFromEnum(abi.AllocatorMode.arena), 1));
    try std.testing.expect(!permitsGlobalFallbackPolicyByte(9));
    try std.testing.expect(!initializesOwnedStatePolicyByte(9));
    try std.testing.expect(!requiresResetOnInitPolicyByte(9));
    try std.testing.expect(!permitsGlobalFallbackPolicyBytes(9, 0));
    try std.testing.expect(!initializesOwnedStatePolicyBytes(9, 0));
    try std.testing.expect(!requiresResetOnInitPolicyBytes(9, 0));
}
