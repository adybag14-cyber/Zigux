const std = @import("std");
const uapi = @import("uapi_dev_t");

pub const abi_version = uapi.abi_version;
pub const major_bits = uapi.major_bits;
pub const minor_bits = uapi.minor_bits;
pub const max_major = uapi.max_major;
pub const max_minor = uapi.max_minor;
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

pub fn validate(fields: Fields) bool {
    return uapi.validate(fields);
}

pub fn validateRange(start: Fields, end: Fields) bool {
    return uapi.validateRange(start, end);
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
}
