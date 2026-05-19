const std = @import("std");
const testing = std.testing;

const uapi_dev_t = @import("uapi_dev_t");
const uapi_version = @import("uapi_version");
const dev_t = @import("dev_t_binding");
const version = @import("version_binding");
const export_shim = @import("export_shim");

test "export and uapi dev_t layouts stay aligned" {
    const fields = dev_t.init(11, 29);
    const uapi_fields = uapi_dev_t.init(11, 29);

    try testing.expectEqual(@as(u32, 1), dev_t.abi_version);
    try testing.expectEqual(uapi_dev_t.fields_size, dev_t.fields_size);
    try testing.expectEqual(uapi_dev_t.fields_align, dev_t.fields_align);
    try testing.expectEqual(uapi_dev_t.major_offset, dev_t.major_offset);
    try testing.expectEqual(uapi_dev_t.minor_offset, dev_t.minor_offset);
    try testing.expectEqual(@as(u32, fields.major), uapi_fields.major);
    try testing.expectEqual(@as(u32, fields.minor), uapi_fields.minor);
    try testing.expectEqual(@as(usize, 8), @sizeOf(export_shim.DevTFields));
    try testing.expectEqual(@as(usize, 4), @alignOf(export_shim.DevTFields));
}

test "export and uapi version layouts stay aligned" {
    const current = version.current();
    const uapi_current = uapi_version.current();

    try testing.expectEqual(@as(u32, 0), version.abi_major);
    try testing.expectEqual(@as(u32, 1), version.abi_minor);
    try testing.expectEqual(@as(u32, 1), version.header_family_revision);
    try testing.expectEqual(uapi_version.version_size, version.version_size);
    try testing.expectEqual(uapi_version.version_align, version.version_align);
    try testing.expectEqual(uapi_version.abi_major_offset, version.abi_major_offset);
    try testing.expectEqual(uapi_version.abi_minor_offset, version.abi_minor_offset);
    try testing.expectEqual(uapi_version.header_family_revision_offset, version.header_family_revision_offset);
    try testing.expect(version.eql(current, uapi_current));
    try testing.expect(version.eql(current, export_shim.currentVersion()));
}

test "export shim encodes starter dev_t numbers without widening the boundary" {
    const fields = export_shim.makeDevTFields(11, 29);
    const encoded = export_shim.encodeDeviceNumber(fields) orelse unreachable;
    const decoded = export_shim.decodeDeviceNumber(encoded);

    try testing.expectEqual(uapi_dev_t.makeDeviceNumber(fields.major, fields.minor), encoded);
    try testing.expectEqual(dev_t.makeDeviceNumber(fields.major, fields.minor), encoded);
    try testing.expectEqual(fields.major, decoded.major);
    try testing.expectEqual(fields.minor, decoded.minor);
    try testing.expect(export_shim.encodeDeviceNumber(
        export_shim.makeDevTFields(dev_t.max_major + 1, 0),
    ) == null);
}

test "export shim reuses the canonical boundary header contract" {
    const header = export_shim.canonicalHeader(0x41);

    try testing.expectEqual(@as(u16, 1), export_shim.abi_version);
    try testing.expectEqual(@as(u32, @sizeOf(export_shim.BoundaryHeader)), export_shim.header_size);
    try testing.expectEqual(export_shim.header_size, header.size);
    try testing.expectEqual(@as(u16, 1), header.abi_version);
    try testing.expectEqual(@as(u16, 0x41), header.flags);
    try testing.expectEqual(@as(usize, 8), @sizeOf(export_shim.BoundaryHeader));
    try testing.expectEqual(@as(usize, 4), @alignOf(export_shim.BoundaryHeader));
    try testing.expectEqual(@as(usize, 0), @offsetOf(export_shim.BoundaryHeader, "size"));
    try testing.expectEqual(@as(usize, 4), @offsetOf(export_shim.BoundaryHeader, "abi_version"));
    try testing.expectEqual(@as(usize, 6), @offsetOf(export_shim.BoundaryHeader, "flags"));
}

test "export shim mirrors boundary header predicate helpers" {
    const canonical = export_shim.canonicalHeader(0x22);
    const future = export_shim.BoundaryHeader{
        .size = export_shim.header_size + 16,
        .abi_version = export_shim.abi_version,
        .flags = 0x22,
    };
    const stale = export_shim.BoundaryHeader{
        .size = export_shim.header_size,
        .abi_version = export_shim.abi_version + 1,
        .flags = 0,
    };
    const canonicalized = export_shim.canonicalizeHeader(future);

    try testing.expect(export_shim.isCurrentAbiVersion(canonical.abi_version));
    try testing.expect(export_shim.isCanonicalSize(canonical.size));
    try testing.expect(export_shim.isCompatibleSize(canonical.size));
    try testing.expect(export_shim.headerIsCanonical(canonical));
    try testing.expect(export_shim.headerIsCompatible(canonical));
    try testing.expect(!export_shim.extendsBoundary(canonical));
    try testing.expectEqual(@as(u32, 0), export_shim.requestedExtraBytes(canonical));

    try testing.expect(!export_shim.isCanonicalSize(future.size));
    try testing.expect(export_shim.isCompatibleSize(future.size));
    try testing.expect(!export_shim.headerIsCanonical(future));
    try testing.expect(export_shim.headerIsCompatible(future));
    try testing.expect(export_shim.extendsBoundary(future));
    try testing.expectEqual(@as(u32, 16), export_shim.requestedExtraBytes(future));

    try testing.expect(!export_shim.isCurrentAbiVersion(stale.abi_version));
    try testing.expect(!export_shim.headerIsCanonical(stale));
    try testing.expect(!export_shim.headerIsCompatible(stale));
    try testing.expect(!export_shim.extendsBoundary(stale));
    try testing.expectEqual(@as(u32, 0), export_shim.requestedExtraBytes(stale));

    try testing.expectEqual(export_shim.header_size, canonicalized.size);
    try testing.expectEqual(export_shim.abi_version, canonicalized.abi_version);
    try testing.expectEqual(future.flags, canonicalized.flags);
    try testing.expect(export_shim.headerIsCanonical(canonicalized));
    try testing.expect(!export_shim.extendsBoundary(canonicalized));
}

test "export shim keeps facility tagged statuses explicit" {
    const ok = export_shim.okStatus(.helpers);
    const err = export_shim.errorStatus(-22, .kernel);
    const positive = export_shim.errorStatus(7, .drivers);

    try testing.expectEqual(@as(i32, 0), ok.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.helpers)), ok.facility);
    try testing.expectEqual(@as(u16, 0), ok.flags);

    try testing.expectEqual(@as(i32, -22), err.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), err.facility);
    try testing.expectEqual(@as(u16, 1), err.flags);

    try testing.expectEqual(@as(i32, 7), positive.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.drivers)), positive.facility);
    try testing.expectEqual(@as(u16, 0), positive.flags);
}
