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
    try std.testing.expectEqual(header, uapi_version.canonicalHeader(0x44));
    try std.testing.expectEqual(header, uapi_version.boundaryHeader(0x44));
    try std.testing.expectEqual(uapi_version.header_size, header.size);
    try std.testing.expect(uapi_version.isCurrentAbiVersion(header.abi_version));
    try std.testing.expect(uapi_version.isCanonicalSize(header.size));
    try std.testing.expect(export_shim.isCanonicalHeader(header));
    try std.testing.expect(uapi_version.isCanonical(header));
    try std.testing.expect(export_shim.isCompatibleHeader(header));
    try std.testing.expect(uapi_version.isCompatible(header));
    try std.testing.expectEqual(header, export_shim.canonicalizeHeader(header).?);
    try std.testing.expectEqual(header, uapi_version.canonicalizeHeader(header).?);

    const undersized_header = uapi_version.compatibleHeader(uapi_version.header_size - 1, 0x11);
    try std.testing.expect(!uapi_version.isCompatibleSize(undersized_header.size));
    try std.testing.expect(!export_shim.isCompatibleHeader(undersized_header));
    try std.testing.expect(!uapi_version.isCompatible(undersized_header));
    try std.testing.expect(export_shim.canonicalizeHeader(undersized_header) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(undersized_header) == null);

    const mismatched_version_header: abi.BoundaryHeader = .{
        .size = uapi_version.header_size,
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0,
    };
    try std.testing.expect(!uapi_version.isCurrentAbiVersion(mismatched_version_header.abi_version));
    try std.testing.expect(!export_shim.isCompatibleHeader(mismatched_version_header));
    try std.testing.expect(!uapi_version.isCompatible(mismatched_version_header));
    try std.testing.expect(export_shim.canonicalizeHeader(mismatched_version_header) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(mismatched_version_header) == null);

    const future_compatible_header = uapi_version.compatibleHeader(uapi_version.header_size + 8, 0x44);
    try std.testing.expectEqual(abi.ABI_VERSION, future_compatible_header.abi_version);
    try std.testing.expectEqual(@as(u16, 0x44), future_compatible_header.flags);
    try std.testing.expect(uapi_version.isCompatibleSize(future_compatible_header.size));
    try std.testing.expect(!uapi_version.isCanonicalSize(future_compatible_header.size));
    try std.testing.expect(!export_shim.isCanonicalHeader(future_compatible_header));
    try std.testing.expect(!uapi_version.isCanonical(future_compatible_header));
    try std.testing.expect(export_shim.isCompatibleHeader(future_compatible_header));
    try std.testing.expect(uapi_version.isCompatible(future_compatible_header));
    try std.testing.expectEqual(header, export_shim.canonicalizeHeader(future_compatible_header).?);
    try std.testing.expectEqual(header, uapi_version.canonicalizeHeader(future_compatible_header).?);

    try std.testing.expectEqual(abi.ABI_VERSION, uapi_version.abi_version);
}
