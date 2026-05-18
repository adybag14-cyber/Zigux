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

pub fn currentVersion() Version {
    return version.current();
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

    try testing.expect(isCurrentAbiVersion(canonical.abi_version));
    try testing.expect(isCanonicalSize(canonical.size));
    try testing.expect(isCompatibleSize(canonical.size));
    try testing.expect(headerIsCanonical(canonical));
    try testing.expect(headerIsCompatible(canonical));
    try testing.expectEqual(abi.headerIsCanonical(canonical), headerIsCanonical(canonical));
    try testing.expectEqual(abi.headerIsCompatible(canonical), headerIsCompatible(canonical));

    try testing.expect(isCompatibleSize(future.size));
    try testing.expect(!isCanonicalSize(future.size));
    try testing.expect(!headerIsCanonical(future));
    try testing.expect(headerIsCompatible(future));
    try testing.expectEqual(abi.headerIsCanonical(future), headerIsCanonical(future));
    try testing.expectEqual(abi.headerIsCompatible(future), headerIsCompatible(future));

    try testing.expect(!isCurrentAbiVersion(stale.abi_version));
    try testing.expect(!headerIsCanonical(stale));
    try testing.expect(!headerIsCompatible(stale));
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
