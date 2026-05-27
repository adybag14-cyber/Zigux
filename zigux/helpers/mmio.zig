const std = @import("std");
const abi = @import("abi_bindings");
const unsafe_policy = @import("unsafe_policy");

pub const PolicyError = error{
    InvalidInteropPolicy,
    UnsafeScopeDenied,
};

pub const MmioRange = extern struct {
    base_addr: usize,
    length: u32,
    stride: u32,
};

fn scopeFromInteropPolicy(policy: abi.InteropPolicy) PolicyError!abi.UnsafeScope {
    return unsafe_policy.scopeFromInteropPolicy(policy) orelse error.InvalidInteropPolicy;
}

fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) PolicyError!abi.UnsafeScope {
    return unsafe_policy.scopeFromInteropPolicyBytes(scope, reserved) orelse error.InvalidInteropPolicy;
}

fn byteOffsetAddress(base_addr: usize, byte_offset: usize) PolicyError!usize {
    return std.math.add(usize, base_addr, byte_offset) catch error.InvalidInteropPolicy;
}

fn validateRangeWindow(base_addr: usize, length: u32) PolicyError!void {
    const byte_len: usize = @intCast(length);
    if (byte_len == 0) return;
    _ = try byteOffsetAddress(base_addr, byte_len - 1);
}

fn rangeContainsAccessBytes(range: MmioRange, byte_offset: usize, byte_len: usize) bool {
    const range_len: usize = @intCast(range.length);
    const access_end = std.math.add(usize, byte_offset, byte_len) catch return false;
    return access_end <= range_len;
}

fn rangeStrideAllowsOffset(range: MmioRange, byte_offset: usize) bool {
    const stride: usize = @intCast(range.stride);
    if (stride == 0) return true;
    return (byte_offset % stride) == 0;
}

fn validateRangeTypedAccess(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!void {
    if ((byte_offset % @alignOf(T)) != 0) return error.InvalidInteropPolicy;
    if (!rangeStrideAllowsOffset(range, byte_offset)) return error.InvalidInteropPolicy;
    if (!rangeContainsAccessBytes(range, byte_offset, @sizeOf(T))) return error.InvalidInteropPolicy;
}

fn offsetConstPointer(comptime T: type, base_addr: usize, byte_offset: usize) PolicyError!*const volatile T {
    if ((byte_offset % @alignOf(T)) != 0) return error.InvalidInteropPolicy;
    return @ptrFromInt(try byteOffsetAddress(base_addr, byte_offset));
}

fn offsetPointer(comptime T: type, base_addr: usize, byte_offset: usize) PolicyError!*volatile T {
    if ((byte_offset % @alignOf(T)) != 0) return error.InvalidInteropPolicy;
    return @ptrFromInt(try byteOffsetAddress(base_addr, byte_offset));
}

pub fn allowsVolatileMmioScope(scope: abi.UnsafeScope) bool {
    return unsafe_policy.permitsVolatileMmio(scope);
}

pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {
    const scope = scopeFromInteropPolicy(policy) catch return false;
    return allowsVolatileMmioScope(scope);
}

pub fn allowsInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    const scope = scopeFromInteropPolicyBytes(unsafe_scope, reserved) catch return false;
    return allowsVolatileMmioScope(scope);
}

pub fn allowsInteropPolicyByte(unsafe_scope: u8) bool {
    return allowsInteropPolicyBytes(unsafe_scope, 0);
}

pub fn requireVolatileMmioScope(scope: abi.UnsafeScope) PolicyError!void {
    if (!allowsVolatileMmioScope(scope)) {
        return error.UnsafeScopeDenied;
    }
}

pub fn requireInteropPolicy(policy: abi.InteropPolicy) PolicyError!void {
    try requireVolatileMmioScope(try scopeFromInteropPolicy(policy));
}

pub fn requireInteropPolicyBytes(unsafe_scope: u8, reserved: u8) PolicyError!void {
    try requireVolatileMmioScope(try scopeFromInteropPolicyBytes(unsafe_scope, reserved));
}

pub fn requireInteropPolicyByte(unsafe_scope: u8) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, 0);
}

pub fn read(comptime T: type, ptr: *const volatile T) T {
    return ptr.*;
}

pub fn write(comptime T: type, ptr: *volatile T, value: T) void {
    ptr.* = value;
}

