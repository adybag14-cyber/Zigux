const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const dev_t = @import("dev_t_binding");
const version = @import("version_binding");

const invalid_argument: i32 = -22;

pub const BoundaryHeader = abi.BoundaryHeader;
pub const ExportStatus = abi.ExportStatus;
pub const Facility = abi.Facility;
pub const Version = version.Version;
pub const DevTFields = dev_t.Fields;
pub const abi_version: u16 = abi.ABI_VERSION;
pub const header_size: u32 = @sizeOf(BoundaryHeader);

pub fn canonicalHeader(flags: u16) BoundaryHeader {
    return abi.defaultHeader(flags);
}

pub fn isCurrentAbiVersion(value: u16) bool {
    return abi.headerHasCurrentAbiVersion(value);
}

pub fn isCanonicalSize(value: u32) bool {
    return value == header_size;
}

pub fn isCompatibleSize(value: u32) bool {
    return value >= header_size;
}

pub fn headerIsCanonical(header: BoundaryHeader) bool {
    return isCanonicalSize(header.size) and isCurrentAbiVersion(header.abi_version);
}

pub fn headerIsCompatible(header: BoundaryHeader) bool {
    return isCompatibleSize(header.size) and isCurrentAbiVersion(header.abi_version);
}

pub fn extendsBoundary(header: BoundaryHeader) bool {
    return headerIsCompatible(header) and !headerIsCanonical(header);
}

pub fn requestedExtraBytes(header: BoundaryHeader) u32 {
    if (!extendsBoundary(header)) return 0;
    return header.size - header_size;
}

pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {
    return abi.canonicalizeHeader(header);
}

pub fn currentVersion() Version {
    return version.current();
}

pub fn versionMatchesCurrent(candidate: Version) bool {
    return version.matchesCurrent(candidate);
}

pub fn validateVersion(candidate: Version) ExportStatus {
    if (versionMatchesCurrent(candidate)) return okStatus(.kernel);
    return errorStatus(invalid_argument, .kernel);
}

pub fn makeDevTFields(major: u32, minor: u32) DevTFields {
    return dev_t.init(major, minor);
}

pub fn encodeDeviceNumber(fields: DevTFields) ?u32 {
    if (!dev_t.validate(fields)) return null;
    return dev_t.makeDeviceNumber(fields.major, fields.minor);
}

