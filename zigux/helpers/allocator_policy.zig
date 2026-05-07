const std = @import("std");
const abi = @import("abi_bindings");

pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.AllocatorMode {
    if (reserved != 0) return null;
    return switch (mode) {
        @intFromEnum(abi.AllocatorMode.caller_provided) => .caller_provided,
        @intFromEnum(abi.AllocatorMode.kernel_heap) => .kernel_heap,
        @intFromEnum(abi.AllocatorMode.arena) => .arena,
        else => null,
    };
}

pub fn modeFromByte(mode: u8) ?abi.AllocatorMode {
    return modeFromInteropPolicyBytes(mode, 0);
}

pub fn recognizesInteropPolicyBytes(mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(mode, reserved) != null;
}

pub fn requiresExplicitCaller(mode: abi.AllocatorMode) bool {
    return mode == .caller_provided;
}

pub fn requiresExplicitCallerPolicyBytes(mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(mode, reserved) == .caller_provided;
}

pub fn requiresExplicitCallerByte(mode: u8) bool {
    return requiresExplicitCallerPolicyBytes(mode, 0);
}

pub fn permitsGlobalFallback(mode: abi.AllocatorMode) bool {
    return switch (mode) {
        .caller_provided => false,
        .kernel_heap, .arena => true,
    };
}

pub fn permitsGlobalFallbackPolicyBytes(mode: u8, reserved: u8) bool {
    return switch (modeFromInteropPolicyBytes(mode, reserved) orelse return false) {
        .caller_provided => false,
        .kernel_heap, .arena => true,
    };
}

pub fn permitsGlobalFallbackByte(mode: u8) bool {
    return permitsGlobalFallbackPolicyBytes(mode, 0);
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

    try std.testing.expect(requiresExplicitCaller(.caller_provided));
    try std.testing.expect(requiresExplicitCallerByte(0));
    try std.testing.expect(requiresExplicitCallerPolicyBytes(0, 0));
    try std.testing.expect(!requiresExplicitCallerPolicyBytes(1, 0));
    try std.testing.expect(!requiresExplicitCallerPolicyBytes(2, 1));
    try std.testing.expect(!requiresExplicitCallerByte(1));
    try std.testing.expect(!requiresExplicitCallerByte(9));

    try std.testing.expect(!permitsGlobalFallback(.caller_provided));
    try std.testing.expect(!permitsGlobalFallbackByte(0));
    try std.testing.expect(!permitsGlobalFallbackPolicyBytes(0, 0));
    try std.testing.expect(permitsGlobalFallback(.kernel_heap));
    try std.testing.expect(permitsGlobalFallback(.arena));
    try std.testing.expect(permitsGlobalFallbackByte(1));
    try std.testing.expect(permitsGlobalFallbackByte(2));
    try std.testing.expect(permitsGlobalFallbackPolicyBytes(1, 0));
    try std.testing.expect(permitsGlobalFallbackPolicyBytes(2, 0));
    try std.testing.expect(!permitsGlobalFallbackPolicyBytes(2, 1));
    try std.testing.expect(!permitsGlobalFallbackByte(9));
}