pub fn exchange(comptime T: type, ptr: *volatile T, value: T) T {
    const before = read(T, @ptrCast(ptr));
    write(T, ptr, value);
    return before;
}

pub fn writeMasked(comptime T: type, ptr: *volatile T, clear_mask: T, set_mask: T) T {
    const before = read(T, @ptrCast(ptr));
    const after = (before & ~clear_mask) | set_mask;
    write(T, ptr, after);
    return after;
}

pub fn readScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *const volatile T) PolicyError!T {
    try requireVolatileMmioScope(scope);
    return read(T, ptr);
}

pub fn writeScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *volatile T, value: T) PolicyError!void {
    try requireVolatileMmioScope(scope);
    write(T, ptr, value);
}

pub fn exchangeScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *volatile T, value: T) PolicyError!T {
    try requireVolatileMmioScope(scope);
    return exchange(T, ptr, value);
}

pub fn writeMaskedScoped(
    comptime T: type,
    scope: abi.UnsafeScope,
    ptr: *volatile T,
    clear_mask: T,
    set_mask: T,
) PolicyError!T {
    try requireVolatileMmioScope(scope);
    return writeMasked(T, ptr, clear_mask, set_mask);
}

pub fn rangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) PolicyError!MmioRange {
    try requireVolatileMmioScope(scope);
    try validateRangeWindow(base_addr, length);
    return .{
        .base_addr = base_addr,
        .length = length,
        .stride = stride,
    };
}

pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) PolicyError!MmioRange {
    try requireInteropPolicy(policy);
    try validateRangeWindow(base_addr, length);
    return .{
        .base_addr = base_addr,
        .length = length,
        .stride = stride,
    };
}

pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) PolicyError!MmioRange {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    try validateRangeWindow(base_addr, length);
    return .{
        .base_addr = base_addr,
        .length = length,
        .stride = stride,
    };
}

pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) PolicyError!MmioRange {
    return rangeInteropPolicyBytes(base_addr, length, stride, unsafe_scope, 0);
}

pub fn readInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *const volatile T) PolicyError!T {
    try requireInteropPolicy(policy);
    return read(T, ptr);
}

pub fn writeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!void {
    try requireInteropPolicy(policy);
    write(T, ptr, value);
}

pub fn exchangeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!T {
    try requireInteropPolicy(policy);
    return exchange(T, ptr, value);
}

pub fn writeMaskedInteropPolicy(
    comptime T: type,
    policy: abi.InteropPolicy,
    ptr: *volatile T,
    clear_mask: T,
    set_mask: T,
) PolicyError!T {
    try requireInteropPolicy(policy);
    return writeMasked(T, ptr, clear_mask, set_mask);
}

pub fn readInteropPolicyBytes(
    comptime T: type,
    unsafe_scope: u8,
    reserved: u8,
    ptr: *const volatile T,
) PolicyError!T {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return read(T, ptr);
}

pub fn readInteropPolicyByte(comptime T: type, unsafe_scope: u8, ptr: *const volatile T) PolicyError!T {
    try requireInteropPolicyByte(unsafe_scope);
    return read(T, ptr);
}

pub fn writeInteropPolicyBytes(
    comptime T: type,
    unsafe_scope: u8,
    reserved: u8,
    ptr: *volatile T,
    value: T,
) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    write(T, ptr, value);
}

pub fn writeInteropPolicyByte(
    comptime T: type,
    unsafe_scope: u8,
    ptr: *volatile T,
    value: T,
) PolicyError!void {
    try requireInteropPolicyByte(unsafe_scope);
    write(T, ptr, value);
}

pub fn exchangeInteropPolicyBytes(
    comptime T: type,
    unsafe_scope: u8,
    reserved: u8,
    ptr: *volatile T,
    value: T,
) PolicyError!T {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return exchange(T, ptr, value);
}

pub fn exchangeInteropPolicyByte(
    comptime T: type,
    unsafe_scope: u8,
    ptr: *volatile T,
    value: T,
) PolicyError!T {
    try requireInteropPolicyByte(unsafe_scope);
    return exchange(T, ptr, value);
}

pub fn writeMaskedInteropPolicyBytes(
    comptime T: type,
    unsafe_scope: u8,
    reserved: u8,
    ptr: *volatile T,
    clear_mask: T,
    set_mask: T,
) PolicyError!T {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return writeMasked(T, ptr, clear_mask, set_mask);
}

