const std = @import("std");

const dev_t_bindings = @import("dev_t_bindings");

pub const minor_bits: u5 = dev_t_bindings.minor_bits;
pub const minor_mask: u32 = dev_t_bindings.minor_mask;
pub const major_max: u32 = dev_t_bindings.max_major;

pub const EncodeError = dev_t_bindings.EncodeError;

pub fn majorValid(major_id: u32) bool {
    return dev_t_bindings.majorValid(major_id);
}

pub fn minorValid(minor_id: u32) bool {
    return dev_t_bindings.minorValid(minor_id);
}

pub fn packMasked(major_id: u32, minor_id: u32) u32 {
    return dev_t_bindings.packMasked(major_id, minor_id);
}

pub fn encode(major_id: u32, minor_id: u32) EncodeError!u32 {
    return dev_t_bindings.encode(major_id, minor_id);
}

pub fn major(dev: u32) u32 {
    return dev_t_bindings.major(dev);
}

pub fn minor(dev: u32) u32 {
    return dev_t_bindings.minor(dev);
}

pub fn rangeFits(first_minor: u32, count: u32) bool {
    return dev_t_bindings.rangeFits(first_minor, count);
}

pub fn lastInRange(major_id: u32, first_minor: u32, count: u32) EncodeError!u32 {
    return dev_t_bindings.lastInRange(major_id, first_minor, count);
}

test "phase3 uapi dev_t starter keeps encode and range parity explicit" {
    const encoded = try encode(73, 0x34567);

    try std.testing.expectEqual(dev_t_bindings.minor_bits, minor_bits);
    try std.testing.expectEqual(dev_t_bindings.minor_mask, minor_mask);
    try std.testing.expectEqual(dev_t_bindings.max_major, major_max);
    try std.testing.expectEqual(try dev_t_bindings.encode(73, 0x34567), encoded);
    try std.testing.expectEqual(@as(u32, 73), major(encoded));
    try std.testing.expectEqual(@as(u32, 0x34567), minor(encoded));
    try std.testing.expect(rangeFits(8, 4));
    try std.testing.expectEqual(try dev_t_bindings.lastInRange(12, 8, 4), try lastInRange(12, 8, 4));
}

test "phase3 uapi dev_t starter keeps masked pack parity explicit" {
    const masked = packMasked(major_max + 7, minor_mask + 9);

    try std.testing.expectEqual(dev_t_bindings.packMasked(major_max + 7, minor_mask + 9), masked);
    try std.testing.expectEqual(packMasked(73, 0x34567), try encode(73, 0x34567));
    try std.testing.expectEqual(@as(u32, 6), major(masked));
    try std.testing.expectEqual(@as(u32, 8), minor(masked));
}

test "phase3 uapi dev_t starter rejects out-of-range inputs" {
    try std.testing.expectError(error.MajorOutOfRange, encode(major_max + 1, 0));
    try std.testing.expectError(error.MinorOutOfRange, encode(0, minor_mask + 1));
    try std.testing.expectError(error.RangeExhausted, lastInRange(5, minor_mask - 1, 3));
}
