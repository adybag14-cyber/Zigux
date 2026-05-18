const std = @import("std");
const uapi = @import("uapi_dev_t");

pub const abi_version = uapi.abi_version;
pub const fields_size = uapi.fields_size;
pub const fields_align = uapi.fields_align;
pub const major_offset = uapi.major_offset;
pub const minor_offset = uapi.minor_offset;

pub const Fields = uapi.Fields;

pub fn init(major: u32, minor: u32) Fields {
    return uapi.init(major, minor);
}

pub fn eql(left: Fields, right: Fields) bool {
    return left.major == right.major and left.minor == right.minor;
}

comptime {
    std.debug.assert(abi_version == 1);
    std.debug.assert(fields_size == 8);
    std.debug.assert(fields_align == 4);
    std.debug.assert(major_offset == 0);
    std.debug.assert(minor_offset == 4);
}

test "dev_t binding keeps the published layout contract" {
    try std.testing.expectEqual(@as(u32, 1), abi_version);
    try std.testing.expectEqual(@as(usize, 8), fields_size);
    try std.testing.expectEqual(@as(usize, 4), fields_align);
    try std.testing.expectEqual(@as(usize, 0), major_offset);
    try std.testing.expectEqual(@as(usize, 4), minor_offset);

    try std.testing.expectEqual(@as(usize, 8), @sizeOf(Fields));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(Fields));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(Fields, "major"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(Fields, "minor"));
}

test "dev_t binding init and eql keep major minor pairing explicit" {
    const left = init(7, 11);
    const same = init(7, 11);
    const different_major = init(8, 11);
    const different_minor = init(7, 12);

    try std.testing.expectEqual(@as(u32, 7), left.major);
    try std.testing.expectEqual(@as(u32, 11), left.minor);
    try std.testing.expect(eql(left, same));
    try std.testing.expect(!eql(left, different_major));
    try std.testing.expect(!eql(left, different_minor));
}
