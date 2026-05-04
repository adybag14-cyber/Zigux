const std = @import("std");
const abi = @import("abi_bindings");
const interop_policy = @import("interop_policy");
const narrow = @import("narrow_unsafe");

pub fn range(base_addr: usize, length: u32, stride: u32) abi.MmioRange {
    return .{
        .base_addr = base_addr,
        .length = length,
        .stride = stride,
    };
}

fn scopeFromPolicy(policy: interop_policy.DecodedInteropPolicy) narrow.ScopeError!narrow.UnsafeScopeTag {
    if (!policy.permitsVolatileMmio()) return error.UnsafeScopeDenied;
    return policy.unsafe_scope;
}

fn ensureApprovedPolicyWidth(comptime T: type) void {
    switch (@typeInfo(T)) {
        .int => |int_info| {
            if (int_info.signedness != .unsigned) {
                @compileError("mmio policy bridges only support unsigned integer widths");
            }
        },
        else => @compileError("mmio policy bridges only support integer widths"),
    }

    const bits = @bitSizeOf(T);
    if (!(bits == 8 or bits == 16 or bits == 32 or bits == 64)) {
        @compileError("mmio policy bridges only support 8, 16, 32, or 64-bit widths");
    }
}

fn readScopedBridge(
    comptime T: type,
    scope: narrow.UnsafeScopeTag,
    base_addr: usize,
    offset: usize,
) narrow.ScopeError!T {
    ensureApprovedPolicyWidth(T);
    const ptr = try narrow.scopedPointerAt(T, scope, base_addr, offset);
    return ptr.*;
}

fn writeScopedBridge(
    comptime T: type,
    scope: narrow.UnsafeScopeTag,
    base_addr: usize,
    offset: usize,
    value: T,
) narrow.ScopeError!void {
    ensureApprovedPolicyWidth(T);
    const ptr = try narrow.scopedPointerAt(T, scope, base_addr, offset);
    ptr.* = value;
}

pub fn readScopedWithPolicy(
    comptime T: type,
    policy: interop_policy.DecodedInteropPolicy,
    base_addr: usize,
    offset: usize,
) narrow.ScopeError!T {
    return readScopedBridge(T, try scopeFromPolicy(policy), base_addr, offset);
}

pub fn writeScopedWithPolicy(
    comptime T: type,
    policy: interop_policy.DecodedInteropPolicy,
    base_addr: usize,
    offset: usize,
    value: T,
) narrow.ScopeError!void {
    try writeScopedBridge(T, try scopeFromPolicy(policy), base_addr, offset, value);
}

pub fn read8Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u8 {
    return readScopedBridge(u8, scope, base_addr, offset);
}

pub fn write8Scoped(
    scope: narrow.UnsafeScopeTag,
    base_addr: usize,
    offset: usize,
    value: u8,
) narrow.ScopeError!void {
    try writeScopedBridge(u8, scope, base_addr, offset, value);
}

pub fn read16Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u16 {
    return readScopedBridge(u16, scope, base_addr, offset);
}

pub fn write16Scoped(
    scope: narrow.UnsafeScopeTag,
    base_addr: usize,
    offset: usize,
    value: u16,
) narrow.ScopeError!void {
    try writeScopedBridge(u16, scope, base_addr, offset, value);
}

pub fn read32Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u32 {
    return readScopedBridge(u32, scope, base_addr, offset);
}

pub fn write32Scoped(
    scope: narrow.UnsafeScopeTag,
    base_addr: usize,
    offset: usize,
    value: u32,
) narrow.ScopeError!void {
    try writeScopedBridge(u32, scope, base_addr, offset, value);
}

pub fn read64Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u64 {
    return readScopedBridge(u64, scope, base_addr, offset);
}

pub fn write64Scoped(
    scope: narrow.UnsafeScopeTag,
    base_addr: usize,
    offset: usize,
    value: u64,
) narrow.ScopeError!void {
    try writeScopedBridge(u64, scope, base_addr, offset, value);
}

pub fn read8Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u8 {
    return readScopedWithPolicy(u8, policy, base_addr, offset);
}

