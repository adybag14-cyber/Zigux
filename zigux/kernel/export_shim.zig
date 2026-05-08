const std = @import("std");
const abi = @import("abi_bindings");
const uapi_version = @import("uapi_version");

pub const Header = uapi_version.Header;
pub const abi_version: u16 = uapi_version.abi_version;
pub const header_size: u32 = uapi_version.header_size;
pub const HeaderCompatibility = uapi_version.Compatibility;
pub const HeaderAcceptance = uapi_version.AcceptedHeader;

pub fn versionedHeader(size: u32, version: u16, flags: u16) Header {
    return uapi_version.versionedHeader(size, version, flags);
}

pub fn canonicalHeader(flags: u16) Header {
    return uapi_version.canonicalHeader(flags);
}

pub fn boundaryHeader(flags: u16) Header {
    return uapi_version.boundaryHeader(flags);
}

pub fn compatibleHeader(size: u32, flags: u16) Header {
    return uapi_version.compatibleHeader(size, flags);
}

pub fn header(flags: u16) Header {
    return canonicalHeader(flags);
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

pub fn acceptHeader(header_value: Header) ?HeaderAcceptance {
    return uapi_version.acceptHeader(header_value);
}

pub fn headerCompatibility(header_value: Header) ?HeaderCompatibility {
    return uapi_version.compatibility(header_value);
}

pub fn isCompatibleHeader(header_value: Header) bool {
    return uapi_version.isCompatible(header_value);
}

pub fn isCanonicalHeader(header_value: Header) bool {
    return uapi_version.isCanonical(header_value);
}

pub fn canonicalizeHeader(header_value: Header) ?Header {
    return uapi_version.canonicalizeHeader(header_value);
}

pub fn compatibilityStatus(
    header_value: Header,
    incompatible_code: i32,
    facility: abi.Facility,
) abi.ExportStatus {
    return if (isCompatibleHeader(header_value)) ok(facility) else errno(incompatible_code, facility);
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
        .flags = 0,
    });
}

pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {
    return .{
        .code = status.code,
        .facility = status.facility,
        .flags = if (status.code < 0) abi.STATUS_FLAG_ERROR else 0,
    };
}

pub fn isOk(status: abi.ExportStatus) bool {
    return status.code >= 0 and (status.flags & abi.STATUS_FLAG_ERROR) == 0;
}

test "phase3 export shim keeps failure encoding explicit" {
    const success = ok(.kernel);
    try std.testing.expect(isOk(success));

    const failure = errno(-22, .helpers);
    try std.testing.expect(!isOk(failure));
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), failure.flags);

    const hdr = header(0x10);
    try std.testing.expectEqual(@as(u32, @sizeOf(abi.BoundaryHeader)), hdr.size);
    try std.testing.expectEqual(abi.ABI_VERSION, hdr.abi_version);
    try std.testing.expectEqual(@as(u16, 0x10), hdr.flags);
}

test "phase3 export shim reuses the shared boundary-header compatibility rules" {
    const canonical = boundaryHeader(0x22);
    const future_compatible = compatibleHeader(header_size + 16, 0x22);
    const mismatched_version = versionedHeader(header_size, abi_version + 1, 0x22);
    const accepted_canonical = acceptHeader(canonical).?;
    const accepted_future = acceptHeader(future_compatible).?;

    try std.testing.expect(isCanonicalHeader(canonical));
    try std.testing.expect(isCompatibleHeader(canonical));
    try std.testing.expectEqual(HeaderCompatibility.canonical, headerCompatibility(canonical).?);
    try std.testing.expectEqual(HeaderCompatibility.canonical, accepted_canonical.compatibility);
    try std.testing.expectEqual(canonical, accepted_canonical.canonical);

    try std.testing.expect(!isCanonicalHeader(future_compatible));
    try std.testing.expect(isCompatibleHeader(future_compatible));
    try std.testing.expectEqual(HeaderCompatibility.future_compatible, headerCompatibility(future_compatible).?);
    try std.testing.expectEqual(HeaderCompatibility.future_compatible, accepted_future.compatibility);
    try std.testing.expectEqual(boundaryHeader(0x22), accepted_future.canonical);
    try std.testing.expectEqual(boundaryHeader(0x22), canonicalizeHeader(future_compatible).?);

    try std.testing.expect(headerCompatibility(mismatched_version) == null);
    try std.testing.expect(acceptHeader(mismatched_version) == null);
    try std.testing.expect(!isCompatibleHeader(mismatched_version));
    try std.testing.expect(canonicalizeHeader(mismatched_version) == null);
}

test "phase3 export shim relays compatibility through explicit status packets" {
    const canonical = boundaryHeader(0x33);
    const future_compatible = compatibleHeader(header_size + 16, 0x33);
    const undersized = compatibleHeader(header_size - 1, 0x33);
    const mismatched_version = versionedHeader(header_size, abi_version + 1, 0x33);

    const canonical_status = compatibilityStatus(canonical, -22, .kernel);
    try std.testing.expect(isOk(canonical_status));
    try std.testing.expectEqual(@as(i32, 0), canonical_status.code);
    try std.testing.expectEqual(@intFromEnum(abi.Facility.kernel), canonical_status.facility);

    const future_status = compatibilityStatus(future_compatible, -75, .helpers);
    try std.testing.expect(isOk(future_status));
    try std.testing.expectEqual(@as(i32, 0), future_status.code);
    try std.testing.expectEqual(@intFromEnum(abi.Facility.helpers), future_status.facility);

    const undersized_status = compatibilityStatus(undersized, -22, .drivers);
    try std.testing.expect(!isOk(undersized_status));
    try std.testing.expectEqual(@as(i32, -22), undersized_status.code);
    try std.testing.expectEqual(@intFromEnum(abi.Facility.drivers), undersized_status.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), undersized_status.flags);

    const mismatched_status = compatibilityStatus(mismatched_version, -71, .kernel);
    try std.testing.expect(!isOk(mismatched_status));
    try std.testing.expectEqual(@as(i32, -71), mismatched_status.code);
    try std.testing.expectEqual(@intFromEnum(abi.Facility.kernel), mismatched_status.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), mismatched_status.flags);
}
