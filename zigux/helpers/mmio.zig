const std = @import("std");
const abi = @import("abi_bindings");
const narrow = @import("narrow_unsafe");

pub const MmioError = narrow.UnsafeScopeError;

pub const Range = struct {
    base_addr: usize,
    length: u32,
    stride: u32,
};

fn pointerAt(comptime T: type, base_addr: usize, offset: usize) *align(1) volatile T {
    return narrow.pointerAt(T, base_addr, offset);
}

fn readValue(comptime T: type, base_addr: usize, offset: usize) T {
    return pointerAt(T, base_addr, offset).*;
}

fn writeValue(comptime T: type, base_addr: usize, offset: usize, value: T) void {
    pointerAt(T, base_addr, offset).* = value;
}

pub fn requireInteropPolicyBytes(unsafe_scope: u8, reserved: u8) MmioError!void {
    try narrow.requireVolatileMmioPolicyBytes(unsafe_scope, reserved);
}

fn readPolicyValueBytes(
    comptime T: type,
    base_addr: usize,
    offset: usize,
    unsafe_scope: u8,
    reserved: u8,
) MmioError!T {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return readValue(T, base_addr, offset);
}

fn writePolicyValueBytes(
    comptime T: type,
    base_addr: usize,
    offset: usize,
    value: T,
    unsafe_scope: u8,
    reserved: u8,
) MmioError!void {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    writeValue(T, base_addr, offset, value);
}

pub fn range(base_addr: usize, length: u32, stride: u32) Range {
    return .{
        .base_addr = base_addr,
        .length = length,
        .stride = stride,
    };
}

pub fn containsOffset(desc: Range, offset: usize) bool {
    return offset < @as(usize, desc.length);
}

pub fn containsAccess(desc: Range, offset: usize, width: usize) bool {
    if (width == 0) return false;
    const end = std.math.add(usize, offset, width) catch return false;
    return end <= @as(usize, desc.length);
}

pub fn offsetForIndex(desc: Range, index: usize) ?usize {
    const offset = std.math.mul(usize, index, @as(usize, desc.stride)) catch return null;
    return if (containsOffset(desc, offset)) offset else null;
}

pub fn typedOffsetForIndex(desc: Range, comptime T: type, index: usize) ?usize {
    const offset = std.math.mul(usize, index, @as(usize, desc.stride)) catch return null;
    return if (containsAccess(desc, offset, @sizeOf(T))) offset else null;
}

pub fn allowsInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return narrow.permitsVolatileMmioPolicyBytes(unsafe_scope, reserved);
}

pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.permitsVolatileMmioInteropPolicy(policy);
}

pub fn allowsInteropPolicyByte(unsafe_scope: u8) bool {
    return allowsInteropPolicyBytes(unsafe_scope, 0);
}

pub fn requireInteropPolicy(policy: abi.InteropPolicy) MmioError!void {
    try narrow.requireVolatileMmioInteropPolicy(policy);
}

pub fn requireInteropPolicyByte(unsafe_scope: u8) MmioError!void {
    try requireInteropPolicyBytes(unsafe_scope, 0);
}

pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) MmioError!Range {
    try requireInteropPolicy(policy);
    return range(base_addr, length, stride);
}

pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) MmioError!Range {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return range(base_addr, length, stride);
}

pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) MmioError!Range {
    return rangeInteropPolicyBytes(base_addr, length, stride, unsafe_scope, 0);
}

pub fn read(comptime T: type, base_addr: usize, offset: usize) T {
    return readValue(T, base_addr, offset);
}

pub fn write(comptime T: type, base_addr: usize, offset: usize, value: T) void {
    writeValue(T, base_addr, offset, value);
}

pub fn read8(base_addr: usize, offset: usize) u8 {
    return read(u8, base_addr, offset);
}

pub fn read16(base_addr: usize, offset: usize) u16 {
    return read(u16, base_addr, offset);
}

pub fn read32(base_addr: usize, offset: usize) u32 {
    return read(u32, base_addr, offset);
}

pub fn read64(base_addr: usize, offset: usize) u64 {
    return read(u64, base_addr, offset);
}

