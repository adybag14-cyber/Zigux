const std = @import("std");

const abi = @import("abi_bindings");

pub const Header = abi.BoundaryHeader;

pub const Compatibility = enum {
    canonical,
    future_compatible,
};

pub const AcceptedHeader = struct {
    compatibility: Compatibility,
    canonical: Header,
};

pub const HeaderEvaluation = struct {
    requested: Header,
    acceptance: ?AcceptedHeader,

    pub fn isAccepted(self: @This()) bool {
        return self.acceptance != null;
    }
};

pub const abi_version: u16 = abi.ABI_VERSION;
pub const header_size: u32 = @sizeOf(Header);

pub fn versionedHeader(size: u32, version: u16, flags: u16) Header {
    return .{
        .size = size,
        .abi_version = version,
        .flags = flags,
    };
}

pub fn canonicalHeader(flags: u16) Header {
    return abi.defaultHeader(flags);
}

pub fn boundaryHeader(flags: u16) Header {
    return canonicalHeader(flags);
}

pub fn compatibleHeader(size: u32, flags: u16) Header {
    return versionedHeader(size, abi_version, flags);
}

pub fn isCurrentAbiVersion(version: u16) bool {
    return version == abi_version;
}

pub fn isCompatibleSize(size: u32) bool {
    return size >= header_size;
}

pub fn isCanonicalSize(size: u32) bool {
    return size == header_size;
}

pub fn compatibility(header: Header) ?Compatibility {
    if (!isCurrentAbiVersion(header.abi_version)) return null;
    if (isCanonicalSize(header.size)) return .canonical;
    if (isCompatibleSize(header.size)) return .future_compatible;
    return null;
}

pub fn acceptHeader(header: Header) ?AcceptedHeader {
    const kind = compatibility(header) orelse return null;
    return .{
        .compatibility = kind,
        .canonical = canonicalHeader(header.flags),
    };
}

pub fn evaluateHeader(header: Header) HeaderEvaluation {
    return .{
        .requested = header,
        .acceptance = acceptHeader(header),
    };
}

pub fn isCompatible(header: Header) bool {
    return compatibility(header) != null;
}

pub fn isCanonical(header: Header) bool {
    return compatibility(header) == .canonical;
}

pub fn canonicalizeHeader(header: Header) ?Header {
    const accepted = acceptHeader(header) orelse return null;
    return accepted.canonical;
}

test "phase3 uapi version follows abi version" {
    try std.testing.expectEqual(abi.ABI_VERSION, abi_version);
}

test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes" {
    const canonical = boundaryHeader(0x11);
    const future_compatible = compatibleHeader(header_size + 8, 0x11);
    const undersized = compatibleHeader(header_size - 1, 0x11);
    const mismatched_version = versionedHeader(header_size, abi_version + 1, 0x11);

    try std.testing.expect(isCanonicalSize(canonical.size));
    try std.testing.expect(isCurrentAbiVersion(canonical.abi_version));
    try std.testing.expect(isCanonical(canonical));
    try std.testing.expect(isCompatible(canonical));
    try std.testing.expectEqual(Compatibility.canonical, compatibility(canonical).?);

    try std.testing.expect(isCompatibleSize(future_compatible.size));
    try std.testing.expect(!isCanonicalSize(future_compatible.size));
    try std.testing.expect(isCompatible(future_compatible));
    try std.testing.expect(!isCanonical(future_compatible));
    try std.testing.expectEqual(Compatibility.future_compatible, compatibility(future_compatible).?);

    try std.testing.expect(!isCompatibleSize(undersized.size));
    try std.testing.expect(compatibility(undersized) == null);
    try std.testing.expect(!isCurrentAbiVersion(mismatched_version.abi_version));
    try std.testing.expect(compatibility(mismatched_version) == null);
}

test "phase3 uapi canonicalizes compatible headers without widening the boundary" {
    const future_compatible = compatibleHeader(header_size + 16, 0x44);
    const canonical = canonicalizeHeader(future_compatible).?;

    try std.testing.expectEqual(boundaryHeader(0x44), canonical);
    try std.testing.expectEqual(header_size, canonical.size);
    try std.testing.expectEqual(abi_version, canonical.abi_version);
    try std.testing.expectEqual(@as(u16, 0x44), canonical.flags);
}

test "phase3 uapi evaluation keeps requested boundary shape explicit" {
    const canonical = boundaryHeader(0x77);
    const future_compatible = compatibleHeader(header_size + 16, 0x77);
    const mismatched_version = versionedHeader(header_size, abi_version + 1, 0x77);

    const accepted_canonical = acceptHeader(canonical).?;
    const accepted_future = acceptHeader(future_compatible).?;
    const rejected = acceptHeader(mismatched_version);

    try std.testing.expectEqual(Compatibility.canonical, accepted_canonical.compatibility);
    try std.testing.expectEqual(canonical, accepted_canonical.canonical);
    try std.testing.expectEqual(Compatibility.future_compatible, accepted_future.compatibility);
    try std.testing.expectEqual(canonical, accepted_future.canonical);
    try std.testing.expect(rejected == null);

    const canonical_evaluation = evaluateHeader(canonical);
    const future_evaluation = evaluateHeader(future_compatible);
    const mismatch_evaluation = evaluateHeader(mismatched_version);

    try std.testing.expectEqual(canonical, canonical_evaluation.requested);
    try std.testing.expect(canonical_evaluation.isAccepted());
    try std.testing.expectEqual(future_compatible, future_evaluation.requested);
    try std.testing.expect(future_evaluation.isAccepted());
    try std.testing.expectEqual(mismatched_version, mismatch_evaluation.requested);
    try std.testing.expect(!mismatch_evaluation.isAccepted());
}
