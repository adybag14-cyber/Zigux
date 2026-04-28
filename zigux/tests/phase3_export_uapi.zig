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

    const header = export_shim.header(0x44);
    try std.testing.expectEqual(header, uapi_version.boundaryHeader(0x44));
    try std.testing.expect(export_shim.isCompatibleHeader(header));
    try std.testing.expect(uapi_version.isCompatible(header));

    try std.testing.expectEqual(abi.ABI_VERSION, uapi_version.abi_version);
}
