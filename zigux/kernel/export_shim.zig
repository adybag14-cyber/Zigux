const std = @import("std");

const abi = @import("abi_bindings");
const uapi_dev_t = @import("uapi_dev_t");
const uapi_version = @import("uapi_version");

pub const Header = uapi_version.Header;
pub const abi_version: u16 = uapi_version.abi_version;
pub const header_size: u32 = uapi_version.header_size;

pub const HeaderCompatibility = uapi_version.Compatibility;
pub const HeaderAcceptance = uapi_version.AcceptedHeader;
pub const HeaderEvaluation = uapi_version.HeaderEvaluation;

pub const CompatibilityDecision = struct {
    evaluation: HeaderEvaluation,
    status: abi.ExportStatus,
};

pub const DeviceEncodingResult = struct {
    value: u32,
    status: abi.ExportStatus,
};

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

pub fn headerCompatibility(header_value: Header) ?HeaderCompatibility {
    return uapi_version.compatibility(header_value);
}

pub fn acceptHeader(header_value: Header) ?HeaderAcceptance {
    return uapi_version.acceptHeader(header_value);
}

pub fn evaluateHeader(
    header_value: Header,
    incompatible_code: i32,
    facility: abi.Facility,
) CompatibilityDecision {
    const evaluation = uapi_version.evaluateHeader(header_value);
    return .{
        .evaluation = evaluation,
        .status = if (evaluation.isAccepted()) ok(facility) else errno(incompatible_code, facility),
    };
}

pub fn compatibilityStatus(
    header_value: Header,
    incompatible_code: i32,
    facility: abi.Facility,
) abi.ExportStatus {
    return evaluateHeader(header_value, incompatible_code, facility).status;
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

pub fn extendsBoundary(header_value: Header) bool {
    return uapi_version.evaluateHeader(header_value).extendsBoundary();
}

pub fn requestedExtraBytes(header_value: Header) ?u32 {
    return uapi_version.evaluateHeader(header_value).requestedExtraBytes();
}

pub fn encodeDeviceNumber(
    major_id: u32,
    minor_id: u32,
    facility: abi.Facility,
) DeviceEncodingResult {
    const value = uapi_dev_t.encode(major_id, minor_id) catch |err| return .{
        .value = 0,
        .status = deviceEncodeStatus(err, facility),
    };
    return .{
        .value = value,
        .status = ok(facility),
    };
}

pub fn lastDeviceNumberInRange(
    major_id: u32,
    first_minor: u32,
    count: u32,
    facility: abi.Facility,
) DeviceEncodingResult {
    const value = uapi_dev_t.lastInRange(major_id, first_minor, count) catch |err| return .{
        .value = 0,
        .status = deviceEncodeStatus(err, facility),
    };
    return .{
        .value = value,
        .status = ok(facility),
    };
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

fn deviceEncodeStatus(err: uapi_dev_t.EncodeError, facility: abi.Facility) abi.ExportStatus {
    const code: i32 = switch (err) {
        error.MajorOutOfRange, error.MinorOutOfRange => -22,
        error.RangeExhausted => -34,
    };
    return errno(code, facility);
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

    try std.testing.expect(isCanonicalHeader(canonical));
    try std.testing.expect(isCompatibleHeader(canonical));
    try std.testing.expectEqual(HeaderCompatibility.canonical, headerCompatibility(canonical).?);

    const accepted_canonical = acceptHeader(canonical).?;
    try std.testing.expect(accepted_canonical.isCanonical());
    try std.testing.expect(!accepted_canonical.extendsBoundary());
    try std.testing.expectEqual(canonical, accepted_canonical.canonical);

    try std.testing.expect(!isCanonicalHeader(future_compatible));
    try std.testing.expect(isCompatibleHeader(future_compatible));
    try std.testing.expectEqual(HeaderCompatibility.future_compatible, headerCompatibility(future_compatible).?);

    const accepted_future = acceptHeader(future_compatible).?;
    try std.testing.expect(!accepted_future.isCanonical());
    try std.testing.expect(accepted_future.extendsBoundary());
    try std.testing.expectEqual(boundaryHeader(0x22), accepted_future.canonical);
    try std.testing.expectEqual(boundaryHeader(0x22), canonicalizeHeader(future_compatible).?);

    try std.testing.expect(headerCompatibility(mismatched_version) == null);
    try std.testing.expect(acceptHeader(mismatched_version) == null);
    try std.testing.expect(!isCompatibleHeader(mismatched_version));
    try std.testing.expect(canonicalizeHeader(mismatched_version) == null);
}

test "phase3 export shim relays compatibility through explicit status packets" {
    const canonical = boundaryHeader(0x66);
    const future_compatible = compatibleHeader(header_size + 32, 0x66);
    const undersized = compatibleHeader(header_size - 1, 0x66);
    const version_mismatch = versionedHeader(header_size, abi_version + 1, 0x66);

    const canonical_status = compatibilityStatus(canonical, -22, .kernel);
    const future_status = compatibilityStatus(future_compatible, -75, .helpers);
    const undersized_status = compatibilityStatus(undersized, -22, .drivers);
    const mismatch_status = compatibilityStatus(version_mismatch, -71, .kernel);

    try std.testing.expect(isOk(canonical_status));
    try std.testing.expect(isOk(future_status));
    try std.testing.expectEqual(@as(i32, 0), canonical_status.code);
    try std.testing.expectEqual(@as(i32, 0), future_status.code);

    try std.testing.expect(!isOk(undersized_status));
    try std.testing.expectEqual(@as(i32, -22), undersized_status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), undersized_status.flags);

    try std.testing.expect(!isOk(mismatch_status));
    try std.testing.expectEqual(@as(i32, -71), mismatch_status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), mismatch_status.flags);
}

