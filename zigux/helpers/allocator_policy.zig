const std = @import("std");
const abi = @import("abi_bindings");

pub fn modeFromByte(mode: u8) ?abi.AllocatorMode {
    return switch (mode) {
        @intFromEnum(abi.AllocatorMode.caller_provided) => .caller_provided,
        @intFromEnum(abi.AllocatorMode.kernel_heap) => .kernel_heap,
        @intFromEnum(abi.AllocatorMode.arena) => .arena,
        else => null,
    };
}

pub fn requiresExplicitCaller(mode: abi.AllocatorMode) bool {
    return mode == .caller_provided;
}

pub fn requiresExplicitCallerByte(mode: u8) bool {
    return modeFromByte(mode) == .caller_provided;
}

pub fn permitsGlobalFallback(mode: abi.AllocatorMode) bool {
    return switch (mode) {
        .caller_provided => false,
        .kernel_heap, .arena => true,
    };
}

pub fn permitsGlobalFallbackByte(mode: u8) bool {
    return switch (modeFromByte(mode) orelse return false) {
        .caller_provided => false,
        .kernel_heap, .arena => true,
    };
}

test "phase3 allocator policy stays explicit" {
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromByte(9));

    try std.testing.expect(requiresExplicitCaller(.caller_provided));
    try std.testing.expect(requiresExplicitCallerByte(0));
    try std.testing.expect(!requiresExplicitCallerByte(1));
    try std.testing.expect(!requiresExplicitCallerByte(9));

    try std.testing.expect(!permitsGlobalFallback(.caller_provided));
    try std.testing.expect(!permitsGlobalFallbackByte(0));
    try std.testing.expect(permitsGlobalFallback(.kernel_heap));
    try std.testing.expect(permitsGlobalFallback(.arena));
    try std.testing.expect(permitsGlobalFallbackByte(1));
    try std.testing.expect(permitsGlobalFallbackByte(2));
    try std.testing.expect(!permitsGlobalFallbackByte(9));
}
