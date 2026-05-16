const std = @import("std");

pub const abi_major: u32 = 0;
pub const abi_minor: u32 = 1;
pub const header_family_revision: u32 = 1;

pub const Version = extern struct {
    abi_major: u32,
    abi_minor: u32,
    header_family_revision: u32,
};

pub fn current() Version {
    return .{
        .abi_major = abi_major,
        .abi_minor = abi_minor,
        .header_family_revision = header_family_revision,
    };
}

comptime {
    std.debug.assert(@sizeOf(Version) == 12);
    std.debug.assert(@alignOf(Version) == 4);
}
