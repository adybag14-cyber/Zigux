const std = @import("std");
const abi = @import("abi_bindings");
const export_shim = @import("export_shim");
const uapi_version = @import("uapi_version");

test "phase3 export and uapi boundary stays explicit" {
    const hdr = export_shim.header(0x24);
    try std.testing.expectEqual(@as(u32, @sizeOf(abi.BoundaryHeader)), hdr.size);
    try std.testing.expectEqual(abi.ABI_VERSION, hdr.abi_version);
    try std.testing.expectEqual(@as(u16, 0x24), hdr.flags);
    try std.testing.expect(export_shim.isCompatibleHeader(hdr));
    try std.testing.expect(uapi_version.isCompatible(hdr));
    try std.testing.expectEqual(hdr, uapi_version.boundaryHeader(0x24));

    const ok = export_shim.ok(.kernel);
    try std.testing.expect(export_shim.isOk(ok));
    try std.testing.expectEqual(@as(i32, 0), ok.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.kernel)), ok.facility);
    try std.testing.expectEqual(@as(u16, 0), ok.flags);

    const err = export_shim.errno(-5, .helpers);
    try std.testing.expect(!export_shim.isOk(err));
    try std.testing.expectEqual(@as(i32, -5), err.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.helpers)), err.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), err.flags);

    try std.testing.expectEqual(abi.ABI_VERSION, uapi_version.abi_version);
}
