const std = @import("std");
const abi = @import("abi_bindings");
const uapi_version = @import("uapi_version");

pub const HeaderCompatibility = uapi_version.Compatibility;

pub fn canonicalHeader(flags: u16) abi.BoundaryHeader {
    return uapi_version.canonicalHeader(flags);
}

pub fn versionedHeader(size: u32, version: u16, flags: u16) abi.BoundaryHeader {
    return uapi_version.versionedHeader(size, version, flags);
}

pub fn header(flags: u16) abi.BoundaryHeader {
    return canonicalHeader(flags);
}

pub fn headerCompatibility(boundary_header: abi.BoundaryHeader) ?HeaderCompatibility {
    return uapi_version.compatibility(boundary_header);
}

pub fn canonicalizeHeader(boundary_header: abi.BoundaryHeader) ?abi.BoundaryHeader {
    return uapi_version.canonicalizeHeader(boundary_header);
}

pub fn isCompatibleHeader(boundary_header: abi.BoundaryHeader) bool {
    return uapi_version.isCompatible(boundary_header);
}

pub fn isCanonicalHeader(boundary_header: abi.BoundaryHeader) bool {
    return uapi_version.isCanonical(boundary_header);
}

pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {
    var normalized = status;
    if (normalized.code < 0) {
        normalized.flags |= abi.STATUS_FLAG_ERROR;
    } else {
        normalized.flags &= ~abi.STATUS_FLAG_ERROR;
    }
    return normalized;
}

pub fn ok(facility: abi.Facility) abi.ExportStatus {
    return normalize(.{
        .code = 0,
        .facility = @intFromEnum(facility),
        .flags = 0,
    });
}

pub fn errno(code: i32, facility: abi.Facility) abi.ExportStatus {
    return normalize(.{
        .code = code,
        .facility = @intFromEnum(facility),
        .flags = if (code < 0) abi.STATUS_FLAG_ERROR else 0,
    });
}

pub fn isOk(status: abi.ExportStatus) bool {
    const normalized = normalize(status);
    return normalized.code >= 0 and (normalized.flags & abi.STATUS_FLAG_ERROR) == 0;
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

    const hdr = canonicalHeader(0x10);
    try std.testing.expectEqual(hdr, header(0x10));
    try std.testing.expectEqual(hdr, versionedHeader(@sizeOf(abi.BoundaryHeader), abi.ABI_VERSION, 0x10));
    try std.testing.expectEqual(@as(u32, @sizeOf(abi.BoundaryHeader)), hdr.size);
    try std.testing.expectEqual(abi.ABI_VERSION, hdr.abi_version);
    try std.testing.expectEqual(@as(u16, 0x10), hdr.flags);
    try std.testing.expectEqual(HeaderCompatibility.canonical, headerCompatibility(hdr).?);
    try std.testing.expect(isCompatibleHeader(hdr));
    try std.testing.expectEqual(hdr, uapi_version.boundaryHeader(0x10));
    try std.testing.expectEqual(hdr, uapi_version.canonicalHeader(0x10));
}

test "phase3 export shim normalizes explicit status decoding" {
    const missing_error_flag = normalize(.{
        .code = -5,
        .facility = @intFromEnum(abi.Facility.kernel),
        .flags = 0,
    });
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), missing_error_flag.flags & abi.STATUS_FLAG_ERROR);
    try std.testing.expect(!isOk(missing_error_flag));

    const stray_error_flag = normalize(.{
        .code = 7,
        .facility = @intFromEnum(abi.Facility.helpers),
        .flags = abi.STATUS_FLAG_ERROR,
    });
    try std.testing.expectEqual(@as(u16, 0), stray_error_flag.flags & abi.STATUS_FLAG_ERROR);
    try std.testing.expect(isOk(stray_error_flag));
}

test "phase3 export shim separates canonical headers from broader compatibility" {
    const canonical = canonicalHeader(0x20);
    try std.testing.expectEqual(canonical, header(0x20));
    try std.testing.expectEqual(HeaderCompatibility.canonical, headerCompatibility(canonical).?);
    try std.testing.expect(isCanonicalHeader(canonical));
    try std.testing.expect(isCompatibleHeader(canonical));

    const future_compatible: abi.BoundaryHeader = .{
        .size = @sizeOf(abi.BoundaryHeader) + 8,
        .abi_version = abi.ABI_VERSION,
        .flags = 0x20,
    };
    try std.testing.expectEqual(HeaderCompatibility.future_compatible, headerCompatibility(future_compatible).?);
    try std.testing.expect(!isCanonicalHeader(future_compatible));
    try std.testing.expect(isCompatibleHeader(future_compatible));
}

test "phase3 export shim versioned header relay keeps arbitrary replay explicit" {
    const replay = versionedHeader(uapi_version.header_size + 4, abi.ABI_VERSION + 1, 0x31);
    try std.testing.expectEqual(replay, uapi_version.versionedHeader(uapi_version.header_size + 4, abi.ABI_VERSION + 1, 0x31));
    try std.testing.expect(headerCompatibility(replay) == null);
    try std.testing.expect(canonicalizeHeader(replay) == null);
}

test "phase3 export shim canonicalizes compatible headers back to the current shape" {
    const canonical = canonicalHeader(0x77);
    try std.testing.expectEqual(canonical, canonicalizeHeader(canonical).?);

    const future_compatible = uapi_version.compatibleHeader(uapi_version.header_size + 8, 0x77);
    try std.testing.expectEqual(HeaderCompatibility.future_compatible, headerCompatibility(future_compatible).?);
    try std.testing.expectEqual(canonical, canonicalizeHeader(future_compatible).?);

    const undersized = uapi_version.compatibleHeader(uapi_version.header_size - 1, 0x77);
    try std.testing.expect(headerCompatibility(undersized) == null);
    try std.testing.expect(canonicalizeHeader(undersized) == null);
}
