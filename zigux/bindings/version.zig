const std = @import("std");
const uapi = @import("uapi_version");

pub const abi_major = uapi.abi_major;
pub const abi_minor = uapi.abi_minor;
pub const header_family_revision = uapi.header_family_revision;
pub const version_size: usize = uapi.version_size;
pub const version_align: usize = uapi.version_align;
pub const abi_major_offset: usize = uapi.abi_major_offset;
pub const abi_minor_offset: usize = uapi.abi_minor_offset;
pub const header_family_revision_offset: usize = uapi.header_family_revision_offset;

pub const Version = uapi.Version;
pub const ExportStatus = @TypeOf(uapi.validate(uapi.current()));

pub fn current() Version {
    return uapi.current();
}

pub fn eql(left: Version, right: Version) bool {
    return left.abi_major == right.abi_major and
        left.abi_minor == right.abi_minor and
        left.header_family_revision == right.header_family_revision;
}

pub fn hasCurrentAbiMajor(value: u32) bool {
    return uapi.hasCurrentAbiMajor(value);
}

pub fn hasCurrentAbiMinor(value: u32) bool {
    return uapi.hasCurrentAbiMinor(value);
}

pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {
    return uapi.hasCurrentHeaderFamilyRevision(value);
}

pub fn matchesCurrent(version: Version) bool {
    return uapi.matchesCurrent(version);
}

pub fn validate(version: Version) ExportStatus {
    return uapi.validate(version);
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

test "version binding keeps current compatibility explicit" {
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
    const stale_revision = Version{
        .abi_major = abi_major,
        .abi_minor = abi_minor,
        .header_family_revision = header_family_revision + 1,
    };

    try std.testing.expect(hasCurrentAbiMajor(live.abi_major));
    try std.testing.expect(hasCurrentAbiMinor(live.abi_minor));
    try std.testing.expect(hasCurrentHeaderFamilyRevision(live.header_family_revision));
    try std.testing.expect(matchesCurrent(live));

    try std.testing.expect(!hasCurrentAbiMajor(stale_major.abi_major));
    try std.testing.expect(!matchesCurrent(stale_major));
    try std.testing.expect(!hasCurrentAbiMinor(stale_minor.abi_minor));
    try std.testing.expect(!matchesCurrent(stale_minor));
    try std.testing.expect(!hasCurrentHeaderFamilyRevision(stale_revision.header_family_revision));
    try std.testing.expect(!matchesCurrent(stale_revision));
}

test "version binding stays aligned with the UAPI layout surface" {
    const live = current();

    try std.testing.expectEqual(uapi.version_size, version_size);
    try std.testing.expectEqual(uapi.version_align, version_align);
    try std.testing.expectEqual(uapi.abi_major_offset, abi_major_offset);
    try std.testing.expectEqual(uapi.abi_minor_offset, abi_minor_offset);
    try std.testing.expectEqual(uapi.header_family_revision_offset, header_family_revision_offset);
    try std.testing.expectEqual(uapi.current(), live);
    try std.testing.expectEqual(uapi.matchesCurrent(live), matchesCurrent(live));
    try std.testing.expect(uapi.eql(live, live));
    try std.testing.expect(eql(live, live));
}

test "version binding relays status-tagged validation from the UAPI surface" {
    const live = current();
    const stale = Version{
        .abi_major = abi_major,
        .abi_minor = abi_minor + 1,
        .header_family_revision = header_family_revision,
    };

    try std.testing.expectEqual(uapi.validate(live), validate(live));
    try std.testing.expectEqual(uapi.validate(stale), validate(stale));
}
