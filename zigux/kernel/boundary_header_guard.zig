const std = @import("std");
const abi = @import("abi_bindings");

pub const HeaderAdmissionError = error{
    StaleAbiVersion,
    UndersizedHeader,
    ExtendedHeader,
};

pub const HeaderAdmissionKind = enum(u8) {
    canonical,
    compatible_extension,
};

pub const HeaderAdmission = struct {
    kind: HeaderAdmissionKind,
    requested_extra_bytes: u32,
    flags: u16,

    pub fn isCanonical(self: HeaderAdmission) bool {
        return self.kind == .canonical;
    }

    pub fn extendsBoundary(self: HeaderAdmission) bool {
        return self.kind == .compatible_extension;
    }
};

pub fn canonicalBoundaryHeaderSize() u32 {
    return @as(u32, @intCast(abi.boundary_header_size));
}

pub fn classifyBoundaryHeader(header: abi.BoundaryHeader) ?HeaderAdmission {
    if (!abi.headerIsCompatible(header)) return null;

    return .{
        .kind = if (abi.headerIsCanonical(header)) .canonical else .compatible_extension,
        .requested_extra_bytes = abi.requestedExtraBytes(header),
        .flags = header.flags,
    };
}

pub fn requireCompatibleBoundaryHeader(header: abi.BoundaryHeader) HeaderAdmissionError!HeaderAdmission {
    if (!abi.headerHasCurrentAbiVersion(header.abi_version)) {
        return error.StaleAbiVersion;
    }
    if (header.size < canonicalBoundaryHeaderSize()) {
        return error.UndersizedHeader;
    }
    return classifyBoundaryHeader(header).?;
}

pub fn requireCanonicalBoundaryHeader(header: abi.BoundaryHeader) HeaderAdmissionError!HeaderAdmission {
    const admission = try requireCompatibleBoundaryHeader(header);
    if (!admission.isCanonical()) return error.ExtendedHeader;
    return admission;
}

pub fn canonicalizeAdmittedBoundaryHeader(header: abi.BoundaryHeader) HeaderAdmissionError!abi.BoundaryHeader {
    _ = try requireCompatibleBoundaryHeader(header);
    return abi.canonicalizeHeader(header);
}

test "boundary header guard admits canonical headers" {
    const header = abi.defaultHeader(0x41);
    const admission = try requireCanonicalBoundaryHeader(header);

    try std.testing.expect(admission.isCanonical());
    try std.testing.expect(!admission.extendsBoundary());
    try std.testing.expectEqual(@as(u32, 0), admission.requested_extra_bytes);
    try std.testing.expectEqual(@as(u16, 0x41), admission.flags);
    try std.testing.expectEqual(@as(?HeaderAdmissionKind, .canonical), classifyBoundaryHeader(header).?.kind);
}

test "boundary header guard admits compatible extensions without canonical admission" {
    const header = abi.compatibleHeader(canonicalBoundaryHeaderSize() + 12, 0x55);
    const admission = try requireCompatibleBoundaryHeader(header);
    const canonicalized = try canonicalizeAdmittedBoundaryHeader(header);

    try std.testing.expect(!admission.isCanonical());
    try std.testing.expect(admission.extendsBoundary());
    try std.testing.expectEqual(@as(u32, 12), admission.requested_extra_bytes);
    try std.testing.expectEqual(@as(u16, 0x55), admission.flags);
    try std.testing.expectError(error.ExtendedHeader, requireCanonicalBoundaryHeader(header));
    try std.testing.expect(abi.headerIsCanonical(canonicalized));
    try std.testing.expectEqual(@as(u16, 0x55), canonicalized.flags);
}

test "boundary header guard rejects stale and undersized headers before admission" {
    const stale = abi.BoundaryHeader{
        .size = canonicalBoundaryHeaderSize(),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0,
    };
    const undersized = abi.BoundaryHeader{
        .size = canonicalBoundaryHeaderSize() - 1,
        .abi_version = abi.ABI_VERSION,
        .flags = 0,
    };

    try std.testing.expectError(error.StaleAbiVersion, requireCompatibleBoundaryHeader(stale));
    try std.testing.expectError(error.UndersizedHeader, requireCompatibleBoundaryHeader(undersized));
    try std.testing.expectEqual(@as(?HeaderAdmission, null), classifyBoundaryHeader(stale));
    try std.testing.expectEqual(@as(?HeaderAdmission, null), classifyBoundaryHeader(undersized));
}
