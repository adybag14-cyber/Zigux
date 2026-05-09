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

    pub fn compatibility(self: @This()) ?Compatibility {
        return if (self.acceptance) |accepted| accepted.compatibility else null;
    }

    pub fn canonical(self: @This()) ?Header {
        return if (self.acceptance) |accepted| accepted.canonical else null;
    }

    pub fn sizeDelta(self: @This()) i64 {
        return @as(i64, self.requested.size) - @as(i64, header_size);
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

pub fn isCompatible(header: Header) bool {
    return compatibility(header) != null;
}

pub fn isCanonical(header: Header) bool {
    return compatibility(header) == .canonical;
}

pub fn acceptHeader(header: Header) ?AcceptedHeader {
    const mode = compatibility(header) orelse return null;
    return .{
        .compatibility = mode,
        .canonical = canonicalHeader(header.flags),
    };
}

pub fn canonicalizeHeader(header: Header) ?Header {
    return (acceptHeader(header) orelse return null).canonical;
}

pub fn evaluateHeader(header: Header) HeaderEvaluation {
    return .{
        .requested = header,
        .acceptance = acceptHeader(header),
    };
}

test "phase3 uapi version follows abi version" {
    try std.testing.expectEqual(abi.ABI_VERSION, abi_version);
}

test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes" {
    const canonical = boundaryHeader(0x11);
    const future_compatible = compatibleHeader(header_size + 8, 0x11);
    const undersized = compatibleHeader(header_size - 1, 0x11);
    const mismatched_version = versionedHeader(header_size, abi_version + 1, 0x11);
    const accepted_canonical = acceptHeader(canonical).?;
    const accepted_future = acceptHeader(future_compatible).?;

    try std.testing.expect(isCanonicalSize(canonical.size));
    try std.testing.expect(isCurrentAbiVersion(canonical.abi_version));
    try std.testing.expect(isCanonical(canonical));
    try std.testing.expect(isCompatible(canonical));
    try std.testing.expectEqual(Compatibility.canonical, compatibility(canonical).?);
    try std.testing.expectEqual(Compatibility.canonical, accepted_canonical.compatibility);
    try std.testing.expectEqual(canonical, accepted_canonical.canonical);

    try std.testing.expect(isCompatibleSize(future_compatible.size));
    try std.testing.expect(!isCanonicalSize(future_compatible.size));
    try std.testing.expect(isCompatible(future_compatible));
    try std.testing.expect(!isCanonical(future_compatible));
    try std.testing.expectEqual(Compatibility.future_compatible, compatibility(future_compatible).?);
    try std.testing.expectEqual(Compatibility.future_compatible, accepted_future.compatibility);
    try std.testing.expectEqual(boundaryHeader(0x11), accepted_future.canonical);

    try std.testing.expect(!isCompatibleSize(undersized.size));
    try std.testing.expect(compatibility(undersized) == null);
    try std.testing.expect(acceptHeader(undersized) == null);

    try std.testing.expect(!isCurrentAbiVersion(mismatched_version.abi_version));
    try std.testing.expect(compatibility(mismatched_version) == null);
    try std.testing.expect(acceptHeader(mismatched_version) == null);
}

test "phase3 uapi canonicalizes compatible headers without widening the boundary" {
    const future_compatible = compatibleHeader(header_size + 16, 0x44);
    const accepted = acceptHeader(future_compatible).?;
    const canonical = accepted.canonical;

    try std.testing.expectEqual(Compatibility.future_compatible, accepted.compatibility);
    try std.testing.expectEqual(boundaryHeader(0x44), canonical);
    try std.testing.expectEqual(header_size, canonical.size);
    try std.testing.expectEqual(abi_version, canonical.abi_version);
    try std.testing.expectEqual(@as(u16, 0x44), canonical.flags);
}

test "phase3 uapi evaluation keeps requested boundary shape explicit" {
    const canonical = evaluateHeader(boundaryHeader(0x19));
    const future_compatible = evaluateHeader(compatibleHeader(header_size + 24, 0x19));
    const undersized = evaluateHeader(compatibleHeader(header_size - 1, 0x19));

    try std.testing.expect(canonical.isAccepted());
    try std.testing.expectEqual(Compatibility.canonical, canonical.compatibility().?);
    try std.testing.expectEqual(boundaryHeader(0x19), canonical.canonical().?);
    try std.testing.expectEqual(@as(i64, 0), canonical.sizeDelta());

    try std.testing.expect(future_compatible.isAccepted());
    try std.testing.expectEqual(Compatibility.future_compatible, future_compatible.compatibility().?);
    try std.testing.expectEqual(boundaryHeader(0x19), future_compatible.canonical().?);
    try std.testing.expectEqual(@as(i64, 24), future_compatible.sizeDelta());

    try std.testing.expect(!undersized.isAccepted());
    try std.testing.expect(undersized.compatibility() == null);
    try std.testing.expect(undersized.canonical() == null);
    try std.testing.expectEqual(@as(i64, -1), undersized.sizeDelta());
}
