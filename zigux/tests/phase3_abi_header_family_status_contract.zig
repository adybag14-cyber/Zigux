const std = @import("std");
const testing = std.testing;

const header_family = @import("header_family_binding");
const version_binding = @import("version_binding");
const dev_t_binding = @import("dev_t_binding");
const abi = @import("abi_bindings");

const invalid_argument: i32 = -22;

fn expectKernelInvalid(status: header_family.ExportStatus) !void {
    try testing.expect(!header_family.statusIsOk(status));
    try testing.expect(header_family.statusHasKnownFacility(status));
    try testing.expectEqual(@as(i32, invalid_argument), status.code);
    try testing.expectEqual(@as(u16, @intFromEnum(header_family.Facility.kernel)), status.facility);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), status.flags);
}

test "header-family status contract pins version fail-closed routing" {
    const current = header_family.currentVersion();
    const stale_major = header_family.Version{
        .abi_major = header_family.abi_major + 1,
        .abi_minor = header_family.abi_minor,
        .header_family_revision = header_family.header_family_revision,
    };
    const stale_minor = header_family.Version{
        .abi_major = header_family.abi_major,
        .abi_minor = header_family.abi_minor + 1,
        .header_family_revision = header_family.header_family_revision,
    };
    const stale_revision = header_family.Version{
        .abi_major = header_family.abi_major,
        .abi_minor = header_family.abi_minor,
        .header_family_revision = header_family.header_family_revision + 1,
    };
    const ok = header_family.validateVersionStatus(current);

    try testing.expect(header_family.versionMatchesCurrent(current));
    try testing.expectEqual(version_binding.current(), current);
    try testing.expect(header_family.statusIsOk(ok));
    try testing.expectEqual(header_family.okStatus(.kernel), ok);

    try testing.expect(!header_family.versionMatchesCurrent(stale_major));
    try testing.expect(!header_family.versionMatchesCurrent(stale_minor));
    try testing.expect(!header_family.versionMatchesCurrent(stale_revision));
    try expectKernelInvalid(header_family.validateVersionStatus(stale_major));
    try expectKernelInvalid(header_family.validateVersionStatus(stale_minor));
    try expectKernelInvalid(header_family.validateVersionStatus(stale_revision));
}

test "header-family status contract pins boundary header compatibility routing" {
    const canonical = header_family.currentBoundaryHeader(0x21);
    const compatible = header_family.compatibleBoundaryHeader(header_family.header_size + 24, 0x21);
    const undersized = header_family.BoundaryHeader{
        .size = header_family.header_size - 1,
        .abi_version = header_family.abi_version,
        .flags = 0x21,
    };
    const stale = header_family.BoundaryHeader{
        .size = header_family.header_size,
        .abi_version = header_family.abi_version + 1,
        .flags = 0x21,
    };

    try testing.expect(header_family.boundaryHeaderIsCanonical(canonical));
    try testing.expect(!header_family.boundaryHeaderExtendsBoundary(canonical));
    try testing.expectEqual(@as(u32, 0), header_family.boundaryHeaderRequestedExtraBytes(canonical));
    try testing.expectEqual(header_family.okStatus(.kernel), header_family.validateBoundaryHeaderStatus(canonical));

    try testing.expect(!header_family.boundaryHeaderIsCanonical(compatible));
    try testing.expect(header_family.boundaryHeaderIsCompatible(compatible));
    try testing.expect(header_family.boundaryHeaderExtendsBoundary(compatible));
    try testing.expectEqual(@as(u32, 24), header_family.boundaryHeaderRequestedExtraBytes(compatible));
    try testing.expectEqual(header_family.okStatus(.kernel), header_family.validateBoundaryHeaderStatus(compatible));

    try testing.expect(!header_family.boundaryHeaderIsCompatible(undersized));
    try testing.expect(!header_family.boundaryHeaderIsCompatible(stale));
    try expectKernelInvalid(header_family.validateBoundaryHeaderStatus(undersized));
    try expectKernelInvalid(header_family.validateBoundaryHeaderStatus(stale));
    try testing.expectEqual(
        header_family.canonicalizeBoundaryHeader(compatible),
        abi.canonicalizeHeader(compatible),
    );
}

test "header-family status contract pins dev_t component and range failures" {
    const max = header_family.initDevTFields(header_family.max_major, header_family.max_minor);
    const invalid_major = header_family.initDevTFields(header_family.max_major + 1, 0);
    const invalid_minor = header_family.initDevTFields(0, header_family.max_minor + 1);
    const earlier = header_family.initDevTFields(header_family.max_major, header_family.max_minor - 1);

    try testing.expect(header_family.validateDevTFields(max));
    try testing.expectEqual(header_family.okStatus(.kernel), header_family.validateDevTFieldsStatus(max));
    try testing.expectEqual(header_family.okStatus(.kernel), header_family.validateDevTComponentsStatus(max.major, max.minor));

    try testing.expect(!header_family.validateDevTFields(invalid_major));
    try testing.expect(!header_family.validateDevTFields(invalid_minor));
    try expectKernelInvalid(header_family.validateDevTFieldsStatus(invalid_major));
    try expectKernelInvalid(header_family.validateDevTFieldsStatus(invalid_minor));
    try expectKernelInvalid(header_family.validateDevTComponentsStatus(invalid_major.major, invalid_major.minor));

    try testing.expect(header_family.validateDevTRange(earlier, max));
    try testing.expect(!header_family.validateDevTRange(max, earlier));
    try testing.expect(!header_family.validateDevTRange(max, invalid_minor));
    try testing.expectEqual(dev_t_binding.makeDeviceNumber(max.major, max.minor), header_family.makeDeviceNumber(max.major, max.minor));
    try testing.expectEqual(header_family.okStatus(.kernel), header_family.validateDevTRangeStatus(earlier, max));
    try expectKernelInvalid(header_family.validateDevTRangeStatus(max, earlier));
    try expectKernelInvalid(header_family.validateDevTRangeStatus(max, invalid_minor));
}

test "header-family status contract keeps facility mapping bounded" {
    const helpers = header_family.okStatus(.helpers);
    const drivers = header_family.errorStatus(7, .drivers);
    const unknown = header_family.ExportStatus{
        .code = 0,
        .facility = 99,
        .flags = 0,
    };

    try testing.expect(header_family.statusIsOk(helpers));
    try testing.expect(header_family.statusIsOk(drivers));
    try testing.expect(!header_family.statusIsOk(header_family.errorStatus(invalid_argument, .kernel)));
    try testing.expect(header_family.statusHasKnownFacility(helpers));
    try testing.expect(header_family.statusHasKnownFacility(drivers));
    try testing.expect(!header_family.statusHasKnownFacility(unknown));

    try testing.expectEqual(@as(?header_family.Facility, .kernel), header_family.facilityFromInt(@intFromEnum(header_family.Facility.kernel)));
    try testing.expectEqual(@as(?header_family.Facility, .helpers), header_family.facilityFromInt(@intFromEnum(header_family.Facility.helpers)));
    try testing.expectEqual(@as(?header_family.Facility, .drivers), header_family.facilityFromInt(@intFromEnum(header_family.Facility.drivers)));
    try testing.expectEqual(@as(?header_family.Facility, null), header_family.facilityFromInt(unknown.facility));
    try testing.expectEqual(abi.okStatus(.helpers), helpers);
    try testing.expectEqual(abi.makeStatus(7, .drivers), drivers);
}
