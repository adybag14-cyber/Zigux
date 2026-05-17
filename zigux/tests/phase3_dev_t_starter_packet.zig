const std = @import("std");
const testing = std.testing;

const uapi_dev_t = @import("uapi_dev_t");
const dev_t = @import("dev_t_binding");
const version = @import("version_binding");
const export_shim = @import("export_shim");

test "dev_t starter binding preserves the current ABI layout" {
    const fields = dev_t.init(11, 29);

    try testing.expectEqual(@as(u32, 1), dev_t.abi_version);
    try testing.expectEqual(@as(usize, 8), dev_t.fields_size);
    try testing.expectEqual(@as(usize, 4), dev_t.fields_align);
    try testing.expectEqual(@as(usize, 0), dev_t.major_offset);
    try testing.expectEqual(@as(usize, 4), dev_t.minor_offset);
    try testing.expectEqual(@as(u32, 11), fields.major);
    try testing.expectEqual(@as(u32, 29), fields.minor);
}

test "dev_t starter binding stays aligned with the UAPI field offsets" {
    try testing.expectEqual(uapi_dev_t.fields_size, dev_t.fields_size);
    try testing.expectEqual(uapi_dev_t.fields_align, dev_t.fields_align);
    try testing.expectEqual(uapi_dev_t.major_offset, dev_t.major_offset);
    try testing.expectEqual(uapi_dev_t.minor_offset, dev_t.minor_offset);
}

test "starter packet version binding preserves the Linux-facing header family layout" {
    const current = version.current();

    try testing.expectEqual(@as(u32, 0), version.abi_major);
    try testing.expectEqual(@as(u32, 1), version.abi_minor);
    try testing.expectEqual(@as(u32, 1), version.header_family_revision);
    try testing.expectEqual(@as(usize, 12), version.version_size);
    try testing.expectEqual(@as(usize, 4), version.version_align);
    try testing.expectEqual(@as(usize, 0), version.abi_major_offset);
    try testing.expectEqual(@as(usize, 4), version.abi_minor_offset);
    try testing.expectEqual(@as(usize, 8), version.header_family_revision_offset);
    try testing.expectEqual(@as(u32, 0), current.abi_major);
    try testing.expectEqual(@as(u32, 1), current.abi_minor);
    try testing.expectEqual(@as(u32, 1), current.header_family_revision);
}

test "dev_t binding equality stays field based" {
    const left = dev_t.init(7, 3);
    const same = dev_t.init(7, 3);
    const different = dev_t.init(7, 4);

    try testing.expect(dev_t.eql(left, same));
    try testing.expect(!dev_t.eql(left, different));
}

test "version binding equality stays field based" {
    const current = version.current();
    const same = version.Version{
        .abi_major = 0,
        .abi_minor = 1,
        .header_family_revision = 1,
    };
    const different = version.Version{
        .abi_major = 0,
        .abi_minor = 1,
        .header_family_revision = 2,
    };

    try testing.expect(version.eql(current, same));
    try testing.expect(!version.eql(current, different));
}

test "starter export shim reuses the canonical boundary header and version snapshot" {
    const header = export_shim.canonicalHeader(0x41);
    const current = export_shim.currentVersion();

    try testing.expectEqual(@as(u32, @sizeOf(export_shim.BoundaryHeader)), header.size);
    try testing.expectEqual(@as(u16, 1), header.abi_version);
    try testing.expectEqual(@as(u16, 0x41), header.flags);
    try testing.expectEqual(@as(u32, 0), current.abi_major);
    try testing.expectEqual(@as(u32, 1), current.abi_minor);
    try testing.expectEqual(@as(u32, 1), current.header_family_revision);
    try testing.expect(version.eql(current, version.current()));
}

test "starter export shim keeps facility-tagged status helpers explicit" {
    const ok = export_shim.okStatus(.helpers);
    const err = export_shim.errorStatus(-12, .kernel);
    const non_error = export_shim.errorStatus(7, .drivers);

    try testing.expectEqual(@as(i32, 0), ok.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.helpers)), ok.facility);
    try testing.expectEqual(@as(u16, 0), ok.flags);

    try testing.expectEqual(@as(i32, -12), err.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), err.facility);
    try testing.expectEqual(@as(u16, 1), err.flags);

    try testing.expectEqual(@as(i32, 7), non_error.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.drivers)), non_error.facility);
    try testing.expectEqual(@as(u16, 0), non_error.flags);
}

test "starter export shim forwards dev_t fields without changing starter layout semantics" {
    const fields = export_shim.makeDevTFields(11, 29);
    const same = export_shim.makeDevTFields(11, 29);
    const different = export_shim.makeDevTFields(11, 30);

    try testing.expectEqual(@as(usize, 8), @sizeOf(export_shim.DevTFields));
    try testing.expectEqual(@as(usize, 4), @alignOf(export_shim.DevTFields));
    try testing.expectEqual(@as(u32, 11), fields.major);
    try testing.expectEqual(@as(u32, 29), fields.minor);
    try testing.expect(dev_t.eql(fields, same));
    try testing.expect(!dev_t.eql(fields, different));
}
