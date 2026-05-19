const std = @import("std");
const abi = @import("abi_bindings");
const dev_t_binding = @import("dev_t_binding");
const version_binding = @import("version_binding");
const uapi_version = @import("uapi_version");

pub const abi_major: u32 = uapi_version.abi_major;
pub const abi_minor: u32 = uapi_version.abi_minor;
pub const header_family_revision: u32 = uapi_version.header_family_revision;
pub const abi_version: u16 = abi.ABI_VERSION;
pub const uapi_dev_t_packet_present: u32 = 1;

pub const Version = version_binding.Version;
pub const BoundaryHeader = abi.BoundaryHeader;
pub const DevTFields = dev_t_binding.Fields;

pub const version_size: usize = version_binding.version_size;
pub const version_align: usize = version_binding.version_align;
pub const abi_major_offset: usize = version_binding.abi_major_offset;
pub const abi_minor_offset: usize = version_binding.abi_minor_offset;
pub const header_family_revision_offset: usize = version_binding.header_family_revision_offset;

pub const header_size: usize = @sizeOf(BoundaryHeader);
pub const header_align: usize = @alignOf(BoundaryHeader);
pub const header_size_offset: usize = @offsetOf(BoundaryHeader, "size");
pub const header_abi_version_offset: usize = @offsetOf(BoundaryHeader, "abi_version");
pub const header_flags_offset: usize = @offsetOf(BoundaryHeader, "flags");

pub const fields_size: usize = dev_t_binding.fields_size;
pub const fields_align: usize = dev_t_binding.fields_align;
pub const major_offset: usize = dev_t_binding.major_offset;
pub const minor_offset: usize = dev_t_binding.minor_offset;
pub const max_major: u32 = dev_t_binding.max_major;
pub const max_minor: u32 = dev_t_binding.max_minor;

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

pub fn boundaryHeaderHasCurrentAbiVersion(abi_version_value: u16) bool {
    return abi.headerHasCurrentAbiVersion(abi_version_value);
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

pub fn initDevTFields(major: u32, minor: u32) DevTFields {
    return dev_t_binding.init(major, minor);
}

pub fn makeDeviceNumber(major: u32, minor: u32) u32 {
    return dev_t_binding.makeDeviceNumber(major, minor);
}

pub fn majorFromDeviceNumber(device_number: u32) u32 {
    return dev_t_binding.majorFromDeviceNumber(device_number);
}

pub fn minorFromDeviceNumber(device_number: u32) u32 {
    return dev_t_binding.minorFromDeviceNumber(device_number);
}

pub fn fieldsFromDeviceNumber(device_number: u32) DevTFields {
    return dev_t_binding.fieldsFromDeviceNumber(device_number);
}

pub fn validateDevTFields(fields: DevTFields) bool {
    return dev_t_binding.validate(fields);
}

pub fn validateDevTRange(start: DevTFields, end: DevTFields) bool {
    return dev_t_binding.validateRange(start, end);
}

test "header family binding mirrors current version compatibility surface" {
    const live = currentVersion();
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

    try std.testing.expectEqual(@as(u32, 1), uapi_dev_t_packet_present);
    try std.testing.expectEqual(version_binding.current(), live);
    try std.testing.expectEqual(@as(usize, 12), version_size);
    try std.testing.expectEqual(@as(usize, 4), version_align);
    try std.testing.expectEqual(@as(usize, 0), abi_major_offset);
    try std.testing.expectEqual(@as(usize, 4), abi_minor_offset);
    try std.testing.expectEqual(@as(usize, 8), header_family_revision_offset);
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

    try std.testing.expectEqual(@as(usize, 8), header_size);
    try std.testing.expectEqual(@as(usize, 4), header_align);
    try std.testing.expectEqual(@as(usize, 0), header_size_offset);
    try std.testing.expectEqual(@as(usize, 4), header_abi_version_offset);
    try std.testing.expectEqual(@as(usize, 6), header_flags_offset);
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

test "header family binding mirrors Linux-facing dev_t helpers" {
    const fields = initDevTFields(11, 29);
    const encoded = makeDeviceNumber(fields.major, fields.minor);
    const roundtrip = fieldsFromDeviceNumber(encoded);
    const same = initDevTFields(11, 29);
    const invalid_major = initDevTFields(max_major + 1, 0);
    const invalid_minor = initDevTFields(0, max_minor + 1);
    const earlier = initDevTFields(11, 28);

    try std.testing.expectEqual(@as(usize, 8), fields_size);
    try std.testing.expectEqual(@as(usize, 4), fields_align);
    try std.testing.expectEqual(@as(usize, 0), major_offset);
    try std.testing.expectEqual(@as(usize, 4), minor_offset);
    try std.testing.expectEqual(dev_t_binding.init(11, 29), fields);
    try std.testing.expectEqual(@as(u32, 11), majorFromDeviceNumber(encoded));
    try std.testing.expectEqual(@as(u32, 29), minorFromDeviceNumber(encoded));
    try std.testing.expect(dev_t_binding.eql(fields, roundtrip));
    try std.testing.expect(validateDevTFields(fields));
    try std.testing.expect(validateDevTFields(same));
    try std.testing.expect(!validateDevTFields(invalid_major));
    try std.testing.expect(!validateDevTFields(invalid_minor));
    try std.testing.expect(validateDevTRange(earlier, fields));
    try std.testing.expect(!validateDevTRange(fields, earlier));
    try std.testing.expect(!validateDevTRange(fields, invalid_minor));
}