pub fn writeMaskedInteropPolicyByte(
    comptime T: type,
    unsafe_scope: u8,
    ptr: *volatile T,
    clear_mask: T,
    set_mask: T,
) PolicyError!T {
    try requireInteropPolicyByte(unsafe_scope);
    return writeMasked(T, ptr, clear_mask, set_mask);
}

pub fn read8InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u8 {
    return readInteropPolicyBytes(u8, unsafe_scope, reserved, try offsetConstPointer(u8, base_addr, byte_offset));
}

pub fn write8InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u8, unsafe_scope: u8, reserved: u8) PolicyError!void {
    try writeInteropPolicyBytes(u8, unsafe_scope, reserved, try offsetPointer(u8, base_addr, byte_offset), value);
}

pub fn read8InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u8 {
    return read8InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, 0);
}

pub fn write8InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u8, unsafe_scope: u8) PolicyError!void {
    try write8InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, 0);
}

pub fn read16InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u16 {
    return readInteropPolicyBytes(u16, unsafe_scope, reserved, try offsetConstPointer(u16, base_addr, byte_offset));
}

pub fn write16InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u16, unsafe_scope: u8, reserved: u8) PolicyError!void {
    try writeInteropPolicyBytes(u16, unsafe_scope, reserved, try offsetPointer(u16, base_addr, byte_offset), value);
}

pub fn read16InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u16 {
    return read16InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, 0);
}

pub fn write16InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u16, unsafe_scope: u8) PolicyError!void {
    try write16InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, 0);
}

pub fn read32InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u32 {
    return readInteropPolicyBytes(u32, unsafe_scope, reserved, try offsetConstPointer(u32, base_addr, byte_offset));
}

pub fn write32InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u32, unsafe_scope: u8, reserved: u8) PolicyError!void {
    try writeInteropPolicyBytes(u32, unsafe_scope, reserved, try offsetPointer(u32, base_addr, byte_offset), value);
}

pub fn read32InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u32 {
    return read32InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, 0);
}

pub fn write32InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u32, unsafe_scope: u8) PolicyError!void {
    try write32InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, 0);
}

pub fn read64InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u64 {
    return readInteropPolicyBytes(u64, unsafe_scope, reserved, try offsetConstPointer(u64, base_addr, byte_offset));
}

pub fn write64InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8, reserved: u8) PolicyError!void {
    try writeInteropPolicyBytes(u64, unsafe_scope, reserved, try offsetPointer(u64, base_addr, byte_offset), value);
}

pub fn read64InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u64 {
    return read64InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, 0);
}

pub fn write64InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8) PolicyError!void {
    try write64InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, 0);
}

test "phase3 mmio helper keeps volatile register reads and writes reviewable" {
    var register: u32 = 0x1234_5678;
    const register_ptr: *volatile u32 = @ptrCast(&register);

    try std.testing.expectEqual(@as(u32, 0x1234_5678), read(u32, register_ptr));
    write(u32, register_ptr, 0xCAFE_BABE);
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);
}

test "phase3 mmio helper keeps exchange-style register updates explicit" {
    var register: u16 = 0x1002;
    const register_ptr: *volatile u16 = @ptrCast(&register);

    try std.testing.expectEqual(@as(u16, 0x1002), exchange(u16, register_ptr, 0xBEEF));
    try std.testing.expectEqual(@as(u16, 0xBEEF), register);
}

test "phase3 mmio helper keeps masked register updates reviewable" {
    var register: u8 = 0b1011_0101;
    const register_ptr: *volatile u8 = @ptrCast(&register);

    try std.testing.expectEqual(
        @as(u8, 0b1001_0110),
        writeMasked(u8, register_ptr, 0b0011_0001, 0b0001_0010),
    );
    try std.testing.expectEqual(@as(u8, 0b1001_0110), register);
}

test "phase3 mmio helper keeps policy allowance predicates explicit" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const no_unsafe_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    try std.testing.expect(allowsVolatileMmioScope(.volatile_mmio));
    try std.testing.expect(!allowsVolatileMmioScope(.none));
    try std.testing.expect(!allowsVolatileMmioScope(.raw_pointer_bridge));

    try std.testing.expect(allowsInteropPolicy(mmio_policy));
    try std.testing.expect(!allowsInteropPolicy(no_unsafe_policy));
    try std.testing.expect(!allowsInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!allowsInteropPolicy(reserved_policy));

    try std.testing.expect(allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 0));
    try std.testing.expect(!allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.none), 0));
    try std.testing.expect(!allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 0));
    try std.testing.expect(!allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 1));

    try std.testing.expect(allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.volatile_mmio)));
    try std.testing.expect(!allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.none)));
    try std.testing.expect(!allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge)));
}

