const std = @import("std");
const abi = @import("abi_bindings");
const export_shim = @import("export_shim");
const uapi_version = @import("uapi_version");

test "phase3 export shim and uapi keep canonical boundary layout" {
    const header = export_shim.header(0x55);
    const uapi_header = uapi_version.boundaryHeader(0x55);

    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.BoundaryHeader, "size"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.BoundaryHeader, "abi_version"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.BoundaryHeader, "flags"));
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.ExportStatus));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ExportStatus, "code"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.ExportStatus, "facility"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.ExportStatus, "flags"));
    try std.testing.expectEqual(@sizeOf(abi.BoundaryHeader), @as(usize, header.size));
    try std.testing.expectEqual(header, uapi_header);
    try std.testing.expect(export_shim.isCanonicalHeader(header));
    try std.testing.expect(uapi_version.isCanonical(uapi_header));

    const future_compatible = export_shim.compatibleHeader(header.size + 8, 0x55);
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(@TypeOf(future_compatible)));
    try std.testing.expect(export_shim.isCompatibleHeader(future_compatible));
    try std.testing.expect(!export_shim.isCanonicalHeader(future_compatible));
    try std.testing.expect(uapi_version.isCompatible(future_compatible));
    try std.testing.expect(!uapi_version.isCanonical(future_compatible));
    try std.testing.expectEqual(header, export_shim.canonicalizeHeader(future_compatible).?);
    try std.testing.expectEqual(uapi_header, uapi_version.canonicalizeHeader(future_compatible).?);

    const mismatched_version = export_shim.versionedHeader(header.size, abi.ABI_VERSION + 1, 0x55);
    try std.testing.expect(export_shim.canonicalizeHeader(mismatched_version) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(mismatched_version) == null);
}
