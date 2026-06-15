const std = @import("std");
const mmio = @import("mmio");

pub const MmioRange = mmio.MmioRange;

pub fn rangeRemainingBytes(range: MmioRange, byte_offset: usize) ?usize {
    const range_len: usize = @intCast(range.length);
    if (byte_offset > range_len) return null;
    return range_len - byte_offset;
}

pub fn rangeAccessEndOffset(range: MmioRange, byte_offset: usize, byte_len: usize) ?usize {
    const remaining = rangeRemainingBytes(range, byte_offset) orelse return null;
    if (byte_len > remaining) return null;
    return byte_offset + byte_len;
}

pub fn rangeContainsAccessBytes(range: MmioRange, byte_offset: usize, byte_len: usize) bool {
    return rangeAccessEndOffset(range, byte_offset, byte_len) != null;
}

pub fn rangeStrideAllowsOffset(range: MmioRange, byte_offset: usize) bool {
    const stride: usize = @intCast(range.stride);
    if (stride == 0) return true;
    return (byte_offset % stride) == 0;
}

pub fn rangeTypedAccessEndOffset(comptime T: type, range: MmioRange, byte_offset: usize) ?usize {
    if ((byte_offset % @alignOf(T)) != 0) return null;
    if (!rangeStrideAllowsOffset(range, byte_offset)) return null;
    return rangeAccessEndOffset(range, byte_offset, @sizeOf(T));
}

pub fn rangeAllowsTypedAccess(comptime T: type, range: MmioRange, byte_offset: usize) bool {
    return rangeTypedAccessEndOffset(T, range, byte_offset) != null;
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
    const empty = MmioRange{
        .base_addr = 0x3000,
        .length = 0,
        .stride = 0,
    };

    try std.testing.expectEqual(@as(?usize, 16), rangeRemainingBytes(strided, 0));
    try std.testing.expectEqual(@as(?usize, 4), rangeRemainingBytes(strided, 12));
    try std.testing.expectEqual(@as(?usize, 0), rangeRemainingBytes(strided, 16));
    try std.testing.expectEqual(@as(?usize, null), rangeRemainingBytes(strided, 17));
    try std.testing.expectEqual(@as(?usize, null), rangeRemainingBytes(strided, std.math.maxInt(usize)));
    try std.testing.expectEqual(@as(?usize, 0), rangeRemainingBytes(empty, 0));
    try std.testing.expectEqual(@as(?usize, null), rangeRemainingBytes(empty, 1));

    try std.testing.expectEqual(@as(?usize, 16), rangeAccessEndOffset(strided, 12, @sizeOf(u32)));
    try std.testing.expectEqual(@as(?usize, 16), rangeAccessEndOffset(strided, 16, 0));
    try std.testing.expectEqual(@as(?usize, null), rangeAccessEndOffset(strided, 13, @sizeOf(u32)));
    try std.testing.expectEqual(@as(?usize, null), rangeAccessEndOffset(strided, 17, 0));
    try std.testing.expectEqual(@as(?usize, null), rangeAccessEndOffset(strided, std.math.maxInt(usize), 4));

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

    try std.testing.expectEqual(@as(?usize, 1), rangeTypedAccessEndOffset(u8, strided, 0));
    try std.testing.expectEqual(@as(?usize, 6), rangeTypedAccessEndOffset(u16, strided, 4));
    try std.testing.expectEqual(@as(?usize, 12), rangeTypedAccessEndOffset(u32, strided, 8));
    try std.testing.expectEqual(@as(?usize, 8), rangeTypedAccessEndOffset(u16, tightly_spaced, 6));
    try std.testing.expectEqual(@as(?usize, null), rangeTypedAccessEndOffset(u16, strided, 2));
    try std.testing.expectEqual(@as(?usize, null), rangeTypedAccessEndOffset(u32, strided, 6));
    try std.testing.expectEqual(@as(?usize, null), rangeTypedAccessEndOffset(u32, strided, 13));
    try std.testing.expectEqual(@as(?usize, null), rangeTypedAccessEndOffset(u64, tightly_spaced, 8));

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