test "phase3 mmio helper keeps policy require helpers explicit" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const no_unsafe_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    try requireInteropPolicy(mmio_policy);
    try std.testing.expectError(error.UnsafeScopeDenied, requireInteropPolicy(no_unsafe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireInteropPolicy(raw_pointer_policy));
    try std.testing.expectError(error.InvalidInteropPolicy, requireInteropPolicy(reserved_policy));

    try requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 0);
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.none), 0),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 0),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 1),
    );

    try requireInteropPolicyByte(@intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyByte(@intFromEnum(abi.UnsafeScope.none)),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyByte(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge)),
    );
}

test "phase3 mmio helper keeps typed scope require gate explicit" {
    try requireVolatileMmioScope(.volatile_mmio);
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioScope(.none));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioScope(.raw_pointer_bridge));
}

test "phase3 mmio helper keeps helper-local ranges and width aliases explicit" {
    var bytes = [_]u8{0} ** 16;
    const base_addr = @intFromPtr(&bytes[0]);
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const mmio_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio);
    const no_unsafe_scope = @intFromEnum(abi.UnsafeScope.none);

    const range = try rangeInteropPolicy(base_addr, 16, 4, mmio_policy);
    try std.testing.expectEqual(base_addr, range.base_addr);
    try std.testing.expectEqual(@as(u32, 16), range.length);
    try std.testing.expectEqual(@as(u32, 4), range.stride);

    try write8InteropPolicyByte(base_addr, 0, 0x31, mmio_scope);
    try std.testing.expectEqual(@as(u8, 0x31), try read8InteropPolicyByte(base_addr, 0, mmio_scope));
    try write8InteropPolicyBytes(base_addr, 1, 0x44, mmio_scope, 0);
    try std.testing.expectEqual(@as(u8, 0x44), try read8InteropPolicyBytes(base_addr, 1, mmio_scope, 0));

    try write16InteropPolicyByte(base_addr, 2, 0xABCD, mmio_scope);
    try std.testing.expectEqual(@as(u16, 0xABCD), try read16InteropPolicyByte(base_addr, 2, mmio_scope));
    try write16InteropPolicyBytes(base_addr, 4, 0xBEEF, mmio_scope, 0);
    try std.testing.expectEqual(@as(u16, 0xBEEF), try read16InteropPolicyBytes(base_addr, 4, mmio_scope, 0));
    try std.testing.expectError(error.InvalidInteropPolicy, read16InteropPolicyBytes(base_addr, 3, mmio_scope, 0));

    try write32InteropPolicyByte(base_addr, 8, 0xC001_D00D, mmio_scope);
    try std.testing.expectEqual(@as(u32, 0xC001_D00D), try read32InteropPolicyByte(base_addr, 8, mmio_scope));
    try write32InteropPolicyBytes(base_addr, 8, 0xFACE_CAFE, mmio_scope, 0);
    try std.testing.expectEqual(@as(u32, 0xFACE_CAFE), try read32InteropPolicyBytes(base_addr, 8, mmio_scope, 0));
    try std.testing.expectEqual(@as(u32, 0xFACE_CAFE), try read32InteropPolicyByte(base_addr, 8, mmio_scope));
    try std.testing.expectError(error.InvalidInteropPolicy, read32InteropPolicyBytes(base_addr, 8, mmio_scope, 1));

    try write64InteropPolicyByte(base_addr, 8, 0x0123_4567_89AB_CDEF, mmio_scope);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89AB_CDEF), try read64InteropPolicyByte(base_addr, 8, mmio_scope));
    try write64InteropPolicyBytes(base_addr, 8, 0x0FED_CBA9_8765_4321, mmio_scope, 0);
    try std.testing.expectEqual(
        @as(u64, 0x0FED_CBA9_8765_4321),
        try read64InteropPolicyBytes(base_addr, 8, mmio_scope, 0),
    );

    try std.testing.expectError(error.UnsafeScopeDenied, write64InteropPolicyBytes(base_addr, 8, 0, no_unsafe_scope, 0));
}

