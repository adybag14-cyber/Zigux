const std = @import("std");
const abi = @import("abi_bindings");
const export_shim = @import("export_shim");
const uapi_version = @import("uapi_version");

test "phase3 export shim and uapi keep canonical boundary layout" {
    const header: export_shim.Header = export_shim.header(0x55);
    const uapi_header: uapi_version.Header = uapi_version.boundaryHeader(0x55);
    const future_compatible: export_shim.Header =
        export_shim.compatibleHeader(export_shim.header_size + 16, 0x55);
    const undersized: export_shim.Header =
        export_shim.compatibleHeader(export_shim.header_size - 1, 0x55);
    const uapi_undersized: uapi_version.Header =
        uapi_version.compatibleHeader(uapi_version.header_size - 1, 0x55);
    const version_mismatch: export_shim.Header = export_shim.versionedHeader(
        export_shim.header_size,
        export_shim.abi_version + 1,
        0x55,
    );

    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.BoundaryHeader, "size"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.BoundaryHeader, "abi_version"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.BoundaryHeader, "flags"));
    try std.testing.expectEqual(@sizeOf(export_shim.Header), @sizeOf(uapi_version.Header));

    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.ExportStatus));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ExportStatus, "code"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.ExportStatus, "facility"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.ExportStatus, "flags"));

    try std.testing.expectEqual(@sizeOf(abi.BoundaryHeader), @as(usize, header.size));
    try std.testing.expectEqual(header, uapi_header);
    try std.testing.expect(export_shim.isCanonicalHeader(header));
    try std.testing.expect(uapi_version.isCanonical(uapi_header));

    try std.testing.expectEqual(
        export_shim.HeaderCompatibility.future_compatible,
        export_shim.headerCompatibility(future_compatible).?,
    );
    try std.testing.expectEqual(
        uapi_version.Compatibility.future_compatible,
        uapi_version.compatibility(future_compatible).?,
    );
    try std.testing.expectEqual(header, export_shim.canonicalizeHeader(future_compatible).?);
    try std.testing.expectEqual(uapi_header, uapi_version.canonicalizeHeader(future_compatible).?);

    try std.testing.expectEqual(undersized, uapi_undersized);
    try std.testing.expect(export_shim.headerCompatibility(undersized) == null);
    try std.testing.expect(uapi_version.compatibility(uapi_undersized) == null);
    try std.testing.expect(!export_shim.isCompatibleHeader(undersized));
    try std.testing.expect(!uapi_version.isCompatible(uapi_undersized));
    try std.testing.expect(export_shim.canonicalizeHeader(undersized) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(uapi_undersized) == null);

    try std.testing.expect(export_shim.headerCompatibility(version_mismatch) == null);
    try std.testing.expect(uapi_version.compatibility(version_mismatch) == null);
    try std.testing.expect(export_shim.canonicalizeHeader(version_mismatch) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(version_mismatch) == null);
}
