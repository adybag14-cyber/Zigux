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

    pub fn action(self: DecodedInteropPolicy) panic_policy.Action {
        return panic_policy.actionFor(self.panic_mode);
    }

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

    pub fn unsafeScope(self: DecodedInteropPolicy) narrow.UnsafeScopeTag {
        return self.unsafe_scope;
    }

    pub fn permitsVolatileMmio(self: DecodedInteropPolicy) bool {
        return narrow.permitsVolatileMmio(self.unsafe_scope);
    }

    pub fn permitsRawPointerBridge(self: DecodedInteropPolicy) bool {
        return narrow.permitsRawPointerBridge(self.unsafe_scope);
    }

    pub fn constSliceAt(
        self: DecodedInteropPolicy,
        comptime T: type,
        base: usize,
        len: usize,
    ) narrow.ScopeError![]const T {
        if (!self.permitsRawPointerBridge()) return error.UnsafeScopeDenied;
        return narrow.scopedConstSliceAt(T, self.unsafe_scope, base, len);
    }

    pub fn constPointerAt(
        self: DecodedInteropPolicy,
        comptime T: type,
        addr: usize,
    ) narrow.ScopeError!*const T {
        if (!self.permitsRawPointerBridge()) return error.UnsafeScopeDenied;
        return narrow.scopedConstPointerAt(T, self.unsafe_scope, addr);
    }

    pub fn readValueAt(
        self: DecodedInteropPolicy,
        comptime T: type,
        addr: usize,
    ) narrow.ScopeError!T {
        if (!self.permitsRawPointerBridge()) return error.UnsafeScopeDenied;
        return narrow.scopedConstValueAt(T, self.unsafe_scope, addr);
    }

    pub fn toInteropPolicy(self: DecodedInteropPolicy) abi.InteropPolicy {
        return .{
            .panic_mode = @intFromEnum(self.panic_mode),
            .allocator_mode = @intFromEnum(self.allocator_mode),
            .unsafe_scope = switch (self.unsafe_scope) {
                .none => @intFromEnum(abi.UnsafeScope.none),
                .volatile_mmio => @intFromEnum(abi.UnsafeScope.volatile_mmio),
                .raw_pointer_bridge => @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
            },
            .reserved = 0,
        };
    }
};

pub fn init(panic_mode: abi.PanicMode, allocator_mode: abi.AllocatorMode, unsafe_scope: narrow.UnsafeScopeTag) DecodedInteropPolicy {
    return .{
        .panic_mode = panic_mode,
        .allocator_mode = allocator_mode,
        .unsafe_scope = unsafe_scope,
    };
}

pub fn encode(panic_mode: abi.PanicMode, allocator_mode: abi.AllocatorMode, unsafe_scope: narrow.UnsafeScopeTag) abi.InteropPolicy {
    return init(panic_mode, allocator_mode, unsafe_scope).toInteropPolicy();
}

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
    try std.testing.expectEqual(panic_policy.Action.warn_and_return, decoded.action());
    try std.testing.expect(decoded.canReturn());
    try std.testing.expect(decoded.permitsGlobalFallback());
    try std.testing.expect(decoded.initializesOwnedState());
    try std.testing.expect(!decoded.requiresResetOnInit());
    try std.testing.expectEqual(narrow.UnsafeScopeTag.volatile_mmio, decoded.unsafeScope());
    try std.testing.expect(decoded.permitsVolatileMmio());
    try std.testing.expect(!decoded.permitsRawPointerBridge());
}

test "phase3 interop policy decoder keeps the panic action explicit" {
    const abort_policy = try decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    });
    try std.testing.expectEqual(panic_policy.Action.abort_now, abort_policy.action());
    try std.testing.expect(!abort_policy.canReturn());

    const bug_policy = try decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    });
    try std.testing.expectEqual(panic_policy.Action.bug_check, bug_policy.action());
    try std.testing.expect(!bug_policy.canReturn());

    const warn_policy = try decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    });
    try std.testing.expectEqual(panic_policy.Action.warn_and_return, warn_policy.action());
    try std.testing.expect(warn_policy.canReturn());
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

test "phase3 interop policy decoder keeps raw-pointer bridge consumers explicit" {
    var words = [_]u32{ 7, 11 };
    const base = narrow.addressOf(&words[0]);

    const raw_pointer_policy = try decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    });
    const mmio_policy = try decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    });

    const words_slice = try raw_pointer_policy.constSliceAt(u32, base, words.len);
    try std.testing.expectEqual(@as(u32, 7), words_slice[0]);
    const second_word = try raw_pointer_policy.constPointerAt(u32, base + @sizeOf(u32));
    try std.testing.expectEqual(@as(u32, 11), second_word.*);
    try std.testing.expectEqual(@as(u32, 11), try raw_pointer_policy.readValueAt(u32, base + @sizeOf(u32)));

    try std.testing.expectError(error.UnsafeScopeDenied, mmio_policy.constSliceAt(u32, base, words.len));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio_policy.constPointerAt(u32, base));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio_policy.readValueAt(u32, base));
    try std.testing.expectError(error.MisalignedAccess, raw_pointer_policy.constSliceAt(u32, base + 1, 1));
    try std.testing.expectError(error.MisalignedAccess, raw_pointer_policy.constPointerAt(u32, base + 1));
    try std.testing.expectError(error.MisalignedAccess, raw_pointer_policy.readValueAt(u32, base + 1));
    try std.testing.expectError(error.AddressOverflow, raw_pointer_policy.constSliceAt(u32, 4, std.math.maxInt(usize)));
}

test "phase3 interop policy keeps canonical abi encoding explicit" {
    const decoded = init(.warn, .arena, .raw_pointer_bridge);
    const encoded = decoded.toInteropPolicy();
    try std.testing.expectEqual(@as(u8, @intFromEnum(abi.PanicMode.warn)), encoded.panic_mode);
    try std.testing.expectEqual(@as(u8, @intFromEnum(abi.AllocatorMode.arena)), encoded.allocator_mode);
    try std.testing.expectEqual(@as(u8, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge)), encoded.unsafe_scope);
    try std.testing.expectEqual(@as(u8, 0), encoded.reserved);

    const round_trip = try decode(encoded);
    try std.testing.expectEqual(decoded.panic_mode, round_trip.panic_mode);
    try std.testing.expectEqual(decoded.allocator_mode, round_trip.allocator_mode);
    try std.testing.expectEqual(decoded.unsafeScope(), round_trip.unsafeScope());
}

test "phase3 interop policy encode helper preserves explicit policy behavior" {
    const policy = encode(.abort, .kernel_heap, .volatile_mmio);
    const decoded = try decode(policy);
    try std.testing.expectEqual(panic_policy.Action.abort_now, decoded.action());
    try std.testing.expect(!decoded.canReturn());
    try std.testing.expect(decoded.permitsGlobalFallback());
    try std.testing.expect(decoded.initializesOwnedState());
    try std.testing.expect(!decoded.requiresResetOnInit());
    try std.testing.expect(decoded.permitsVolatileMmio());
    try std.testing.expect(!decoded.permitsRawPointerBridge());
    try std.testing.expect(recognizes(policy));
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