test "phase3 mmio helper keeps MmioRange typed-access windows explicit before future range-bound accessors land" {
    const strided = MmioRange{
        .base_addr = 0x1000,
        .length = 16,
        .stride = 4,
    };
    const tightly_spaced = MmioRange{
        .base_addr = 0x2000,
        .length = 12,
        .stride = 0,
    };

    try validateRangeTypedAccess(u8, strided, 0);
    try validateRangeTypedAccess(u16, strided, 4);
    try validateRangeTypedAccess(u32, strided, 8);
    try std.testing.expect(rangeContainsAccessBytes(strided, 12, @sizeOf(u32)));
    try std.testing.expect(!rangeContainsAccessBytes(strided, 13, @sizeOf(u32)));
    try std.testing.expect(rangeStrideAllowsOffset(strided, 12));
    try std.testing.expect(!rangeStrideAllowsOffset(strided, 10));

    try validateRangeTypedAccess(u16, tightly_spaced, 6);
    try std.testing.expect(rangeStrideAllowsOffset(tightly_spaced, 7));
    try std.testing.expect(rangeContainsAccessBytes(tightly_spaced, 10, @sizeOf(u16)));

    try std.testing.expectError(error.InvalidInteropPolicy, validateRangeTypedAccess(u16, strided, 2));
    try std.testing.expectError(error.InvalidInteropPolicy, validateRangeTypedAccess(u32, strided, 6));
    try std.testing.expectError(error.InvalidInteropPolicy, validateRangeTypedAccess(u32, strided, 13));
    try std.testing.expectError(error.InvalidInteropPolicy, validateRangeTypedAccess(u64, tightly_spaced, 8));
    try std.testing.expect(!rangeContainsAccessBytes(strided, std.math.maxInt(usize), 4));
}

test "phase3 mmio helper rejects overflowing range windows before blessing unsafe access" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const mmio_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio);
    const near_end = std.math.maxInt(usize) - 3;

    const bounded = try rangeScoped(near_end, 4, 1, .volatile_mmio);
    try std.testing.expectEqual(near_end, bounded.base_addr);
    try std.testing.expectEqual(@as(u32, 4), bounded.length);
    try std.testing.expectEqual(@as(u32, 1), bounded.stride);

    try std.testing.expectError(error.InvalidInteropPolicy, rangeScoped(near_end, 5, 1, .volatile_mmio));
    try std.testing.expectError(error.InvalidInteropPolicy, rangeInteropPolicy(near_end, 5, 1, mmio_policy));
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        rangeInteropPolicyBytes(near_end, 5, 1, mmio_scope, 0),
    );
    try std.testing.expectError(error.InvalidInteropPolicy, rangeInteropPolicyByte(near_end, 5, 1, mmio_scope));

    const empty = try rangeInteropPolicyByte(std.math.maxInt(usize), 0, 0, mmio_scope);
    try std.testing.expectEqual(std.math.maxInt(usize), empty.base_addr);
    try std.testing.expectEqual(@as(u32, 0), empty.length);
    try std.testing.expectEqual(@as(u32, 0), empty.stride);
}

test "phase3 mmio helper keeps 64-bit const reads and masked updates reviewable" {
    var register: u64 = 0x1234_5678_9ABC_DEF0;
    const register_ptr: *volatile u64 = @ptrCast(&register);
    const const_register_ptr: *const volatile u64 = @ptrCast(&register);

    try std.testing.expectEqual(@as(u64, 0x1234_5678_9ABC_DEF0), read(u64, const_register_ptr));
    try std.testing.expectEqual(@as(u64, 0x1234_5678_9ABC_DEF0), exchange(u64, register_ptr, 0x0F0E_0D0C_0B0A_0908));
    try std.testing.expectEqual(@as(u64, 0x0F0E_0D0C_0B0A_0908), register);

    write(u64, register_ptr, 0x1234_5678_9ABC_DEF0);
    try std.testing.expectEqual(
        @as(u64, 0x1255_5678_9A11_DEA0),
        writeMasked(u64, register_ptr, 0x00FF_0000_00FF_00F0, 0x0055_0000_0011_00A0),
    );
    try std.testing.expectEqual(@as(u64, 0x1255_5678_9A11_DEA0), register);
    try std.testing.expectEqual(@as(u64, 0x1255_5678_9A11_DEA0), read(u64, const_register_ptr));
}

