const std = @import("std");
const abi = @import("abi_bindings");
const export_shim = @import("export_shim");
const uapi_version = @import("uapi_version");

test "phase3 export shim and uapi keep canonical boundary layout" {
    const header = export_shim.header(0x55);
    const uapi_header = uapi_version.boundaryHeader(0x55);

    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.ExportStatus));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.BoundaryHeader, "abi_version"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.ExportStatus, "flags"));
    try std.testing.expectEqual(@sizeOf(abi.BoundaryHeader), @as(usize, header.size));
    try std.testing.expectEqual(header, uapi_header);
    try std.testing.expect(export_shim.isCanonicalHeader(header));
    try std.testing.expect(uapi_version.isCanonical(uapi_header));
}
