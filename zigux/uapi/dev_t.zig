const std = @import("std");

pub const abi_version: u32 = 1;

pub const Fields = extern struct {
    major: u32,
    minor: u32,
};

pub const fields_size: usize = @sizeOf(Fields);
pub const fields_align: usize = @alignOf(Fields);
pub const major_offset: usize = @offsetOf(Fields, "major");
pub const minor_offset: usize = @offsetOf(Fields, "minor");

pub fn init(major: u32, minor: u32) Fields {
    return .{
        .major = major,
        .minor = minor,
    };
}

comptime {
    std.debug.assert(fields_size == 8);
    std.debug.assert(fields_align == 4);
    std.debug.assert(major_offset == 0);
    std.debug.assert(minor_offset == 4);
}