test "phase3 mmio helper gates volatile access through typed unsafe scope" {
    var register: u32 = 0xAABB_CCDD;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    try std.testing.expectError(error.UnsafeScopeDenied, readScoped(u32, .none, const_register_ptr));
    try std.testing.expectError(error.UnsafeScopeDenied, writeScoped(u32, .raw_pointer_bridge, register_ptr, 0x1111_2222));
    try std.testing.expectEqual(@as(u32, 0xAABB_CCDD), try readScoped(u32, .volatile_mmio, const_register_ptr));
    try writeScoped(u32, .volatile_mmio, register_ptr, 0x1234_5678);
    try std.testing.expectEqual(@as(u32, 0x1234_5678), register);
    try std.testing.expectEqual(@as(u32, 0x1234_5678), try exchangeScoped(u32, .volatile_mmio, register_ptr, 0xCAFE_BABE));
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);
}

test "phase3 mmio helper gates volatile access through interop policy records" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    var register: u16 = 0x0F00;
    const register_ptr: *volatile u16 = @ptrCast(&register);
    const const_register_ptr: *const volatile u16 = @ptrCast(&register);

    try std.testing.expectError(error.InvalidInteropPolicy, readInteropPolicy(u16, reserved_policy, const_register_ptr));
    try std.testing.expectError(error.UnsafeScopeDenied, readInteropPolicy(u16, raw_pointer_policy, const_register_ptr));

    try std.testing.expectEqual(@as(u16, 0x0F00), try readInteropPolicy(u16, mmio_policy, const_register_ptr));
    try writeInteropPolicy(u16, mmio_policy, register_ptr, 0x00F0);
    try std.testing.expectEqual(@as(u16, 0x00F0), register);
    try std.testing.expectEqual(@as(u16, 0x00F0), try exchangeInteropPolicy(u16, mmio_policy, register_ptr, 0xF000));
    try std.testing.expectEqual(@as(u16, 0xF000), register);

    try std.testing.expectError(error.InvalidInteropPolicy, readInteropPolicyBytes(u16, @intFromEnum(abi.UnsafeScope.volatile_mmio), 1, const_register_ptr));
    try std.testing.expectError(error.UnsafeScopeDenied, writeInteropPolicyBytes(u16, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 0, register_ptr, 0xAAAA));
    try std.testing.expectEqual(
        @as(u16, 0xF00F),
        try writeMaskedInteropPolicyBytes(
            u16,
            @intFromEnum(abi.UnsafeScope.volatile_mmio),
            0,
            register_ptr,
            0x00F0,
            0x000F,
        ),
    );
    try std.testing.expectEqual(@as(u16, 0xF00F), register);
}

test "phase3 mmio helper keeps whole-record interop-policy writes side-effect free when denied" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const no_unsafe_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    var register: u32 = 0x1234_5678;
    const register_ptr: *volatile u32 = @ptrCast(&register);

    try std.testing.expectError(error.UnsafeScopeDenied, writeInteropPolicy(u32, no_unsafe_policy, register_ptr, 0xAAAA_5555));
    try std.testing.expectError(error.UnsafeScopeDenied, exchangeInteropPolicy(u32, raw_pointer_policy, register_ptr, 0xCAFE_BABE));
    try std.testing.expectError(error.InvalidInteropPolicy, writeInteropPolicy(u32, reserved_policy, register_ptr, 0x0BAD_C0DE));
    try std.testing.expectError(error.InvalidInteropPolicy, exchangeInteropPolicy(u32, reserved_policy, register_ptr, 0xFACE_CAFE));
    try std.testing.expectEqual(@as(u32, 0x1234_5678), register);

    try writeInteropPolicy(u32, mmio_policy, register_ptr, 0xAAAA_5555);
    try std.testing.expectEqual(@as(u32, 0xAAAA_5555), register);
    try std.testing.expectEqual(@as(u32, 0xAAAA_5555), try exchangeInteropPolicy(u32, mmio_policy, register_ptr, 0xCAFE_BABE));
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);
}

