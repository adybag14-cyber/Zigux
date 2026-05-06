const std = @import("std");

pub const minor_bits: u5 = 20;
pub const minor_mask: u32 = (1 << minor_bits) - 1;
pub const max_major: u32 = std.math.maxInt(u32) >> minor_bits;

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

pub fn encode(major_id: u32, minor_id: u32) EncodeError!u32 {
    if (!majorValid(major_id))
        return error.MajorOutOfRange;
    if (!minorValid(minor_id))
        return error.MinorOutOfRange;
    return (major_id << minor_bits) | minor_id;
}

pub fn major(dev: u32) u32 {
    return dev >> minor_bits;
}

pub fn minor(dev: u32) u32 {
    return dev & minor_mask;
}

pub fn rangeFits(first_minor: u32, count: u32) bool {
    if (!minorValid(first_minor))
        return false;
    if (count == 0)
        return true;
    return count - 1 <= minor_mask - first_minor;
}

pub fn lastInRange(major_id: u32, first_minor: u32, count: u32) EncodeError!u32 {
    if (!majorValid(major_id))
        return error.MajorOutOfRange;
    if (!minorValid(first_minor))
        return error.MinorOutOfRange;
    if (!rangeFits(first_minor, count))
        return error.RangeExhausted;
    if (count == 0)
        return encode(major_id, first_minor);
    return encode(major_id, first_minor + count - 1);
}

test "dev_t codec round-trips a major and minor pair" {
    const encoded = try encode(73, 0x34567);
    try std.testing.expectEqual(@as(u32, 73), major(encoded));
    try std.testing.expectEqual(@as(u32, 0x34567), minor(encoded));
}

test "dev_t codec keeps the boundary minor values intact" {
    const encoded = try encode(max_major, minor_mask);
    try std.testing.expectEqual(max_major, major(encoded));
    try std.testing.expectEqual(minor_mask, minor(encoded));
}

test "dev_t range helpers track bounded minor spans" {
    try std.testing.expect(rangeFits(8, 4));
    try std.testing.expectEqual(try encode(12, 11), try lastInRange(12, 8, 4));
    try std.testing.expect(rangeFits(minor_mask, 0));
    try std.testing.expectEqual(try encode(9, minor_mask), try lastInRange(9, minor_mask, 0));
}

test "dev_t codec rejects out-of-range inputs" {
    try std.testing.expectError(error.MajorOutOfRange, encode(max_major + 1, 0));
    try std.testing.expectError(error.MinorOutOfRange, encode(0, minor_mask + 1));
    try std.testing.expectError(error.RangeExhausted, lastInRange(5, minor_mask - 1, 3));
}
