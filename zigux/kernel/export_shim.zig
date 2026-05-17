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

test "export shim preserves the canonical boundary header and version snapshot" {
    const header = canonicalHeader(0x41);
    const current = currentVersion();

    try testing.expectEqual(@as(u32, @sizeOf(BoundaryHeader)), header.size);
    try testing.expectEqual(@as(u16, abi.ABI_VERSION), header.abi_version);
    try testing.expectEqual(@as(u16, 0x41), header.flags);
    try testing.expectEqual(@as(usize, 8), @sizeOf(BoundaryHeader));
    try testing.expectEqual(@as(usize, 4), @alignOf(BoundaryHeader));

    try testing.expectEqual(@as(u32, 0), current.abi_major);
    try testing.expectEqual(@as(u32, 1), current.abi_minor);
    try testing.expectEqual(@as(u32, 1), current.header_family_revision);
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
