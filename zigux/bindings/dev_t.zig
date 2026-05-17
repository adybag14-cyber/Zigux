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

test "phase3 binding dev_t mirrors uapi layout constants" {
    try std.testing.expectEqual(uapi.abi_version, abi_version);
    try std.testing.expectEqual(uapi.fields_size, fields_size);
    try std.testing.expectEqual(uapi.fields_align, fields_align);
    try std.testing.expectEqual(uapi.major_offset, major_offset);
    try std.testing.expectEqual(uapi.minor_offset, minor_offset);

    try std.testing.expectEqual(@as(usize, 8), fields_size);
    try std.testing.expectEqual(@as(usize, 4), fields_align);
    try std.testing.expectEqual(@as(usize, 0), major_offset);
    try std.testing.expectEqual(@as(usize, 4), minor_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(Fields)), fields_size);
    try std.testing.expectEqual(@as(usize, @alignOf(Fields)), fields_align);
}

test "phase3 binding dev_t init and eql stay field-wise" {
    const bound = init(7, 19);
    const mirrored = uapi.init(7, 19);
    const different_major = init(8, 19);
    const different_minor = init(7, 23);

    try std.testing.expectEqual(mirrored.major, bound.major);
    try std.testing.expectEqual(mirrored.minor, bound.minor);
    try std.testing.expectEqual(@as(u32, 7), bound.major);
    try std.testing.expectEqual(@as(u32, 19), bound.minor);
    try std.testing.expect(eql(bound, mirrored));
    try std.testing.expect(!eql(bound, different_major));
    try std.testing.expect(!eql(bound, different_minor));
}

comptime {
    std.debug.assert(abi_version == 1);
    std.debug.assert(fields_size == 8);
    std.debug.assert(fields_align == 4);
    std.debug.assert(major_offset == 0);
    std.debug.assert(minor_offset == 4);
}
