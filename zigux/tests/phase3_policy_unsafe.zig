const std = @import("std");
const abi = @import("abi_bindings");
const panic_policy = @import("panic_policy");
const allocator_policy = @import("allocator_policy");
const interop_policy = @import("interop_policy");
const layout_assert = @import("layout_assert");
const mmio = @import("mmio");
const narrow = @import("narrow_unsafe");

test "phase3 policy helpers stay ABI aligned" {
    try std.testing.expectEqual(panic_policy.Action.abort_now, panic_policy.actionFor(.abort));
    try std.testing.expectEqual(panic_policy.Action.bug_check, panic_policy.actionFor(.bug));
    try std.testing.expectEqual(panic_policy.Action.warn_and_return, panic_policy.actionFor(.warn));
    try std.testing.expect(!panic_policy.canReturn(.abort));
    try std.testing.expect(!panic_policy.canReturn(.bug));
    try std.testing.expect(panic_policy.canReturn(.warn));
    try std.testing.expectEqual(abi.PanicMode.abort, panic_policy.modeFromInteropPolicyByte(@intFromEnum(abi.PanicMode.abort)).?);
    try std.testing.expectEqual(abi.PanicMode.bug, panic_policy.modeFromInteropPolicyByte(@intFromEnum(abi.PanicMode.bug)).?);
    try std.testing.expectEqual(abi.PanicMode.warn, panic_policy.modeFromInteropPolicyByte(@intFromEnum(abi.PanicMode.warn)).?);
    try std.testing.expect(panic_policy.recognizesInteropPolicyByte(@intFromEnum(abi.PanicMode.warn)));
    try std.testing.expect(!panic_policy.recognizesInteropPolicyByte(9));
    try std.testing.expect(panic_policy.canReturnPolicyByte(@intFromEnum(abi.PanicMode.warn)));
    try std.testing.expect(!panic_policy.canReturnPolicyByte(@intFromEnum(abi.PanicMode.abort)));
    try std.testing.expect(!panic_policy.canReturnPolicyByte(9));

    try std.testing.expectEqual(allocator_policy.InitFlow.caller_prepared, allocator_policy.initFlowFor(.caller_provided));
    try std.testing.expectEqual(allocator_policy.InitFlow.helper_owned, allocator_policy.initFlowFor(.kernel_heap));
    try std.testing.expectEqual(allocator_policy.InitFlow.helper_owned_with_reset, allocator_policy.initFlowFor(.arena));
    try std.testing.expectEqual(abi.AllocatorMode.caller_provided, allocator_policy.modeFromInteropPolicyByte(@intFromEnum(abi.AllocatorMode.caller_provided)).?);
    try std.testing.expectEqual(abi.AllocatorMode.kernel_heap, allocator_policy.modeFromInteropPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)).?);
    try std.testing.expectEqual(abi.AllocatorMode.arena, allocator_policy.modeFromInteropPolicyByte(@intFromEnum(abi.AllocatorMode.arena)).?);
    try std.testing.expect(allocator_policy.recognizesInteropPolicyByte(@intFromEnum(abi.AllocatorMode.arena)));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicyByte(9));
    try std.testing.expect(allocator_policy.requiresExplicitCallerPolicyByte(@intFromEnum(abi.AllocatorMode.caller_provided)));
    try std.testing.expect(!allocator_policy.permitsGlobalFallback(.caller_provided));
    try std.testing.expect(allocator_policy.permitsGlobalFallback(.kernel_heap));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)));
    try std.testing.expect(allocator_policy.requiresResetOnInit(.arena));
    try std.testing.expect(allocator_policy.initializesOwnedStatePolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)));
    try std.testing.expect(allocator_policy.requiresResetOnInitPolicyByte(@intFromEnum(abi.AllocatorMode.arena)));
    try std.testing.expect(!allocator_policy.permitsGlobalFallbackPolicyByte(9));
}

test "phase3 policy layout stays explicit at the ABI boundary" {
    comptime {
        layout_assert.assertInteropPolicyLayout();
    }

    const policy: abi.InteropPolicy = .{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    try std.testing.expectEqual(@intFromEnum(abi.PanicMode.warn), policy.panic_mode);
    try std.testing.expectEqual(@intFromEnum(abi.AllocatorMode.arena), policy.allocator_mode);
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge), policy.unsafe_scope);
}