pub fn write8(base_addr: usize, offset: usize, value: u8) void {
    write(u8, base_addr, offset, value);
}

pub fn write16(base_addr: usize, offset: usize, value: u16) void {
    write(u16, base_addr, offset, value);
}

pub fn write32(base_addr: usize, offset: usize, value: u32) void {
    write(u32, base_addr, offset, value);
}

pub fn write64(base_addr: usize, offset: usize, value: u64) void {
    write(u64, base_addr, offset, value);
}

pub fn readInteropPolicy(comptime T: type, base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!T {
    return readPolicyValueBytes(T, base_addr, offset, policy.unsafe_scope, policy.reserved);
}

pub fn writeInteropPolicy(
    comptime T: type,
    base_addr: usize,
    offset: usize,
    value: T,
    policy: abi.InteropPolicy,
) MmioError!void {
    try writePolicyValueBytes(T, base_addr, offset, value, policy.unsafe_scope, policy.reserved);
}

pub fn read8InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u8 {
    return readInteropPolicy(u8, base_addr, offset, policy);
}

pub fn read16InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u16 {
    return readInteropPolicy(u16, base_addr, offset, policy);
}

pub fn read32InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u32 {
    return readInteropPolicy(u32, base_addr, offset, policy);
}

pub fn read64InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u64 {
    return readInteropPolicy(u64, base_addr, offset, policy);
}

pub fn write8InteropPolicy(base_addr: usize, offset: usize, value: u8, policy: abi.InteropPolicy) MmioError!void {
    try writeInteropPolicy(u8, base_addr, offset, value, policy);
}

pub fn write16InteropPolicy(base_addr: usize, offset: usize, value: u16, policy: abi.InteropPolicy) MmioError!void {
    try writeInteropPolicy(u16, base_addr, offset, value, policy);
}

pub fn write32InteropPolicy(base_addr: usize, offset: usize, value: u32, policy: abi.InteropPolicy) MmioError!void {
    try writeInteropPolicy(u32, base_addr, offset, value, policy);
}

pub fn write64InteropPolicy(base_addr: usize, offset: usize, value: u64, policy: abi.InteropPolicy) MmioError!void {
    try writeInteropPolicy(u64, base_addr, offset, value, policy);
}

pub fn readInteropPolicyBytes(
    comptime T: type,
    base_addr: usize,
    offset: usize,
    unsafe_scope: u8,
    reserved: u8,
) MmioError!T {
    return readPolicyValueBytes(T, base_addr, offset, unsafe_scope, reserved);
}

pub fn writeInteropPolicyBytes(
    comptime T: type,
    base_addr: usize,
    offset: usize,
    value: T,
    unsafe_scope: u8,
    reserved: u8,
) MmioError!void {
    try writePolicyValueBytes(T, base_addr, offset, value, unsafe_scope, reserved);
}

pub fn read8InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) MmioError!u8 {
    return readInteropPolicyBytes(u8, base_addr, offset, unsafe_scope, reserved);
}

pub fn read16InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) MmioError!u16 {
    return readInteropPolicyBytes(u16, base_addr, offset, unsafe_scope, reserved);
}

pub fn read32InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) MmioError!u32 {
    return readInteropPolicyBytes(u32, base_addr, offset, unsafe_scope, reserved);
}

pub fn read64InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) MmioError!u64 {
    return readInteropPolicyBytes(u64, base_addr, offset, unsafe_scope, reserved);
}

pub fn write8InteropPolicyBytes(base_addr: usize, offset: usize, value: u8, unsafe_scope: u8, reserved: u8) MmioError!void {
    try writeInteropPolicyBytes(u8, base_addr, offset, value, unsafe_scope, reserved);
}

pub fn write16InteropPolicyBytes(base_addr: usize, offset: usize, value: u16, unsafe_scope: u8, reserved: u8) MmioError!void {
    try writeInteropPolicyBytes(u16, base_addr, offset, value, unsafe_scope, reserved);
}

