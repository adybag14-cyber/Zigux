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

test "starter version binding keeps compatibility predicates and status explicit" {
    const live = version.current();
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
    const valid = version.validate(live);
    const invalid_major = version.validate(stale_major);
    const invalid_minor = version.validate(stale_minor);
    const invalid_revision = version.validate(stale_revision);

    try testing.expect(version.hasCurrentAbiMajor(live.abi_major));
    try testing.expect(version.hasCurrentAbiMinor(live.abi_minor));
    try testing.expect(version.hasCurrentHeaderFamilyRevision(live.header_family_revision));
    try testing.expect(version.matchesCurrent(live));

    try testing.expect(!version.hasCurrentAbiMajor(stale_major.abi_major));
    try testing.expect(!version.hasCurrentAbiMinor(stale_minor.abi_minor));
    try testing.expect(!version.hasCurrentHeaderFamilyRevision(stale_revision.header_family_revision));
    try testing.expect(!version.matchesCurrent(stale_major));
    try testing.expect(!version.matchesCurrent(stale_minor));
    try testing.expect(!version.matchesCurrent(stale_revision));

    try testing.expectEqual(@as(i32, 0), valid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), valid.facility);
    try testing.expectEqual(@as(u16, 0), valid.flags);

    try testing.expectEqual(@as(i32, -22), invalid_major.code);
    try testing.expectEqual(@as(i32, -22), invalid_minor.code);
    try testing.expectEqual(@as(i32, -22), invalid_revision.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid_major.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid_minor.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid_revision.facility);
    try testing.expectEqual(@as(u16, 1), invalid_major.flags);
    try testing.expectEqual(@as(u16, 1), invalid_minor.flags);
    try testing.expectEqual(@as(u16, 1), invalid_revision.flags);
}

test "dev_t binding equality stays field based" {
    const left = dev_t.init(7, 3);
    const same = dev_t.init(7, 3);
    const different = dev_t.init(7, 4);

    try testing.expect(dev_t.eql(left, same));
    try testing.expect(!dev_t.eql(left, different));
}