pub fn write8Policy(
    policy: interop_policy.DecodedInteropPolicy,
    base_addr: usize,
    offset: usize,
    value: u8,
) narrow.ScopeError!void {
    try writeScopedWithPolicy(u8, policy, base_addr, offset, value);
}

pub fn read16Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u16 {
    return readScopedWithPolicy(u16, policy, base_addr, offset);
}

pub fn write16Policy(
    policy: interop_policy.DecodedInteropPolicy,
    base_addr: usize,
    offset: usize,
    value: u16,
) narrow.ScopeError!void {
    try writeScopedWithPolicy(u16, policy, base_addr, offset, value);
}

pub fn read32Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u32 {
    return readScopedWithPolicy(u32, policy, base_addr, offset);
}

pub fn write32Policy(
    policy: interop_policy.DecodedInteropPolicy,
    base_addr: usize,
    offset: usize,
    value: u32,
) narrow.ScopeError!void {
    try writeScopedWithPolicy(u32, policy, base_addr, offset, value);
}

pub fn read64Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u64 {
    return readScopedWithPolicy(u64, policy, base_addr, offset);
}

pub fn write64Policy(
    policy: interop_policy.DecodedInteropPolicy,
    base_addr: usize,
    offset: usize,
    value: u64,
) narrow.ScopeError!void {
    try writeScopedWithPolicy(u64, policy, base_addr, offset, value);
}

pub fn read8(base_addr: usize, offset: usize) u8 {
    return read8Scoped(.volatile_mmio, base_addr, offset) catch unreachable;
}

pub fn write8(base_addr: usize, offset: usize, value: u8) void {
    write8Scoped(.volatile_mmio, base_addr, offset, value) catch unreachable;
}

pub fn read16(base_addr: usize, offset: usize) u16 {
    return read16Scoped(.volatile_mmio, base_addr, offset) catch unreachable;
}

pub fn write16(base_addr: usize, offset: usize, value: u16) void {
    write16Scoped(.volatile_mmio, base_addr, offset, value) catch unreachable;
}

pub fn read32(base_addr: usize, offset: usize) u32 {
    return read32Scoped(.volatile_mmio, base_addr, offset) catch unreachable;
}

pub fn write32(base_addr: usize, offset: usize, value: u32) void {
    write32Scoped(.volatile_mmio, base_addr, offset, value) catch unreachable;
}

pub fn read64(base_addr: usize, offset: usize) u64 {
    return read64Scoped(.volatile_mmio, base_addr, offset) catch unreachable;
}

pub fn write64(base_addr: usize, offset: usize, value: u64) void {
    write64Scoped(.volatile_mmio, base_addr, offset, value) catch unreachable;
}

test "phase3 mmio wrapper uses bounded volatile access" {
    var regs32 = [_]u32{ 0, 0 };
    const base32 = narrow.addressOf(&regs32[0]);
    write8(base32, 1, 0x5a);
    try std.testing.expectEqual(@as(u8, 0x5a), read8(base32, 1));
    write16(base32, 0, 0xbeef);
    try std.testing.expectEqual(@as(u16, 0xbeef), read16(base32, 0));

    write32(base32, @sizeOf(u32), 0xfeedbeef);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), regs32[1]);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), read32(base32, @sizeOf(u32)));

    var regs64 = [_]u64{ 0, 0 };
    const base64 = narrow.addressOf(&regs64[0]);
    write64(base64, @sizeOf(u64), 0x0123_4567_89ab_cdef);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), regs64[1]);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), read64(base64, @sizeOf(u64)));

    const desc = range(base32, 8, 4);
    try std.testing.expectEqual(base32, desc.base_addr);
    try std.testing.expectEqual(@as(u32, 8), desc.length);
    try std.testing.expectEqual(@as(u32, 4), desc.stride);
}

