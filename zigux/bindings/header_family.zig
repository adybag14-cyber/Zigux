const std = @import("std");
const abi = @import("abi_bindings");
const dev_t_binding = @import("dev_t_binding");
const version_binding = @import("version_binding");
const uapi_version = @import("uapi_version");

pub const uapi_abi_major: u32 = uapi_version.abi_major;
pub const uapi_abi_minor: u32 = uapi_version.abi_minor;
pub const uapi_header_family_revision: u32 = uapi_version.header_family_revision;
pub const uapi_dev_t_packet_present: u32 = 1;

pub const Version = version_binding.Version;
pub const BoundaryHeader = abi.BoundaryHeader;
pub const DevTFields = dev_t_binding.Fields;

pub fn currentVersion() Version {
    return version_binding.current();
}

pub fn hasCurrentAbiMajor(value: u32) bool {
    return uapi_version.hasCurrentAbiMajor(value);
}

pub fn hasCurrentAbiMinor(value: u32) bool {
    return uapi_version.hasCurrentAbiMinor(value);
}

pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {
    return uapi_version.hasCurrentHeaderFamilyRevision(value);
}

pub fn versionMatchesCurrent(version: Version) bool {
    return version_binding.matchesCurrent(version);
}

pub fn currentBoundaryHeader(flags: u16) BoundaryHeader {
    return abi.defaultHeader(flags);
}

pub fn compatibleBoundaryHeader(size: u32, flags: u16) BoundaryHeader {
    return abi.compatibleHeader(size, flags);
}

pub fn boundaryHeaderHasCurrentAbiVersion(abi_version: u16) bool {
    return abi.headerHasCurrentAbiVersion(abi_version);
}

pub fn boundaryHeaderIsCompatibleSize(size: u32) bool {
    return size >= @sizeOf(BoundaryHeader);
}

pub fn boundaryHeaderIsCanonicalSize(size: u32) bool {
    return size == @sizeOf(BoundaryHeader);
}

pub fn boundaryHeaderIsCanonical(header: BoundaryHeader) bool {
    return abi.headerIsCanonical(header);
}

pub fn boundaryHeaderIsCompatible(header: BoundaryHeader) bool {
    return abi.headerIsCompatible(header);
}

pub fn boundaryHeaderExtendsBoundary(header: BoundaryHeader) bool {
    return boundaryHeaderIsCompatible(header) and !boundaryHeaderIsCanonical(header);
}

pub fn boundaryHeaderRequestedExtraBytes(header: BoundaryHeader) u32 {
    if (!boundaryHeaderExtendsBoundary(header)) return 0;
    return header.size - @sizeOf(BoundaryHeader);
}

pub fn canonicalizeBoundaryHeader(header: BoundaryHeader) BoundaryHeader {
    return abi.canonicalizeHeader(header);
}

pub fn devTFieldsAreValid(fields: DevTFields) bool {
    return dev_t_binding.validate(fields);
}

pub fn devTFieldsRangeIsValid(start: DevTFields, end: DevTFields) bool {
    return dev_t_binding.validateRange(start, end);
}

test "header family binding mirrors current version compatibility surface" {
    const live = currentVersion();
    const stale_major = Version{
        .abi_major = uapi_abi_major + 1,
        .abi_minor = uapi_abi_minor,
        .header_family_revision = uapi_header_family_revision,
    };
    const stale_minor = Version{
        .abi_major = uapi_abi_major,
        .abi_minor = uapi_abi_minor + 1,
        .header_family_revision = uapi_header_family_revision,
    };
    const stale_revision = Version{
        .abi_major = uapi_abi_major,
        .abi_minor = uapi_abi_minor,
        .header_family_revision = uapi_header_family_revision + 1,
    };

    try std.testing.expectEqual(@as(u32, 1), uapi_dev_t_packet_present);
    try std.testing.expectEqual(version_binding.current(), live);
    try std.testing.expect(hasCurrentAbiMajor(live.abi_major));
    try std.testing.expect(hasCurrentAbiMinor(live.abi_minor));
    try std.testing.expect(hasCurrentHeaderFamilyRevision(live.header_family_revision));
    try std.testing.expect(versionMatchesCurrent(live));
    try std.testing.expect(version_binding.eql(live, version_binding.current()));

    try std.testing.expect(!hasCurrentAbiMajor(stale_major.abi_major));
    try std.testing.expect(!versionMatchesCurrent(stale_major));
    try std.testing.expect(!hasCurrentAbiMinor(stale_minor.abi_minor));
    try std.testing.expect(!versionMatchesCurrent(stale_minor));
    try std.testing.expect(!hasCurrentHeaderFamilyRevision(stale_revision.header_family_revision));
    try std.testing.expect(!versionMatchesCurrent(stale_revision));
}

