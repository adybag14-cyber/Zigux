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

pub fn hasCurrentAbiMajor(value: u32) bool {
    return value == abi_major;
}

pub fn hasCurrentAbiMinor(value: u32) bool {
    return value == abi_minor;
}

pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {
    return value == header_family_revision;
}

pub fn matchesCurrent(version: Version) bool {
    return hasCurrentAbiMajor(version.abi_major) and
        hasCurrentAbiMinor(version.abi_minor) and
        hasCurrentHeaderFamilyRevision(version.header_family_revision);
}

comptime {
    std.debug.assert(version_size == 12);
    std.debug.assert(version_align == 4);
    std.debug.assert(abi_major_offset == 0);
    std.debug.assert(abi_minor_offset == 4);
    std.debug.assert(header_family_revision_offset == 8);
}

test "version helpers keep current compatibility explicit" {
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

test "version helpers preserve layout and equality semantics" {
    const left = current();
    const same = current();
    const different = Version{
        .abi_major = abi_major,
        .abi_minor = abi_minor,
        .header_family_revision = header_family_revision + 1,
    };

    try std.testing.expectEqual(@as(usize, 12), version_size);
    try std.testing.expectEqual(@as(usize, 4), version_align);
    try std.testing.expectEqual(@as(usize, 0), abi_major_offset);
    try std.testing.expectEqual(@as(usize, 4), abi_minor_offset);
    try std.testing.expectEqual(@as(usize, 8), header_family_revision_offset);

    try std.testing.expect(eql(left, same));
    try std.testing.expect(!eql(left, different));
}
