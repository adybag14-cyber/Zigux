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
    return uapi.eql(left, right);
}

pub fn hasCurrentAbiMajor(version: Version) bool {
    return version.abi_major == abi_major;
}

pub fn hasCurrentAbiMinor(version: Version) bool {
    return version.abi_minor == abi_minor;
}

pub fn hasCurrentHeaderFamilyRevision(version: Version) bool {
    return version.header_family_revision == header_family_revision;
}

pub fn matchesCurrent(version: Version) bool {
    return hasCurrentAbiMajor(version) and
        hasCurrentAbiMinor(version) and
        hasCurrentHeaderFamilyRevision(version);
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

test "binding version compatibility helpers stay aligned with current constants" {
    const live = current();
    const stale_major = Version{
        .abi_major = abi_major + 1,
        .abi_minor = abi_minor,
        .header_family_revision = header_family_revision,
    };
    const stale_minor = Version{
        .abi_major = abi_major,
        .abi_minor = abi_minor + 1,
        .header_family_revision = header_family_revision,
    };
    const stale_family = Version{
        .abi_major = abi_major,
        .abi_minor = abi_minor,
        .header_family_revision = header_family_revision + 1,
    };

    try std.testing.expect(hasCurrentAbiMajor(live));
    try std.testing.expect(hasCurrentAbiMinor(live));
    try std.testing.expect(hasCurrentHeaderFamilyRevision(live));
    try std.testing.expect(matchesCurrent(live));
    try std.testing.expect(!hasCurrentAbiMajor(stale_major));
    try std.testing.expect(!matchesCurrent(stale_major));
    try std.testing.expect(!hasCurrentAbiMinor(stale_minor));
    try std.testing.expect(!matchesCurrent(stale_minor));
    try std.testing.expect(!hasCurrentHeaderFamilyRevision(stale_family));
    try std.testing.expect(!matchesCurrent(stale_family));
}