test "header family binding keeps boundary header compatibility helpers direct" {
    const canonical = currentBoundaryHeader(0x55);
    const expanded = compatibleBoundaryHeader(@sizeOf(BoundaryHeader) + 16, 0x55);
    const stale = BoundaryHeader{
        .size = @sizeOf(BoundaryHeader),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0x11,
    };
    const normalized = canonicalizeBoundaryHeader(expanded);

    try std.testing.expectEqual(@as(u32, @sizeOf(BoundaryHeader)), canonical.size);
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), canonical.abi_version);
    try std.testing.expectEqual(@as(u16, 0x55), canonical.flags);
    try std.testing.expect(boundaryHeaderHasCurrentAbiVersion(canonical.abi_version));
    try std.testing.expect(boundaryHeaderIsCanonicalSize(canonical.size));
    try std.testing.expect(boundaryHeaderIsCompatibleSize(canonical.size));
    try std.testing.expect(boundaryHeaderIsCanonical(canonical));
    try std.testing.expect(boundaryHeaderIsCompatible(canonical));
    try std.testing.expect(!boundaryHeaderExtendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), boundaryHeaderRequestedExtraBytes(canonical));

    try std.testing.expect(!boundaryHeaderIsCanonicalSize(expanded.size));
    try std.testing.expect(boundaryHeaderIsCompatibleSize(expanded.size));
    try std.testing.expect(!boundaryHeaderIsCanonical(expanded));
    try std.testing.expect(boundaryHeaderIsCompatible(expanded));
    try std.testing.expect(boundaryHeaderExtendsBoundary(expanded));
    try std.testing.expectEqual(@as(u32, 16), boundaryHeaderRequestedExtraBytes(expanded));

    try std.testing.expect(!boundaryHeaderHasCurrentAbiVersion(stale.abi_version));
    try std.testing.expect(boundaryHeaderIsCanonicalSize(stale.size));
    try std.testing.expect(boundaryHeaderIsCompatibleSize(stale.size));
    try std.testing.expect(!boundaryHeaderIsCanonical(stale));
    try std.testing.expect(!boundaryHeaderIsCompatible(stale));
    try std.testing.expect(!boundaryHeaderExtendsBoundary(stale));
    try std.testing.expectEqual(@as(u32, 0), boundaryHeaderRequestedExtraBytes(stale));

    try std.testing.expectEqual(@as(u32, @sizeOf(BoundaryHeader)), normalized.size);
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), normalized.abi_version);
    try std.testing.expectEqual(expanded.flags, normalized.flags);
    try std.testing.expect(boundaryHeaderIsCanonical(normalized));
}

test "header family binding mirrors Linux-facing dev_t validation helpers" {
    const valid = DevTFields{
        .major = dev_t_binding.max_major,
        .minor = dev_t_binding.max_minor,
    };
    const same = DevTFields{
        .major = dev_t_binding.max_major,
        .minor = dev_t_binding.max_minor,
    };
    const invalid_major = DevTFields{
        .major = dev_t_binding.max_major + 1,
        .minor = 0,
    };
    const invalid_minor = DevTFields{
        .major = 0,
        .minor = dev_t_binding.max_minor + 1,
    };
    const earlier = DevTFields{
        .major = dev_t_binding.max_major,
        .minor = dev_t_binding.max_minor - 1,
    };

    try std.testing.expect(devTFieldsAreValid(valid));
    try std.testing.expect(dev_t_binding.validate(valid));
    try std.testing.expect(devTFieldsAreValid(same));
    try std.testing.expect(!devTFieldsAreValid(invalid_major));
    try std.testing.expect(!devTFieldsAreValid(invalid_minor));

    try std.testing.expect(devTFieldsRangeIsValid(valid, same));
    try std.testing.expect(dev_t_binding.validateRange(valid, same));
    try std.testing.expect(!devTFieldsRangeIsValid(valid, earlier));
    try std.testing.expect(!devTFieldsRangeIsValid(valid, invalid_minor));
    try std.testing.expect(!devTFieldsRangeIsValid(invalid_major, same));
}
