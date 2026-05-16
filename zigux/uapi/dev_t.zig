const std = @import("std");

pub const abi_version: u32 = 1;

pub const Fields = extern struct {
    major: u32,
    minor: u32,
};

pub fn init(major: u32, minor: u32) Fields {
    return .{
        .major = major,
        .minor = minor,
    };
}

comptime {
    std.debug.assert(@sizeOf(Fields) == 8);
    std.debug.assert(@alignOf(Fields) == 4);
}
