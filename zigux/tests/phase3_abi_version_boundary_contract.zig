const std = @import("std");

const abi = @import("abi_bindings");
const version = @import("version_binding");

const invalid_argument: i32 = -22;

fn expectKernelStatus(status: abi.ExportStatus, code: i32) !void {
    try std.testing.expectEqual(code, status.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.kernel)), status.facility);
    try std.testing.expect(abi.statusHasKnownFacility(status));

    if (code < 0) {
        try std.testing.expect(!abi.statusIsOk(status));
        try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), status.flags);
    } else {
        try std.testing.expect(abi.statusIsOk(status));
        try std.testing.expectEqual(@as(u16, 0), status.flags);
    }
}

test "phase3 uapi version boundary layout stays abi shaped" {
    try std.testing.expectEqual(@as(usize, 12), version.version_size);
    try std.testing.expectEqual(@as(usize, 4), version.version_align);
    try std.testing.expectEqual(@as(usize, 0), version.abi_major_offset);
    try std.testing.expectEqual(@as(usize, 4), version.abi_minor_offset);
    try std.testing.expectEqual(@as(usize, 8), version.header_family_revision_offset);

    try std.testing.expectEqual(@as(u32, @intCast(abi.boundary_header_size)), version.header_size);
    try std.testing.expectEqual(abi.boundary_header_align, version.header_align);
    try std.testing.expectEqual(abi.boundary_header_size_offset, version.header_size_offset);
    try std.testing.expectEqual(abi.boundary_header_abi_version_offset, version.header_abi_version_offset);
    try std.testing.expectEqual(abi.boundary_header_flags_offset, version.header_flags_offset);
}

test "phase3 uapi version validation reports kernel status tags" {
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

    try std.testing.expect(version.eql(live, version.current()));
    try std.testing.expect(version.matchesCurrent(live));
    try std.testing.expect(!version.matchesCurrent(stale_major));
    try std.testing.expect(!version.matchesCurrent(stale_minor));
    try std.testing.expect(!version.matchesCurrent(stale_revision));

    try expectKernelStatus(version.validate(live), 0);
    try expectKernelStatus(version.validate(stale_major), invalid_argument);
    try expectKernelStatus(version.validate(stale_minor), invalid_argument);
    try expectKernelStatus(version.validate(stale_revision), invalid_argument);
}

test "phase3 uapi boundary accepts canonical and future compatible headers" {
    const canonical = version.boundaryHeader(0x51);
    const future = version.compatibleHeader(version.header_size + 24, 0x51);
    const undersized = abi.BoundaryHeader{
        .size = version.header_size - 1,
        .abi_version = abi.ABI_VERSION,
        .flags = 0x51,
    };
    const stale = abi.BoundaryHeader{
        .size = version.header_size,
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0x51,
    };

    try std.testing.expect(version.hasCurrentAbiVersion(canonical.abi_version));
    try std.testing.expect(version.isCanonicalSize(canonical.size));
    try std.testing.expect(version.isCompatibleSize(canonical.size));
    try std.testing.expect(version.isCanonical(canonical));
    try std.testing.expect(version.isCompatible(canonical));
    try std.testing.expect(!version.extendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), version.requestedExtraBytes(canonical));

    try std.testing.expect(!version.isCanonicalSize(future.size));
    try std.testing.expect(version.isCompatibleSize(future.size));
    try std.testing.expect(!version.isCanonical(future));
    try std.testing.expect(version.isCompatible(future));
    try std.testing.expect(version.extendsBoundary(future));
    try std.testing.expectEqual(@as(u32, 24), version.requestedExtraBytes(future));

    try std.testing.expect(!version.isCompatibleSize(undersized.size));
    try std.testing.expect(!version.isCompatible(undersized));
    try std.testing.expect(!version.extendsBoundary(undersized));
    try std.testing.expectEqual(@as(u32, 0), version.requestedExtraBytes(undersized));

    try std.testing.expect(!version.hasCurrentAbiVersion(stale.abi_version));
    try std.testing.expect(!version.isCompatible(stale));
    try std.testing.expect(!version.extendsBoundary(stale));
    try std.testing.expectEqual(@as(u32, 0), version.requestedExtraBytes(stale));
}

test "phase3 uapi boundary canonicalizes without widening the boundary" {
    const future = version.compatibleHeader(version.header_size + 16, 0xA5);
    const canonicalized = version.canonicalizeHeader(future);
    const valid = version.validateBoundaryHeader(future);

    try std.testing.expectEqual(version.header_size, canonicalized.size);
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), canonicalized.abi_version);
    try std.testing.expectEqual(@as(u16, 0xA5), canonicalized.flags);
    try std.testing.expect(version.isCanonical(canonicalized));
    try std.testing.expect(!version.extendsBoundary(canonicalized));
    try std.testing.expectEqual(@as(u32, 0), version.requestedExtraBytes(canonicalized));
    try expectKernelStatus(valid, 0);

    const stale = abi.BoundaryHeader{
        .size = version.header_size + 16,
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0xA5,
    };
    try expectKernelStatus(version.validateBoundaryHeader(stale), invalid_argument);
}
