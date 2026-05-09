const std = @import("std");
const abi = @import("abi_bindings");
const export_shim = @import("export_shim");
const uapi_version = @import("uapi_version");

test "phase3 export shim and uapi share the bounded boundary-header contract" {
    const canonical = export_shim.canonicalHeader(0x44);
    const boundary = export_shim.boundaryHeader(0x44);
    const export_alias = export_shim.header(0x44);
    const uapi_canonical = uapi_version.canonicalHeader(0x44);
    const uapi_boundary = uapi_version.boundaryHeader(0x44);
    const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 16, 0x44);
    const undersized = export_shim.compatibleHeader(export_shim.header_size - 1, 0x44);
    const mismatched_version = export_shim.versionedHeader(
        export_shim.header_size,
        export_shim.abi_version + 1,
        0x44,
    );

    try std.testing.expectEqual(canonical, boundary);
    try std.testing.expectEqual(canonical, export_alias);
    try std.testing.expectEqual(canonical, uapi_canonical);
    try std.testing.expectEqual(canonical, uapi_boundary);
    try std.testing.expectEqual(@as(u32, export_shim.header_size), canonical.size);
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), canonical.abi_version);
    try std.testing.expectEqual(@as(u16, 0x44), canonical.flags);

    try std.testing.expect(export_shim.isCanonicalHeader(canonical));
    try std.testing.expect(export_shim.isCompatibleHeader(canonical));
    try std.testing.expect(uapi_version.isCanonical(canonical));
    try std.testing.expect(uapi_version.isCompatible(canonical));

    try std.testing.expect(!export_shim.isCanonicalHeader(future_compatible));
    try std.testing.expect(export_shim.isCompatibleHeader(future_compatible));
    try std.testing.expect(!uapi_version.isCanonical(future_compatible));
    try std.testing.expect(uapi_version.isCompatible(future_compatible));
    try std.testing.expectEqual(canonical, export_shim.canonicalizeHeader(future_compatible).?);
    try std.testing.expectEqual(canonical, uapi_version.canonicalizeHeader(future_compatible).?);

    try std.testing.expect(export_shim.acceptHeader(undersized) == null);
    try std.testing.expect(uapi_version.acceptHeader(undersized) == null);
    try std.testing.expect(export_shim.canonicalizeHeader(undersized) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(undersized) == null);

    try std.testing.expect(export_shim.acceptHeader(mismatched_version) == null);
    try std.testing.expect(uapi_version.acceptHeader(mismatched_version) == null);
    try std.testing.expect(export_shim.canonicalizeHeader(mismatched_version) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(mismatched_version) == null);
}

test "phase3 export shim keeps compatibility-status relays explicit" {
    const canonical = export_shim.canonicalHeader(0x55);
    const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 8, 0x55);
    const undersized = export_shim.compatibleHeader(export_shim.header_size - 1, 0x55);
    const mismatched_version = export_shim.versionedHeader(
        export_shim.header_size,
        export_shim.abi_version + 1,
        0x55,
    );

    const canonical_status = export_shim.compatibilityStatus(canonical, -22, .kernel);
    const future_status = export_shim.compatibilityStatus(future_compatible, -75, .helpers);
    const undersized_status = export_shim.compatibilityStatus(undersized, -22, .drivers);
    const mismatch_status = export_shim.compatibilityStatus(mismatched_version, -71, .kernel);

    try std.testing.expect(export_shim.isOk(canonical_status));
    try std.testing.expect(export_shim.isOk(future_status));
    try std.testing.expectEqual(@as(i32, 0), canonical_status.code);
    try std.testing.expectEqual(@as(i32, 0), future_status.code);
    try std.testing.expectEqual(@intFromEnum(abi.Facility.kernel), canonical_status.facility);
    try std.testing.expectEqual(@intFromEnum(abi.Facility.helpers), future_status.facility);

    try std.testing.expect(!export_shim.isOk(undersized_status));
    try std.testing.expectEqual(@as(i32, -22), undersized_status.code);
    try std.testing.expectEqual(@intFromEnum(abi.Facility.drivers), undersized_status.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), undersized_status.flags);

    try std.testing.expect(!export_shim.isOk(mismatch_status));
    try std.testing.expectEqual(@as(i32, -71), mismatch_status.code);
    try std.testing.expectEqual(@intFromEnum(abi.Facility.kernel), mismatch_status.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), mismatch_status.flags);
}