pub fn decodeDeviceNumber(device_number: u32) DevTFields {
    return dev_t.fieldsFromDeviceNumber(device_number);
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

pub fn statusIsOk(status: ExportStatus) bool {
    return (status.flags & abi.STATUS_FLAG_ERROR) == 0;
}

pub fn validateDeviceFields(fields: DevTFields) ExportStatus {
    if (dev_t.validate(fields)) return okStatus(.kernel);
    return errorStatus(invalid_argument, .kernel);
}

pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {
    return validateDeviceFields(makeDevTFields(major, minor));
}

pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {
    if (dev_t.validateRange(start, end)) return okStatus(.kernel);
    return errorStatus(invalid_argument, .kernel);
}

test "export shim preserves the canonical boundary header and version snapshot" {
    const header = canonicalHeader(0x41);
    const current = currentVersion();

    try testing.expectEqual(@as(u16, abi.ABI_VERSION), abi_version);
    try testing.expectEqual(@as(u32, @sizeOf(BoundaryHeader)), header_size);
    try testing.expectEqual(header_size, header.size);
    try testing.expectEqual(@as(u16, abi.ABI_VERSION), header.abi_version);
    try testing.expectEqual(@as(u16, 0x41), header.flags);
    try testing.expectEqual(@as(usize, 8), @sizeOf(BoundaryHeader));
    try testing.expectEqual(@as(usize, 4), @alignOf(BoundaryHeader));

    try testing.expectEqual(@as(u32, 0), current.abi_major);
    try testing.expectEqual(@as(u32, 1), current.abi_minor);
    try testing.expectEqual(@as(u32, 1), current.header_family_revision);
    try testing.expect(version.eql(current, version.current()));
}

test "export shim keeps boundary header predicates aligned with ABI helpers" {
    const canonical = canonicalHeader(0x15);
    const future = abi.compatibleHeader(header_size + 8, 0x15);
    const stale = BoundaryHeader{
        .size = header_size,
        .abi_version = abi_version + 1,
        .flags = 0,
    };
    const canonicalized = canonicalizeHeader(future);

    try testing.expect(isCurrentAbiVersion(canonical.abi_version));
    try testing.expect(isCanonicalSize(canonical.size));
    try testing.expect(isCompatibleSize(canonical.size));
    try testing.expect(headerIsCanonical(canonical));
    try testing.expect(headerIsCompatible(canonical));
    try testing.expectEqual(abi.headerIsCanonical(canonical), headerIsCanonical(canonical));
    try testing.expectEqual(abi.headerIsCompatible(canonical), headerIsCompatible(canonical));
    try testing.expect(!extendsBoundary(canonical));
    try testing.expectEqual(@as(u32, 0), requestedExtraBytes(canonical));

    try testing.expect(isCompatibleSize(future.size));
    try testing.expect(!isCanonicalSize(future.size));
    try testing.expect(!headerIsCanonical(future));
    try testing.expect(headerIsCompatible(future));
    try testing.expectEqual(abi.headerIsCanonical(future), headerIsCanonical(future));
    try testing.expectEqual(abi.headerIsCompatible(future), headerIsCompatible(future));
    try testing.expect(extendsBoundary(future));
    try testing.expectEqual(@as(u32, 8), requestedExtraBytes(future));

    try testing.expect(!isCurrentAbiVersion(stale.abi_version));
    try testing.expect(!headerIsCanonical(stale));
    try testing.expect(!headerIsCompatible(stale));
    try testing.expect(!extendsBoundary(stale));
    try testing.expectEqual(@as(u32, 0), requestedExtraBytes(stale));

    try testing.expectEqual(@as(u32, header_size), canonicalized.size);
    try testing.expectEqual(@as(u16, abi_version), canonicalized.abi_version);
    try testing.expectEqual(future.flags, canonicalized.flags);
    try testing.expect(headerIsCanonical(canonicalized));
    try testing.expect(!extendsBoundary(canonicalized));
}

test "export shim relays starter version compatibility through status helpers" {
    const live = currentVersion();
    const stale_major = Version{
        .abi_major = version.abi_major + 1,
        .abi_minor = version.abi_minor,
        .header_family_revision = version.header_family_revision,
    };
    const stale_minor = Version{
        .abi_major = version.abi_major,
        .abi_minor = version.abi_minor + 1,
        .header_family_revision = version.header_family_revision,
    };
    const stale_revision = Version{
        .abi_major = version.abi_major,
        .abi_minor = version.abi_minor,
        .header_family_revision = version.header_family_revision + 1,
    };
    const valid = validateVersion(live);
    const invalid_major = validateVersion(stale_major);
    const invalid_minor = validateVersion(stale_minor);
    const invalid_revision = validateVersion(stale_revision);

    try testing.expect(versionMatchesCurrent(live));
    try testing.expect(!versionMatchesCurrent(stale_major));
    try testing.expect(!versionMatchesCurrent(stale_minor));
    try testing.expect(!versionMatchesCurrent(stale_revision));

    try testing.expectEqual(@as(i32, 0), valid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), valid.facility);
    try testing.expectEqual(@as(u16, 0), valid.flags);

    try testing.expectEqual(@as(i32, invalid_argument), invalid_major.code);
    try testing.expectEqual(@as(i32, invalid_argument), invalid_minor.code);
    try testing.expectEqual(@as(i32, invalid_argument), invalid_revision.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), invalid_major.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), invalid_minor.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), invalid_revision.facility);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_major.flags);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_minor.flags);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_revision.flags);
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

test "export shim mirrors the exported status-ok flag contract" {
    const ok = okStatus(.helpers);
    const negative = errorStatus(-12, .kernel);
    const positive = errorStatus(7, .drivers);
    const flagged_positive = ExportStatus{
        .code = 7,
        .facility = @intFromEnum(Facility.drivers),
        .flags = abi.STATUS_FLAG_ERROR,
    };

    try testing.expect(statusIsOk(ok));
    try testing.expect(!statusIsOk(negative));
    try testing.expect(statusIsOk(positive));
    try testing.expect(!statusIsOk(flagged_positive));
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

test "export shim keeps validated dev_t encoding explicit" {
    const fields = makeDevTFields(11, 29);
    const encoded = encodeDeviceNumber(fields) orelse unreachable;
    const decoded = decodeDeviceNumber(encoded);
    const invalid = makeDevTFields(dev_t.max_major + 1, 0);

    try testing.expectEqual(dev_t.makeDeviceNumber(fields.major, fields.minor), encoded);
    try testing.expect(dev_t.eql(fields, decoded));
    try testing.expect(encodeDeviceNumber(invalid) == null);
}

test "export shim relays bounded dev_t validation through status helpers" {
    const valid = validateDeviceNumber(dev_t.max_major, dev_t.max_minor);
    const invalid = validateDeviceNumber(dev_t.max_major + 1, 0);
    const good_range = validateDeviceRange(
        makeDevTFields(1, 2),
        makeDevTFields(1, 3),
    );
    const bad_range = validateDeviceRange(
        makeDevTFields(1, 3),
        makeDevTFields(1, 2),
    );

    try testing.expectEqual(@as(i32, 0), valid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), valid.facility);
    try testing.expectEqual(@as(u16, 0), valid.flags);

    try testing.expectEqual(@as(i32, invalid_argument), invalid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), invalid.facility);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid.flags);

    try testing.expectEqual(@as(i32, 0), good_range.code);
    try testing.expectEqual(@as(i32, invalid_argument), bad_range.code);
}