test "phase3 mmio wrapper consumes decoded interop policy" {
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

    try write32Policy(mmio_policy, base32, @sizeOf(u32), 0xaabbccdd);
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), regs32[1]);
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), try read32Policy(mmio_policy, base32, @sizeOf(u32)));
    try write64Policy(mmio_policy, base64, @sizeOf(u64), 0x0123_4567_89ab_cdef);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), regs64[1]);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), try read64Policy(mmio_policy, base64, @sizeOf(u64)));

    try writeScopedWithPolicy(u8, mmio_policy, base32, 1, 0x3c);
    try std.testing.expectEqual(@as(u8, 0x3c), try readScopedWithPolicy(u8, mmio_policy, base32, 1));
    try writeScopedWithPolicy(u16, mmio_policy, base32, 0, 0x7bcd);
    try std.testing.expectEqual(@as(u16, 0x7bcd), try readScopedWithPolicy(u16, mmio_policy, base32, 0));
    try writeScopedWithPolicy(u32, mmio_policy, base32, @sizeOf(u32), 0xdecafbad);
    try std.testing.expectEqual(@as(u32, 0xdecafbad), regs32[1]);
    try std.testing.expectEqual(@as(u32, 0xdecafbad), try readScopedWithPolicy(u32, mmio_policy, base32, @sizeOf(u32)));
    try writeScopedWithPolicy(u64, mmio_policy, base64, 0, 0x5555_6666_7777_8888);
    try std.testing.expectEqual(@as(u64, 0x5555_6666_7777_8888), regs64[0]);
    try std.testing.expectEqual(@as(u64, 0x5555_6666_7777_8888), try readScopedWithPolicy(u64, mmio_policy, base64, 0));

    try std.testing.expectError(error.UnsafeScopeDenied, write32Policy(raw_pointer_policy, base32, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, read32Policy(raw_pointer_policy, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, write32Policy(none_policy, base32, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, read32Policy(none_policy, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, write64Policy(raw_pointer_policy, base64, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, read64Policy(raw_pointer_policy, base64, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, write64Policy(none_policy, base64, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, read64Policy(none_policy, base64, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, writeScopedWithPolicy(u16, raw_pointer_policy, base32, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, readScopedWithPolicy(u16, raw_pointer_policy, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, writeScopedWithPolicy(u64, none_policy, base64, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, readScopedWithPolicy(u64, none_policy, base64, 0));
}

test "phase3 mmio wrapper keeps declared scope explicit across widths" {
    var regs32 = [_]u32{ 0, 0 };
    const base32 = narrow.addressOf(&regs32[0]);

    try std.testing.expectError(error.UnsafeScopeDenied, write8Scoped(.none, base32, 0, 0xab));
    try std.testing.expectError(error.UnsafeScopeDenied, read8Scoped(.raw_pointer_bridge, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, write16Scoped(.none, base32, 0, 0xabcd));
    try std.testing.expectError(error.UnsafeScopeDenied, read16Scoped(.raw_pointer_bridge, base32, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, write32Scoped(.none, base32, 0, 0x12345678));
    try std.testing.expectError(error.UnsafeScopeDenied, read32Scoped(.raw_pointer_bridge, base32, 0));

    try write8Scoped(.volatile_mmio, base32, 1, 0xab);
    try std.testing.expectEqual(@as(u8, 0xab), try read8Scoped(.volatile_mmio, base32, 1));
    try write16Scoped(.volatile_mmio, base32, 0, 0xabcd);
    try std.testing.expectEqual(@as(u16, 0xabcd), try read16Scoped(.volatile_mmio, base32, 0));
    try write32Scoped(.volatile_mmio, base32, @sizeOf(u32), 0xaabbccdd);
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), regs32[1]);
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), try read32Scoped(.volatile_mmio, base32, @sizeOf(u32)));

    var regs64 = [_]u64{ 0, 0 };
    const base64 = narrow.addressOf(&regs64[0]);
    try std.testing.expectError(error.UnsafeScopeDenied, write64Scoped(.none, base64, 0, 0x0123_4567_89ab_cdef));
    try std.testing.expectError(error.UnsafeScopeDenied, read64Scoped(.raw_pointer_bridge, base64, 0));
    try write64Scoped(.volatile_mmio, base64, @sizeOf(u64), 0x0123_4567_89ab_cdef);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), regs64[1]);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), try read64Scoped(.volatile_mmio, base64, @sizeOf(u64)));
}

test "phase3 mmio wrapper shares one bounded scoped bridge" {
    var regs32 = [_]u32{ 0, 0, 0 };
    const base32 = narrow.addressOf(&regs32[0]);
    try std.testing.expectError(error.UnsafeScopeDenied, writeScopedBridge(u8, .none, base32, 0, 0xab));
    try std.testing.expectError(error.UnsafeScopeDenied, readScopedBridge(u8, .raw_pointer_bridge, base32, 0));

    try writeScopedBridge(u16, .volatile_mmio, base32, 0, 0xabcd);
    try std.testing.expectEqual(@as(u16, 0xabcd), try readScopedBridge(u16, .volatile_mmio, base32, 0));
    try writeScopedBridge(u32, .volatile_mmio, base32, @sizeOf(u32), 0xaabbccdd);
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), regs32[1]);
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), try readScopedBridge(u32, .volatile_mmio, base32, @sizeOf(u32)));

    var regs64 = [_]u64{ 0, 0 };
    const base64 = narrow.addressOf(&regs64[0]);
    try writeScopedBridge(u64, .volatile_mmio, base64, @sizeOf(u64), 0x0123_4567_89ab_cdef);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), regs64[1]);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), try readScopedBridge(u64, .volatile_mmio, base64, @sizeOf(u64)));

    try std.testing.expectError(error.MisalignedAccess, writeScopedBridge(u16, .volatile_mmio, base32, 1, 0xabcd));
    try std.testing.expectError(error.MisalignedAccess, readScopedBridge(u32, .volatile_mmio, base32, 2));
    try std.testing.expectError(error.AddressOverflow, writeScopedBridge(u64, .volatile_mmio, std.math.maxInt(usize), 8, 1));
    try std.testing.expectError(error.AddressOverflow, readScopedBridge(u8, .volatile_mmio, std.math.maxInt(usize), 1));
}

