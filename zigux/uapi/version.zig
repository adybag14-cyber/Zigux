const std = @import("std");

pub const abi_major: u32 = 0;
pub const abi_minor: u32 = 1;
pub const header_family_revision: u32 = 1;

pub const Version = extern struct {
    abi_major: u32,
    abi_minor: u32,
    header_family_revision: u32,
};

pub const version_size: usize = @sizeOf(Version);
pub const version_align: usize = @alignOf(Version);
pub const abi_major_offset: usize = @offsetOf(Version, "abi_major");
pub const abi_minor_offset: usize = @offsetOf(Version, "abi_minor");
pub const header_family_revision_offset: usize = @offsetOf(Version, "header_family_revision");

pub fn current() Version {
    return .{
        .abi_major = abi_major,
        .abi_minor = abi_minor,
        .header_family_revision = header_family_revision,
    };
}

pub fn eql(left: Version, right: Version) bool {
    return left.abi_major == right.abi_major and
        left.abi_minor == right.abi_minor and
        left.header_family_revision == right.header_family_revision;
}

comptime {
    std.debug.assert(version_size == 12);
    std.debug.assert(version_align == 4);
    std.debug.assert(abi_major_offset == 0);
    std.debug.assert(abi_minor_offset == 4);
    std.debug.assert(header_family_revision_offset == 8);
}