test "phase3 export shim evaluation keeps compatibility evidence and status together" {
    const canonical = boundaryHeader(0x77);
    const future_compatible = compatibleHeader(header_size + 24, 0x77);
    const version_mismatch = versionedHeader(header_size, abi_version + 1, 0x77);

    const accepted = evaluateHeader(future_compatible, -75, .helpers);
    try std.testing.expect(accepted.evaluation.isAccepted());
    try std.testing.expectEqual(future_compatible, accepted.evaluation.requested);
    try std.testing.expect(accepted.evaluation.extendsBoundary());
    try std.testing.expectEqual(@as(u32, 24), accepted.evaluation.requestedExtraBytes().?);
    try std.testing.expectEqual(boundaryHeader(0x77), accepted.evaluation.acceptance.?.canonical);
    try std.testing.expect(isOk(accepted.status));

    const direct_canonical = evaluateHeader(canonical, -22, .kernel);
    try std.testing.expect(direct_canonical.evaluation.isAccepted());
    try std.testing.expect(!direct_canonical.evaluation.extendsBoundary());
    try std.testing.expectEqual(@as(u32, 0), direct_canonical.evaluation.requestedExtraBytes().?);
    try std.testing.expectEqual(@as(u32, 24), requestedExtraBytes(future_compatible).?);
    try std.testing.expect(extendsBoundary(future_compatible));
    try std.testing.expect(!extendsBoundary(canonical));

    const rejected = evaluateHeader(version_mismatch, -71, .kernel);
    try std.testing.expectEqual(version_mismatch, rejected.evaluation.requested);
    try std.testing.expect(!rejected.evaluation.isAccepted());
    try std.testing.expect(!rejected.evaluation.extendsBoundary());
    try std.testing.expect(rejected.evaluation.requestedExtraBytes() == null);
    try std.testing.expect(requestedExtraBytes(version_mismatch) == null);
    try std.testing.expectEqual(@as(i32, -71), rejected.status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), rejected.status.flags);
}

test "phase3 export shim keeps dev_t starter relay status explicit" {
    const encoded = encodeDeviceNumber(42, 7, .drivers);
    try std.testing.expect(isOk(encoded.status));
    try std.testing.expectEqual((@as(u32, 42) << uapi_dev_t.minor_bits) | 7, encoded.value);

    const range_last = lastDeviceNumberInRange(42, 7, 4, .helpers);
    try std.testing.expect(isOk(range_last.status));
    try std.testing.expectEqual((@as(u32, 42) << uapi_dev_t.minor_bits) | 10, range_last.value);

    const bad_major = encodeDeviceNumber(uapi_dev_t.major_max + 1, 0, .kernel);
    try std.testing.expect(!isOk(bad_major.status));
    try std.testing.expectEqual(@as(i32, -22), bad_major.status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), bad_major.status.flags);

    const exhausted = lastDeviceNumberInRange(42, uapi_dev_t.minor_mask - 1, 3, .helpers);
    try std.testing.expect(!isOk(exhausted.status));
    try std.testing.expectEqual(@as(i32, -34), exhausted.status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), exhausted.status.flags);
}