test "phase3 mmio wrapper rejects misaligned scoped accesses" {
    var regs32 = [_]u32{ 0, 0, 0 };
    const base32 = narrow.addressOf(&regs32[0]);
    try std.testing.expectError(error.MisalignedAccess, write16Scoped(.volatile_mmio, base32, 1, 0xabcd));
    try std.testing.expectError(error.MisalignedAccess, read16Scoped(.volatile_mmio, base32, 1));
    try std.testing.expectError(error.MisalignedAccess, write32Scoped(.volatile_mmio, base32, 2, 0x12345678));
    try std.testing.expectError(error.MisalignedAccess, read32Scoped(.volatile_mmio, base32, 2));

    var regs64 = [_]u64{ 0, 0 };
    const base64 = narrow.addressOf(&regs64[0]);
    try std.testing.expectError(error.MisalignedAccess, write64Scoped(.volatile_mmio, base64, 4, 0x0123_4567_89ab_cdef));
    try std.testing.expectError(error.MisalignedAccess, read64Scoped(.volatile_mmio, base64, 4));
}

test "phase3 mmio wrapper rejects overflowed scoped accesses" {
    const max = std.math.maxInt(usize);

    try std.testing.expectError(error.AddressOverflow, write8Scoped(.volatile_mmio, max, 1, 0xab));
    try std.testing.expectError(error.AddressOverflow, read8Scoped(.volatile_mmio, max, 1));
    try std.testing.expectError(error.AddressOverflow, write16Scoped(.volatile_mmio, max, 1, 0xabcd));
    try std.testing.expectError(error.AddressOverflow, read16Scoped(.volatile_mmio, max, 1));
    try std.testing.expectError(error.AddressOverflow, write32Scoped(.volatile_mmio, max, 4, 0x12345678));
    try std.testing.expectError(error.AddressOverflow, read32Scoped(.volatile_mmio, max, 4));
    try std.testing.expectError(error.AddressOverflow, write64Scoped(.volatile_mmio, max, 8, 0x0123_4567_89ab_cdef));
    try std.testing.expectError(error.AddressOverflow, read64Scoped(.volatile_mmio, max, 8));
}
