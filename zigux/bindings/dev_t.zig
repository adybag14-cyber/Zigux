const std = @import("std");
const uapi = @import("uapi_dev_t");

pub const abi_version = uapi.abi_version;
pub const fields_size: usize = @sizeOf(uapi.Fields);
pub const fields_align: usize = @alignOf(uapi.Fields);
pub const major_offset: usize = @offsetOf(uapi.Fields, "major");
pub const minor_offset: usize = @offsetOf(uapi.Fields, "minor");

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
