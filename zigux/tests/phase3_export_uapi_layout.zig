const std = @import("std");
const testing = std.testing;

const uapi_dev_t = @import("uapi_dev_t");
const uapi_version = @import("uapi_version");
const dev_t = @import("dev_t_binding");
const version = @import("version_binding");
const header_family = @import("header_family_binding");
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

test "header-family binding keeps the bounded relay surface explicit" {
    const current = header_family.currentVersion();
    const canonical = header_family.currentBoundaryHeader(0x31);
    const expanded = header_family.compatibleBoundaryHeader(
        @sizeOf(header_family.BoundaryHeader) + 8,
        0x31,
    );
    const fields = header_family.initDevTFields(11, 29);
    const encoded = header_family.makeDeviceNumber(fields.major, fields.minor);
    const uapi_current = uapi_version.current();

    try testing.expectEqual(version.current(), current);
    try testing.expectEqual(uapi_current.abi_major, current.abi_major);
    try testing.expectEqual(uapi_current.abi_minor, current.abi_minor);
    try testing.expectEqual(uapi_current.header_family_revision, current.header_family_revision);
    try testing.expectEqual(@as(usize, 12), header_family.version_size);
    try testing.expectEqual(@as(usize, 8), header_family.header_size);
    try testing.expectEqual(@as(usize, 8), header_family.fields_size);
    try testing.expect(header_family.boundaryHeaderIsCanonical(canonical));
    try testing.expect(header_family.boundaryHeaderIsCompatible(expanded));
    try testing.expect(header_family.boundaryHeaderExtendsBoundary(expanded));
    try testing.expectEqual(@as(u32, 8), header_family.boundaryHeaderRequestedExtraBytes(expanded));
    try testing.expectEqual(uapi_dev_t.makeDeviceNumber(11, 29), encoded);
    try testing.expectEqual(dev_t.makeDeviceNumber(11, 29), encoded);
    try testing.expectEqual(@as(u32, 11), header_family.majorFromDeviceNumber(encoded));
    try testing.expectEqual(@as(u32, 29), header_family.minorFromDeviceNumber(encoded));
    try testing.expect(header_family.validateDevTFields(fields));
    try testing.expect(header_family.validateDevTRange(
        header_family.initDevTFields(11, 28),
        fields,
    ));
}

test "export shim relays version compatibility without widening the boundary" {
    const current = version.current();
    const stale_major = version.Version{
        .abi_major = version.abi_major + 1,
        .abi_minor = version.abi_minor,
        .header_family_revision = version.header_family_revision,
    };
    const stale_minor = version.Version{
        .abi_major = version.abi_major,
        .abi_minor = version.abi_minor + 1,
        .header_family_revision = version.header_family_revision,
    };
    const stale_revision = version.Version{
        .abi_major = version.abi_major,
        .abi_minor = version.abi_minor,
        .header_family_revision = version.header_family_revision + 1,
    };
    const valid = export_shim.validateVersion(current);
    const invalid_major = export_shim.validateVersion(stale_major);
    const invalid_minor = export_shim.validateVersion(stale_minor);
    const invalid_revision = export_shim.validateVersion(stale_revision);

    try testing.expect(version.matchesCurrent(current));
    try testing.expect(export_shim.versionMatchesCurrent(current));
    try testing.expectEqual(version.matchesCurrent(current), export_shim.versionMatchesCurrent(current));

    try testing.expect(!version.matchesCurrent(stale_major));
    try testing.expect(!version.matchesCurrent(stale_minor));
    try testing.expect(!version.matchesCurrent(stale_revision));
    try testing.expectEqual(version.matchesCurrent(stale_major), export_shim.versionMatchesCurrent(stale_major));
    try testing.expectEqual(version.matchesCurrent(stale_minor), export_shim.versionMatchesCurrent(stale_minor));
    try testing.expectEqual(version.matchesCurrent(stale_revision), export_shim.versionMatchesCurrent(stale_revision));

    try testing.expectEqual(@as(i32, 0), valid.code);
    try testing.expectEqual(@as(i32, -22), invalid_major.code);
    try testing.expectEqual(@as(i32, -22), invalid_minor.code);
    try testing.expectEqual(@as(i32, -22), invalid_revision.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), valid.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid_major.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid_minor.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid_revision.facility);
    try testing.expectEqual(@as(u16, 0), valid.flags);
    try testing.expectEqual(@as(u16, 1), invalid_major.flags);
    try testing.expectEqual(@as(u16, 1), invalid_minor.flags);
    try testing.expectEqual(@as(u16, 1), invalid_revision.flags);
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

test "export shim relays starter dev_t validation and range checks through the focused replay" {
    const valid = export_shim.validateDeviceNumber(uapi_dev_t.max_major, uapi_dev_t.max_minor);
    const invalid = export_shim.validateDeviceNumber(uapi_dev_t.max_major + 1, 0);
    const good_range = export_shim.validateDeviceRange(
        export_shim.makeDevTFields(1, 2),
        export_shim.makeDevTFields(1, 3),
    );
    const bad_range = export_shim.validateDeviceRange(
        export_shim.makeDevTFields(1, 3),
        export_shim.makeDevTFields(1, 2),
    );

    try testing.expect(export_shim.statusIsOk(valid));
    try testing.expectEqual(@as(i32, 0), valid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), valid.facility);
    try testing.expectEqual(@as(u16, 0), valid.flags);

    try testing.expect(!export_shim.statusIsOk(invalid));
    try testing.expectEqual(@as(i32, -22), invalid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid.facility);
    try testing.expectEqual(@as(u16, 1), invalid.flags);

    try testing.expect(export_shim.statusIsOk(good_range));
    try testing.expectEqual(@as(i32, 0), good_range.code);
    try testing.expect(!export_shim.statusIsOk(bad_range));
    try testing.expectEqual(@as(i32, -22), bad_range.code);
}
