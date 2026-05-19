const std = @import("std");
const abi = @import("../bindings/abi.zig");
const uapi_dev_t = @import("dev_t.zig");
const uapi_version = @import("version.zig");

pub const dev_t_packet_present: bool = true;
pub const invalid_argument: i32 = -22;

pub const Version = uapi_version.Version;
pub const BoundaryHeader = abi.BoundaryHeader;
pub const ExportStatus = abi.ExportStatus;
pub const DevTFields = uapi_dev_t.Fields;

pub const abi_major: u32 = uapi_version.abi_major;
pub const abi_minor: u32 = uapi_version.abi_minor;
pub const header_family_revision: u32 = uapi_version.header_family_revision;
pub const version_size: usize = @sizeOf(Version);
pub const version_align: usize = @alignOf(Version);
pub const dev_t_fields_size: usize = @sizeOf(DevTFields);
pub const dev_t_fields_align: usize = @alignOf(DevTFields);

pub fn currentVersion() Version {
    return uapi_version.current();
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
    return uapi_version.matchesCurrent(version);
}

pub fn validateVersion(version: Version) ExportStatus {
    if (versionMatchesCurrent(version)) return abi.okStatus(.kernel);
    return abi.makeStatus(invalid_argument, .kernel);
}

pub fn boundaryHeaderCurrent(flags: u16) BoundaryHeader {
    return abi.defaultHeader(flags);
}

pub fn boundaryHeaderCompatible(size: u32, flags: u16) BoundaryHeader {
    return abi.compatibleHeader(size, flags);
}

pub fn boundaryHeaderHasCurrentAbiVersion(abi_version: u16) bool {
    return abi.headerHasCurrentAbiVersion(abi_version);
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

pub fn boundaryHeaderCanonicalize(header: BoundaryHeader) BoundaryHeader {
    return abi.canonicalizeHeader(header);
}

pub fn devTFieldsIsValid(fields: DevTFields) bool {
    return uapi_dev_t.validate(fields);
}

pub fn validateDevTFields(fields: DevTFields) ExportStatus {
    if (devTFieldsIsValid(fields)) return abi.okStatus(.kernel);
    return abi.makeStatus(invalid_argument, .kernel);
}

pub fn validateDevTComponents(major: u32, minor: u32) ExportStatus {
    return validateDevTFields(uapi_dev_t.init(major, minor));
}

pub fn devTFieldsRangeIsValid(start: DevTFields, end: DevTFields) bool {
    return uapi_dev_t.validateRange(start, end);
}

pub fn validateDevTRange(start: DevTFields, end: DevTFields) ExportStatus {
    if (devTFieldsRangeIsValid(start, end)) return abi.okStatus(.kernel);
    return abi.makeStatus(invalid_argument, .kernel);
}

test "header family mirrors the live version and boundary helpers" {
    const current = currentVersion();
    const compatible = boundaryHeaderCompatible(@sizeOf(BoundaryHeader) + 16, 0x41);
    const canonical = boundaryHeaderCurrent(0x41);
    const stale = Version{
        .abi_major = abi_major,
        .abi_minor = abi_minor + 1,
        .header_family_revision = header_family_revision,
    };

    try std.testing.expect(dev_t_packet_present);
    try std.testing.expect(versionMatchesCurrent(current));
    try std.testing.expect(!versionMatchesCurrent(stale));
    try std.testing.expectEqual(@as(i32, 0), validateVersion(current).code);
    try std.testing.expectEqual(invalid_argument, validateVersion(stale).code);

    try std.testing.expect(boundaryHeaderIsCanonical(canonical));
    try std.testing.expect(boundaryHeaderIsCompatible(canonical));
    try std.testing.expect(!boundaryHeaderExtendsBoundary(canonical));
    try std.testing.expect(boundaryHeaderIsCompatible(compatible));
    try std.testing.expect(boundaryHeaderExtendsBoundary(compatible));
    try std.testing.expectEqual(@as(u32, 16), boundaryHeaderRequestedExtraBytes(compatible));

    const canonicalized = boundaryHeaderCanonicalize(compatible);
    try std.testing.expect(boundaryHeaderIsCanonical(canonicalized));
    try std.testing.expectEqual(@as(u32, @sizeOf(BoundaryHeader)), canonicalized.size);
}

test "header family keeps dev_t validation explicit" {
    const valid = uapi_dev_t.init(uapi_dev_t.max_major, uapi_dev_t.max_minor);
    const invalid = uapi_dev_t.init(uapi_dev_t.max_major + 1, 0);
    const earlier = uapi_dev_t.init(4, 7);
    const later = uapi_dev_t.init(4, 9);

    try std.testing.expect(devTFieldsIsValid(valid));
    try std.testing.expect(!devTFieldsIsValid(invalid));
    try std.testing.expectEqual(@as(i32, 0), validateDevTFields(valid).code);
    try std.testing.expectEqual(invalid_argument, validateDevTFields(invalid).code);
    try std.testing.expectEqual(@as(i32, 0), validateDevTComponents(4, 9).code);
    try std.testing.expect(devTFieldsRangeIsValid(earlier, later));
    try std.testing.expect(!devTFieldsRangeIsValid(later, earlier));
    try std.testing.expectEqual(@as(i32, 0), validateDevTRange(earlier, later).code);
    try std.testing.expectEqual(invalid_argument, validateDevTRange(later, earlier).code);
}
