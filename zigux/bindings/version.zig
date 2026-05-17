const std = @import("std");
const uapi = @import("uapi_version");

pub const abi_major = uapi.abi_major;
pub const abi_minor = uapi.abi_minor;
pub const header_family_revision = uapi.header_family_revision;
pub const version_size: usize = @sizeOf(uapi.Version);
pub const version_align: usize = @alignOf(uapi.Version);
pub const abi_major_offset: usize = @offsetOf(uapi.Version, "abi_major");
pub const abi_minor_offset: usize = @offsetOf(uapi.Version, "abi_minor");
pub const header_family_revision_offset: usize = @offsetOf(uapi.Version, "header_family_revision");

pub const Version = uapi.Version;

pub fn current() Version {
    return uapi.current();
}

pub fn eql(left: Version, right: Version) bool {
    return left.abi_major == right.abi_major and
        left.abi_minor == right.abi_minor and
        left.header_family_revision == right.header_family_revision;
}

comptime {
    std.debug.assert(abi_major == 0);
    std.debug.assert(abi_minor == 1);
    std.debug.assert(header_family_revision == 1);
    std.debug.assert(version_size == 12);
    std.debug.assert(version_align == 4);
    std.debug.assert(abi_major_offset == 0);
    std.debug.assert(abi_minor_offset == 4);
    std.debug.assert(header_family_revision_offset == 8);
}
