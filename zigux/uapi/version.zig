const std = @import("std");
const abi = @import("abi_bindings");

const invalid_argument: i32 = -22;

pub const abi_major: u32 = 0;
pub const abi_minor: u32 = 1;
pub const header_family_revision: u32 = 1;

pub const Version = extern struct {
    abi_major: u32,
    abi_minor: u32,
    header_family_revision: u32,
};

pub const Header = abi.BoundaryHeader;

pub const version_size: usize = @sizeOf(Version);
pub const version_align: usize = @alignOf(Version);
pub const abi_major_offset: usize = @offsetOf(Version, "abi_major");
pub const abi_minor_offset: usize = @offsetOf(Version, "abi_minor");
pub const header_family_revision_offset: usize = @offsetOf(Version, "header_family_revision");

pub const header_size: u32 = @sizeOf(Header);
pub const header_align: usize = @alignOf(Header);
pub const header_size_offset: usize = @offsetOf(Header, "size");
pub const header_abi_version_offset: usize = @offsetOf(Header, "abi_version");
pub const header_flags_offset: usize = @offsetOf(Header, "flags");

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

pub fn validate(version: Version) abi.ExportStatus {
    if (matchesCurrent(version)) return abi.okStatus(.kernel);
    return abi.makeStatus(invalid_argument, .kernel);
}

pub fn boundaryHeader(flags: u16) Header {
    return abi.defaultHeader(flags);
}

pub fn compatibleHeader(size: u32, flags: u16) Header {
    return abi.compatibleHeader(size, flags);
}

pub fn hasCurrentAbiVersion(value: u16) bool {
    return abi.headerHasCurrentAbiVersion(value);
}

pub fn isCanonicalSize(value: u32) bool {
    return value == header_size;
}

pub fn isCompatibleSize(value: u32) bool {
    return value >= header_size;
}

pub fn isCanonical(header: Header) bool {
    return abi.headerIsCanonical(header);
}

pub fn isCompatible(header: Header) bool {
    return abi.headerIsCompatible(header);
}

pub fn extendsBoundary(header: Header) bool {
    return abi.extendsBoundary(header);
}

pub fn requestedExtraBytes(header: Header) u32 {
    return abi.requestedExtraBytes(header);
}

pub fn canonicalizeHeader(header: Header) Header {
    return abi.canonicalizeHeader(header);
}

pub fn validateBoundaryHeader(header: Header) abi.ExportStatus {
    if (isCompatible(header)) return abi.okStatus(.kernel);
    return abi.makeStatus(invalid_argument, .kernel);
}

comptime {
    std.debug.assert(version_size == 12);
    std.debug.assert(version_align == 4);
    std.debug.assert(abi_major_offset == 0);
    std.debug.assert(abi_minor_offset == 4);
    std.debug.assert(header_family_revision_offset == 8);
    std.debug.assert(header_size == 8);
    std.debug.assert(header_align == 4);
    std.debug.assert(header_size_offset == 0);
    std.debug.assert(header_abi_version_offset == 4);
    std.debug.assert(header_flags_offset == 6);
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

test "version helpers keep boundary header compatibility explicit" {
    const canonical = boundaryHeader(0x31);
    const expanded = compatibleHeader(header_size + 8, 0x31);
    const stale = Header{
        .size = header_size,
        .abi_version = @as(u16, abi.ABI_VERSION + 1),
        .flags = 0x11,
    };
    const canonicalized = canonicalizeHeader(expanded);
    const valid = validateBoundaryHeader(canonical);
    const invalid = validateBoundaryHeader(stale);

    try std.testing.expectEqual(@as(u32, 8), header_size);
    try std.testing.expectEqual(@as(usize, 4), header_align);
    try std.testing.expectEqual(@as(usize, 0), header_size_offset);
    try std.testing.expectEqual(@as(usize, 4), header_abi_version_offset);
    try std.testing.expectEqual(@as(usize, 6), header_flags_offset);

    try std.testing.expect(hasCurrentAbiVersion(canonical.abi_version));
    try std.testing.expect(isCanonicalSize(canonical.size));
    try std.testing.expect(isCompatibleSize(canonical.size));
    try std.testing.expect(isCanonical(canonical));
    try std.testing.expect(isCompatible(canonical));
    try std.testing.expect(!extendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), requestedExtraBytes(canonical));
    try std.testing.expectEqual(@as(i32, 0), valid.code);

    try std.testing.expect(!isCanonicalSize(expanded.size));
    try std.testing.expect(isCompatibleSize(expanded.size));
    try std.testing.expect(!isCanonical(expanded));
    try std.testing.expect(isCompatible(expanded));
    try std.testing.expect(extendsBoundary(expanded));
    try std.testing.expectEqual(@as(u32, 8), requestedExtraBytes(expanded));

    try std.testing.expect(!hasCurrentAbiVersion(stale.abi_version));
    try std.testing.expect(isCanonicalSize(stale.size));
    try std.testing.expect(isCompatibleSize(stale.size));
    try std.testing.expect(!isCanonical(stale));
    try std.testing.expect(!isCompatible(stale));
    try std.testing.expect(!extendsBoundary(stale));
    try std.testing.expectEqual(@as(u32, 0), requestedExtraBytes(stale));
    try std.testing.expectEqual(@as(i32, invalid_argument), invalid.code);

    try std.testing.expectEqual(header_size, canonicalized.size);
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), canonicalized.abi_version);
    try std.testing.expectEqual(expanded.flags, canonicalized.flags);
    try std.testing.expect(isCanonical(canonicalized));
}

test "version helpers expose status-tagged compatibility validation" {
    const live = current();
    const stale = Version{
        .abi_major = abi_major,
        .abi_minor = abi_minor + 1,
        .header_family_revision = header_family_revision,
    };
    const valid = validate(live);
    const invalid = validate(stale);

    try std.testing.expectEqual(@as(i32, 0), valid.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.kernel)), valid.facility);
    try std.testing.expectEqual(@as(u16, 0), valid.flags);

    try std.testing.expectEqual(@as(i32, invalid_argument), invalid.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.kernel)), invalid.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid.flags);
}
