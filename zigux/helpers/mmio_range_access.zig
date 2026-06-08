const std = @import("std");
const mmio = @import("mmio.zig");

pub const MmioRange = mmio.MmioRange;

pub fn rangeContainsAccessBytes(range: MmioRange, byte_offset: usize, byte_len: usize) bool {
    const range_len: usize = @intCast(range.length);
    const access_end = std.math.add(usize, byte_offset, byte_len) catch return false;
    return access_end <= range_len;
}

pub fn rangeStrideAllowsOffset(range: MmioRange, byte_offset: usize) bool {
    const stride: usize = @intCast(range.stride);
    if (stride == 0) return true;
    return (byte_offset % stride) == 0;
}

pub fn rangeAllowsTypedAccess(comptime T: type, range: MmioRange, byte_offset: usize) bool {
    if ((byte_offset % @alignOf(T)) != 0) return false;
    if (!rangeStrideAllowsOffset(range, byte_offset)) return false;
    return rangeContainsAccessBytes(range, byte_offset, @sizeOf(T));
}

pub fn validateRangeTypedAccess(comptime T: type, range: MmioRange, byte_offset: usize) mmio.PolicyError!void {
    if (!rangeAllowsTypedAccess(T, range, byte_offset)) return error.InvalidInteropPolicy;
}

test "phase3 mmio range access helper exposes byte and stride predicates" {
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

    try std.testing.expect(rangeContainsAccessBytes(strided, 12, @sizeOf(u32)));
    try std.testing.expect(!rangeContainsAccessBytes(strided, 13, @sizeOf(u32)));
    try std.testing.expect(rangeContainsAccessBytes(strided, 16, 0));
    try std.testing.expect(!rangeContainsAccessBytes(strided, std.math.maxInt(usize), 4));

    try std.testing.expect(rangeStrideAllowsOffset(strided, 12));
    try std.testing.expect(!rangeStrideAllowsOffset(strided, 10));
    try std.testing.expect(rangeStrideAllowsOffset(tightly_spaced, 7));
}

test "phase3 mmio range access helper mirrors typed accessor admission" {
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

    try std.testing.expect(rangeAllowsTypedAccess(u8, strided, 0));
    try std.testing.expect(rangeAllowsTypedAccess(u16, strided, 4));
    try std.testing.expect(rangeAllowsTypedAccess(u32, strided, 8));
    try std.testing.expect(rangeAllowsTypedAccess(u16, tightly_spaced, 6));

    try std.testing.expect(!rangeAllowsTypedAccess(u16, strided, 2));
    try std.testing.expect(!rangeAllowsTypedAccess(u32, strided, 6));
    try std.testing.expect(!rangeAllowsTypedAccess(u32, strided, 13));
    try std.testing.expect(!rangeAllowsTypedAccess(u64, tightly_spaced, 8));

    try validateRangeTypedAccess(u32, strided, 8);
    try validateRangeTypedAccess(u16, tightly_spaced, 6);
    try std.testing.expectError(error.InvalidInteropPolicy, validateRangeTypedAccess(u16, strided, 2));
    try std.testing.expectError(error.InvalidInteropPolicy, validateRangeTypedAccess(u32, strided, 13));
}