pub fn write32InteropPolicyBytes(base_addr: usize, offset: usize, value: u32, unsafe_scope: u8, reserved: u8) MmioError!void {
    try writeInteropPolicyBytes(u32, base_addr, offset, value, unsafe_scope, reserved);
}

pub fn write64InteropPolicyBytes(base_addr: usize, offset: usize, value: u64, unsafe_scope: u8, reserved: u8) MmioError!void {
    try writeInteropPolicyBytes(u64, base_addr, offset, value, unsafe_scope, reserved);
}

pub fn readInteropPolicyByte(comptime T: type, base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!T {
    return readInteropPolicyBytes(T, base_addr, offset, unsafe_scope, 0);
}

pub fn writeInteropPolicyByte(
    comptime T: type,
    base_addr: usize,
    offset: usize,
    value: T,
    unsafe_scope: u8,
) MmioError!void {
    try writeInteropPolicyBytes(T, base_addr, offset, value, unsafe_scope, 0);
}

pub fn read8InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!u8 {
    return readInteropPolicyByte(u8, base_addr, offset, unsafe_scope);
}

pub fn read16InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!u16 {
    return readInteropPolicyByte(u16, base_addr, offset, unsafe_scope);
}

pub fn read32InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!u32 {
    return readInteropPolicyByte(u32, base_addr, offset, unsafe_scope);
}

pub fn read64InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!u64 {
    return readInteropPolicyByte(u64, base_addr, offset, unsafe_scope);
}

pub fn write8InteropPolicyByte(base_addr: usize, offset: usize, value: u8, unsafe_scope: u8) MmioError!void {
    try writeInteropPolicyByte(u8, base_addr, offset, value, unsafe_scope);
}

pub fn write16InteropPolicyByte(base_addr: usize, offset: usize, value: u16, unsafe_scope: u8) MmioError!void {
    try writeInteropPolicyByte(u16, base_addr, offset, value, unsafe_scope);
}

pub fn write32InteropPolicyByte(base_addr: usize, offset: usize, value: u32, unsafe_scope: u8) MmioError!void {
    try writeInteropPolicyByte(u32, base_addr, offset, value, unsafe_scope);
}

pub fn write64InteropPolicyByte(base_addr: usize, offset: usize, value: u64, unsafe_scope: u8) MmioError!void {
    try writeInteropPolicyByte(u64, base_addr, offset, value, unsafe_scope);
}

test "phase3 mmio wrappers keep direct reads and writes reviewable" {
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);
    const generic_halfword: *align(1) const u16 = @ptrCast(&bytes[2]);
    const generic_word: *align(1) const u32 = @ptrCast(&bytes[4]);
    const generic_doubleword: *align(1) const u64 = @ptrCast(&bytes[8]);
    const aligned_halfword: *align(1) const u16 = @ptrCast(&bytes[12]);
    const aligned_word: *align(1) const u32 = @ptrCast(&bytes[14]);
    const aligned_doubleword: *align(1) const u64 = @ptrCast(&bytes[16]);

    const desc = range(base, 24, 4);
    try std.testing.expectEqual(base, desc.base_addr);
    try std.testing.expectEqual(@as(u32, 24), desc.length);
    try std.testing.expectEqual(@as(u32, 4), desc.stride);

    write(u8, base, 0, 0xa5);
    try std.testing.expectEqual(@as(u8, 0xa5), bytes[0]);
    try std.testing.expectEqual(@as(u8, 0xa5), read(u8, base, 0));

    write(u16, base, 2, 0x1357);
    try std.testing.expectEqual(@as(u16, 0x1357), generic_halfword.*);
    try std.testing.expectEqual(@as(u16, 0x1357), read(u16, base, 2));

    write(u32, base, 4, 0xfeed_beef);
    try std.testing.expectEqual(@as(u32, 0xfeed_beef), generic_word.*);
    try std.testing.expectEqual(@as(u32, 0xfeed_beef), read(u32, base, 4));

    write(u64, base, 8, 0x0123_4567_89ab_cdef);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), generic_doubleword.*);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), read(u64, base, 8));

    write8(base, 1, 0x5a);
    try std.testing.expectEqual(@as(u8, 0x5a), read8(base, 1));

    write16(base, 12, 0xbeef);
    try std.testing.expectEqual(@as(u16, 0xbeef), aligned_halfword.*);
    try std.testing.expectEqual(@as(u16, 0xbeef), read16(base, 12));

    write32(base, 14, 0x89ab_cdef);
    try std.testing.expectEqual(@as(u32, 0x89ab_cdef), aligned_word.*);
    try std.testing.expectEqual(@as(u32, 0x89ab_cdef), read32(base, 14));

    write64(base, 16, 0xfedc_ba98_7654_3210);
    try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), aligned_doubleword.*);
    try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), read64(base, 16));
}