test "phase3 policy decoder validates the whole interop record" {
    const decoded = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    });
    try std.testing.expect(decoded.canReturn());
    try std.testing.expect(decoded.requiresExplicitCaller());
    try std.testing.expect(!decoded.permitsGlobalFallback());
    try std.testing.expect(!decoded.initializesOwnedState());
    try std.testing.expect(!decoded.requiresResetOnInit());
    try std.testing.expect(decoded.permitsRawPointerBridge());
    try std.testing.expect(!decoded.permitsVolatileMmio());
    try std.testing.expect(interop_policy.recognizes(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    }));
}

test "phase3 policy decoder keeps allocator init and reset requirements reviewable" {
    const kernel_heap = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    });
    try std.testing.expect(kernel_heap.permitsGlobalFallback());
    try std.testing.expect(kernel_heap.initializesOwnedState());
    try std.testing.expect(!kernel_heap.requiresResetOnInit());

    const arena = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    });
    try std.testing.expect(arena.permitsGlobalFallback());
    try std.testing.expect(arena.initializesOwnedState());
    try std.testing.expect(arena.requiresResetOnInit());
}

test "phase3 policy decoder rejects partial or reserved policy bytes" {
    try std.testing.expectError(error.InvalidPanicMode, interop_policy.decode(.{
        .panic_mode = 9,
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    }));
    try std.testing.expectError(error.InvalidAllocatorMode, interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = 9,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    }));
    try std.testing.expectError(error.ReservedBitsSet, interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 1,
    }));
    try std.testing.expectError(error.InvalidUnsafeScope, interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = 9,
        .reserved = 0,
    }));
}

test "phase3 policy encoder keeps a canonical interop record" {
    const encoded = interop_policy.encode(.warn, .arena, .raw_pointer_bridge);
    try std.testing.expectEqual(@as(u8, @intFromEnum(abi.PanicMode.warn)), encoded.panic_mode);
    try std.testing.expectEqual(@as(u8, @intFromEnum(abi.AllocatorMode.arena)), encoded.allocator_mode);
    try std.testing.expectEqual(@as(u8, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge)), encoded.unsafe_scope);
    try std.testing.expectEqual(@as(u8, 0), encoded.reserved);

    const decoded = try interop_policy.decode(encoded);
    try std.testing.expect(decoded.canReturn());
    try std.testing.expect(decoded.permitsGlobalFallback());
    try std.testing.expect(decoded.initializesOwnedState());
    try std.testing.expect(decoded.requiresResetOnInit());
    try std.testing.expect(decoded.permitsRawPointerBridge());
    try std.testing.expect(!decoded.permitsVolatileMmio());
}

test "phase3 policy init helper round trips through decode without widening scope" {
    const decoded = interop_policy.init(.abort, .caller_provided, .none);
    const encoded = decoded.toInteropPolicy();
    const round_trip = try interop_policy.decode(encoded);
    try std.testing.expectEqual(decoded.panic_mode, round_trip.panic_mode);
    try std.testing.expectEqual(decoded.allocator_mode, round_trip.allocator_mode);
    try std.testing.expectEqual(decoded.unsafe_scope, round_trip.unsafe_scope);
    try std.testing.expectEqual(@as(u8, @intFromEnum(abi.UnsafeScope.none)), encoded.unsafe_scope);
}

