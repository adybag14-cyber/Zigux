const std = @import("std");

const abi = @import("abi_bindings");
const export_shim = @import("export_shim");
const uapi_version = @import("uapi_version");

test "phase3 export shim and uapi keep starter boundary layout explicit" {
    const header = export_shim.boundaryHeader(0x55);
    const uapi_header = uapi_version.boundaryHeader(0x55);

    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(abi.BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.BoundaryHeader, "size"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.BoundaryHeader, "abi_version"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.BoundaryHeader, "flags"));

    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.ExportStatus));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(abi.ExportStatus));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ExportStatus, "code"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.ExportStatus, "facility"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.ExportStatus, "flags"));

    try std.testing.expectEqual(header, uapi_header);
    try std.testing.expectEqual(@sizeOf(abi.BoundaryHeader), @as(usize, header.size));
    try std.testing.expect(export_shim.isCanonicalHeader(header));
    try std.testing.expect(uapi_version.isCanonical(uapi_header));
}

test "phase3 export shim and uapi reject undersized boundary headers symmetrically" {
    const undersized = export_shim.compatibleHeader(export_shim.header_size - 1, 0x44);

    try std.testing.expectEqual(undersized, uapi_version.compatibleHeader(uapi_version.header_size - 1, 0x44));

    try std.testing.expect(export_shim.headerCompatibility(undersized) == null);
    try std.testing.expect(uapi_version.compatibility(undersized) == null);

    try std.testing.expect(export_shim.acceptHeader(undersized) == null);
    try std.testing.expect(uapi_version.acceptHeader(undersized) == null);

    try std.testing.expect(!export_shim.isCompatibleHeader(undersized));
    try std.testing.expect(!uapi_version.isCompatible(undersized));
    try std.testing.expect(!export_shim.isCanonicalHeader(undersized));
    try std.testing.expect(!uapi_version.isCanonical(undersized));

    try std.testing.expect(export_shim.canonicalizeHeader(undersized) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(undersized) == null);
    try std.testing.expect(export_shim.requestedExtraBytes(undersized) == null);
    try std.testing.expect(uapi_version.evaluateHeader(undersized).requestedExtraBytes() == null);
}