test "starter dev_t validation keeps the boundary range explicit" {
    const valid = dev_t.init(dev_t.max_major, dev_t.max_minor);
    const invalid_major = dev_t.init(dev_t.max_major + 1, 0);
    const invalid_minor = dev_t.init(0, dev_t.max_minor + 1);

    try testing.expect(dev_t.validate(valid));
    try testing.expect(!dev_t.validate(invalid_major));
    try testing.expect(!dev_t.validate(invalid_minor));
    try testing.expect(dev_t.validateRange(dev_t.init(1, 2), dev_t.init(1, 3)));
    try testing.expect(!dev_t.validateRange(dev_t.init(1, 3), dev_t.init(1, 2)));
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

test "starter export shim keeps boundary-header predicates explicit" {
    const canonical = export_shim.canonicalHeader(0x41);
    const extended = export_shim.compatibleHeader(export_shim.header_size + 8, 0x41);
    const undersized = export_shim.BoundaryHeader{
        .size = export_shim.header_size - 1,
        .abi_version = export_shim.abi_version,
        .flags = 0x41,
    };
    const stale = export_shim.BoundaryHeader{
        .size = export_shim.header_size,
        .abi_version = export_shim.abi_version + 1,
        .flags = 0x41,
    };
    const canonicalized = export_shim.canonicalizeHeader(extended);

    try testing.expect(export_shim.isCurrentAbiVersion(canonical.abi_version));
    try testing.expect(export_shim.isCanonicalSize(canonical.size));
    try testing.expect(export_shim.isCompatibleSize(canonical.size));
    try testing.expect(export_shim.headerIsCanonical(canonical));
    try testing.expect(export_shim.headerIsCompatible(canonical));
    try testing.expect(!export_shim.extendsBoundary(canonical));
    try testing.expectEqual(@as(u32, 0), export_shim.requestedExtraBytes(canonical));

    try testing.expect(!export_shim.isCanonicalSize(extended.size));
    try testing.expect(export_shim.isCompatibleSize(extended.size));
    try testing.expect(!export_shim.headerIsCanonical(extended));
    try testing.expect(export_shim.headerIsCompatible(extended));
    try testing.expect(export_shim.extendsBoundary(extended));
    try testing.expectEqual(@as(u32, 8), export_shim.requestedExtraBytes(extended));

    try testing.expect(!export_shim.isCanonicalSize(undersized.size));
    try testing.expect(!export_shim.isCompatibleSize(undersized.size));
    try testing.expect(!export_shim.headerIsCanonical(undersized));
    try testing.expect(!export_shim.headerIsCompatible(undersized));
    try testing.expect(!export_shim.extendsBoundary(undersized));
    try testing.expectEqual(@as(u32, 0), export_shim.requestedExtraBytes(undersized));

    try testing.expect(!export_shim.isCurrentAbiVersion(stale.abi_version));
    try testing.expect(!export_shim.headerIsCanonical(stale));
    try testing.expect(!export_shim.headerIsCompatible(stale));
    try testing.expect(!export_shim.extendsBoundary(stale));
    try testing.expectEqual(@as(u32, 0), export_shim.requestedExtraBytes(stale));

    try testing.expectEqual(export_shim.header_size, canonicalized.size);
    try testing.expectEqual(export_shim.abi_version, canonicalized.abi_version);
    try testing.expectEqual(extended.flags, canonicalized.flags);
    try testing.expect(export_shim.headerIsCanonical(canonicalized));
    try testing.expect(!export_shim.extendsBoundary(canonicalized));
}

test "starter export shim relays version compatibility status" {
    const live = export_shim.currentVersion();
    const stale_major = export_shim.Version{
        .abi_major = version.abi_major + 1,
        .abi_minor = version.abi_minor,
        .header_family_revision = version.header_family_revision,
    };
    const stale_minor = export_shim.Version{
        .abi_major = version.abi_major,
        .abi_minor = version.abi_minor + 1,
        .header_family_revision = version.header_family_revision,
    };
    const stale_revision = export_shim.Version{
        .abi_major = version.abi_major,
        .abi_minor = version.abi_minor,
        .header_family_revision = version.header_family_revision + 1,
    };
    const valid = export_shim.validateVersion(live);
    const invalid_major = export_shim.validateVersion(stale_major);
    const invalid_minor = export_shim.validateVersion(stale_minor);
    const invalid_revision = export_shim.validateVersion(stale_revision);

    try testing.expect(export_shim.hasCurrentAbiMajor(live.abi_major));
    try testing.expect(export_shim.hasCurrentAbiMinor(live.abi_minor));
    try testing.expect(export_shim.hasCurrentHeaderFamilyRevision(live.header_family_revision));
    try testing.expect(export_shim.versionMatchesCurrent(live));
    try testing.expect(export_shim.statusIsOk(valid));

    try testing.expect(!export_shim.hasCurrentAbiMajor(stale_major.abi_major));
    try testing.expect(!export_shim.hasCurrentAbiMinor(stale_minor.abi_minor));
    try testing.expect(!export_shim.hasCurrentHeaderFamilyRevision(stale_revision.header_family_revision));
    try testing.expect(!export_shim.versionMatchesCurrent(stale_major));
    try testing.expect(!export_shim.versionMatchesCurrent(stale_minor));
    try testing.expect(!export_shim.versionMatchesCurrent(stale_revision));
    try testing.expect(!export_shim.statusIsOk(invalid_major));
    try testing.expect(!export_shim.statusIsOk(invalid_minor));
    try testing.expect(!export_shim.statusIsOk(invalid_revision));

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

test "starter export shim relays dev_t validation status" {
    const fields = export_shim.makeDevTFields(11, 29);
    const encoded = export_shim.encodeDeviceNumber(fields) orelse return error.TestUnexpectedResult;
    const decoded = export_shim.decodeDeviceNumber(encoded);
    const valid_fields_status = export_shim.validateDeviceFields(fields);
    const invalid_fields_status = export_shim.validateDeviceFields(
        export_shim.makeDevTFields(dev_t.max_major + 1, 0),
    );
    const valid = export_shim.validateDeviceNumber(dev_t.max_major, dev_t.max_minor);
    const invalid = export_shim.validateDeviceNumber(dev_t.max_major + 1, 0);
    const valid_range = export_shim.validateDeviceRange(
        export_shim.makeDevTFields(1, 2),
        export_shim.makeDevTFields(1, 3),
    );
    const invalid_range = export_shim.validateDeviceRange(
        export_shim.makeDevTFields(1, 3),
        export_shim.makeDevTFields(1, 2),
    );

    try testing.expectEqual(dev_t.makeDeviceNumber(fields.major, fields.minor), encoded);
    try testing.expectEqual(fields.major, decoded.major);
    try testing.expectEqual(fields.minor, decoded.minor);
    try testing.expect(export_shim.encodeDeviceNumber(
        export_shim.makeDevTFields(dev_t.max_major + 1, 0),
    ) == null);

    try testing.expect(export_shim.statusIsOk(valid_fields_status));
    try testing.expectEqual(@as(i32, 0), valid_fields_status.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), valid_fields_status.facility);
    try testing.expectEqual(@as(u16, 0), valid_fields_status.flags);

    try testing.expect(!export_shim.statusIsOk(invalid_fields_status));
    try testing.expectEqual(@as(i32, -22), invalid_fields_status.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid_fields_status.facility);
    try testing.expectEqual(@as(u16, 1), invalid_fields_status.flags);

    try testing.expectEqual(@as(i32, 0), valid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), valid.facility);
    try testing.expectEqual(@as(u16, 0), valid.flags);

    try testing.expectEqual(@as(i32, -22), invalid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid.facility);
    try testing.expectEqual(@as(u16, 1), invalid.flags);

    try testing.expectEqual(@as(i32, 0), valid_range.code);
    try testing.expectEqual(@as(i32, -22), invalid_range.code);
}