test "phase3 policy gate reaches a second boundary helper through decoded policy" {
    var regs32 = [_]u32{ 0, 0 };
    const base32 = narrow.addressOf(&regs32[0]);
    var regs64 = [_]u64{ 0, 0 };
    const base64 = narrow.addressOf(&regs64[0]);

    const mmio_policy = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    });
    const raw_pointer_policy = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    });
    const none_policy = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    });

    try mmio.writeScopedWithPolicy(u32, mmio_policy, base32, 0, 0x10213243);
    try std.testing.expectEqual(@as(u32, 0x10213243), regs32[0]);
    try std.testing.expectEqual(@as(u32, 0x10213243), try mmio.readScopedWithPolicy(u32, mmio_policy, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeScopedWithPolicy(u32, raw_pointer_policy, base32, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.readScopedWithPolicy(u32, raw_pointer_policy, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeScopedWithPolicy(u32, none_policy, base32, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.readScopedWithPolicy(u32, none_policy, base32, 0));

    try mmio.write8Policy(mmio_policy, base32, 0, 0x2a);
    try std.testing.expectEqual(@as(u8, 0x2a), try mmio.read8Policy(mmio_policy, base32, 0));
    try mmio.write16Policy(mmio_policy, base32, 2, 0x7bcd);
    try std.testing.expectEqual(@as(u16, 0x7bcd), try mmio.read16Policy(mmio_policy, base32, 2));
    try mmio.write32Policy(mmio_policy, base32, @sizeOf(u32), 0xdecafbad);
    try std.testing.expectEqual(@as(u32, 0xdecafbad), regs32[1]);
    try std.testing.expectEqual(@as(u32, 0xdecafbad), try mmio.read32Policy(mmio_policy, base32, @sizeOf(u32)));
    try mmio.write64Policy(mmio_policy, base64, @sizeOf(u64), 0x1111_2222_3333_4444);
    try std.testing.expectEqual(@as(u64, 0x1111_2222_3333_4444), regs64[1]);
    try std.testing.expectEqual(@as(u64, 0x1111_2222_3333_4444), try mmio.read64Policy(mmio_policy, base64, @sizeOf(u64)));

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Policy(raw_pointer_policy, base32, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8Policy(raw_pointer_policy, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Policy(none_policy, base32, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8Policy(none_policy, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Policy(raw_pointer_policy, base32, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read16Policy(raw_pointer_policy, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Policy(none_policy, base32, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read16Policy(none_policy, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(raw_pointer_policy, base32, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(raw_pointer_policy, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(none_policy, base32, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(none_policy, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Policy(raw_pointer_policy, base64, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read64Policy(raw_pointer_policy, base64, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Policy(none_policy, base64, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read64Policy(none_policy, base64, 0));
}

test "phase3 policy gate reaches raw-pointer bridge consumers through decoded policy" {
    var words = [_]u32{ 7, 11 };
    const base = narrow.addressOf(&words[0]);

    const raw_pointer_policy = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    });
    const mmio_policy = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    });
    const none_policy = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
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
    try std.testing.expectError(error.UnsafeScopeDenied, none_policy.constSliceAt(u32, base, words.len));
    try std.testing.expectError(error.UnsafeScopeDenied, none_policy.constPointerAt(u32, base));
    try std.testing.expectError(error.UnsafeScopeDenied, none_policy.readValueAt(u32, base));
    try std.testing.expectError(error.MisalignedAccess, raw_pointer_policy.constSliceAt(u32, base + 1, 1));
    try std.testing.expectError(error.MisalignedAccess, raw_pointer_policy.constPointerAt(u32, base + 1));
    try std.testing.expectError(error.MisalignedAccess, raw_pointer_policy.readValueAt(u32, base + 1));
    try std.testing.expectError(error.AddressOverflow, raw_pointer_policy.constSliceAt(u32, 4, std.math.maxInt(usize)));
}

test "phase3 narrow unsafe helpers stay explicit" {
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.none), @intFromEnum(narrow.UnsafeScopeTag.none));
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.volatile_mmio), @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio));
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge), @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge));

    try std.testing.expect(!narrow.permitsVolatileMmio(.none));
    try std.testing.expect(narrow.permitsVolatileMmio(.volatile_mmio));
    try std.testing.expect(!narrow.permitsVolatileMmio(.raw_pointer_bridge));

    try std.testing.expect(!narrow.permitsRawPointerBridge(.none));
    try std.testing.expect(!narrow.permitsRawPointerBridge(.volatile_mmio));
    try std.testing.expect(narrow.permitsRawPointerBridge(.raw_pointer_bridge));

    var words = [_]u32{ 7, 11 };
    const base = narrow.addressOf(&words[0]);
    try std.testing.expectEqual(base + @sizeOf(u32), narrow.byteOffset(base, @sizeOf(u32)));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.constSliceAt(u32, .volatile_mmio, base, words.len));
    const words_slice = try narrow.constSliceAt(u32, .raw_pointer_bridge, base, words.len);
    try std.testing.expectEqual(@as(u32, 7), words_slice[0]);
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.constPointerAt(u32, .volatile_mmio, base));
    const second_word = try narrow.constPointerAt(u32, .raw_pointer_bridge, base + @sizeOf(u32));
    try std.testing.expectEqual(@as(u32, 11), second_word.*);
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.constValueAt(u32, .volatile_mmio, base));
    try std.testing.expectEqual(@as(u32, 11), try narrow.constValueAt(u32, .raw_pointer_bridge, base + @sizeOf(u32)));
}

test "phase3 policy gate decodes interop-policy unsafe bytes explicitly" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const invalid_scope_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = 9,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 1,
    };

    try std.testing.expectEqual(narrow.UnsafeScopeTag.volatile_mmio, narrow.scopeFromInteropPolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved).?);
    try std.testing.expect(narrow.recognizesInteropPolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved));
    try std.testing.expect(narrow.permitsVolatileMmioPolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved));
    try std.testing.expect(!narrow.permitsRawPointerBridgePolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved));

    try std.testing.expectEqual(narrow.UnsafeScopeTag.raw_pointer_bridge, narrow.scopeFromInteropPolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved).?);
    try std.testing.expect(narrow.recognizesInteropPolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved));
    try std.testing.expect(!narrow.permitsVolatileMmioPolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved));
    try std.testing.expect(narrow.permitsRawPointerBridgePolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved));

    try std.testing.expectEqual(@as(?narrow.UnsafeScopeTag, null), narrow.scopeFromInteropPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));
    try std.testing.expect(!narrow.recognizesInteropPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));
    try std.testing.expect(!narrow.permitsVolatileMmioPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));
    try std.testing.expect(!narrow.permitsRawPointerBridgePolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));

    try std.testing.expectEqual(@as(?narrow.UnsafeScopeTag, null), narrow.scopeFromInteropPolicyBytes(reserved_policy.unsafe_scope, reserved_policy.reserved));
    try std.testing.expect(!narrow.recognizesInteropPolicyBytes(reserved_policy.unsafe_scope, reserved_policy.reserved));
}

