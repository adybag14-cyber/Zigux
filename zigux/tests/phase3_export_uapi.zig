const std = @import("std");
const abi = @import("abi_bindings");
const export_shim = @import("export_shim");
const uapi_version = @import("uapi_version");

test "phase3 export shim and uapi stay aligned" {
    const success = export_shim.ok(.kernel);
    try std.testing.expect(export_shim.isOk(success));
    try std.testing.expectEqual(@as(i32, 0), success.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.kernel)), success.facility);
    try std.testing.expectEqual(@as(u16, 0), success.flags);

    const failure = export_shim.errno(-22, .helpers);
    try std.testing.expect(!export_shim.isOk(failure));
    try std.testing.expectEqual(@as(i32, -22), failure.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.helpers)), failure.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), failure.flags);

    const header = export_shim.canonicalHeader(0x44);
    try std.testing.expectEqual(header, export_shim.header(0x44));
    try std.testing.expectEqual(header, export_shim.compatibleHeader(export_shim.header_size, 0x44));
    try std.testing.expectEqual(header, export_shim.versionedHeader(export_shim.header_size, export_shim.abi_version, 0x44));
    try std.testing.expectEqual(header, uapi_version.canonicalHeader(0x44));
    try std.testing.expectEqual(header, uapi_version.boundaryHeader(0x44));
    try std.testing.expectEqual(export_shim.header_size, header.size);
    try std.testing.expect(export_shim.isCurrentAbiVersion(header.abi_version));
    try std.testing.expect(export_shim.isCanonicalSize(header.size));
    try std.testing.expectEqual(uapi_version.Compatibility.canonical, uapi_version.compatibility(header).?);
    try std.testing.expectEqual(export_shim.HeaderCompatibility.canonical, export_shim.headerCompatibility(header).?);
    try std.testing.expect(export_shim.isCanonicalHeader(header));
    try std.testing.expect(uapi_version.isCanonical(header));
    try std.testing.expect(export_shim.isCompatibleHeader(header));
    try std.testing.expect(uapi_version.isCompatible(header));
    try std.testing.expectEqual(header, export_shim.canonicalizeHeader(header).?);
    try std.testing.expectEqual(header, uapi_version.canonicalizeHeader(header).?);

    const canonical_positive = export_shim.normalize(.{
        .code = 5,
        .facility = @intFromEnum(abi.Facility.kernel),
        .flags = @as(u16, abi.STATUS_FLAG_ERROR | 0x80),
    });
    try std.testing.expectEqual(@as(u16, 0), canonical_positive.flags);
    try std.testing.expect(export_shim.isOk(canonical_positive));

    const canonical_negative = export_shim.normalize(.{
        .code = -5,
        .facility = @intFromEnum(abi.Facility.kernel),
        .flags = 0x80,
    });
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), canonical_negative.flags);
    try std.testing.expect(!export_shim.isOk(canonical_negative));

    const undersized_header = export_shim.compatibleHeader(export_shim.header_size - 1, 0x11);
    try std.testing.expectEqual(undersized_header, uapi_version.compatibleHeader(uapi_version.header_size - 1, 0x11));
    try std.testing.expect(!export_shim.isCompatibleSize(undersized_header.size));
    try std.testing.expect(export_shim.headerCompatibility(undersized_header) == null);
    try std.testing.expect(uapi_version.compatibility(undersized_header) == null);
    try std.testing.expect(!export_shim.isCompatibleHeader(undersized_header));
    try std.testing.expect(!uapi_version.isCompatible(undersized_header));
    try std.testing.expect(export_shim.canonicalizeHeader(undersized_header) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(undersized_header) == null);

    const mismatched_version_header = export_shim.versionedHeader(export_shim.header_size, export_shim.abi_version + 1, 0);
    try std.testing.expectEqual(mismatched_version_header, uapi_version.versionedHeader(uapi_version.header_size, abi.ABI_VERSION + 1, 0));
    try std.testing.expect(!export_shim.isCurrentAbiVersion(mismatched_version_header.abi_version));
    try std.testing.expect(export_shim.headerCompatibility(mismatched_version_header) == null);
    try std.testing.expect(uapi_version.compatibility(mismatched_version_header) == null);
    try std.testing.expect(!export_shim.isCompatibleHeader(mismatched_version_header));
    try std.testing.expect(!uapi_version.isCompatible(mismatched_version_header));
    try std.testing.expect(export_shim.canonicalizeHeader(mismatched_version_header) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(mismatched_version_header) == null);

    const future_compatible_header = export_shim.compatibleHeader(export_shim.header_size + 8, 0x44);
    try std.testing.expectEqual(future_compatible_header, uapi_version.compatibleHeader(uapi_version.header_size + 8, 0x44));
    try std.testing.expectEqual(export_shim.abi_version, future_compatible_header.abi_version);
    try std.testing.expectEqual(@as(u16, 0x44), future_compatible_header.flags);
    try std.testing.expect(export_shim.isCompatibleSize(future_compatible_header.size));
    try std.testing.expect(!export_shim.isCanonicalSize(future_compatible_header.size));
    try std.testing.expectEqual(uapi_version.Compatibility.future_compatible, uapi_version.compatibility(future_compatible_header).?);
    try std.testing.expectEqual(export_shim.HeaderCompatibility.future_compatible, export_shim.headerCompatibility(future_compatible_header).?);
    try std.testing.expect(!export_shim.isCanonicalHeader(future_compatible_header));
    try std.testing.expect(!uapi_version.isCanonical(future_compatible_header));
    try std.testing.expect(export_shim.isCompatibleHeader(future_compatible_header));
    try std.testing.expect(uapi_version.isCompatible(future_compatible_header));
    try std.testing.expectEqual(header, export_shim.canonicalizeHeader(future_compatible_header).?);
    try std.testing.expectEqual(header, uapi_version.canonicalizeHeader(future_compatible_header).?);

    try std.testing.expectEqual(export_shim.abi_version, uapi_version.abi_version);
}
