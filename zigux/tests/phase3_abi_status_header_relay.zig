const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const export_shim = @import("export_shim");
const header_family = @import("header_family_binding");

test "phase3 abi status relay keeps facility-tagged status helpers aligned" {
    const ok = abi.okStatus(.helpers);
    const ok_export = export_shim.okStatus(.helpers);
    const ok_header = header_family.okStatus(.helpers);
    const err = abi.makeStatus(-71, .drivers);
    const err_export = export_shim.errorStatus(-71, .drivers);
    const err_header = header_family.errorStatus(-71, .drivers);
    const positive = abi.makeStatus(7, .kernel);
    const positive_export = export_shim.errorStatus(7, .kernel);
    const positive_header = header_family.errorStatus(7, .kernel);

    try testing.expect(std.meta.eql(ok, ok_export));
    try testing.expect(std.meta.eql(ok, ok_header));
    try testing.expect(abi.statusIsOk(ok));
    try testing.expect(export_shim.statusIsOk(ok_export));
    try testing.expect(header_family.statusIsOk(ok_header));

    try testing.expect(std.meta.eql(err, err_export));
    try testing.expect(std.meta.eql(err, err_header));
    try testing.expect(!abi.statusIsOk(err));
    try testing.expect(!export_shim.statusIsOk(err_export));
    try testing.expect(!header_family.statusIsOk(err_header));

    try testing.expect(std.meta.eql(positive, positive_export));
    try testing.expect(std.meta.eql(positive, positive_header));
    try testing.expect(abi.statusIsOk(positive));
    try testing.expect(export_shim.statusIsOk(positive_export));
    try testing.expect(header_family.statusIsOk(positive_header));
}

test "phase3 abi status relay keeps boundary-header predicates and validation aligned" {
    const canonical = abi.defaultHeader(0x2A);
    const expanded = abi.compatibleHeader(@sizeOf(abi.BoundaryHeader) + 12, 0x2A);
    const undersized = abi.BoundaryHeader{
        .size = @sizeOf(abi.BoundaryHeader) - 1,
        .abi_version = abi.ABI_VERSION,
        .flags = 0x2A,
    };
    const stale = abi.BoundaryHeader{
        .size = @sizeOf(abi.BoundaryHeader),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0x2A,
    };
    const canonicalized = abi.canonicalizeHeader(expanded);
    const ok = export_shim.validateBoundaryHeader(canonical);
    const ok_expanded = export_shim.validateBoundaryHeader(expanded);
    const invalid_size = export_shim.validateBoundaryHeader(undersized);
    const invalid_version = export_shim.validateBoundaryHeader(stale);

    try testing.expect(abi.headerIsCanonical(canonical));
    try testing.expect(export_shim.headerIsCanonical(canonical));
    try testing.expect(header_family.boundaryHeaderIsCanonical(canonical));
    try testing.expect(abi.headerIsCompatible(canonical));
    try testing.expect(export_shim.headerIsCompatible(canonical));
    try testing.expect(header_family.boundaryHeaderIsCompatible(canonical));
    try testing.expect(!abi.extendsBoundary(canonical));
    try testing.expect(!export_shim.extendsBoundary(canonical));
    try testing.expect(!header_family.boundaryHeaderExtendsBoundary(canonical));
    try testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(canonical));
    try testing.expectEqual(@as(u32, 0), export_shim.requestedExtraBytes(canonical));
    try testing.expectEqual(@as(u32, 0), header_family.boundaryHeaderRequestedExtraBytes(canonical));

    try testing.expect(!abi.headerIsCanonical(expanded));
    try testing.expect(!export_shim.headerIsCanonical(expanded));
    try testing.expect(!header_family.boundaryHeaderIsCanonical(expanded));
    try testing.expect(abi.headerIsCompatible(expanded));
    try testing.expect(export_shim.headerIsCompatible(expanded));
    try testing.expect(header_family.boundaryHeaderIsCompatible(expanded));
    try testing.expect(abi.extendsBoundary(expanded));
    try testing.expect(export_shim.extendsBoundary(expanded));
    try testing.expect(header_family.boundaryHeaderExtendsBoundary(expanded));
    try testing.expectEqual(@as(u32, 12), abi.requestedExtraBytes(expanded));
    try testing.expectEqual(@as(u32, 12), export_shim.requestedExtraBytes(expanded));
    try testing.expectEqual(@as(u32, 12), header_family.boundaryHeaderRequestedExtraBytes(expanded));

    try testing.expect(!abi.headerIsCanonical(undersized));
    try testing.expect(!export_shim.headerIsCanonical(undersized));
    try testing.expect(!header_family.boundaryHeaderIsCanonical(undersized));
    try testing.expect(!abi.headerIsCompatible(undersized));
    try testing.expect(!export_shim.headerIsCompatible(undersized));
    try testing.expect(!header_family.boundaryHeaderIsCompatible(undersized));

    try testing.expect(!abi.headerIsCanonical(stale));
    try testing.expect(!export_shim.headerIsCanonical(stale));
    try testing.expect(!header_family.boundaryHeaderIsCanonical(stale));
    try testing.expect(!abi.headerIsCompatible(stale));
    try testing.expect(!export_shim.headerIsCompatible(stale));
    try testing.expect(!header_family.boundaryHeaderIsCompatible(stale));
    try testing.expect(header_family.boundaryHeaderIsCanonicalSize(stale.size));
    try testing.expect(header_family.boundaryHeaderIsCompatibleSize(stale.size));

    try testing.expect(std.meta.eql(canonicalized, export_shim.canonicalizeHeader(expanded)));
    try testing.expect(std.meta.eql(canonicalized, header_family.canonicalizeBoundaryHeader(expanded)));
    try testing.expect(export_shim.statusIsOk(ok));
    try testing.expect(export_shim.statusIsOk(ok_expanded));
    try testing.expect(!export_shim.statusIsOk(invalid_size));
    try testing.expect(!export_shim.statusIsOk(invalid_version));
}

test "phase3 abi status relay keeps header-family status wrappers aligned with shared helpers" {
    const live = header_family.currentVersion();
    const stale = header_family.Version{
        .abi_major = live.abi_major,
        .abi_minor = live.abi_minor,
        .header_family_revision = live.header_family_revision + 1,
    };
    const valid_fields = header_family.initDevTFields(header_family.max_major, header_family.max_minor);
    const invalid_fields = header_family.initDevTFields(header_family.max_major + 1, 0);
    const earlier = header_family.initDevTFields(1, 2);
    const later = header_family.initDevTFields(1, 3);

    try testing.expect(std.meta.eql(export_shim.okStatus(.kernel), header_family.validateVersionStatus(live)));
    try testing.expect(std.meta.eql(export_shim.errorStatus(-22, .kernel), header_family.validateVersionStatus(stale)));
    try testing.expect(std.meta.eql(export_shim.okStatus(.kernel), header_family.validateDevTFieldsStatus(valid_fields)));
    try testing.expect(std.meta.eql(export_shim.errorStatus(-22, .kernel), header_family.validateDevTFieldsStatus(invalid_fields)));
    try testing.expect(std.meta.eql(export_shim.okStatus(.kernel), header_family.validateDevTRangeStatus(earlier, later)));
    try testing.expect(std.meta.eql(export_shim.errorStatus(-22, .kernel), header_family.validateDevTRangeStatus(later, earlier)));
}