test "phase3 policy gate enforces the declared unsafe scope" {
    var value: u32 = 11;
    const base = narrow.addressOf(&value);

    try std.testing.expectError(error.UnsafeScopeDenied, narrow.pointerAt(u32, .none, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedPointerAt(u32, .none, base, 0));
    const mmio_ptr = try narrow.pointerAt(u32, .volatile_mmio, base, 0);
    mmio_ptr.* = 17;
    try std.testing.expectEqual(@as(u32, 17), value);

    try std.testing.expectError(error.UnsafeScopeDenied, narrow.constSliceAt(u32, .volatile_mmio, base, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstSliceAt(u32, .volatile_mmio, base, 1));
    const raw_slice = try narrow.constSliceAt(u32, .raw_pointer_bridge, base, 1);
    try std.testing.expectEqual(@as(u32, 17), raw_slice[0]);

    try std.testing.expectError(error.UnsafeScopeDenied, narrow.constPointerAt(u32, .volatile_mmio, base));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstPointerAt(u32, .volatile_mmio, base));
    const raw_ptr = try narrow.constPointerAt(u32, .raw_pointer_bridge, base);
    try std.testing.expectEqual(@as(u32, 17), raw_ptr.*);
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.constValueAt(u32, .volatile_mmio, base));
    try std.testing.expectEqual(@as(u32, 17), try narrow.constValueAt(u32, .raw_pointer_bridge, base));

    try std.testing.expectError(error.MisalignedAccess, narrow.scopedPointerAt(u32, .volatile_mmio, base, 1));
    try std.testing.expectError(error.MisalignedAccess, narrow.scopedConstSliceAt(u32, .raw_pointer_bridge, base + 1, 1));
    try std.testing.expectError(error.MisalignedAccess, narrow.scopedConstPointerAt(u32, .raw_pointer_bridge, base + 1));
    try std.testing.expectError(error.MisalignedAccess, narrow.scopedConstValueAt(u32, .raw_pointer_bridge, base + 1));
}

test "phase3 policy gate rejects overflowed unsafe address math" {
    const max = std.math.maxInt(usize);

    try std.testing.expectError(error.AddressOverflow, narrow.checkedByteOffset(max, 1));
    try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanBytes(u32, max));
    try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanEnd(u32, 4, max));
    try std.testing.expectError(error.AddressOverflow, narrow.scopedPointerAt(u32, .volatile_mmio, max, 1));
    try std.testing.expectError(error.AddressOverflow, narrow.scopedConstSliceAt(u32, .raw_pointer_bridge, 4, max));
}
