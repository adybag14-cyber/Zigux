const std = @import("std");
const abi = @import("abi_bindings");
const panic_policy = @import("panic_policy");
const allocator_policy = @import("allocator_policy");
const narrow = @import("narrow_unsafe");

pub const DecodeError = error{
    InvalidPanicMode,
    InvalidAllocatorMode,
    InvalidUnsafeScope,
    ReservedBitsSet,
};

pub const DecodedInteropPolicy = struct {
    panic_mode: abi.PanicMode,
    allocator_mode: abi.AllocatorMode,
    unsafe_scope: narrow.UnsafeScopeTag,

    pub fn canReturn(self: DecodedInteropPolicy) bool {
        return panic_policy.canReturn(self.panic_mode);
    }

    pub fn requiresExplicitCaller(self: DecodedInteropPolicy) bool {
        return allocator_policy.requiresExplicitCaller(self.allocator_mode);
    }

    pub fn permitsGlobalFallback(self: DecodedInteropPolicy) bool {
        return allocator_policy.permitsGlobalFallback(self.allocator_mode);
    }

    pub fn initializesOwnedState(self: DecodedInteropPolicy) bool {
        return allocator_policy.initializesOwnedState(self.allocator_mode);
    }

    pub fn requiresResetOnInit(self: DecodedInteropPolicy) bool {
        return allocator_policy.requiresResetOnInit(self.allocator_mode);
    }

    pub fn permitsVolatileMmio(self: DecodedInteropPolicy) bool {
        return narrow.permitsVolatileMmio(self.unsafe_scope);
    }

    pub fn permitsRawPointerBridge(self: DecodedInteropPolicy) bool {
        return narrow.permitsRawPointerBridge(self.unsafe_scope);
    }
};

pub fn decode(policy: abi.InteropPolicy) DecodeError!DecodedInteropPolicy {
    if (policy.reserved != 0) {
        return error.ReservedBitsSet;
    }

    return .{
        .panic_mode = panic_policy.modeFromInteropPolicyByte(policy.panic_mode) orelse return error.InvalidPanicMode,
        .allocator_mode = allocator_policy.modeFromInteropPolicyByte(policy.allocator_mode) orelse return error.InvalidAllocatorMode,
        .unsafe_scope = narrow.scopeFromInteropPolicyBytes(policy.unsafe_scope, policy.reserved) orelse return error.InvalidUnsafeScope,
    };
}

pub fn recognizes(policy: abi.InteropPolicy) bool {
    _ = decode(policy) catch return false;
    return true;
}

test "phase3 interop policy decoder keeps the boundary typed" {
    const decoded = try decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    });
    try std.testing.expect(decoded.canReturn());
    try std.testing.expect(decoded.permitsGlobalFallback());
    try std.testing.expect(decoded.initializesOwnedState());
    try std.testing.expect(!decoded.requiresResetOnInit());
    try std.testing.expect(decoded.permitsVolatileMmio());
    try std.testing.expect(!decoded.permitsRawPointerBridge());
}

test "phase3 interop policy decoder keeps allocator init requirements explicit" {
    const caller_policy = try decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    });
    try std.testing.expect(caller_policy.requiresExplicitCaller());
    try std.testing.expect(!caller_policy.initializesOwnedState());
    try std.testing.expect(!caller_policy.requiresResetOnInit());

    const arena_policy = try decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    });
    try std.testing.expect(!arena_policy.requiresExplicitCaller());
    try std.testing.expect(arena_policy.permitsGlobalFallback());
    try std.testing.expect(arena_policy.initializesOwnedState());
    try std.testing.expect(arena_policy.requiresResetOnInit());
}

test "phase3 interop policy decoder rejects invalid bytes and reserved bits" {
    try std.testing.expectError(error.InvalidPanicMode, decode(.{
        .panic_mode = 9,
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    }));
    try std.testing.expectError(error.InvalidAllocatorMode, decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = 9,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    }));
    try std.testing.expectError(error.InvalidUnsafeScope, decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = 9,
        .reserved = 0,
    }));
    try std.testing.expectError(error.ReservedBitsSet, decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 1,
    }));
}