test "phase3 mmio helper keeps scoped masked writes and byte-policy exchanges explicit" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    var register: u16 = 0x0FF0;
    const register_ptr: *volatile u16 = @ptrCast(&register);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        writeMaskedScoped(u16, .raw_pointer_bridge, register_ptr, 0x00F0, 0x0005),
    );
    try std.testing.expectEqual(@as(u16, 0x0FF0), register);

    try std.testing.expectEqual(
        @as(u16, 0x0F05),
        try writeMaskedScoped(u16, .volatile_mmio, register_ptr, 0x00F0, 0x0005),
    );
    try std.testing.expectEqual(@as(u16, 0x0F05), register);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        exchangeInteropPolicyBytes(u16, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 0, register_ptr, 0x5500),
    );
    try std.testing.expectEqual(@as(u16, 0x0F05), register);

    try std.testing.expectEqual(
        @as(u16, 0x0F05),
        try exchangeInteropPolicyBytes(u16, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0, register_ptr, 0x5500),
    );
    try std.testing.expectEqual(@as(u16, 0x5500), register);

    try std.testing.expectError(
        error.InvalidInteropPolicy,
        writeMaskedInteropPolicy(u16, reserved_policy, register_ptr, 0x0F00, 0x00A0),
    );
    try std.testing.expectEqual(@as(u16, 0x5500), register);

    try std.testing.expectEqual(
        @as(u16, 0x50A0),
        try writeMaskedInteropPolicy(u16, mmio_policy, register_ptr, 0x0F00, 0x00A0),
    );
    try std.testing.expectEqual(@as(u16, 0x50A0), register);
}

test "phase3 mmio helper keeps byte-policy shorthand access explicit" {
    var register: u32 = 0x00AA_5500;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);
    const mmio_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio);
    const no_unsafe_scope = @intFromEnum(abi.UnsafeScope.none);
    const raw_pointer_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge);

    try std.testing.expectEqual(@as(u32, 0x00AA_5500), try readInteropPolicyByte(u32, mmio_scope, const_register_ptr));
    try std.testing.expectError(error.UnsafeScopeDenied, readInteropPolicyByte(u32, no_unsafe_scope, const_register_ptr));

    try writeInteropPolicyByte(u32, mmio_scope, register_ptr, 0x1234_5678);
    try std.testing.expectEqual(@as(u32, 0x1234_5678), register);
    try std.testing.expectError(error.UnsafeScopeDenied, writeInteropPolicyByte(u32, raw_pointer_scope, register_ptr, 0));
    try std.testing.expectEqual(@as(u32, 0x1234_5678), register);

    try std.testing.expectEqual(
        @as(u32, 0x1234_5678),
        try exchangeInteropPolicyByte(u32, mmio_scope, register_ptr, 0xCAFE_BABE),
    );
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        exchangeInteropPolicyByte(u32, no_unsafe_scope, register_ptr, 0),
    );
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);

    try std.testing.expectEqual(
        @as(u32, 0xCA0E_B00E),
        try writeMaskedInteropPolicyByte(u32, mmio_scope, register_ptr, 0x00F0_0FF0, 0x000E_000E),
    );
    try std.testing.expectEqual(@as(u32, 0xCA0E_B00E), register);
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        writeMaskedInteropPolicyByte(u32, raw_pointer_scope, register_ptr, 0xFFFF_0000, 0),
    );
    try std.testing.expectEqual(@as(u32, 0xCA0E_B00E), register);
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        writeMaskedInteropPolicyBytes(u32, mmio_scope, 1, register_ptr, 0xFFFF_0000, 0),
    );
    try std.testing.expectEqual(@as(u32, 0xCA0E_B00E), register);
}

test "phase3 mmio helper keeps interop-policy reads and writes routed through require helpers" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    var register: u16 = 0x0F00;
    const register_ptr: *volatile u16 = @ptrCast(&register);
    const const_register_ptr: *const volatile u16 = @ptrCast(&register);

    try std.testing.expectEqual(@as(u16, 0x0F00), try readInteropPolicy(u16, mmio_policy, const_register_ptr));
    try writeInteropPolicy(u16, mmio_policy, register_ptr, 0x00F0);
    try std.testing.expectEqual(@as(u16, 0x00F0), register);
    try std.testing.expectEqual(@as(u16, 0x00F0), try exchangeInteropPolicyBytes(
        u16,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        0,
        register_ptr,
        0xF000,
    ));
    try std.testing.expectEqual(@as(u16, 0xF000), register);

    try std.testing.expectError(error.InvalidInteropPolicy, readInteropPolicy(u16, reserved_policy, const_register_ptr));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        writeInteropPolicyBytes(u16, @intFromEnum(abi.UnsafeScope.none), 0, register_ptr, 0xAAAA),
    );
}
