const std = @import("std");
const abi = @import("abi_bindings");
const uapi_version = @import("uapi_version");

pub const Header = abi.BoundaryHeader;
pub const HeaderCompatibility = uapi_version.Compatibility;
pub const abi_version: u16 = uapi_version.abi_version;
pub const header_size: u32 = uapi_version.header_size;

pub fn canonicalHeader(flags: u16) abi.BoundaryHeader {
    return uapi_version.canonicalHeader(flags);
}

pub fn compatibleHeader(size: u32, flags: u16) abi.BoundaryHeader {
    return uapi_version.compatibleHeader(size, flags);
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

pub fn isCurrentAbiVersion(version: u16) bool {
    return uapi_version.isCurrentAbiVersion(version);
}

pub fn isCompatibleSize(size: u32) bool {
    return uapi_version.isCompatibleSize(size);
}

pub fn isCanonicalSize(size: u32) bool {
    return uapi_version.isCanonicalSize(size);
}

pub fn isCompatibleHeader(boundary_header: abi.BoundaryHeader) bool {
    return uapi_version.isCompatible(boundary_header);
}

pub fn isCanonicalHeader(boundary_header: abi.BoundaryHeader) bool {
    return uapi_version.isCanonical(boundary_header);
}

pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {
    var normalized = status;
    normalized.flags = if (normalized.code < 0) abi.STATUS_FLAG_ERROR else 0;
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
    try std.testing.expectEqual(hdr, compatibleHeader(header_size, 0x10));
    try std.testing.expectEqual(hdr, versionedHeader(header_size, abi_version, 0x10));
    try std.testing.expectEqual(header_size, hdr.size);
    try std.testing.expectEqual(abi_version, hdr.abi_version);
    try std.testing.expect(isCurrentAbiVersion(hdr.abi_version));
    try std.testing.expect(isCompatibleSize(hdr.size));
    try std.testing.expect(isCanonicalSize(hdr.size));
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

    const stray_unknown_ok = normalize(.{
        .code = 9,
        .facility = @intFromEnum(abi.Facility.drivers),
        .flags = @as(u16, abi.STATUS_FLAG_ERROR | 0x80),
    });
    try std.testing.expectEqual(@as(u16, 0), stray_unknown_ok.flags);
    try std.testing.expect(isOk(stray_unknown_ok));

    const stray_unknown_err = normalize(.{
        .code = -9,
        .facility = @intFromEnum(abi.Facility.drivers),
        .flags = 0x80,
    });
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), stray_unknown_err.flags);
    try std.testing.expect(!isOk(stray_unknown_err));
}

test "phase3 export shim separates canonical headers from broader compatibility" {
    const canonical = canonicalHeader(0x20);
    try std.testing.expectEqual(canonical, header(0x20));
    try std.testing.expectEqual(HeaderCompatibility.canonical, headerCompatibility(canonical).?);
    try std.testing.expect(isCanonicalHeader(canonical));
    try std.testing.expect(isCompatibleHeader(canonical));
    try std.testing.expect(isCanonicalSize(canonical.size));

    const future_compatible = compatibleHeader(header_size + 8, 0x20);
    try std.testing.expectEqual(future_compatible, uapi_version.compatibleHeader(header_size + 8, 0x20));
    try std.testing.expectEqual(HeaderCompatibility.future_compatible, headerCompatibility(future_compatible).?);
    try std.testing.expect(!isCanonicalHeader(future_compatible));
    try std.testing.expect(isCompatibleHeader(future_compatible));
    try std.testing.expect(isCompatibleSize(future_compatible.size));
    try std.testing.expect(!isCanonicalSize(future_compatible.size));
}

test "phase3 export shim versioned header relay keeps arbitrary replay explicit" {
    const replay = versionedHeader(header_size + 4, abi_version + 1, 0x31);
    try std.testing.expectEqual(replay, uapi_version.versionedHeader(header_size + 4, abi_version + 1, 0x31));
    try std.testing.expect(!isCurrentAbiVersion(replay.abi_version));
    try std.testing.expect(isCompatibleSize(replay.size));
    try std.testing.expect(headerCompatibility(replay) == null);
    try std.testing.expect(canonicalizeHeader(replay) == null);
}

test "phase3 export shim canonicalizes compatible headers back to the current shape" {
    const canonical = canonicalHeader(0x77);
    try std.testing.expectEqual(canonical, canonicalizeHeader(canonical).?);

    const future_compatible = compatibleHeader(header_size + 8, 0x77);
    try std.testing.expectEqual(future_compatible, uapi_version.compatibleHeader(header_size + 8, 0x77));
    try std.testing.expectEqual(HeaderCompatibility.future_compatible, headerCompatibility(future_compatible).?);
    try std.testing.expectEqual(canonical, canonicalizeHeader(future_compatible).?);

    const undersized = compatibleHeader(header_size - 1, 0x77);
    try std.testing.expect(headerCompatibility(undersized) == null);
    try std.testing.expect(canonicalizeHeader(undersized) == null);
}