test "phase3 mmio ranges keep byte and stride boundaries explicit" {
    const desc = range(0x1000, 32, 8);
    const empty = range(0x2000, 0, 4);

    try std.testing.expect(containsOffset(desc, 0));
    try std.testing.expect(containsOffset(desc, 31));
    try std.testing.expect(!containsOffset(desc, 32));

    try std.testing.expect(containsAccess(desc, 0, 1));
    try std.testing.expect(containsAccess(desc, 24, @sizeOf(u64)));
    try std.testing.expect(!containsAccess(desc, 25, @sizeOf(u64)));
    try std.testing.expect(!containsAccess(desc, 32, 1));
    try std.testing.expect(!containsAccess(desc, 0, 33));
    try std.testing.expect(!containsAccess(desc, 0, 0));

    try std.testing.expectEqual(@as(?usize, 0), offsetForIndex(desc, 0));
    try std.testing.expectEqual(@as(?usize, 8), offsetForIndex(desc, 1));
    try std.testing.expectEqual(@as(?usize, 24), offsetForIndex(desc, 3));
    try std.testing.expectEqual(@as(?usize, null), offsetForIndex(desc, 4));
    try std.testing.expectEqual(@as(?usize, null), offsetForIndex(empty, 0));

    try std.testing.expectEqual(@as(?usize, 0), typedOffsetForIndex(desc, u32, 0));
    try std.testing.expectEqual(@as(?usize, 8), typedOffsetForIndex(desc, u32, 1));
    try std.testing.expectEqual(@as(?usize, 24), typedOffsetForIndex(desc, u64, 3));
    try std.testing.expectEqual(@as(?usize, null), typedOffsetForIndex(desc, u16, 4));
    try std.testing.expectEqual(@as(?usize, null), typedOffsetForIndex(desc, u64, std.math.maxInt(usize)));
    try std.testing.expectEqual(@as(?usize, null), typedOffsetForIndex(empty, u8, 0));
}

test "phase3 mmio wrappers keep odd-offset volatile accesses reviewable" {
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);
    const mmio_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio);
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = mmio_scope,
        .reserved = 0,
    };

    const odd_halfword: *align(1) const u16 = @ptrCast(&bytes[1]);
    write16(base, 1, 0x1234);
    try std.testing.expectEqual(@as(u16, 0x1234), odd_halfword.*);
    try std.testing.expectEqual(@as(u16, 0x1234), read16(base, 1));

    try write16InteropPolicyByte(base, 1, 0x4321, mmio_scope);
    try std.testing.expectEqual(@as(u16, 0x4321), odd_halfword.*);
    try std.testing.expectEqual(@as(u16, 0x4321), try read16InteropPolicyByte(base, 1, mmio_scope));

    const odd_word: *align(1) const u32 = @ptrCast(&bytes[3]);
    write32(base, 3, 0x89ab_cdef);
    try std.testing.expectEqual(@as(u32, 0x89ab_cdef), odd_word.*);
    try std.testing.expectEqual(@as(u32, 0x89ab_cdef), read32(base, 3));

    try write32InteropPolicyBytes(base, 3, 0xc001_d00d, mmio_scope, 0);
    try std.testing.expectEqual(@as(u32, 0xc001_d00d), odd_word.*);
    try std.testing.expectEqual(
        @as(u32, 0xc001_d00d),
        try read32InteropPolicyBytes(base, 3, mmio_scope, 0),
    );

    const odd_doubleword: *align(1) const u64 = @ptrCast(&bytes[5]);
    write64(base, 5, 0xfedc_ba98_7654_3210);
    try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), odd_doubleword.*);
    try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), read64(base, 5));

    try writeInteropPolicy(u64, base, 5, 0x0bad_f00d_dead_beef, mmio_policy);
    try std.testing.expectEqual(@as(u64, 0x0bad_f00d_dead_beef), odd_doubleword.*);
    try std.testing.expectEqual(@as(u64, 0x0bad_f00d_dead_beef), try readInteropPolicy(u64, base, 5, mmio_policy));
}

