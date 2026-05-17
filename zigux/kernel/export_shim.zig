const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const dev_t = @import("dev_t_binding");
const version = @import("version_binding");

pub const BoundaryHeader = abi.BoundaryHeader;
pub const ExportStatus = abi.ExportStatus;
pub const Facility = abi.Facility;
pub const Version = version.Version;
pub const DevTFields = dev_t.Fields;

pub fn canonicalHeader(flags: u16) BoundaryHeader {
    return abi.defaultHeader(flags);
}

pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader {
    return abi.compatibleHeader(size, flags);
}

pub fn headerHasCurrentAbiVersion(abi_version: u16) bool {
    return abi.headerHasCurrentAbiVersion(abi_version);
}

pub fn headerIsCanonical(header: BoundaryHeader) bool {
    return abi.headerIsCanonical(header);
}

pub fn headerIsCompatible(header: BoundaryHeader) bool {
    return abi.headerIsCompatible(header);
}

pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {
    return abi.canonicalizeHeader(header);
}

pub fn currentVersion() Version {
    return version.current();
}

pub fn currentVersionHasAbiMajor(abi_major: u32) bool {
    return abi_major == version.abi_major;
}

pub fn currentVersionHasAbiMinor(abi_minor: u32) bool {
    return abi_minor == version.abi_minor;
}

pub fn currentVersionHasHeaderFamilyRevision(header_family_revision: u32) bool {
    return header_family_revision == version.header_family_revision;
}

pub fn currentVersionMatches(snapshot: Version) bool {
    return currentVersionHasAbiMajor(snapshot.abi_major) and
        currentVersionHasAbiMinor(snapshot.abi_minor) and
        currentVersionHasHeaderFamilyRevision(snapshot.header_family_revision);
}

pub fn makeDevTFields(major: u32, minor: u32) DevTFields {
    return dev_t.init(major, minor);
}

pub fn okStatus(facility: Facility) ExportStatus {
    return .{
        .code = 0,
        .facility = @intFromEnum(facility),
        .flags = 0,
    };
}

pub fn errorStatus(code: i32, facility: Facility) ExportStatus {
    return .{
        .code = code,
        .facility = @intFromEnum(facility),
        .flags = if (code < 0) abi.STATUS_FLAG_ERROR else 0,
    };
}

test "export shim preserves boundary header compatibility helpers" {
    const canonical = canonicalHeader(0x41);
    const expanded = compatibleHeader(@sizeOf(BoundaryHeader) + 8, 0x41);
    const stale = BoundaryHeader{
        .size = @sizeOf(BoundaryHeader),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0,
    };
    const canonicalized = canonicalizeHeader(expanded);

    try testing.expect(headerHasCurrentAbiVersion(canonical.abi_version));
    try testing.expect(headerIsCanonical(canonical));
    try testing.expect(headerIsCompatible(canonical));

    try testing.expect(!headerIsCanonical(expanded));
    try testing.expect(headerIsCompatible(expanded));

    try testing.expect(!headerHasCurrentAbiVersion(stale.abi_version));
    try testing.expect(!headerIsCanonical(stale));
    try testing.expect(!headerIsCompatible(stale));

    try testing.expectEqual(@as(u32, @sizeOf(BoundaryHeader)), canonicalized.size);
    try testing.expectEqual(@as(u16, abi.ABI_VERSION), canonicalized.abi_version);
    try testing.expectEqual(expanded.flags, canonicalized.flags);
    try testing.expect(headerIsCanonical(canonicalized));
}

test "export shim preserves current version compatibility helpers" {
    const current = currentVersion();
    const stale_major = Version{
        .abi_major = current.abi_major + 1,
        .abi_minor = current.abi_minor,
        .header_family_revision = current.header_family_revision,
    };
    const stale_minor = Version{
        .abi_major = current.abi_major,
        .abi_minor = current.abi_minor + 1,
        .header_family_revision = current.header_family_revision,
    };
    const stale_revision = Version{
        .abi_major = current.abi_major,
        .abi_minor = current.abi_minor,
        .header_family_revision = current.header_family_revision + 1,
    };

    try testing.expect(currentVersionHasAbiMajor(current.abi_major));
    try testing.expect(!currentVersionHasAbiMajor(stale_major.abi_major));
    try testing.expect(currentVersionHasAbiMinor(current.abi_minor));
    try testing.expect(!currentVersionHasAbiMinor(stale_minor.abi_minor));
    try testing.expect(currentVersionHasHeaderFamilyRevision(current.header_family_revision));
    try testing.expect(!currentVersionHasHeaderFamilyRevision(stale_revision.header_family_revision));

    try testing.expect(currentVersionMatches(current));
    try testing.expect(!currentVersionMatches(stale_major));
    try testing.expect(!currentVersionMatches(stale_minor));
    try testing.expect(!currentVersionMatches(stale_revision));
    try testing.expect(version.eql(current, version.current()));
}

test "export shim status helpers keep facility and error flags explicit" {
    const ok = okStatus(.helpers);
    const err = errorStatus(-12, .kernel);
    const non_error = errorStatus(7, .drivers);

    try testing.expectEqual(@as(i32, 0), ok.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.helpers)), ok.facility);
    try testing.expectEqual(@as(u16, 0), ok.flags);

    try testing.expectEqual(@as(i32, -12), err.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), err.facility);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), err.flags);

    try testing.expectEqual(@as(i32, 7), non_error.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.drivers)), non_error.facility);
    try testing.expectEqual(@as(u16, 0), non_error.flags);
}

test "export shim forwards starter dev_t fields without changing layout semantics" {
    const fields = makeDevTFields(11, 29);
    const same = makeDevTFields(11, 29);
    const different = makeDevTFields(11, 30);

    try testing.expectEqual(@as(usize, 8), @sizeOf(DevTFields));
    try testing.expectEqual(@as(usize, 4), @alignOf(DevTFields));
    try testing.expectEqual(@as(u32, 11), fields.major);
    try testing.expectEqual(@as(u32, 29), fields.minor);
    try testing.expect(dev_t.eql(fields, same));
    try testing.expect(!dev_t.eql(fields, different));
}
