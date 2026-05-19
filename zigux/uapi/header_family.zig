const std = @import("std");

const abi = @import("abi_bindings");
const dev_t = @import("uapi_dev_t");
const version = @import("uapi_version");

pub const BoundaryHeader = abi.BoundaryHeader;
pub const Version = version.Version;
pub const DevTFields = dev_t.Fields;

pub const abi_version: u16 = abi.ABI_VERSION;
pub const header_size: u32 = @sizeOf(BoundaryHeader);
pub const dev_t_packet_present: u32 = 1;

pub fn currentVersion() Version {
    return version.current();
}

pub fn hasCurrentAbiMajor(value: u32) bool {
    return version.hasCurrentAbiMajor(value);
}

pub fn hasCurrentAbiMinor(value: u32) bool {
    return version.hasCurrentAbiMinor(value);
}

pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {
    return version.hasCurrentHeaderFamilyRevision(value);
}

pub fn versionMatchesCurrent(value: Version) bool {
    return version.matchesCurrent(value);
}

pub fn currentBoundaryHeader(flags: u16) BoundaryHeader {
    return abi.defaultHeader(flags);
}

pub fn compatibleBoundaryHeader(size: u32, flags: u16) BoundaryHeader {
    return abi.compatibleHeader(size, flags);
}

pub fn hasCurrentBoundaryAbiVersion(value: u16) bool {
    return abi.headerHasCurrentAbiVersion(value);
}

pub fn boundaryHeaderIsCanonical(header: BoundaryHeader) bool {
    return abi.headerIsCanonical(header);
}

pub fn boundaryHeaderIsCompatible(header: BoundaryHeader) bool {
    return abi.headerIsCompatible(header);
}

pub fn boundaryHeaderExtendsBoundary(header: BoundaryHeader) bool {
    return abi.extendsBoundary(header);
}

pub fn boundaryHeaderRequestedExtraBytes(header: BoundaryHeader) u32 {
    return abi.requestedExtraBytes(header);
}

pub fn canonicalizeBoundaryHeader(header: BoundaryHeader) BoundaryHeader {
    return abi.canonicalizeHeader(header);
}

pub fn makeDevTFields(major: u32, minor: u32) DevTFields {
    return dev_t.init(major, minor);
}

pub fn validateDevTFields(fields: DevTFields) bool {
    return dev_t.validate(fields);
}

pub fn validateDevTFieldsRange(start: DevTFields, end: DevTFields) bool {
    return dev_t.validateRange(start, end);
}

test "header family mirrors the current version and boundary header surface" {
    const live = currentVersion();
    const canonical = currentBoundaryHeader(0x21);
    const expanded = compatibleBoundaryHeader(header_size + 12, 0x21);
    const stale = BoundaryHeader{
        .size = header_size,
        .abi_version = abi_version + 1,
        .flags = 0,
    };
    const canonicalized = canonicalizeBoundaryHeader(expanded);

    try std.testing.expectEqual(version.current(), live);
    try std.testing.expect(hasCurrentAbiMajor(live.abi_major));
    try std.testing.expect(hasCurrentAbiMinor(live.abi_minor));
    try std.testing.expect(hasCurrentHeaderFamilyRevision(live.header_family_revision));
    try std.testing.expect(versionMatchesCurrent(live));

    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), abi_version);
    try std.testing.expectEqual(@as(u32, @sizeOf(BoundaryHeader)), header_size);
    try std.testing.expect(hasCurrentBoundaryAbiVersion(canonical.abi_version));
    try std.testing.expect(boundaryHeaderIsCanonical(canonical));
    try std.testing.expect(boundaryHeaderIsCompatible(canonical));
    try std.testing.expect(!boundaryHeaderExtendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), boundaryHeaderRequestedExtraBytes(canonical));

    try std.testing.expect(!boundaryHeaderIsCanonical(expanded));
    try std.testing.expect(boundaryHeaderIsCompatible(expanded));
    try std.testing.expect(boundaryHeaderExtendsBoundary(expanded));
    try std.testing.expectEqual(@as(u32, 12), boundaryHeaderRequestedExtraBytes(expanded));

    try std.testing.expect(!hasCurrentBoundaryAbiVersion(stale.abi_version));
    try std.testing.expect(!boundaryHeaderIsCanonical(stale));
    try std.testing.expect(!boundaryHeaderIsCompatible(stale));
    try std.testing.expect(!boundaryHeaderExtendsBoundary(stale));

    try std.testing.expectEqual(canonical.size, canonicalized.size);
    try std.testing.expectEqual(canonical.abi_version, canonicalized.abi_version);
    try std.testing.expectEqual(expanded.flags, canonicalized.flags);
}

test "header family mirrors dev_t validation helpers" {
    const valid = makeDevTFields(dev_t.max_major, dev_t.max_minor);
    const invalid_major = makeDevTFields(dev_t.max_major + 1, 0);
    const invalid_minor = makeDevTFields(0, dev_t.max_minor + 1);
    const range_end = makeDevTFields(dev_t.max_major, dev_t.max_minor);
    const earlier = makeDevTFields(dev_t.max_major, dev_t.max_minor - 1);

    try std.testing.expectEqual(@as(u32, 1), dev_t_packet_present);
    try std.testing.expect(validateDevTFields(valid));
    try std.testing.expect(!validateDevTFields(invalid_major));
    try std.testing.expect(!validateDevTFields(invalid_minor));
    try std.testing.expect(validateDevTFieldsRange(valid, range_end));
    try std.testing.expect(!validateDevTFieldsRange(valid, earlier));
}
