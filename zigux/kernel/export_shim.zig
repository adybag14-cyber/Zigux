const std = @import("std");
const abi = @import("abi_bindings");
const uapi_version = @import("uapi_version");

pub fn header(flags: u16) abi.BoundaryHeader {
    return uapi_version.boundaryHeader(flags);
}

pub fn isCompatibleHeader(boundary_header: abi.BoundaryHeader) bool {
    return uapi_version.isCompatible(boundary_header);
}

pub fn ok(facility: abi.Facility) abi.ExportStatus {
    return .{
        .code = 0,
        .facility = @intFromEnum(facility),
        .flags = 0,
    };
}

pub fn errno(code: i32, facility: abi.Facility) abi.ExportStatus {
    return .{
        .code = code,
        .facility = @intFromEnum(facility),
        .flags = if (code < 0) abi.STATUS_FLAG_ERROR else 0,
    };
}

pub fn isOk(status: abi.ExportStatus) bool {
    return status.code >= 0 and (status.flags & abi.STATUS_FLAG_ERROR) == 0;
}

test "phase3 export shim keeps failure encoding explicit" {
    const success = ok(.kernel);
    try std.testing.expect(isOk(success));

    const neutral = errno(0, .kernel);
    try std.testing.expect(isOk(neutral));
    try std.testing.expectEqual(@as(u16, 0), neutral.flags);

    const failure = errno(-22, .helpers);
    try std.testing.expect(!isOk(failure));
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.helpers)), failure.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), failure.flags);

    const hdr = header(0x10);
    try std.testing.expectEqual(@as(u32, @sizeOf(abi.BoundaryHeader)), hdr.size);
    try std.testing.expectEqual(abi.ABI_VERSION, hdr.abi_version);
    try std.testing.expectEqual(@as(u16, 0x10), hdr.flags);
    try std.testing.expect(isCompatibleHeader(hdr));
    try std.testing.expectEqual(hdr, uapi_version.boundaryHeader(0x10));
}
