const std = @import("std");
const abi = @import("abi_bindings");
const mmio = @import("mmio");

pub const PolicyError = mmio.PolicyError;
pub const MmioRange = mmio.MmioRange;
pub const UnsafeScope = abi.UnsafeScope;

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

pub fn typedAccessAllowed(comptime T: type, range: MmioRange, byte_offset: usize) bool {
    if ((byte_offset % @alignOf(T)) != 0) return false;
    if (!rangeStrideAllowsOffset(range, byte_offset)) return false;
    return rangeContainsAccessBytes(range, byte_offset, @sizeOf(T));
}

pub fn validateTypedAccess(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!void {
    if (!typedAccessAllowed(T, range, byte_offset)) {
        return error.InvalidInteropPolicy;
    }
}

pub fn constPointerAt(
    comptime T: type,
    range: MmioRange,
    byte_offset: usize,
) PolicyError!*const volatile T {
    try validateTypedAccess(T, range, byte_offset);
    return @ptrFromInt(try std.math.add(usize, range.base_addr, byte_offset));
}

pub fn pointerAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!*volatile T {
    try validateTypedAccess(T, range, byte_offset);
    return @ptrFromInt(try std.math.add(usize, range.base_addr, byte_offset));
}

pub fn readAt(comptime T: type, range: MmioRange, byte_offset: usize) PolicyError!T {
    return mmio.read(T, try constPointerAt(T, range, byte_offset));
}

pub fn writeAt(
    comptime T: type,
    range: MmioRange,
    byte_offset: usize,
    value: T,
) PolicyError!void {
    mmio.write(T, try pointerAt(T, range, byte_offset), value);
}

pub fn exchangeAt(
    comptime T: type,
    range: MmioRange,
    byte_offset: usize,
    value: T,
) PolicyError!T {
    return mmio.exchange(T, try pointerAt(T, range, byte_offset), value);
}

pub fn writeMaskedAt(
    comptime T: type,
    range: MmioRange,
    byte_offset: usize,
    clear_mask: T,
    set_mask: T,
) PolicyError!T {
    return mmio.writeMasked(T, try pointerAt(T, range, byte_offset), clear_mask, set_mask);
}

test "phase3 mmio-range helper reuses scoped MMIO windows for typed access" {
    var bytes = [_]u8{0} ** 16;
    const base_addr = @intFromPtr(&bytes[0]);
    const range = try mmio.rangeScoped(base_addr, 16, 4, .volatile_mmio);

    try writeAt(u32, range, 4, 0x1122_3344);
    try std.testing.expectEqual(@as(u32, 0x1122_3344), try readAt(u32, range, 4));
    try std.testing.expectEqual(@as(u32, 0x1122_3344), try exchangeAt(u32, range, 4, 0x5566_7788));
    try std.testing.expectEqual(@as(u32, 0x5566_7788), try readAt(u32, range, 4));
    try std.testing.expectEqual(
        @as(u32, 0x5500_0088),
        try writeMaskedAt(u32, range, 4, 0x00FF_FF00, 0x5500_0088),
    );

    const const_ptr = try constPointerAt(u32, range, 4);
    const ptr = try pointerAt(u32, range, 4);
    try std.testing.expectEqual(@as(u32, 0x5500_0088), const_ptr.*);
    ptr.* = 0xCAFE_BABE;
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try readAt(u32, range, 4));
}

test "phase3 mmio-range helper keeps policy-created windows and typed-access predicates explicit" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };

    var bytes = [_]u8{0} ** 16;
    const base_addr = @intFromPtr(&bytes[0]);
    const range = try mmio.rangeInteropPolicy(base_addr, 16, 4, mmio_policy);

    try std.testing.expect(typedAccessAllowed(u8, range, 0));
    try std.testing.expect(typedAccessAllowed(u32, range, 4));
    try std.testing.expect(!typedAccessAllowed(u16, range, 2));
    try std.testing.expect(!typedAccessAllowed(u32, range, 14));

    try writeAt(u16, range, 4, 0xABCD);
    try std.testing.expectEqual(@as(u16, 0xABCD), (try constPointerAt(u16, range, 4)).*);
}

test "phase3 mmio-range helper rejects misaligned strided and out-of-range offsets" {
    var bytes = [_]u8{0} ** 16;
    const base_addr = @intFromPtr(&bytes[0]);
    const range = try mmio.rangeScoped(base_addr, 16, 4, .volatile_mmio);

    try std.testing.expectError(error.InvalidInteropPolicy, validateTypedAccess(u16, range, 2));
    try std.testing.expectError(error.InvalidInteropPolicy, readAt(u16, range, 2));
    try std.testing.expectError(error.InvalidInteropPolicy, writeAt(u32, range, 2, 1));
    try std.testing.expectError(error.InvalidInteropPolicy, exchangeAt(u32, range, 14, 1));
    try std.testing.expectError(error.InvalidInteropPolicy, writeMaskedAt(u32, range, 13, 0, 1));
}