test "phase3 mmio wrappers keep volatile-mmio policy gates reviewable" {
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);

    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const none_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const raw_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };

    try std.testing.expect(allowsInteropPolicy(mmio_policy));
    try std.testing.expect(allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 0));
    try std.testing.expect(allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.volatile_mmio)));
    try std.testing.expect(!allowsInteropPolicy(none_policy));
    try std.testing.expect(!allowsInteropPolicy(raw_policy));
    try std.testing.expect(!allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.none)));
    try std.testing.expect(!allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge)));
    try std.testing.expect(!allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 1));

    try requireInteropPolicy(mmio_policy);
    try requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 0);
    try requireInteropPolicyByte(@intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 1),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyByte(@intFromEnum(abi.UnsafeScope.none)),
    );

    const desc = try rangeInteropPolicy(base, 32, 8, mmio_policy);
    try std.testing.expectEqual(@as(u32, 8), desc.stride);
    try std.testing.expectEqual(base, (try rangeInteropPolicyByte(base, 32, 4, @intFromEnum(abi.UnsafeScope.volatile_mmio))).base_addr);
    try std.testing.expectError(error.UnsafeScopeDenied, rangeInteropPolicy(base, 32, 4, none_policy));

    try writeInteropPolicy(u8, base, 0, 0x33, mmio_policy);
    try std.testing.expectEqual(@as(u8, 0x33), try readInteropPolicy(u8, base, 0, mmio_policy));

    try writeInteropPolicy(u16, base, 2, 0x1234, mmio_policy);
    try std.testing.expectEqual(@as(u16, 0x1234), try readInteropPolicy(u16, base, 2, mmio_policy));

    try writeInteropPolicyByte(u32, base, 4, 0xc001_d00d, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(
        @as(u32, 0xc001_d00d),
        try readInteropPolicyByte(u32, base, 4, @intFromEnum(abi.UnsafeScope.volatile_mmio)),
    );

    try writeInteropPolicyBytes(
        u64,
        base,
        8,
        0x0bad_f00d_dead_beef,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        0,
    );
    try std.testing.expectEqual(
        @as(u64, 0x0bad_f00d_dead_beef),
        try readInteropPolicyBytes(u64, base, 8, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0),
    );

    try write16InteropPolicy(base, 16, 0x5678, mmio_policy);
    try std.testing.expectEqual(@as(u16, 0x5678), try read16InteropPolicy(base, 16, mmio_policy));

    try write32InteropPolicyByte(base, 18, 0xfeed_beef, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(
        @as(u32, 0xfeed_beef),
        try read32InteropPolicyByte(base, 18, @intFromEnum(abi.UnsafeScope.volatile_mmio)),
    );

    try write64InteropPolicyBytes(
        base,
        24,
        0x0123_4567_89ab_cdef,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        0,
    );
    try std.testing.expectEqual(
        @as(u64, 0x0123_4567_89ab_cdef),
        try read64InteropPolicyBytes(base, 24, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0),
    );

    try std.testing.expectError(error.UnsafeScopeDenied, readInteropPolicy(u8, base, 0, none_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, writeInteropPolicy(u8, base, 0, 0x44, raw_policy));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        readInteropPolicyBytes(u16, base, 2, @intFromEnum(abi.UnsafeScope.volatile_mmio), 1),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        readInteropPolicyByte(u32, base, 4, @intFromEnum(abi.UnsafeScope.none)),
    );
}
