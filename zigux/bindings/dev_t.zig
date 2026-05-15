const std = @import("std");

pub const minor_bits: u5 = 20;
pub const minor_mask: u32 = (@as(u32, 1) << minor_bits) - 1;
pub const max_major: u32 = ~@as(u32, 0) >> minor_bits;

pub const EncodeError = error{
    MajorOutOfRange,
    MinorOutOfRange,
    RangeExhausted,
};

pub fn majorValid(major_id: u32) bool {
    return major_id <= max_major;
}

pub fn minorValid(minor_id: u32) bool {
    return minor_id <= minor_mask;
}

pub fn packMasked(major_id: u32, minor_id: u32) u32 {
    return @as(u32, @truncate((@as(u64, major_id) << minor_bits) | (@as(u64, minor_id) & minor_mask)));
}

pub fn encode(major_id: u32, minor_id: u32) EncodeError!u32 {
    if (!majorValid(major_id)) return error.MajorOutOfRange;
    if (!minorValid(minor_id)) return error.MinorOutOfRange;
    return packMasked(major_id, minor_id);
}

pub fn major(dev: u32) u32 {
    return dev >> minor_bits;
}

pub fn minor(dev: u32) u32 {
    return dev & minor_mask;
}

pub fn rangeFits(first_minor: u32, count: u32) bool {
    if (count == 0) return true;
    if (!minorValid(first_minor)) return false;
    const last = first_minor + count - 1;
    return last <= minor_mask and last >= first_minor;
}

pub fn lastInRange(major_id: u32, first_minor: u32, count: u32) EncodeError!u32 {
    if (!majorValid(major_id)) return error.MajorOutOfRange;
    if (count == 0) return encode(major_id, first_minor);
    if (!rangeFits(first_minor, count)) return error.RangeExhausted;
    return encode(major_id, first_minor + count - 1);
}

test "dev_t binding keeps canonical bit geometry explicit" {
    try std.testing.expectEqual(@as(u5, 20), minor_bits);
    try std.testing.expectEqual(@as(u32, 1_048_575), minor_mask);
    try std.testing.expectEqual(@as(u32, 4_095), max_major);
    try std.testing.expect(majorValid(max_major));
    try std.testing.expect(!majorValid(max_major + 1));
    try std.testing.expect(minorValid(minor_mask));
    try std.testing.expect(!minorValid(minor_mask + 1));
}

test "dev_t binding keeps encoding and masked packing reviewable" {
    const encoded = try encode(73, 0x34567);
    const masked = packMasked(max_major + 7, minor_mask + 9);

    try std.testing.expectEqual(@as(u32, 76_760_423), encoded);
    try std.testing.expectEqual(@as(u32, 73), major(encoded));
    try std.testing.expectEqual(@as(u32, 0x34567), minor(encoded));
    try std.testing.expectEqual(@as(u32, 6), major(masked));
    try std.testing.expectEqual(@as(u32, 8), minor(masked));
}

test "dev_t binding keeps range boundaries and failures explicit" {
    try std.testing.expect(rangeFits(8, 4));
    try std.testing.expect(rangeFits(minor_mask, 0));
    try std.testing.expect(!rangeFits(minor_mask, 2));
    try std.testing.expectEqual(@as(u32, 12), major(try lastInRange(12, 8, 4)));
    try std.testing.expectEqual(@as(u32, 11), minor(try lastInRange(12, 8, 4)));
    try std.testing.expectError(error.MajorOutOfRange, encode(max_major + 1, 0));
    try std.testing.expectError(error.MinorOutOfRange, encode(0, minor_mask + 1));
    try std.testing.expectError(error.RangeExhausted, lastInRange(5, minor_mask - 1, 3));
}
