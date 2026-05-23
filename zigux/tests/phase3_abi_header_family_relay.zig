const std = @import("std");

const abi = @import("abi_bindings");
const export_shim = @import("export_shim");
const header_family = @import("header_family_binding");

test "phase3 abi keeps Linux-facing header-family relays aligned with the shared ABI helpers" {
    const current = header_family.currentVersion();
    const stale = header_family.Version{
        .abi_major = current.abi_major,
        .abi_minor = current.abi_minor,
        .header_family_revision = current.header_family_revision + 1,
    };
    const canonical = header_family.currentBoundaryHeader(0x33);
    const expanded = header_family.compatibleBoundaryHeader(@sizeOf(header_family.BoundaryHeader) + 12, 0x33);
    const normalized = header_family.canonicalizeBoundaryHeader(expanded);
    const fields = header_family.initDevTFields(11, 29);
    const earlier = header_family.initDevTFields(11, 28);
    const encoded = header_family.makeDeviceNumber(fields.major, fields.minor);
    const decoded = header_family.fieldsFromDeviceNumber(encoded);
    const version_ok = header_family.validateVersionStatus(current);
    const version_bad = header_family.validateVersionStatus(stale);
    const fields_ok = header_family.validateDevTFieldsStatus(fields);
    const fields_bad = header_family.validateDevTComponentsStatus(header_family.max_major + 1, 0);
    const range_ok = header_family.validateDevTRangeStatus(earlier, fields);
    const range_bad = header_family.validateDevTRangeStatus(fields, earlier);

    try std.testing.expect(std.meta.eql(current, export_shim.currentVersion()));
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), header_family.abi_version);
    try std.testing.expectEqual(@as(u32, 1), header_family.uapi_dev_t_packet_present);

    try std.testing.expect(std.meta.eql(canonical, export_shim.canonicalHeader(0x33)));
    try std.testing.expect(header_family.boundaryHeaderHasCurrentAbiVersion(canonical.abi_version));
    try std.testing.expect(header_family.boundaryHeaderIsCanonicalSize(canonical.size));
    try std.testing.expect(header_family.boundaryHeaderIsCompatibleSize(canonical.size));
    try std.testing.expect(header_family.boundaryHeaderIsCanonical(canonical));
    try std.testing.expect(header_family.boundaryHeaderIsCompatible(canonical));
    try std.testing.expect(!header_family.boundaryHeaderExtendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), header_family.boundaryHeaderRequestedExtraBytes(canonical));

    try std.testing.expect(!header_family.boundaryHeaderIsCanonical(expanded));
    try std.testing.expect(header_family.boundaryHeaderIsCompatible(expanded));
    try std.testing.expect(header_family.boundaryHeaderExtendsBoundary(expanded));
    try std.testing.expectEqual(@as(u32, 12), header_family.boundaryHeaderRequestedExtraBytes(expanded));
    try std.testing.expectEqual(@as(u32, 12), export_shim.requestedExtraBytes(expanded));

    try std.testing.expectEqual(@as(u32, @intCast(header_family.header_size)), normalized.size);
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), normalized.abi_version);
    try std.testing.expectEqual(expanded.flags, normalized.flags);

    try std.testing.expect(header_family.validateDevTFields(fields));
    try std.testing.expectEqual(@as(u32, 11), header_family.majorFromDeviceNumber(encoded));
    try std.testing.expectEqual(@as(u32, 29), header_family.minorFromDeviceNumber(encoded));
    try std.testing.expectEqual(fields.major, decoded.major);
    try std.testing.expectEqual(fields.minor, decoded.minor);

    try std.testing.expect(std.meta.eql(export_shim.okStatus(.kernel), version_ok));
    try std.testing.expect(!export_shim.statusIsOk(version_bad));
    try std.testing.expect(std.meta.eql(export_shim.okStatus(.kernel), fields_ok));
    try std.testing.expect(!export_shim.statusIsOk(fields_bad));
    try std.testing.expect(std.meta.eql(export_shim.okStatus(.kernel), range_ok));
    try std.testing.expect(!export_shim.statusIsOk(range_bad));
}

test "phase3 abi keeps stale header-family and dev_t range failures visible through the standalone relay" {
    const current = header_family.currentVersion();
    const stale_major = header_family.Version{
        .abi_major = current.abi_major + 1,
        .abi_minor = current.abi_minor,
        .header_family_revision = current.header_family_revision,
    };
    const stale_minor = header_family.Version{
        .abi_major = current.abi_major,
        .abi_minor = current.abi_minor + 1,
        .header_family_revision = current.header_family_revision,
    };
    const stale_header = header_family.BoundaryHeader{
        .size = @sizeOf(header_family.BoundaryHeader),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0x44,
    };
    const invalid_fields = header_family.initDevTFields(header_family.max_major + 1, 0);
    const later = header_family.initDevTFields(11, 29);
    const earlier = header_family.initDevTFields(11, 28);

    try std.testing.expect(!header_family.versionMatchesCurrent(stale_major));
    try std.testing.expect(!header_family.versionMatchesCurrent(stale_minor));
    try std.testing.expect(!export_shim.statusIsOk(header_family.validateVersionStatus(stale_major)));
    try std.testing.expect(!export_shim.statusIsOk(header_family.validateVersionStatus(stale_minor)));

    try std.testing.expect(!header_family.boundaryHeaderHasCurrentAbiVersion(stale_header.abi_version));
    try std.testing.expect(!header_family.boundaryHeaderIsCanonical(stale_header));
    try std.testing.expect(!header_family.boundaryHeaderIsCompatible(stale_header));
    try std.testing.expectEqual(@as(u32, 0), header_family.boundaryHeaderRequestedExtraBytes(stale_header));

    try std.testing.expect(!header_family.validateDevTFields(invalid_fields));
    try std.testing.expect(!export_shim.statusIsOk(header_family.validateDevTFieldsStatus(invalid_fields)));
    try std.testing.expect(!header_family.validateDevTRange(later, earlier));
    try std.testing.expect(!export_shim.statusIsOk(header_family.validateDevTRangeStatus(later, earlier)));
}
